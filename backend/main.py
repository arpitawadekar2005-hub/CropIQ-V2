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
# AI MODEL
# =====================================================

# =====================================================
# AI MODEL
# =====================================================

MODEL_PATH = "model/cropiq_final_efficientnetb0.keras"

class_names = [
    "Guava_Anthracnose",
    "Guava_fruit_fly",
    "Guava_healthy_guava",
    "Pomegranate_Alternaria",
    "Pomegranate_Anthracnose",
    "Pomegranate_Cercospora",
    "Pomegranate_Healthy"
]

model = tf.keras.models.load_model(MODEL_PATH)

print("CropIQ AI model loaded successfully")


def predict_image(image_data):
    image = Image.open(io.BytesIO(image_data)).convert("RGB")

    image = image.resize((224, 224))

    image_array = np.array(image, dtype=np.float32)

    image_array = np.expand_dims(image_array, axis=0)

    predictions = model.predict(image_array, verbose=0)

    predicted_index = int(np.argmax(predictions[0]))

    confidence = float(predictions[0][predicted_index]) * 100

    predicted_class = class_names[predicted_index]

    return predicted_class, confidence


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

ai_prediction = None
ai_confidence = 0.0


# =====================================================
# ESP32 ROVER STATE
# =====================================================

esp32_socket = None

esp32_online = False

rover_status = "STOPPED"

rover_speed = 50


# =====================================================
# DOSAGE MODEL
# =====================================================

class SprayRequest(BaseModel):

    amount_ml: float


# =====================================================
# STATUS MODEL
# =====================================================

class StatusRequest(BaseModel):

    status: str

    amount_ml: float = 0.0


# =====================================================
# ROVER COMMAND MODEL
# =====================================================

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

        "message":
        "CropIQ backend is running"

    }


# =====================================================
# TEST
# =====================================================

@app.get("/test")
def test():

    return {

        "status": "success",

        "message":
        "Backend connection is working"

    }


# =====================================================
# HEALTH CHECK
# =====================================================

