import gc
import io
import os
import threading
from contextlib import asynccontextmanager
from datetime import datetime, timezone

import numpy as np
import onnxruntime as ort
from fastapi import FastAPI, File, Form, HTTPException, Response, UploadFile, WebSocket, WebSocketDisconnect
from PIL import Image
from pydantic import BaseModel, Field

from dosage_engine import calculate_dosage

# =====================================================
# PATHS & CONFIGURATION
# =====================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, "model")

CLASSIFIER_PATH = os.path.join(MODEL_DIR, "classifier.onnx")
UNET_MODEL_PATH = os.path.join(MODEL_DIR, "segmenter.onnx")

IMAGE_UPLOAD_MAX_BYTES = 12 * 1024 * 1024
MAX_SPRAY_ML = 5000.0

class_names = [
    "Guava_Anthracnose",
    "Guava_fruit_fly",
    "Guava_healthy_guava",
    "Pomegranate_Alternaria",
    "Pomegranate_Anthracnose",
    "Pomegranate_Cercospora",
    "Pomegranate_Healthy",
]

HEALTHY_CLASSES = {"Guava_healthy_guava", "Pomegranate_Healthy"}

CLASS_DETAILS = {
    "Guava_Anthracnose": {"crop": "Guava", "disease": "Anthracnose"},
    "Guava_fruit_fly": {"crop": "Guava", "disease": "Fruit fly"},
    "Guava_healthy_guava": {"crop": "Guava", "disease": "Healthy"},
    "Pomegranate_Alternaria": {"crop": "Pomegranate", "disease": "Alternaria"},
    "Pomegranate_Anthracnose": {"crop": "Pomegranate", "disease": "Anthracnose"},
    "Pomegranate_Cercospora": {"crop": "Pomegranate", "disease": "Cercospora"},
    "Pomegranate_Healthy": {"crop": "Pomegranate", "disease": "Healthy"},
}

classifier_session = None
ai_lock = threading.Lock()
state_lock = threading.Lock()

# =====================================================
# ONNX OPTIONS
# =====================================================

def get_onnx_options():
    opts = ort.SessionOptions()
    opts.intra_op_num_threads = 1
    opts.inter_op_num_threads = 1
    opts.execution_mode = ort.ExecutionMode.ORT_SEQUENTIAL
    opts.enable_cpu_mem_arena = False
    return opts


# =====================================================
# LIFESPAN
# =====================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    global classifier_session

    print("Loading ONNX Classifier Session...")
    classifier_session = ort.InferenceSession(
        CLASSIFIER_PATH,
        sess_options=get_onnx_options(),
    )
    gc.collect()
    print("CropIQ classifier loaded successfully.")

    yield

    print("Shutting down CropIQ backend...")
    classifier_session = None
    gc.collect()


app = FastAPI(title="CropIQ API", lifespan=lifespan)

# =====================================================
# GLOBAL RASPBERRY PI / IMAGE / AI STATE
# =====================================================

spray_command = None
spray_status = "Ready"
sprayed_amount = 0.0

latest_image = None
latest_image_type = "image/jpeg"
image_version = 0
image_source = None
image_uploaded_at = None
capture_requested_at = None
last_pi_seen_at = None

# AI result must only exist after the user explicitly asks for prediction.
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
ai_message = "Awaiting AI Prediction"
analysis_image_version = None

# =====================================================
# ESP32 STATE
# =====================================================

esp32_socket = None
esp32_online = False
rover_status = "STOPPED"
rover_speed = 50


# =====================================================
# REQUEST MODELS
# =====================================================

class SprayRequest(BaseModel):
    amount_ml: float = Field(gt=0, le=MAX_SPRAY_ML)


class StatusRequest(BaseModel):
    status: str
    amount_ml: float = 0.0


class RoverRequest(BaseModel):
    command: str
    speed: int = 50


# =====================================================
# STATE HELPERS
# =====================================================

def reset_ai_state(message="Awaiting AI Prediction"):
    global ai_prediction, ai_confidence, ai_crop, ai_disease
    global ai_is_healthy, segmentation_performed, fruit_area_pixels
    global disease_area_pixels, severity_percent, pesticide
    global base_dosage_ml, recommended_dosage_ml, spray_required
    global ai_message, analysis_image_version

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
    ai_message = message
    analysis_image_version = None


def image_state_payload():
    global last_pi_seen_at
    pi_online = False
    if last_pi_seen_at:
        try:
            seen_dt = datetime.fromisoformat(last_pi_seen_at)
            pi_online = (datetime.now(timezone.utc) - seen_dt).total_seconds() <= 15
        except Exception:
            pi_online = False

    return {
        "image_available": latest_image is not None,
        "image_version": image_version,
        "image_source": image_source,
        "image_uploaded_at": image_uploaded_at,
        "capture_requested_at": capture_requested_at,
        "raspberry_pi_online": pi_online,
    }


