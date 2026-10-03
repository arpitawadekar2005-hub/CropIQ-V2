from fastapi import (
    FastAPI,
    HTTPException,
    UploadFile,
    File,
    WebSocket,
    WebSocketDisconnect,
)

import gc
import io
import os

# Keep TensorFlow's CPU/thread memory overhead as low as practical on
# Render's 512 MB free instance.
os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "2")
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("TF_NUM_INTRAOP_THREADS", "1")
os.environ.setdefault("TF_NUM_INTEROP_THREADS", "1")

import numpy as np
import tensorflow as tf
from PIL import Image
from fastapi.responses import Response
from pydantic import BaseModel

# Set these before loading any model.
tf.config.threading.set_intra_op_parallelism_threads(1)
tf.config.threading.set_inter_op_parallelism_threads(1)

# =====================================================
# PATHS
# =====================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, "model")

CLASSIFIER_PATH = os.path.join(
    MODEL_DIR,
    "cropiq_final_efficientnetb0.keras",
)

UNET_MODEL_PATH = os.path.join(
    MODEL_DIR,
    "CropIQ_FINAL_UNETPP_BEST.keras",
)

# =====================================================
# CLASSIFIER
# =====================================================

class_names = [
    "Guava_Anthracnose",
    "Guava_fruit_fly",
    "Guava_healthy_guava",
    "Pomegranate_Alternaria",
    "Pomegranate_Anthracnose",
    "Pomegranate_Cercospora",
    "Pomegranate_Healthy",
]

HEALTHY_CLASSES = {
    "Guava_healthy_guava",
    "Pomegranate_Healthy",
}

CLASS_DETAILS = {
    "Guava_Anthracnose": {
        "crop": "Guava",
        "disease": "Anthracnose",
    },
    "Guava_fruit_fly": {
        "crop": "Guava",
        "disease": "Fruit fly",
    },
    "Guava_healthy_guava": {
        "crop": "Guava",
        "disease": "Healthy",
    },
    "Pomegranate_Alternaria": {
        "crop": "Pomegranate",
        "disease": "Alternaria",
    },
    "Pomegranate_Anthracnose": {
        "crop": "Pomegranate",
        "disease": "Anthracnose",
    },
    "Pomegranate_Cercospora": {
        "crop": "Pomegranate",
        "disease": "Cercospora",
    },
    "Pomegranate_Healthy": {
        "crop": "Pomegranate",
        "disease": "Healthy",
    },
}

# Only one AI model is kept in memory at a time.
classifier_model = None
segmenter_model = None


def load_classifier():
    global classifier_model

    if classifier_model is None:
        print("Loading CropIQ EfficientNetB0 classifier...")
        classifier_model = tf.keras.models.load_model(
            CLASSIFIER_PATH,
            compile=False,
        )
        print("CropIQ AI model loaded successfully")

    return classifier_model


def unload_classifier():
    global classifier_model

    if classifier_model is not None:
        del classifier_model
        classifier_model = None

    tf.keras.backend.clear_session()
    gc.collect()


def load_segmenter():
    global segmenter_model

    if segmenter_model is None:
        print("Loading CropIQ U-Net++ segmentation model...")
        segmenter_model = tf.keras.models.load_model(
            UNET_MODEL_PATH,
            compile=False,
        )
        print("CropIQ U-Net++ model loaded successfully")

    return segmenter_model


def unload_segmenter():
    global segmenter_model

    if segmenter_model is not None:
        del segmenter_model
        segmenter_model = None

    tf.keras.backend.clear_session()
    gc.collect()


def predict_image(image_data):
    image = Image.open(io.BytesIO(image_data)).convert("RGB")
    image = image.resize((224, 224))

    image_array = np.array(image, dtype=np.float32)
    image_array = np.expand_dims(image_array, axis=0)

    model = load_classifier()

    predictions = model.predict(
        image_array,
        batch_size=1,
        verbose=0,
    )

    predicted_index = int(np.argmax(predictions[0]))
    confidence = float(predictions[0][predicted_index]) * 100.0
    predicted_class = class_names[predicted_index]

    # Return plain Python values; the model can then be released before
    # U-Net++ is loaded.
    del predictions
    del image_array
    gc.collect()

    return predicted_class, confidence


