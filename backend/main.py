from fastapi import (
    FastAPI,
    HTTPException,
    UploadFile,
    File,
    WebSocket,
    WebSocketDisconnect
)

import io
import numpy as np
import tensorflow as tf
from PIL import Image

from fastapi.responses import Response
from pydantic import BaseModel


# =====================================================
# PATHS
# =====================================================

MODEL_DIR = "model"

CLASSIFIER_MODEL_PATH = (
    f"{MODEL_DIR}/cropiq_final_efficientnetb0.keras"
)

UNET_MODEL_PATH = (
    f"{MODEL_DIR}/CropIQ_FINAL_UNETPP_BEST.keras"
)


# =====================================================
# CLASSIFICATION MODEL
# =====================================================

class_names = [
    "Guava_Anthracnose",
    "Guava_fruit_fly",
    "Guava_healthy_guava",
    "Pomegranate_Alternaria",
    "Pomegranate_Anthracnose",
    "Pomegranate_Cercospora",
    "Pomegranate_Healthy"
]

HEALTHY_CLASSES = {
    "Guava_healthy_guava",
    "Pomegranate_Healthy"
}


print("Loading CropIQ classification model...")

model = tf.keras.models.load_model(
    CLASSIFIER_MODEL_PATH,
    compile=False
)

print("CropIQ AI model loaded successfully")


# =====================================================
# U-NET++ SEGMENTATION MODEL
# =====================================================

print("Loading CropIQ U-Net++ model...")

unet_model = tf.keras.models.load_model(
    UNET_MODEL_PATH,
    compile=False
)

print("CropIQ U-Net++ model loaded successfully")


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
# CAMERA STATE
# =====================================================

latest_image = None

latest_image_type = "image/jpeg"


# =====================================================
# AI STATE
# =====================================================

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
# DOSAGE RULE ENGINE
# =====================================================
#
# Rules from the CropIQ pesticide workflow CSV.
#
# Base dosage is stored internally in ml.
#
# Pomegranate:
#   Anthracnose -> Kitazin 48% EC -> 650 ml
#   Alternaria  -> Mancozeb       -> 650 ml
#   Cercospora  -> Mancozeb       -> 650 ml
#
# Guava:
#   Anthracnose -> Copper oxychloride -> 2800 ml
#   Fruit fly   -> Dimethoate 30 EC + jaggery/molasses bait
#                  -> 90 ml
#
# Healthy plants do not have a spray rule.
# =====================================================

DOSAGE_RULES = {

    ("Pomegranate", "Anthracnose"): {
        "pesticide": "Kitazin 48% EC",
        "base_dosage_ml": 650.0
    },

    ("Pomegranate", "Alternaria"): {
        "pesticide": "Mancozeb",
        "base_dosage_ml": 650.0
    },

    ("Pomegranate", "Cercospora"): {
        "pesticide": "Mancozeb",
        "base_dosage_ml": 650.0
    },

    ("Guava", "Anthracnose"): {
        "pesticide": "Copper oxychloride",
        "base_dosage_ml": 2800.0
    },

    ("Guava", "Fruit fly"): {
        "pesticide": (
            "Dimethoate 30 EC + jaggery/molasses bait"
        ),
        "base_dosage_ml": 90.0
    }
}


# =====================================================
# CLASSIFICATION HELPERS
# =====================================================

CLASS_DETAILS = {

    "Guava_Anthracnose": {
        "crop": "Guava",
        "disease": "Anthracnose",
        "healthy": False
    },

    "Guava_fruit_fly": {
        "crop": "Guava",
        "disease": "Fruit fly",
        "healthy": False
    },

    "Guava_healthy_guava": {
        "crop": "Guava",
        "disease": "Healthy",
        "healthy": True
    },

    "Pomegranate_Alternaria": {
        "crop": "Pomegranate",
        "disease": "Alternaria",
        "healthy": False
    },

    "Pomegranate_Anthracnose": {
        "crop": "Pomegranate",
        "disease": "Anthracnose",
        "healthy": False
    },

    "Pomegranate_Cercospora": {
        "crop": "Pomegranate",
        "disease": "Cercospora",
        "healthy": False
    },

    "Pomegranate_Healthy": {
        "crop": "Pomegranate",
        "disease": "Healthy",
        "healthy": True
    }
}


# =====================================================
# CLASSIFICATION
# =====================================================