def ai_state_payload():
    return {
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
        "analysis_image_version": analysis_image_version,
        "analysis_available": ai_prediction is not None,
    }


# =====================================================
# AI PIPELINE -- KEPT FROM final_backend_AIpipe
# =====================================================

def predict_image(image_bytes: bytes):
    if classifier_session is None:
        raise RuntimeError("AI classifier is not loaded yet")

    with Image.open(io.BytesIO(image_bytes)) as img:
        img = img.convert("RGB").resize((224, 224))
        image_array = np.expand_dims(np.array(img, dtype=np.float32), axis=0)

    input_name = classifier_session.get_inputs()[0].name
    preds = classifier_session.run(None, {input_name: image_array})[0]

    predicted_index = int(np.argmax(preds[0]))
    confidence = float(preds[0][predicted_index]) * 100.0
    predicted_class = class_names[predicted_index]

    del image_array, preds
    gc.collect()
    return predicted_class, confidence


def segment_image_lazy(image_bytes: bytes):
    # Lazy-load U-Net++ only for diseased predictions to stay within Render memory limits.
    segmenter_session = ort.InferenceSession(
        UNET_MODEL_PATH,
        sess_options=get_onnx_options(),
    )

    try:
        with Image.open(io.BytesIO(image_bytes)) as img:
            img = img.convert("RGB").resize((512, 512))
            image_array = np.array(img, dtype=np.float32)

        image_array = (image_array / 127.5) - 1.0
        image_array = np.expand_dims(image_array, axis=0)

        input_name = segmenter_session.get_inputs()[0].name
        preds = segmenter_session.run(None, {input_name: image_array})[0]

        pred_labels = np.argmax(preds[0], axis=-1)
        fruit_area = int(np.sum(pred_labels == 1))
        disease_area = int(np.sum(pred_labels == 2))

        del image_array, preds, pred_labels
        gc.collect()
        return fruit_area, disease_area
    finally:
        del segmenter_session
        gc.collect()


def analyze_image(image_bytes: bytes):
    global ai_prediction, ai_confidence, ai_crop, ai_disease
    global ai_is_healthy, segmentation_performed, fruit_area_pixels
    global disease_area_pixels, severity_percent, pesticide
    global base_dosage_ml, recommended_dosage_ml, spray_required, ai_message
    global analysis_image_version

    with ai_lock:
        # Clear the previous prediction first so no result from an older image can leak through.
        reset_ai_state("Running AI Prediction")

        prediction, confidence = predict_image(image_bytes)

        ai_prediction = prediction
        ai_confidence = float(confidence)

        details = CLASS_DETAILS.get(prediction)
        if not details:
            ai_message = "Unknown classification returned by the AI model."
            return ai_state_payload()

        ai_crop = details["crop"]
        ai_disease = details["disease"]

        # Healthy plant: classification only. No segmentation and no spray.
        if prediction in HEALTHY_CLASSES:
            ai_is_healthy = True
            ai_disease = "Healthy"
            ai_message = f"{ai_crop} is healthy. No spraying required."
            return ai_state_payload()

        # Diseased plant: run U-Net++ segmentation only now.
        fruit_area, disease_area = segment_image_lazy(image_bytes)

        segmentation_performed = True
        fruit_area_pixels = int(fruit_area)
        disease_area_pixels = int(disease_area)

        if fruit_area_pixels <= 0:
            ai_message = f"{ai_disease} detected, but no fruit area was found for severity calculation."
            return ai_state_payload()

        try:
            dosage_result = calculate_dosage(
                crop=ai_crop,
                disease=ai_disease,
                fruit_area=fruit_area_pixels,
                diseased_area=disease_area_pixels,
            )

            severity_percent = float(dosage_result["severity_percentage"])
            pesticide = dosage_result["pesticide"]
            base_dosage_ml = float(dosage_result["base_dosage_ml"])
            recommended_dosage_ml = float(dosage_result["final_dosage_ml"])

        except Exception as exc:
            ai_message = f"{ai_disease} detected, but dosage calculation failed: {exc}"
            return ai_state_payload()

        spray_required = (
            pesticide is not None
            and pesticide.strip().lower() != "no treatment"
            and recommended_dosage_ml > 0.0
        )

        if spray_required:
            ai_message = (
                f"{ai_disease} detected. Severity: {severity_percent:.2f}%. "
                f"Recommended dosage: {recommended_dosage_ml:.2f} ml."
            )
        else:
            ai_message = f"{ai_disease} detected. No spraying required."

        return ai_state_payload()


# =====================================================
# HOME / HEALTH
# =====================================================