# =====================================================
# DOSAGE RULES
# =====================================================
# These are the rules supplied for the CropIQ workflow.
# Final physical application must still be checked against the
# pesticide product label, sprayer calibration, and applicable rules.

DOSAGE_RULES = {
    ("Pomegranate", "Anthracnose"): {
        "pesticide": "Kitazin 48% EC",
        "base_dosage_ml": 650.0,
    },
    ("Pomegranate", "Alternaria"): {
        "pesticide": "Mancozeb",
        "base_dosage_ml": 650.0,
    },
    ("Pomegranate", "Cercospora"): {
        "pesticide": "Mancozeb",
        "base_dosage_ml": 650.0,
    },
    ("Guava", "Anthracnose"): {
        "pesticide": "Copper oxychloride",
        "base_dosage_ml": 2800.0,
    },
    ("Guava", "Fruit fly"): {
        "pesticide": "Dimethoate 30 EC + jaggery/molasses bait",
        "base_dosage_ml": 90.0,
    },
}


def segment_image(image_data):
    """Run the trained 3-class U-Net++ model on one image.

    Model classes:
        0 = background
        1 = fruit
        2 = disease
    """

    image = Image.open(io.BytesIO(image_data)).convert("RGB")
    image = image.resize((512, 512))

    image_array = np.array(image, dtype=np.float32)

    # Exact preprocessing used by the U-Net++ notebook.
    image_array = tf.keras.applications.mobilenet_v2.preprocess_input(
        image_array
    )
    image_array = np.expand_dims(image_array, axis=0)

    model = load_segmenter()

    predictions = model.predict(
        image_array,
        batch_size=1,
        verbose=0,
    )

    pred_labels = np.argmax(predictions[0], axis=-1)

    fruit_area = int(np.sum(pred_labels == 1))
    disease_area = int(np.sum(pred_labels == 2))

    del predictions
    del pred_labels
    del image_array
    gc.collect()

    return fruit_area, disease_area


def calculate_dosage(crop, disease, severity_percent):
    rule = DOSAGE_RULES.get((crop, disease))

    if rule is None:
        return None, 0.0, 0.0

    base_dosage = float(rule["base_dosage_ml"])
    final_dosage = base_dosage * float(severity_percent) / 100.0

    return (
        rule["pesticide"],
        base_dosage,
        final_dosage,
    )


