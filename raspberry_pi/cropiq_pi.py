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

PULSES_PER_ML = 180

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
# SEND STATUS
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
# GET COMMAND
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

        data = response.json()

        return data

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

    # Capture image
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

    # Upload image
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

    target_pulses = (
        amount_ml * PULSES_PER_ML
    )

    print(
        f"Target pulses: {target_pulses:.0f}"
    )

    pulse_count = 0

    send_status(
        "Spraying...",
        0.0
    )

    print("Relay ON")
    print("Pump ON")

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

        relay.off()

        print()
        print("Relay OFF")
        print("Pump OFF")

    actual_ml = (

        pulse_count /
        PULSES_PER_ML

    )

    print(
        f"Actual volume: {actual_ml:.2f} ml"
    )

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


# Make sure pump is OFF
relay.off()

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

            # -----------------------------------------
            # CAPTURE COMMAND
            # -----------------------------------------

            if command == "CAPTURE":

                capture_image()


            # -----------------------------------------
            # SPRAY COMMAND
            # -----------------------------------------

            elif command == "SPRAY":

                amount = float(
                    command_data["amount_ml"]
                )

                spray(amount)


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

    relay.off()

    if camera.isOpened():

        camera.release()

    GPIO.cleanup()

    print(
        "System safely stopped"
    )