def predict_image(image_data):

    image = Image.open(
        io.BytesIO(image_data)
    ).convert("RGB")

    image = image.resize(
        (224, 224)
    )

    image_array = np.array(
        image,
        dtype=np.float32
    )

    image_array = np.expand_dims(
        image_array,
        axis=0
    )

    predictions = model.predict(
        image_array,
        verbose=0
    )

    predicted_index = int(
        np.argmax(predictions[0])
    )

    confidence = float(
        predictions[0][predicted_index]
    ) * 100.0

    predicted_class = class_names[
        predicted_index
    ]

    return predicted_class, confidence


# =====================================================
# U-NET++ SEGMENTATION
# =====================================================

def segment_image(image_data):

    image = Image.open(
        io.BytesIO(image_data)
    ).convert("RGB")

    # Exact U-Net++ training input size
    image = image.resize(
        (512, 512)
    )

    image_array = np.array(
        image,
        dtype=np.float32
    )

    # Exact MobileNetV2 preprocessing
    image_array = (
        tf.keras.applications
        .mobilenet_v2
        .preprocess_input(
            image_array
        )
    )

    image_array = np.expand_dims(
        image_array,
        axis=0
    )

    predictions = unet_model.predict(
        image_array,
        verbose=0
    )

    # 0 = background
    # 1 = fruit
    # 2 = disease
    predicted_mask = np.argmax(
        predictions[0],
        axis=-1
    )

    fruit_pixels = int(
        np.sum(
            predicted_mask == 1
        )
    )

    disease_pixels = int(
        np.sum(
            predicted_mask == 2
        )
    )

    return (
        predicted_mask,
        fruit_pixels,
        disease_pixels
    )


# =====================================================
# DOSAGE CALCULATION
# =====================================================

def calculate_dosage(
    crop,
    disease,
    fruit_pixels,
    disease_pixels
):

    if fruit_pixels <= 0:

        raise ValueError(
            "U-Net++ detected no fruit area."
        )

    severity = (
        disease_pixels
        /
        fruit_pixels
    ) * 100.0

    severity = max(
        0.0,
        min(
            100.0,
            severity
        )
    )

    rule = DOSAGE_RULES.get(
        (crop, disease)
    )

    if rule is None:

        raise ValueError(
            f"No dosage rule found for "
            f"{crop} + {disease}"
        )

    base_dosage = float(
        rule["base_dosage_ml"]
    )

    recommended_dosage = (
        base_dosage
        *
        severity
        /
        100.0
    )

    return {
        "severity_percent": severity,
        "pesticide": rule["pesticide"],
        "base_dosage_ml": base_dosage,
        "recommended_dosage_ml": recommended_dosage
    }


# =====================================================
# COMPLETE AI PIPELINE
# =====================================================

def analyze_image(image_data):

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

    # -------------------------------------------------
    # RESET PREVIOUS ANALYSIS
    # -------------------------------------------------

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
    # STEP 1: CLASSIFICATION
    # -------------------------------------------------

    prediction, confidence = predict_image(
        image_data
    )

    ai_prediction = prediction

    ai_confidence = confidence


    # -------------------------------------------------
    # GET CROP + DISEASE
    # -------------------------------------------------

    details = CLASS_DETAILS.get(
        prediction
    )

    if details is None:

        raise ValueError(
            f"Unknown classification: {prediction}"
        )

    ai_crop = details["crop"]

    ai_disease = details["disease"]

    ai_is_healthy = details["healthy"]


    # -------------------------------------------------
    # HEALTHY EARLY EXIT
    # -------------------------------------------------

    if ai_is_healthy:

        ai_message = (
            f"{ai_crop} is healthy. "
            "No spraying required."
        )

        spray_required = False

        segmentation_performed = False

        return {
            "prediction": ai_prediction,
            "confidence": ai_confidence,
            "crop": ai_crop,
            "disease": ai_disease,
            "healthy": True,
            "segmentation_performed": False,
            "spray_required": False,
            "message": ai_message
        }


    # -------------------------------------------------
    # STEP 2: U-NET++ SEGMENTATION
    # -------------------------------------------------

    segmentation_performed = True

    (
        predicted_mask,
        fruit_pixels,
        disease_pixels
    ) = segment_image(
        image_data
    )

    fruit_area_pixels = fruit_pixels

    disease_area_pixels = disease_pixels


    # -------------------------------------------------
    # STEP 3: DOSAGE
    # -------------------------------------------------

    dosage = calculate_dosage(
        ai_crop,
        ai_disease,
        fruit_pixels,
        disease_pixels
    )

    severity_percent = dosage[
        "severity_percent"
    ]

    pesticide = dosage[
        "pesticide"
    ]

    base_dosage_ml = dosage[
        "base_dosage_ml"
    ]

    recommended_dosage_ml = dosage[
        "recommended_dosage_ml"
    ]

    spray_required = (
        recommended_dosage_ml > 0
    )

    ai_message = (
        f"{ai_disease} detected. "
        f"Severity {severity_percent:.2f}%. "
        f"Recommended spray dosage "
        f"{recommended_dosage_ml:.2f} ml."
    )

    return {
        "prediction": ai_prediction,
        "confidence": ai_confidence,
        "crop": ai_crop,
        "disease": ai_disease,
        "healthy": False,
        "segmentation_performed": True,
        "fruit_area_pixels": fruit_area_pixels,
        "disease_area_pixels": disease_area_pixels,
        "severity_percent": severity_percent,
        "pesticide": pesticide,
        "base_dosage_ml": base_dosage_ml,
        "recommended_dosage_ml": recommended_dosage_ml,
        "spray_required": spray_required,
        "message": ai_message
    }


