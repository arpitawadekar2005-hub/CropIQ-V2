from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import Response
from pydantic import BaseModel


app = FastAPI(title="CropIQ API")


# =====================================================
# SYSTEM STATE
# =====================================================

spray_command = None

spray_status = "Ready"

sprayed_amount = 0.0

latest_image = None

latest_image_type = "image/jpeg"


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
        "status": spray_status,
        "sprayed_amount": sprayed_amount,
        "command_pending": spray_command is not None,
        "image_available": latest_image is not None
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

    # Check amount
    if amount <= 0:

        raise HTTPException(
            status_code=400,
            detail="Dosage must be greater than 0 ml"
        )

    if amount > 500:

        raise HTTPException(
            status_code=400,
            detail="Maximum dosage is 500 ml"
        )

    # Don't allow another command
    if spray_command is not None:

        raise HTTPException(
            status_code=409,
            detail="Another command is already pending"
        )

    # Don't allow spraying again while spraying
    if spray_status == "Spraying...":

        raise HTTPException(
            status_code=409,
            detail="Spraying is already in progress"
        )

    # Create command
    spray_command = {
        "command": "SPRAY",
        "amount_ml": amount
    }

    # Reset previous amount
    sprayed_amount = 0.0

    return {
        "message": "Spray command created",
        "amount_ml": amount,
        "status": "Ready"
    }


# =====================================================
# CAPTURE COMMAND
# =====================================================

@app.post("/capture")
def capture():

    global spray_command

    # Don't capture while another command exists
    if spray_command is not None:

        raise HTTPException(
            status_code=409,
            detail="Another command is already pending"
        )

    # Don't capture during spraying
    if spray_status == "Spraying...":

        raise HTTPException(
            status_code=409,
            detail="Cannot capture while spraying"
        )

    spray_command = {
        "command": "CAPTURE"
    }

    return {
        "message": "Capture command created",
        "command": "CAPTURE"
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
def update_status(request: StatusRequest):

    global spray_status
    global sprayed_amount

    spray_status = request.status

    sprayed_amount = request.amount_ml

    return {
        "message": "Status updated",
        "status": spray_status,
        "amount_ml": sprayed_amount
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
        file.content_type or "image/jpeg"
    )

    return {
        "message": "Image uploaded successfully"
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
        media_type=latest_image_type
    )
