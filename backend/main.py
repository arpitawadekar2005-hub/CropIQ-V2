import gc
import io
import os
import threading
from contextlib import asynccontextmanager

import numpy as np
import onnxruntime as ort
from fastapi import FastAPI, File, HTTPException, Response, UploadFile
from PIL import Image
from pydantic import BaseModel

from dosage_engine import calculate_dosage

# =====================================================
# PATHS & CONFIGURATION
# =====================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, "model")

CLASSIFIER_PATH = os.path.join(MODEL_DIR, "classifier.onnx")
UNET_MODEL_PATH = os.path.join(MODEL_DIR, "segmenter.onnx")

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

# Global ONNX Sessions & Thread Lock
classifier_session = None
segmenter_session = None
ai_lock = threading.Lock()

# =====================================================
# LIFESPAN & ONNX SESSION LOADING
# =====================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    global classifier_session, segmenter_session
    opts = ort.SessionOptions()
    opts.intra_op_num_threads = 1
    opts.inter_op_num_threads = 1

    print("Loading Lightweight ONNX Classifier...")
    classifier_session = ort.InferenceSession(CLASSIFIER_PATH, sess_options=opts)

    print("Loading Lightweight ONNX Segmenter...")
    segmenter_session = ort.InferenceSession(UNET_MODEL_PATH, sess_options=opts)

    gc.collect()
    yield
    print("Shutting down CropIQ backend...")

app = FastAPI(title="CropIQ API", lifespan=lifespan)

# =====================================================
# INFERENCE HELPERS
# =====================================================

def predict_image(image_bytes: bytes):
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


def segment_image(image_bytes: bytes):
    with Image.open(io.BytesIO(image_bytes)) as img:
        img = img.convert("RGB").resize((512, 512))
        image_array = np.array(img, dtype=np.float32)

    # MobileNetV2 preprocessing normalization [-1, 1]
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


def analyze_image(image_bytes: bytes):
    global ai_prediction, ai_confidence, ai_crop, ai_disease
    global ai_is_healthy, segmentation_performed, fruit_area_pixels
    global disease_area_pixels, severity_percent, pesticide
    global base_dosage_ml, recommended_dosage_ml, spray_required, ai_message

    with ai_lock:
        prediction, confidence = predict_image(image_bytes)

        ai_prediction = prediction
        ai_confidence = float(confidence)

        details = CLASS_DETAILS.get(prediction)
        if not details:
            ai_message = "Unknown classification returned by the AI model."
            return {
                "message": ai_message,
                "prediction": ai_prediction,
                "confidence": ai_confidence,
                "crop": None,
                "disease": None,
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

        # Disease segmentation step
        fruit_area, disease_area = segment_image(image_bytes)

        segmentation_performed = True
        fruit_area_pixels = int(fruit_area)
        disease_area_pixels = int(disease_area)

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
            return {
                "message": f"{ai_disease} detected, but dosage calculation failed: {exc}",
                "prediction": ai_prediction,
                "confidence": ai_confidence,
                "crop": ai_crop,
                "disease": ai_disease,
                "healthy": False,
                "segmentation_performed": segmentation_performed,
                "fruit_area_pixels": fruit_area_pixels,
                "disease_area_pixels": disease_area_pixels,
                "severity_percent": 0.0,
                "pesticide": None,
                "base_dosage_ml": 0.0,
                "recommended_dosage_ml": 0.0,
                "spray_required": False,
            }

        spray_required = (
            pesticide is not None
            and pesticide.strip().lower() != "no treatment"
            and recommended_dosage_ml > 0.0
        )

        ai_message = (
            f"{ai_disease} detected. Severity: {severity_percent:.2f}%. "
            f"Recommended dosage: {recommended_dosage_ml:.2f} ml."
            if spray_required
            else f"{ai_disease} detected. No spraying required."
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
# FASTAPI ENDPOINTS
# =====================================================

spray_command = None
spray_status = "Ready"
sprayed_amount = 0.0

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

esp32_online = False
rover_status = "STOPPED"
rover_speed = 50


@app.get("/")
def home():
    return {"project": "CropIQ", "message": "CropIQ backend running"}


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


@app.post("/predict-manual")
async def predict_manual(file: UploadFile = File(...)):
    global latest_image, latest_image_type

    image_data = await file.read()
    if not image_data:
        raise HTTPException(status_code=400, detail="Empty file")

    try:
        result = analyze_image(image_data)
    except Exception as e:
        print("Analysis Error:", e)
        raise HTTPException(status_code=500, detail=str(e))

    latest_image = image_data
    latest_image_type = file.content_type or "image/jpeg"
    return result


@app.get("/latest-image")
def get_latest_image():
    if latest_image is None:
        raise HTTPException(status_code=404, detail="No image")
    return Response(content=latest_image, media_type=latest_image_type)