# =====================================================
# HOME
# =====================================================

@app.get("/")
def home():

    return {
        "project": "CropIQ",
        "message": "CropIQ backend is running"
    }


# =====================================================
# TEST
# =====================================================

@app.get("/test")
def test():

    return {
        "status": "success",
        "message": "Backend connection is working"
    }


# =====================================================
# SYSTEM STATE
# =====================================================

@app.get("/state")
def get_state():

    return {

        "raspberry_pi": {

            "spray_status":
                spray_status,

            "sprayed_amount":
                sprayed_amount,

            "command_pending":
                spray_command is not None,

            "image_available":
                latest_image is not None,

            "ai_prediction":
                ai_prediction,

            "ai_confidence":
                ai_confidence,

            "crop":
                ai_crop,

            "disease":
                ai_disease,

            "healthy":
                ai_is_healthy,

            "segmentation_performed":
                segmentation_performed,

            "fruit_area_pixels":
                fruit_area_pixels,

            "disease_area_pixels":
                disease_area_pixels,

            "severity_percent":
                severity_percent,

            "pesticide":
                pesticide,

            "base_dosage_ml":
                base_dosage_ml,

            "recommended_dosage_ml":
                recommended_dosage_ml,

            "spray_required":
                spray_required,

            "ai_message":
                ai_message
        },

        "esp32": {

            "online":
                esp32_online,

            "rover_status":
                rover_status,

            "speed":
                rover_speed
        }
    }


# =====================================================
# SPRAY COMMAND
# =====================================================

@app.post("/spray")
def spray(request: SprayRequest):

    global spray_command
    global spray_status
    global sprayed_amount

    amount = request.amount_ml


    # -------------------------------------------------
    # HEALTH CHECK
    # -------------------------------------------------

    if ai_is_healthy:

        raise HTTPException(
            status_code=400,
            detail=(
                "Plant is healthy. "
                "No spraying is required."
            )
        )


    # -------------------------------------------------
    # DOSAGE CHECK
    # -------------------------------------------------

    if not spray_required:

        raise HTTPException(
            status_code=400,
            detail="No spray is currently required."
        )


    if amount <= 0:

        raise HTTPException(
            status_code=400,
            detail="Dosage must be greater than 0 ml"
        )


    # -------------------------------------------------
    # PREVENT WRONG DOSAGE
    # -------------------------------------------------

    allowed_dosage = recommended_dosage_ml

    tolerance = max(
        1.0,
        allowed_dosage * 0.05
    )

    if abs(
        amount - allowed_dosage
    ) > tolerance:

        raise HTTPException(
            status_code=400,
            detail=(
                f"Dosage should be approximately "
                f"{allowed_dosage:.2f} ml "
                f"for the current analysis."
            )
        )


    # -------------------------------------------------
    # CHECK PENDING COMMAND
    # -------------------------------------------------

    if spray_command is not None:

        raise HTTPException(
            status_code=409,
            detail=(
                "Another Raspberry Pi command "
                "is pending"
            )
        )


    # -------------------------------------------------
    # CHECK CURRENT SPRAY
    # -------------------------------------------------

    if spray_status == "Spraying...":

        raise HTTPException(
            status_code=409,
            detail="Spraying is already in progress"
        )


    # -------------------------------------------------
    # CREATE SPRAY COMMAND
    # -------------------------------------------------

    spray_command = {

        "command": "SPRAY",

        "amount_ml": amount
    }


    sprayed_amount = 0.0

    spray_status = "Spraying..."


    return {

        "message":
            "Precision spray command created",

        "amount_ml":
            amount,

        "status":
            spray_status
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
            detail=(
                "Another Raspberry Pi command "
                "is pending"
            )
        )


    if spray_status == "Spraying...":

        raise HTTPException(
            status_code=409,
            detail=(
                "Cannot capture while spraying"
            )
        )


    spray_command = {

        "command": "CAPTURE"
    }


    return {

        "message":
            "Capture command created",

        "command":
            "CAPTURE"
    }