@app.get("/health")
def health():

    return {
        "status": "ok",
        "model_loaded": model is not None,
        "model_path": MODEL_PATH,
        "classes": len(class_names)
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
            latest_image is not None

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
    # CHECK DOSAGE
    # -------------------------------------------------

    if amount <= 0:

        raise HTTPException(

            status_code=400,

            detail=
            "Dosage must be greater than 0 ml"

        )


    if amount > 500:

        raise HTTPException(

            status_code=400,

            detail=
            "Maximum dosage is 500 ml"

        )


    # -------------------------------------------------
    # CHECK PENDING COMMAND
    # -------------------------------------------------

    if spray_command is not None:

        raise HTTPException(

            status_code=409,

            detail=
            "Another Raspberry Pi command is pending"

        )


    # -------------------------------------------------
    # CHECK CURRENT SPRAY
    # -------------------------------------------------

    if spray_status == "Spraying...":

        raise HTTPException(

            status_code=409,

            detail=
            "Spraying is already in progress"

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
        "Spray command created",

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


    # -------------------------------------------------
    # CHECK PENDING COMMAND
    # -------------------------------------------------

    if spray_command is not None:

        raise HTTPException(

            status_code=409,

            detail=
            "Another Raspberry Pi command is pending"

        )


    # -------------------------------------------------
    # DON'T CAPTURE DURING SPRAY
    # -------------------------------------------------

    if spray_status == "Spraying...":

        raise HTTPException(

            status_code=409,

            detail=
            "Cannot capture while spraying"

        )


    # -------------------------------------------------
    # CREATE CAPTURE COMMAND
    # -------------------------------------------------

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


    # Remove command after Pi receives it

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
    global ai_prediction
    global ai_confidence


    image_data = await file.read()


    if not image_data:

        raise HTTPException(

            status_code=400,

            detail="Empty image"

        )


    latest_image = image_data

    ai_prediction, ai_confidence = predict_image(image_data)


    latest_image_type = (

        file.content_type
        or
        "image/jpeg"

    )


    return {
    "message": "Image uploaded successfully",
    "prediction": ai_prediction,
    "confidence": ai_confidence
}


# =====================================================
# MANUAL IMAGE PREDICTION
# =====================================================

@app.post("/predict")
async def manual_predict(
    file: UploadFile = File(...)
):
    """
    Predict a manually uploaded plant image.

    This endpoint is used by the Streamlit AI Detection page.
    It does NOT replace or modify the Raspberry Pi image flow.

    Request:
        multipart/form-data
        field name: file

    Response:
        prediction
        plant
        disease
        confidence
        confidence_percent
        infection_percentage
        pesticide
        dose_ml
    """

    global ai_prediction
    global ai_confidence

    # -------------------------------------------------
    # CHECK FILE TYPE
    # -------------------------------------------------

    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=400,
            detail="Please upload a JPG, JPEG or PNG image."
        )

    # -------------------------------------------------
    # READ IMAGE
    # -------------------------------------------------

    image_data = await file.read()

    if not image_data:
        raise HTTPException(
            status_code=400,
            detail="Empty image"
        )

    # -------------------------------------------------
    # RUN EXISTING CROP IQ MODEL
    # -------------------------------------------------

    try:
        predicted_class, confidence = predict_image(image_data)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"ML prediction failed: {str(e)}"
        )

    # Save latest AI result so the rest of the backend
    # can access the most recent prediction.
    ai_prediction = predicted_class
    ai_confidence = confidence

    # -------------------------------------------------
    # SPLIT CLASS NAME
    # -------------------------------------------------
    #
    # Your current classes are:
    #
    # Guava_Anthracnose
    # Guava_fruit_fly
    # Guava_healthy_guava
    # Pomegranate_Alternaria
    # Pomegranate_Anthracnose
    # Pomegranate_Cercospora
    # Pomegranate_Healthy
    #
    # The first "_" separates plant and disease.

    parts = predicted_class.split("_", 1)

    if len(parts) == 2:
        plant = parts[0]
        disease = parts[1].replace("_", " ")
    else:
        plant = predicted_class
        disease = predicted_class

    # Make the display text cleaner.
    plant = plant.replace("_", " ").strip()
    disease = disease.replace("_", " ").strip()

    # -------------------------------------------------
    # HEALTHY / DISEASE STATUS
    # -------------------------------------------------

    disease_lower = disease.lower()

    if "healthy" in disease_lower:
        condition = "Healthy"
    else:
        condition = disease

    # -------------------------------------------------
    # RESPONSE
    # -------------------------------------------------

    return {
        "message": "Manual image prediction successful",

        "prediction": predicted_class,

        "plant": plant,

        "disease": condition,

        "confidence": confidence,

        "confidence_percent": confidence,

        # Your current EfficientNetB0 classifier only
        # predicts the class and confidence. It does not
        # calculate infection percentage.
        "infection_percentage": None,

        # Treatment values are not generated by the
        # current model, so they are returned as None
        # rather than inventing values.
        "pesticide": None,

        "dose_ml": None
    }


# =====================================================
# GET LATEST IMAGE
# =====================================================

@app.get("/latest-image")
def get_latest_image():


    if latest_image is None:

        raise HTTPException(

            status_code=404,

            detail=
            "No image available"

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


    # -------------------------------------------------
    # ACCEPT CONNECTION
    # -------------------------------------------------

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

            # Wait for messages from ESP32

            message = (
                await websocket.receive_text()
            )


            message = message.strip()


            print(
                "ESP32:",
                message
            )


            # -------------------------------------------------
            # ESP32 STARTUP MESSAGE
            # -------------------------------------------------

            if message == "ESP32_READY":

                esp32_online = True

                rover_status = "STOPPED"


            # -------------------------------------------------
            # ESP32 STATUS
            # -------------------------------------------------

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


    # -------------------------------------------------
    # COMMAND
    # -------------------------------------------------

    command = (
        request.command
        .upper()
        .strip()
    )


    # -------------------------------------------------
    # VALID COMMANDS
    # -------------------------------------------------

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

            detail=
            "Invalid rover command. "
            "Use F, B, L, R or S."

        )


    # -------------------------------------------------
    # CHECK ESP32
    # -------------------------------------------------

    if (

        not esp32_online

        or

        esp32_socket is None

    ):

        raise HTTPException(

            status_code=503,

            detail=
            "ESP32 rover is offline"

        )


    # -------------------------------------------------
    # SPEED
    # -------------------------------------------------

    speed = max(

        0,

        min(
            100,
            request.speed
        )

    )


    rover_speed = speed


    # -------------------------------------------------
    # SEND COMMAND TO ESP32
    # -------------------------------------------------

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

            detail=
            "ESP32 connection lost"

        )


    # -------------------------------------------------
    # UPDATE STATUS
    # -------------------------------------------------

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
