import requests
import time
import cv2

import RPi.GPIO as GPIO
from gpiozero import OutputDevice


# =====================================================
# CONFIGURATION
# =====================================================

BACKEND_URL = "YOUR_RENDER_URL"

RELAY_PIN = 17
FLOW_PIN = 18

# Your measured calibration
PULSES_PER_ML = 47.64

# How often the camera uploads an image
IMAGE_INTERVAL = 10

# How often Raspberry Pi checks for spray command
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
# RELAY SETUP
# =====================================================

# Your relay is Active LOW
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
# CAMERA SETUP
# =====================================================

camera = cv2.VideoCapture(0)

if not camera.isOpened():

    print("ERROR: USB camera not found!")

else:

    print("Camera: READY")


# =====================================================
# SEND STATUS TO RENDER
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
# GET SPRAY COMMAND
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

        if data.get("command") == "SPRAY":

            return float(
                data["amount_ml"]
            )

    except Exception as e:

        print(
            "Backend connection error:",
            e
        )

    return None


# =====================================================
# CAPTURE AND UPLOAD PLANT IMAGE
# =====================================================

def upload_plant_image():

    if not camera.isOpened():

        print(
            "Camera unavailable"
        )

        return

    # Capture frame
    ret, frame = camera.read()

    if not ret:

        print(
            "Failed to capture image"
        )

        return

    # Temporary image location
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
            "Failed to save image"
        )

        return

    # Upload image to Render
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
                "Plant image uploaded successfully"
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
# SPRAY FUNCTION
# =====================================================

def spray(amount_ml):

    global pulse_count

    print()
    print(
        "==================================="
    )

    print(
        f"STARTING SPRAY: {amount_ml:.2f} ml"
    )

    print(
        "==================================="
    )

    # Calculate required pulses
    target_pulses = (
        amount_ml * PULSES_PER_ML
    )

    print(
        f"Target pulses: {target_pulses:.0f}"
    )

    # Reset pulse count
    pulse_count = 0

    # Inform dashboard
    send_status(
        "Spraying...",
        0.0
    )

    # Start pump
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

        # SAFETY:
        # Pump must always turn OFF
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

    print()


# =====================================================
# STARTUP
# =====================================================

print()
print(
    "==================================="
)

print(
    "       CropIQ Raspberry Pi"
)

print(
    "==================================="
)

print(
    "Relay: READY"
)

print(
    "Flow Sensor: READY"
)

if camera.isOpened():

    print(
        "Camera: READY"
    )

else:

    print(
        "Camera: NOT FOUND"
    )

print(
    "Backend: CONNECTING"
)

print(
    "==================================="
)


# Make absolutely sure pump is OFF
relay.off()


# Tell dashboard Raspberry Pi is ready
send_status(
    "Ready",
    0.0
)


# =====================================================
# MAIN LOOP
# =====================================================

last_image_time = 0


try:

    while True:

        # ---------------------------------------------
        # CAMERA
        # ---------------------------------------------

        if (

            time.time() -
            last_image_time

        ) >= IMAGE_INTERVAL:

            upload_plant_image()

            last_image_time = time.time()


        # ---------------------------------------------
        # SPRAY COMMAND
        # ---------------------------------------------

        amount = get_command()

        if amount is not None:

            spray(amount)


        # Wait before checking again
        time.sleep(
            CHECK_INTERVAL
        )


# =====================================================
# STOP PROGRAM
# =====================================================

except KeyboardInterrupt:

    print()
    print(
        "Stopping CropIQ..."
    )


# =====================================================
# CLEANUP
# =====================================================

finally:

    # Pump OFF
    relay.off()

    # Release camera
    if camera.isOpened():

        camera.release()

    # Cleanup GPIO
    GPIO.cleanup()

    print(
        "Relay OFF - System safely stopped"
    )