def analyze_image(image_data):
    """Complete CropIQ pipeline.

    1. EfficientNet classification
    2. Healthy early-stop
    3. U-Net++ segmentation for disease cases
    4. Severity calculation
    5. Dosage rule lookup
    """

    global ai_prediction
    global ai_confidence
    global ai_crop
    global ai_disease
    global ai_is_healthy
    global segmentation_performed
    global fruit_area_pixels
    global disease_area_pixels
    global severity_percent
    global pesticide
    global base_dosage_ml
    global recommended_dosage_ml
    global spray_required
    global ai_message

    # Reset analysis state for the new image.
    ai_prediction = None
    ai_confidence = 0.0
    ai_crop = None
    ai_disease = None
    ai_is_healthy = False
    segmentation_performed = False
    fruit_area_pixels = 0
    disease_area_pixels = 0
    severity_percent = 0.0
    pesticide = None
    base_dosage_ml = 0.0
    recommended_dosage_ml = 0.0
    spray_required = False
    ai_message = "Analyzing image..."

    # -------------------------------------------------
    # 1. CLASSIFICATION
    # -------------------------------------------------

    try:
        prediction, confidence = predict_image(image_data)
    finally:
        # Critical for the Render 512 MB instance: never keep
        # EfficientNet resident while U-Net++ is loaded.
        unload_classifier()

    ai_prediction = prediction
    ai_confidence = float(confidence)

    details = CLASS_DETAILS.get(prediction)

    if details is None:
        ai_message = "Unknown classification returned by the AI model."
        return {
            "message": ai_message,
            "prediction": ai_prediction,
            "confidence": ai_confidence,
            "crop": ai_crop,
            "disease": ai_disease,
            "healthy": False,
            "segmentation_performed": False,
            "fruit_area_pixels": 0,
            "disease_area_pixels": 0,
            "severity_percent": 0.0,
            "pesticide": None,
            "base_dosage_ml": 0.0,
            "recommended_dosage_ml": 0.0,
            "spray_required": False,
        }

    ai_crop = details["crop"]
    ai_disease = details["disease"]

    # -------------------------------------------------
    # 2. HEALTHY EARLY STOP
    # -------------------------------------------------

    if prediction in HEALTHY_CLASSES:
        ai_is_healthy = True
        ai_message = f"{ai_crop} is healthy. No spraying required."

        return {
            "message": ai_message,
            "prediction": ai_prediction,
            "confidence": ai_confidence,
            "crop": ai_crop,
            "disease": "Healthy",
            "healthy": True,
            "segmentation_performed": False,
            "fruit_area_pixels": 0,
            "disease_area_pixels": 0,
            "severity_percent": 0.0,
            "pesticide": None,
            "base_dosage_ml": 0.0,
            "recommended_dosage_ml": 0.0,
            "spray_required": False,
        }

    # -------------------------------------------------
    # 3. U-NET++ SEGMENTATION
    # -------------------------------------------------

    try:
        fruit_area, disease_area = segment_image(image_data)
    finally:
        # Do not leave the large segmentation model resident after
        # the request has finished.
        unload_segmenter()

    segmentation_performed = True
    fruit_area_pixels = int(fruit_area)
    disease_area_pixels = int(disease_area)

    # Avoid division by zero if the model finds no fruit.
    if fruit_area_pixels > 0:
        severity_percent = (
            disease_area_pixels / fruit_area_pixels
        ) * 100.0
    else:
        severity_percent = 0.0

    # Keep severity in a sensible percentage range.
    severity_percent = max(
        0.0,
        min(100.0, float(severity_percent)),
    )

    # -------------------------------------------------
    # 4. DOSAGE RULE
    # -------------------------------------------------

    pesticide, base_dosage_ml, recommended_dosage_ml = calculate_dosage(
        ai_crop,
        ai_disease,
        severity_percent,
    )

    spray_required = (
        pesticide is not None
        and recommended_dosage_ml > 0.0
    )

    if pesticide is None:
        ai_message = (
            f"{ai_disease} detected, but no dosage rule is configured."
        )
        spray_required = False
    elif spray_required:
        ai_message = (
            f"{ai_disease} detected. "
            f"Severity: {severity_percent:.2f}%. "
            f"Recommended dosage: {recommended_dosage_ml:.2f} ml."
        )
    else:
        ai_message = (
            f"{ai_disease} detected, but the calculated dosage is zero."
        )

    return {
        "message": ai_message,
        "prediction": ai_prediction,
        "confidence": ai_confidence,
        "crop": ai_crop,
        "disease": ai_disease,
        "healthy": False,
        "segmentation_performed": segmentation_performed,
        "fruit_area_pixels": fruit_area_pixels,
        "disease_area_pixels": disease_area_pixels,
        "severity_percent": severity_percent,
        "pesticide": pesticide,
        "base_dosage_ml": base_dosage_ml,
        "recommended_dosage_ml": recommended_dosage_ml,
        "spray_required": spray_required,
    }


# =====================================================
# APP
# =====================================================

app = FastAPI(title="CropIQ API")


# =====================================================
# RASPBERRY PI STATE
# =====================================================

spray_command = None
spray_status = "Ready"
sprayed_amount = 0.0


# =====================================================
# CAMERA / AI STATE
# =====================================================

latest_image = None
latest_image_type = "image/jpeg"

ai_prediction = None
ai_confidence = 0.0
ai_crop = None
ai_disease = None
ai_is_healthy = False
segmentation_performed = False
fruit_area_pixels = 0
disease_area_pixels = 0
severity_percent = 0.0
pesticide = None
base_dosage_ml = 0.0
recommended_dosage_ml = 0.0
spray_required = False
ai_message = "Awaiting Analysis"


# =====================================================
# ESP32 ROVER STATE
# =====================================================

esp32_socket = None
esp32_online = False
rover_status = "STOPPED"
rover_speed = 50


# =====================================================
# REQUEST MODELS
# =====================================================

class SprayRequest(BaseModel):
    amount_ml: float


class StatusRequest(BaseModel):
    status: str
    amount_ml: float = 0.0


class RoverRequest(BaseModel):
    command: str
    speed: int = 50


# =====================================================
# HOME
# =====================================================