@app.get("/")
def home():
    return {
        "project": "CropIQ",
        "message": "CropIQ backend is running",
        "ai_pipeline": "ONNX EfficientNetB0 + lazy U-Net++",
    }


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
    with state_lock:
        return {
            "raspberry_pi": {
                "spray_status": spray_status,
                "sprayed_amount": sprayed_amount,
                "command_pending": spray_command is not None,
                **image_state_payload(),
                **ai_state_payload(),
                "online": image_state_payload()["raspberry_pi_online"],
            },
            "esp32": {
                "online": esp32_online,
                "rover_status": rover_status,
                "speed": rover_speed,
            },
        }


# =====================================================
# SPRAY COMMAND -- PRESERVED FROM old_backend, UPDATED FOR AI DOSAGE RANGE
# =====================================================

@app.post("/spray")
def spray(request: SprayRequest):
    global spray_command, spray_status, sprayed_amount

    amount = float(request.amount_ml)

    with state_lock:
        if not spray_required or ai_prediction is None:
            raise HTTPException(
                status_code=400,
                detail="No active AI treatment is available. Run AI prediction before spraying.",
            )

        if amount <= 0:
            raise HTTPException(status_code=400, detail="Dosage must be greater than 0 ml")

        if amount > MAX_SPRAY_ML:
            raise HTTPException(status_code=400, detail=f"Maximum dosage is {MAX_SPRAY_ML:.0f} ml")

        if spray_command is not None:
            raise HTTPException(status_code=409, detail="Another Raspberry Pi command is pending")

        if spray_status == "Spraying...":
            raise HTTPException(status_code=409, detail="Spraying is already in progress")

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
    global spray_command, capture_requested_at

    with state_lock:
        if spray_command is not None:
            raise HTTPException(status_code=409, detail="Another Raspberry Pi command is pending")

        if spray_status == "Spraying...":
            raise HTTPException(status_code=409, detail="Cannot capture while spraying")

        spray_command = {"command": "CAPTURE"}
        capture_requested_at = datetime.now(timezone.utc).isoformat()
        reset_ai_state("Waiting for Raspberry Pi to upload the new captured image.")

    return {
        "message": "Capture command created",
        "command": "CAPTURE",
        "current_image_version": image_version,
    }


# =====================================================
# RASPBERRY PI GETS COMMAND
# =====================================================

@app.get("/command")
def get_command():
    global spray_command, last_pi_seen_at

    with state_lock:
        last_pi_seen_at = datetime.now(timezone.utc).isoformat()
        if spray_command is None:
            return {"command": None}

        command = spray_command
        spray_command = None
        return command


# =====================================================
# RASPBERRY PI SENDS SPRAY STATUS
# =====================================================

@app.post("/status")
def update_status(request: StatusRequest):
    global spray_status, sprayed_amount, last_pi_seen_at

    with state_lock:
        last_pi_seen_at = datetime.now(timezone.utc).isoformat()
        spray_status = request.status
        sprayed_amount = float(request.amount_ml)

    return {
        "message": "Status updated",
        "status": spray_status,
        "amount_ml": sprayed_amount,
    }


# =====================================================
# RASPBERRY PI UPLOADS IMAGE
# IMPORTANT: UPLOAD ONLY. DO NOT RUN AI HERE.
# The user must press AI Prediction in Streamlit.
# =====================================================

@app.post("/upload-image")
async def upload_image(
    file: UploadFile = File(...),
    source: str = Form("raspberry_pi"),
):
    global latest_image, latest_image_type, image_version
    global image_source, image_uploaded_at, capture_requested_at, last_pi_seen_at

    image_data = await file.read()

    if not image_data:
        raise HTTPException(status_code=400, detail="Empty image")

    if len(image_data) > IMAGE_UPLOAD_MAX_BYTES:
        raise HTTPException(
            status_code=413,
            detail=f"Image is too large. Maximum allowed size is {IMAGE_UPLOAD_MAX_BYTES // (1024 * 1024)} MB.",
        )

    try:
        # Validate that the upload is actually an image.
        with Image.open(io.BytesIO(image_data)) as img:
            img.verify()
    except Exception:
        raise HTTPException(status_code=400, detail="Uploaded file is not a valid image")

    if source is None:
        source = "raspberry_pi"
    source = source.strip().lower()
    if source not in {"raspberry_pi", "manual"}:
        source = "manual"

    with state_lock:
        latest_image = image_data
        latest_image_type = file.content_type or "image/jpeg"
        image_version += 1
        image_source = source
        image_uploaded_at = datetime.now(timezone.utc).isoformat()
        capture_requested_at = None
        if source == "raspberry_pi":
            last_pi_seen_at = image_uploaded_at

        # NEW IMAGE = NEW ANALYSIS SESSION.
        reset_ai_state("Image uploaded. Ready for AI Prediction.")

        current_version = image_version

    return {
        "message": "Image uploaded successfully. AI prediction has not been run.",
        "image_version": current_version,
        "source": source,
        "prediction": None,
        "confidence": 0.0,
    }


