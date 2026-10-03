import io
import time
import base64
import asyncio
from typing import Optional
from PIL import Image

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from pydantic import BaseModel

# ============================================================
# APP CONFIGURATION & CORS
# ============================================================

app = FastAPI(
    title="CropIQ Backend API",
    description="Backend service managing ESP32 Rover, Raspberry Pi camera/sprayer, and AI disease detection.",
    version="2.0.0"
)

# Enable CORS for Streamlit frontend and external connections
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================
# IN-MEMORY SYSTEM STATE & GLOBAL STORAGE
# ============================================================

system_state = {
    "esp32": {
        "online": False,
        "rover_status": "STOPPED",
        "speed": 50
    },
    "raspberry_pi": {
        "online": False,
        "spray_status": "READY",
        "sprayed_amount": 0.0,
        "crop": "Guava",
        "ai_prediction": "Guava healthy guava",
        "ai_confidence": 98.54,
        "disease_area_percentage": 0.00,
        "pesticide_name": "None",
        "recommended_dosage_ml": 0.00
    }
}

# Global references for active WebSocket connections and images
active_esp32_ws: Optional[WebSocket] = None
active_raspi_ws: Optional[WebSocket] = None
latest_camera_image: Optional[bytes] = None

# Default placeholder image setup (blank canvas if no image uploaded yet)
def create_placeholder_image() -> bytes:
    img = Image.new("RGB", (640, 480), color=(220, 230, 225))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()

latest_camera_image = create_placeholder_image()

# ============================================================
# PYDANTIC DATA MODELS
# ============================================================

class RoverCommand(BaseModel):
    command: str
    speed: int = 50

class SprayCommand(BaseModel):
    amount_ml: float

# ============================================================
# AI MODEL MOCK / INFERENCE PIPELINE
# ============================================================

def run_ai_inference(file_bytes: bytes, filename: str = ""):
    """
    Mock AI disease inference model.
    In production, replace this with your TensorFlow/PyTorch model loader.
    """
    filename_lower = filename.lower()
    
    # Check if filename or image indicates a healthy crop
    if "healthy" in filename_lower or "uns" in filename_lower:
        return {
            "crop": "Guava",
            "prediction": "Healthy",
            "confidence": 98.54,
            "disease_area_percentage": 0.00,
            "pesticide_name": "None",
            "recommended_dosage_ml": 0.00
        }
    else:
        return {
            "crop": "Guava",
            "prediction": "Guava fruit fly",
            "confidence": 89.32,
            "disease_area_percentage": 39.24,
            "pesticide_name": "Copper oxychloride",
            "recommended_dosage_ml": 11.51
        }

# ============================================================
# WEBSOCKET ENDPOINTS
# ============================================================

@app.websocket("/ws/esp32")
async def websocket_esp32(websocket: WebSocket):
    """WebSocket handler for ESP32 Rover control and telemetry."""
    global active_esp32_ws
    await websocket.accept()
    active_esp32_ws = websocket
    system_state["esp32"]["online"] = True
    print("✅ ESP32 Connected via WebSocket")

    try:
        while True:
            # Receive heartbeat or telemetry from ESP32
            data = await websocket.receive_text()
            if data.startswith("STATUS:"):
                system_state["esp32"]["rover_status"] = data.split(":")[1]
    except WebSocketDisconnect:
        print("❌ ESP32 Disconnected")
    except Exception as e:
        print(f"⚠️ ESP32 WebSocket Error: {e}")
    finally:
        active_esp32_ws = None
        system_state["esp32"]["online"] = False
        system_state["esp32"]["rover_status"] = "STOPPED"


@app.websocket("/ws/raspberry")
async def websocket_raspberry(websocket: WebSocket):
    """WebSocket handler for Raspberry Pi camera and sprayer telemetry."""
    global active_raspi_ws, latest_camera_image
    await websocket.accept()
    active_raspi_ws = websocket
    system_state["raspberry_pi"]["online"] = True
    print("✅ Raspberry Pi Connected via WebSocket")

    try:
        while True:
            data = await websocket.receive_text()
            # Handle incoming camera frames or status updates
            if data.startswith("FRAME:"):
                b64_data = data.split("FRAME:")[1]
                latest_camera_image = base64.b64decode(b64_data)
            elif data.startswith("SPRAY_COMPLETE:"):
                amount = float(data.split(":")[1])
                system_state["raspberry_pi"]["sprayed_amount"] += amount
                system_state["raspberry_pi"]["spray_status"] = "READY"
    except WebSocketDisconnect:
        print("❌ Raspberry Pi Disconnected")
    except Exception as e:
        print(f"⚠️ Raspberry Pi WebSocket Error: {e}")
    finally:
        active_raspi_ws = None
        system_state["raspberry_pi"]["online"] = False

