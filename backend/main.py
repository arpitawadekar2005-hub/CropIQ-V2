from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="CropIQ API")


# ==========================================
# SYSTEM STATE
# ==========================================

spray_command = None
spray_status = "Ready"
sprayed_amount = 0.0


# ==========================================
# DOSAGE MODEL
# ==========================================

class SprayRequest(BaseModel):
    amount_ml: float


# ==========================================
# HOME
# ==========================================

@app.get("/")
def home():
    return {
        "project": "CropIQ",
        "message": "CropIQ backend is running"
    }


# ==========================================
# CONNECTION TEST
# ==========================================

@app.get("/test")
def test():
    return {
        "status": "success",
        "message": "Backend connection is working"
    }


# ==========================================
# GET SYSTEM STATE
# ==========================================

@app.get("/state")
def get_state():

    return {
        "status": spray_status,
        "sprayed_amount": sprayed_amount,
        "command_pending": spray_command is not None
    }


# ==========================================
# SPRAY REQUEST
# ==========================================

@app.post("/spray")
def spray(request: SprayRequest):

    global spray_command
    global spray_status
    global sprayed_amount

    amount = request.amount_ml

    # Check dosage
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

    # Don't accept another command
    # if one is already waiting
    if spray_command is not None:

        raise HTTPException(
            status_code=409,
            detail="A spray command is already pending"
        )

    # Store command
    spray_command = amount

    # Update status
    spray_status = "Spraying..."

    sprayed_amount = 0.0

    return {
        "message": "Spray command created",
        "amount_ml": amount,
        "status": spray_status
    }

# ==========================================
# RASPBERRY PI GETS SPRAY COMMAND
# ==========================================

@app.get("/command")
def get_command():

    global spray_command

    if spray_command is None:

        return {
            "command": None
        }

    amount = spray_command

    # Remove command after Raspberry Pi receives it
    spray_command = None

    return {
        "command": "SPRAY",
        "amount_ml": amount
    }
