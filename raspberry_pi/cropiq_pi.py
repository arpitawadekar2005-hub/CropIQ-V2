import requests
import time

import RPi.GPIO as GPIO
from gpiozero import OutputDevice


# =====================================================
# CONFIGURATION
# =====================================================

BACKEND_URL = "https://cropiq-backend-mecl.onrender.com"

RELAY_PIN = 17

FLOW_PIN = 18

PULSES_PER_ML = 280

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
            "Connection error:",
            e
        )

    return None


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

    # Calculate required pulses
    target_pulses = (
        amount_ml * PULSES_PER_ML
    )

    print(
        f"Target pulses: {target_pulses:.0f}"
    )

    # Reset counter
    pulse_count = 0

    # Tell dashboard
    send_status(
        "Spraying...",
        0.0
    )

    # -------------------------------------------------
    # START PUMP
    # -------------------------------------------------

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

        # -------------------------------------------------
        # SAFETY: ALWAYS TURN PUMP OFF
        # -------------------------------------------------

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

    # -------------------------------------------------
    # SEND COMPLETED STATUS
    # -------------------------------------------------

    send_status(
        "Completed",
        actual_ml
    )

    print("Spraying completed.")
    print()


# =====================================================
# MAIN PROGRAM
# =====================================================

print("===================================")
print("          CropIQ Raspberry Pi")
print("===================================")
print("Relay: READY")
print("Flow Sensor: READY")
print("Backend: CONNECTING")
print("===================================")


# Make sure pump starts OFF
relay.off()

# Tell dashboard that system is ready
send_status(
    "Ready",
    0.0
)


try:

    while True:

        amount = get_command()

        if amount is not None:

            spray(amount)

        time.sleep(
            CHECK_INTERVAL
        )


except KeyboardInterrupt:

    print()
    print("Stopping CropIQ...")


finally:

    # Safety shutdown
    relay.off()

    GPIO.cleanup()

    print(
        "Relay OFF - System safely stopped"
    )