# ============================================================
# REST API ENDPOINTS
# ============================================================

@app.get("/")
def root_check():
    return {"status": "running", "service": "CropIQ Backend API"}


@app.get("/state")
def get_system_state():
    """Returns the current state of connected hardware and AI values."""
    return system_state


@app.get("/latest-image")
def get_latest_image():
    """Returns the latest captured JPEG frame from the camera."""
    if latest_camera_image:
        return Response(content=latest_camera_image, media_type="image/jpeg")
    raise HTTPException(status_code=444, detail="No camera image available")


@app.post("/rover")
async def control_rover(rover_cmd: RoverCommand):
    """Sends directional movement and speed commands to the ESP32 rover."""
    global active_esp32_ws
    
    # Map command codes
    command_map = {"F": "FORWARD", "B": "BACKWARD", "L": "LEFT", "R": "RIGHT", "S": "STOP"}
    mapped_status = command_map.get(rover_cmd.command.upper(), rover_cmd.command)
    
    system_state["esp32"]["speed"] = rover_cmd.speed
    system_state["esp32"]["rover_status"] = mapped_status

    if active_esp32_ws:
        try:
            payload = f"{rover_cmd.command.upper()}:{rover_cmd.speed}"
            await active_esp32_ws.send_text(payload)
            return {"status": "success", "message": f"Command '{payload}' sent to ESP32"}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to communicate with ESP32: {str(e)}")
    else:
        return {"status": "warning", "message": "Command updated in state, but ESP32 is offline"}


@app.post("/capture")
async def capture_image():
    """Triggers image capture on the connected Raspberry Pi."""
    global active_raspi_ws
    if active_raspi_ws:
        try:
            await active_raspi_ws.send_text("CAPTURE")
            return {"status": "success", "message": "Capture command sent to Raspberry Pi"}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to trigger capture: {str(e)}")
    else:
        return {"status": "warning", "message": "Raspberry Pi is offline. Unable to capture live image."}


@app.post("/spray")
async def trigger_spray(spray_cmd: SprayCommand):
    """Triggers precision sprayer with specified dosage amount in ml."""
    global active_raspi_ws
    amount = spray_cmd.amount_ml
    
    system_state["raspberry_pi"]["spray_status"] = "SPRAYING"

    if active_raspi_ws:
        try:
            await active_raspi_ws.send_text(f"SPRAY:{amount}")
            return {"status": "success", "message": f"Spray command for {amount}ml sent to Raspberry Pi"}
        except Exception as e:
            system_state["raspberry_pi"]["spray_status"] = "ERROR"
            raise HTTPException(status_code=500, detail=f"Failed to send spray command: {str(e)}")
    else:
        # Simulate local state update if hardware isn't physically connected
        system_state["raspberry_pi"]["sprayed_amount"] += amount
        system_state["raspberry_pi"]["spray_status"] = "READY"
        return {"status": "warning", "message": f"Raspberry Pi offline. Simulated spraying {amount}ml"}


@app.post("/predict-manual")
async def predict_manual_image(file: UploadFile = File(...)):
    """Receives uploaded leaf image and performs AI disease diagnosis."""
    global latest_camera_image
    try:
        contents = await file.read()
        
        # Save uploaded image as latest camera image
        latest_camera_image = contents
        
        # Execute AI inference logic
        results = run_ai_inference(contents, file.filename)
        
        # Sync state with diagnosis
        system_state["raspberry_pi"]["crop"] = results["crop"]
        system_state["raspberry_pi"]["ai_prediction"] = results["prediction"]
        system_state["raspberry_pi"]["ai_confidence"] = results["confidence"]
        system_state["raspberry_pi"]["disease_area_percentage"] = results["disease_area_percentage"]
        system_state["raspberry_pi"]["pesticide_name"] = results["pesticide_name"]
        system_state["raspberry_pi"]["recommended_dosage_ml"] = results["recommended_dosage_ml"]
        
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Inference error: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