@app.get("/")
def home():
    return {
        "project": "CropIQ",
        "message": "CropIQ backend is running",
    }


# =====================================================
# TEST
# =====================================================

@app.get("/test")
def test():
    return {
        "status": "success",
        "message": "Backend connection is working",
    }


# =====================================================
# SYSTEM STATE
# =====================================================

@app.get("/state")
def get_state():
    return {
        "raspberry_pi": {
            "spray_status": spray_status,
            "sprayed_amount": sprayed_amount,
            "command_pending": spray_command is not None,
            "image_available": latest_image is not None,
            "ai_prediction": ai_prediction,
            "ai_confidence": ai_confidence,
            "crop": ai_crop,
            "disease": ai_disease,
            "healthy": ai_is_healthy,
            "segmentation_performed": segmentation_performed,
            "fruit_area_pixels": fruit_area_pixels,
            "disease_area_pixels": disease_area_pixels,
            "severity_percent": severity_percent,
            "pesticide": pesticide,
            "base_dosage_ml": base_dosage_ml,
            "recommended_dosage_ml": recommended_dosage_ml,
            "spray_required": spray_required,
            "ai_message": ai_message,
        },
        "esp32": {
            "online": esp32_online,
            "rover_status": rover_status,
            "speed": rover_speed,
        },
    }


# =====================================================
# SPRAY COMMAND
# =====================================================

@app.post("/spray")
def spray(request: SprayRequest):
    global spray_command
    global spray_status
    global sprayed_amount

    amount = float(request.amount_ml)

    if amount <= 0:
        raise HTTPException(
            status_code=400,
            detail="Dosage must be greater than 0 ml",
        )

    # The dashboard should only send the AI-recommended dosage.
    if not spray_required:
        raise HTTPException(
            status_code=400,
            detail="No active AI spray recommendation is available",
        )

    if recommended_dosage_ml <= 0:
        raise HTTPException(
            status_code=400,
            detail="AI recommended dosage is not valid",
        )

    # Prevent accidental manual values from bypassing the AI result.
    tolerance = max(1.0, recommended_dosage_ml * 0.05)
    if abs(amount - recommended_dosage_ml) > tolerance:
        raise HTTPException(
            status_code=400,
            detail=(
                "Spray amount must match the AI recommended dosage "
                f"({recommended_dosage_ml:.2f} ml) within 5%"
            ),
        )

    if spray_command is not None:
        raise HTTPException(
            status_code=409,
            detail="Another Raspberry Pi command is pending",
        )

    if spray_status == "Spraying...":
        raise HTTPException(
            status_code=409,
            detail="Spraying is already in progress",
        )

    spray_command = {
        "command": "SPRAY",
        "amount_ml": amount,
    }

    sprayed_amount = 0.0
    spray_status = "Spraying..."

    return {
        "message": "Spray command created",
        "amount_ml": amount,
        "status": spray_status,
    }


# =====================================================
# CAPTURE COMMAND
# =====================================================

@app.post("/capture")
def capture():
    global spray_command

    if spray_command is not None:
        raise HTTPException(
            status_code=409,
            detail="Another Raspberry Pi command is pending",
        )

    if spray_status == "Spraying...":
        raise HTTPException(
            status_code=409,
            detail="Cannot capture while spraying",
        )

    spray_command = {"command": "CAPTURE"}

    return {
        "message": "Capture command created",
        "command": "CAPTURE",
    }


# =====================================================
# RASPBERRY PI GETS COMMAND
# =====================================================

@app.get("/command")
def get_command():
    global spray_command

    if spray_command is None:
        return {"command": None}

    command = spray_command
    spray_command = None

    return command


# =====================================================
# RASPBERRY PI SENDS STATUS
# =====================================================

@app.post("/status")
def update_status(request: StatusRequest):
    global spray_status
    global sprayed_amount

    spray_status = request.status
    sprayed_amount = request.amount_ml

    return {
        "message": "Status updated",
        "status": spray_status,
        "amount_ml": sprayed_amount,
    }


# =====================================================
# RASPBERRY PI UPLOADS IMAGE
# =====================================================

