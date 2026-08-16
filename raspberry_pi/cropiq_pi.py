import requests
import time
import cv2

import RPi.GPIO as GPIO
from gpiozero import OutputDevice


# =====================================================
# CONFIGURATION
# =====================================================

BACKEND_URL = "https://cropiq-backend-mecl.onrender.com"

RELAY_PIN = 17
FLOW_PIN = 18

# Your previous calibration:
# 3806 pulses / 80 ml = 47.6375 pulses/ml
PULSES_PER_ML = 47.64

CHECK_INTERVAL = 2


# =====================================================
# GPIO SETUP
# =====================================================

GPIO.setmode(GPIO.BCM)

GPIO.setup(
    FLOW_PIN,
    GPIO.IN,
    pull_up_down=GPIO.PUD_UP
)


# =====================================================
# RELAY
# =====================================================

# Active LOW relay
relay = OutputDevice(
    RELAY_PIN,
    active_high=False,
    initial_value=False
)


# =====================================================
# FLOW SENSOR
# =====================================================

pulse_count = 0


def pulse_callback(channel):

    global pulse_count

    pulse_count += 1


GPIO.add_event_detect(
    FLOW_PIN,
    GPIO.FALLING,
    callback=pulse_callback,
    bouncetime=1
)


# =====================================================
# CAMERA
# =====================================================

camera = cv2.VideoCapture(0)

if camera.isOpened():

    print("Camera: READY")

else:

    print("Camera: NOT FOUND")


# =====================================================
# SEND STATUS TO BACKEND
# =====================================================

def send_status(status, amount=0.0):

    try:

        response = requests.post(

            BACKEND_URL + "/status",

            json={
                "status": status,
                "amount_ml": amount
            },

            timeout=10
        )

        print(
            "Status:",
            status,
            "| Response:",
            response.status_code
        )

    except Exception as e:

        print(
            "Status update error:",
            e
        )


# =====================================================
# GET COMMAND FROM BACKEND
# =====================================================

def get_command():

    try:

        response = requests.get(

            BACKEND_URL + "/command",

            timeout=10
        )

        if response.status_code != 200:

            print(
                "Command error:",
                response.status_code
            )

            return None

        return response.json()

    except Exception as e:

        print(
            "Backend connection error:",
            e
        )

        return None


# =====================================================
# CAPTURE IMAGE
# =====================================================

def capture_image():

    print()
    print("===================================")
    print("Capturing plant image...")
    print("===================================")

    if not camera.isOpened():

        print(
            "ERROR: Camera not available"
        )

        return

    # Capture frame
    ret, frame = camera.read()

    if not ret:

        print(
            "ERROR: Failed to capture image"
        )

        return

    # Temporary file
    filename = "/tmp/cropiq_plant.jpg"

    # Save image
    success = cv2.imwrite(

        filename,
        frame,

        [
            cv2.IMWRITE_JPEG_QUALITY,
            85
        ]
    )

    if not success:

        print(
            "ERROR: Could not save image"
        )

        return

    print(
        "Image captured successfully"
    )

    # Upload to Render
    try:

        with open(
            filename,
            "rb"
        ) as image_file:

            files = {

                "file": (

                    "plant.jpg",
                    image_file,
                    "image/jpeg"
                )
            }

            response = requests.post(

                BACKEND_URL + "/upload-image",

                files=files,

                timeout=15
            )

        if response.status_code == 200:

            print(
                "Image uploaded successfully"
            )

        else:

            print(
                "Image upload failed:",
                response.status_code
            )

            print(
                response.text
            )

    except Exception as e:

        print(
            "Image upload error:",
            e
        )


# =====================================================
# SPRAY
# =====================================================

def spray(amount_ml):

    global pulse_count

    print()
    print("===================================")
    print(
        f"STARTING SPRAY: {amount_ml:.2f} ml"
    )
    print("===================================")

    # Calculate target pulses
    target_pulses = (
        amount_ml * PULSES_PER_ML
    )

    print(
        f"Target pulses: {target_pulses:.0f}"
    )

    # Reset pulse count
    pulse_count = 0

    # Tell backend spraying has started
    send_status(
        "Spraying...",
        0.0
    )

    print("Relay ON")
    print("Pump ON")

    # Start pump
    relay.on()

    try:

        while pulse_count < target_pulses:

            current_ml = (
                pulse_count /
                PULSES_PER_ML
            )

            print(

                f"\rPulses: {pulse_count} | "
                f"Volume: {current_ml:.2f} ml",

                end="",
                flush=True
            )

            time.sleep(0.01)

    finally:

        # VERY IMPORTANT:
        # Pump is always turned OFF
        # even if an error occurs.

        relay.off()

        print()
        print("Relay OFF")
        print("Pump OFF")

    # Calculate actual volume
    actual_ml = (
        pulse_count /
        PULSES_PER_ML
    )

    print(
        f"Actual volume: {actual_ml:.2f} ml"
    )

    # Tell backend spraying is complete
    send_status(
        "Completed",
        actual_ml
    )

    print(
        "Spraying completed."
    )


# =====================================================
# STARTUP
# =====================================================

print()
print("===================================")
print("       CropIQ Raspberry Pi")
print("===================================")

print("Relay: READY")
print("Flow Sensor: READY")

if camera.isOpened():

    print("Camera: READY")

else:

    print("Camera: NOT FOUND")

print("Backend: CONNECTING")

print("===================================")


# =====================================================
# SAFETY: PUMP OFF AT START
# =====================================================

relay.off()


# =====================================================
# TELL BACKEND SYSTEM IS READY
# =====================================================

send_status(
    "Ready",
    0.0
)


# =====================================================
# MAIN LOOP
# =====================================================

try:

    while True:

        command_data = get_command()

        if command_data is not None:

            command = command_data.get(
                "command"
            )

            # =========================================
            # CAPTURE
            # =========================================

            if command == "CAPTURE":

                capture_image()


            # =========================================
            # SPRAY
            # =========================================

            elif command == "SPRAY":

                try:

                    amount = float(
                        command_data["amount_ml"]
                    )

                    if amount <= 0:

                        print(
                            "Invalid spray amount"
                        )

                    else:

                        spray(amount)

                except (
                    KeyError,
                    ValueError,
                    TypeError
                ):

                    print(
                        "Invalid spray command"
                    )

        time.sleep(
            CHECK_INTERVAL
        )


# =====================================================
# STOP
# =====================================================

except KeyboardInterrupt:

    print()
    print("Stopping CropIQ...")


# =====================================================
# CLEANUP
# =====================================================

finally:

    # Safety: pump OFF
    relay.off()

    # Release camera
    if camera.isOpened():

        camera.release()

    # Cleanup GPIO
    GPIO.cleanup()

    print(
        "System safely stopped"
    )