# =====================================================
# PREDICT LATEST IMAGE
# This is the button-driven endpoint used by Streamlit for BOTH sources.
# =====================================================

@app.post("/predict-latest")
def predict_latest():
    global analysis_image_version

    with state_lock:
        if latest_image is None:
            raise HTTPException(status_code=404, detail="No image available. Capture or upload an image first.")

        image_data = latest_image
        current_version = image_version

    try:
        result = analyze_image(image_data)
    except Exception as exc:
        print("Analysis Error:", exc)
        reset_ai_state(f"AI prediction failed: {exc}")
        raise HTTPException(status_code=500, detail=str(exc))

    analysis_image_version = current_version
    result = dict(result)
    result["analysis_image_version"] = current_version
    result["image_version"] = current_version
    result["image_source"] = image_source
    return result


# =====================================================
# MANUAL PREDICTION -- BACKWARD-COMPATIBILITY ENDPOINT
# This uploads the image and immediately predicts in one request.
# Streamlit will use /upload-image + /predict-latest for the desired workflow.
# =====================================================

@app.post("/predict-manual")
async def predict_manual(file: UploadFile = File(...)):
    image_data = await file.read()

    if not image_data:
        raise HTTPException(status_code=400, detail="Empty file")

    # Reuse the same validation/storage path as a manual upload.
    global latest_image, latest_image_type, image_version, image_source, image_uploaded_at, last_pi_seen_at

    try:
        with Image.open(io.BytesIO(image_data)) as img:
            img.verify()
    except Exception:
        raise HTTPException(status_code=400, detail="Uploaded file is not a valid image")

    with state_lock:
        latest_image = image_data
        latest_image_type = file.content_type or "image/jpeg"
        image_version += 1
        image_source = "manual"
        image_uploaded_at = datetime.now(timezone.utc).isoformat()
        reset_ai_state("Running AI Prediction")
        current_version = image_version

    try:
        result = analyze_image(image_data)
    except Exception as exc:
        print("Manual Analysis Error:", exc)
        raise HTTPException(status_code=500, detail=str(exc))

    analysis_image_version = current_version
    result = dict(result)
    result["analysis_image_version"] = current_version
    result["image_version"] = current_version
    result["image_source"] = "manual"
    return result


# =====================================================
# GET LATEST IMAGE
# =====================================================

@app.get("/latest-image")
def get_latest_image():
    if latest_image is None:
        raise HTTPException(status_code=404, detail="No image available")

    return Response(content=latest_image, media_type=latest_image_type)


# =====================================================
# ESP32 WEBSOCKET -- PRESERVED FROM old_backend
# =====================================================

@app.websocket("/ws/esp32")
async def esp32_websocket(websocket: WebSocket):
    global esp32_socket, esp32_online, rover_status

    await websocket.accept()

    esp32_socket = websocket
    esp32_online = True
    rover_status = "STOPPED"

    print("==============================")
    print("ESP32 CONNECTED")
    print("==============================")

    try:
        while True:
            message = (await websocket.receive_text()).strip()
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
        print("ESP32 DISCONNECTED")
        esp32_online = False
        esp32_socket = None
        rover_status = "OFFLINE"

    except Exception as exc:
        print("ESP32 WebSocket error:", exc)
        esp32_online = False
        esp32_socket = None
        rover_status = "OFFLINE"


# =====================================================
# ROVER CONTROL -- PRESERVED FROM old_backend
# =====================================================

@app.post("/rover")
async def rover_control(request: RoverRequest):
    global esp32_socket, esp32_online, rover_status, rover_speed

    command = request.command.upper().strip()
    allowed_commands = {"F", "B", "L", "R", "S"}

    if command not in allowed_commands:
        raise HTTPException(
            status_code=400,
            detail="Invalid rover command. Use F, B, L, R or S.",
        )

    if not esp32_online or esp32_socket is None:
        raise HTTPException(status_code=503, detail="ESP32 rover is offline")

    speed = max(0, min(100, int(request.speed)))
    rover_speed = speed

    try:
        await esp32_socket.send_text(command)
    except Exception as exc:
        print("Failed to send rover command:", exc)
        esp32_online = False
        esp32_socket = None
        rover_status = "OFFLINE"
        raise HTTPException(status_code=503, detail="ESP32 connection lost")

    if command == "F":
        rover_status = "FORWARD"
    elif command == "B":
        rover_status = "BACKWARD"
    elif command == "L":
        rover_status = "LEFT"
    elif command == "R":
        rover_status = "RIGHT"
    else:
        rover_status = "STOPPED"

    return {
        "message": "Rover command sent",
        "command": command,
        "speed": speed,
        "status": rover_status,
    }