@app.post("/upload-image")
async def upload_image(file: UploadFile = File(...)):
    global latest_image
    global latest_image_type

    image_data = await file.read()

    if not image_data:
        raise HTTPException(
            status_code=400,
            detail="Empty image",
        )

    try:
        result = analyze_image(image_data)
    except Exception as e:
        # Normal Python/TensorFlow exceptions are returned as 500.
        # A true Render OOM is killed by the platform and cannot be
        # caught here, which is why model unloading is important.
        print("AI analysis failed:", repr(e))
        raise HTTPException(
            status_code=500,
            detail=f"AI analysis failed: {str(e)}",
        )

    latest_image = image_data
    latest_image_type = file.content_type or "image/jpeg"

    return result


# =====================================================
# MANUAL IMAGE PREDICTION
# =====================================================

@app.post("/predict-manual")
async def predict_manual(file: UploadFile = File(...)):
    global latest_image
    global latest_image_type

    image_data = await file.read()

    if not image_data:
        raise HTTPException(
            status_code=400,
            detail="Empty image",
        )

    try:
        result = analyze_image(image_data)
    except Exception as e:
        print("AI analysis failed:", repr(e))
        raise HTTPException(
            status_code=500,
            detail=f"AI analysis failed: {str(e)}",
        )

    latest_image = image_data
    latest_image_type = file.content_type or "image/jpeg"

    return result


# =====================================================
# GET LATEST IMAGE
# =====================================================

@app.get("/latest-image")
def get_latest_image():
    if latest_image is None:
        raise HTTPException(
            status_code=404,
            detail="No image available",
        )

    return Response(
        content=latest_image,
        media_type=latest_image_type,
    )


# =====================================================
# ESP32 WEBSOCKET
# =====================================================

@app.websocket("/ws/esp32")
async def esp32_websocket(websocket: WebSocket):
    global esp32_socket
    global esp32_online
    global rover_status

    await websocket.accept()

    esp32_socket = websocket
    esp32_online = True
    rover_status = "STOPPED"

    print()
    print("==============================")
    print("ESP32 CONNECTED")
    print("==============================")

    try:
        while True:
            message = await websocket.receive_text()
            message = message.strip()

            print("ESP32:", message)

            if message == "ESP32_READY":
                esp32_online = True
                rover_status = "STOPPED"

            elif message == "ROVER_STOPPED":
                rover_status = "STOPPED"

            elif message == "ROVER_FORWARD":
                rover_status = "FORWARD"

            elif message == "ROVER_BACKWARD":
                rover_status = "BACKWARD"

            elif message == "ROVER_LEFT":
                rover_status = "LEFT"

            elif message == "ROVER_RIGHT":
                rover_status = "RIGHT"

    except WebSocketDisconnect:
        print()
        print("ESP32 DISCONNECTED")
        esp32_online = False
        esp32_socket = None
        rover_status = "OFFLINE"

    except Exception as e:
        print("ESP32 WebSocket error:", e)
        esp32_online = False
        esp32_socket = None
        rover_status = "OFFLINE"


# =====================================================
# ROVER CONTROL
# =====================================================

@app.post("/rover")
async def rover_control(request: RoverRequest):
    global esp32_socket
    global esp32_online
    global rover_status
    global rover_speed

    command = request.command.upper().strip()

    allowed_commands = ["F", "B", "L", "R", "S"]

    if command not in allowed_commands:
        raise HTTPException(
            status_code=400,
            detail="Invalid rover command. Use F, B, L, R or S.",
        )

    if not esp32_online or esp32_socket is None:
        raise HTTPException(
            status_code=503,
            detail="ESP32 rover is offline",
        )

    speed = max(0, min(100, request.speed))
    rover_speed = speed

    try:
        await esp32_socket.send_text(command)
    except Exception as e:
        print("Failed to send command:", e)
        esp32_online = False
        esp32_socket = None
        rover_status = "OFFLINE"

        raise HTTPException(
            status_code=503,
            detail="ESP32 connection lost",
        )

    if command == "F":
        rover_status = "FORWARD"
    elif command == "B":
        rover_status = "BACKWARD"
    elif command == "L":
        rover_status = "LEFT"
    elif command == "R":
        rover_status = "RIGHT"
    elif command == "S":
        rover_status = "STOPPED"

    return {
        "message": "Rover command sent",
        "command": command,
        "speed": speed,
        "status": rover_status,
    }
