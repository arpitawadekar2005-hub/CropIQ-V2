from fastapi import (
    FastAPI,
    HTTPException,
    UploadFile,
    File,
    WebSocket,
    WebSocketDisconnect
)

from fastapi.responses import Response

from pydantic import BaseModel


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


    image_data = await file.read()


    if not image_data:

        raise HTTPException(

            status_code=400,

            detail="Empty image"

        )


    latest_image = image_data


    latest_image_type = (

        file.content_type
        or
        "image/jpeg"

    )


    return {

        "message":
        "Image uploaded successfully"

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
