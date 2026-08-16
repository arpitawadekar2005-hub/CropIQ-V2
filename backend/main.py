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


# =====================================================
# DOSAGE MODEL
# =====================================================

class SprayRequest(BaseModel):

    amount_ml: float


# =====================================================
# PI STATUS MODEL
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
# GET SYSTEM STATE
# =====================================================

@app.get("/state")
def get_state():

    return {
        "status": spray_status,
        "sprayed_amount": sprayed_amount,
        "command_pending": spray_command is not None
    }


# =====================================================
# CREATE SPRAY COMMAND
# =====================================================

@app.post("/spray")
def spray(request: SprayRequest):

    global spray_command
    global spray_status
    global sprayed_amount

    amount = request.amount_ml

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

    if spray_command is not None:

        raise HTTPException(
            status_code=409,
            detail="A spray command is already pending"
        )

    spray_command = amount

    spray_status = "Spraying..."

    sprayed_amount = 0.0

    latest_image = None
latest_image_type = "image/jpeg"

    return {
        "message": "Spray command created",
        "amount_ml": amount,
        "status": spray_status
    }


# =====================================================
# RASPBERRY PI GET COMMAND
# =====================================================

@app.get("/command")
def get_command():

    global spray_command

    if spray_command is None:

        return {
            "command": None
        }

    amount = spray_command

    # Command is consumed by Raspberry Pi
    spray_command = None

    return {
        "command": "SPRAY",
        "amount_ml": amount
    }


# =====================================================
# RASPBERRY PI REPORTS STATUS
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
# RASPBERRY PI UPLOADS PLANT IMAGE
# =====================================================

@app.post("/upload-image")
async def upload_image(file: UploadFile = File(...)):

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
# STREAMLIT GETS LATEST IMAGE
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