# =====================================================
# RASPBERRY PI GETS COMMAND
# =====================================================

@app.get("/command")
def get_command():

    global spray_command


    if spray_command is None:

        return {
            "command": None
        }


    command = spray_command


    spray_command = None


    return command


# =====================================================
# RASPBERRY PI SENDS STATUS
# =====================================================

@app.post("/status")
def update_status(
    request: StatusRequest
):

    global spray_status
    global sprayed_amount


    spray_status = request.status

    sprayed_amount = request.amount_ml


    return {

        "message":
            "Status updated",

        "status":
            spray_status,

        "amount_ml":
            sprayed_amount
    }


# =====================================================
# RASPBERRY PI UPLOADS IMAGE
# =====================================================

@app.post("/upload-image")
async def upload_image(
    file: UploadFile = File(...)
):

    global latest_image
    global latest_image_type


    image_data = await file.read()


    if not image_data:

        raise HTTPException(
            status_code=400,
            detail="Empty image"
        )


    # -------------------------------------------------
    # STORE IMAGE
    # -------------------------------------------------

    latest_image = image_data

    latest_image_type = (
        file.content_type
        or
        "image/jpeg"
    )


    # -------------------------------------------------
    # RUN COMPLETE AI PIPELINE
    # -------------------------------------------------

    try:

        result = analyze_image(
            image_data
        )

    except Exception as e:

        print(
            "AI analysis failed:",
            e
        )

        raise HTTPException(
            status_code=500,
            detail=(
                f"AI analysis failed: {str(e)}"
            )
        )


    return {

        "message":
            "Image uploaded and analyzed successfully",

        **result
    }


# =====================================================
# MANUAL IMAGE PREDICTION
# =====================================================

@app.post("/predict-manual")
async def predict_manual(
    file: UploadFile = File(...)
):

    image_data = await file.read()


    if not image_data:

        raise HTTPException(
            status_code=400,
            detail="Empty image"
        )


    try:

        result = analyze_image(
            image_data
        )

    except Exception as e:

        raise HTTPException(
            status_code=400,
            detail=(
                f"Prediction failed: {str(e)}"
            )
        )


    return {

        "message":
            "Manual image analyzed successfully",

        **result
    }


# =====================================================
# GET LATEST IMAGE
# =====================================================

@app.get("/latest-image")
def get_latest_image():

    if latest_image is None:

        raise HTTPException(
            status_code=404,
            detail="No image available"
        )


    return Response(

        content=latest_image,

        media_type=
            latest_image_type
    )


# =====================================================
# ESP32 WEBSOCKET
# =====================================================

@app.websocket("/ws/esp32")
async def esp32_websocket(
    websocket: WebSocket
):

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

            message = (
                await websocket.receive_text()
            )

            message = message.strip()


            print(
                "ESP32:",
                message
            )


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

        print(
            "ESP32 WebSocket error:",
            e
        )


        esp32_online = False

        esp32_socket = None

        rover_status = "OFFLINE"


# =====================================================
# ROVER CONTROL
# =====================================================

@app.post("/rover")
async def rover_control(
    request: RoverRequest
):

    global esp32_socket
    global esp32_online
    global rover_status
    global rover_speed


    command = (
        request.command
        .upper()
        .strip()
    )


    allowed_commands = [
        "F",
        "B",
        "L",
        "R",
        "S"
    ]


    if command not in allowed_commands:

        raise HTTPException(
            status_code=400,
            detail=(
                "Invalid rover command. "
                "Use F, B, L, R or S."
            )
        )


    if (
        not esp32_online
        or
        esp32_socket is None
    ):

        raise HTTPException(
            status_code=503,
            detail="ESP32 rover is offline"
        )


    speed = max(
        0,
        min(
            100,
            request.speed
        )
    )


    rover_speed = speed


    try:

        await esp32_socket.send_text(
            command
        )


    except Exception as e:

        print(
            "Failed to send command:",
            e
        )


        esp32_online = False

        esp32_socket = None

        rover_status = "OFFLINE"


        raise HTTPException(
            status_code=503,
            detail="ESP32 connection lost"
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

        "message":
            "Rover command sent",

        "command":
            command,

        "speed":
            speed,

        "status":
            rover_status
    }
