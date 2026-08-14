import requests
import time


# ==========================================
# CROP IQ BACKEND
# ==========================================

BACKEND_URL = "https://cropiq-backend-mecl.onrender.com"


# ==========================================
# CHECK FOR SPRAY COMMAND
# ==========================================

def check_command():

    try:

        response = requests.get(
            BACKEND_URL + "/command",
            timeout=10
        )

        if response.status_code == 200:

            data = response.json()

            return data

        else:

            print(
                "Backend error:",
                response.status_code
            )

    except Exception as e:

        print(
            "Connection error:",
            e
        )

    return None


# ==========================================
# MAIN PROGRAM
# ==========================================

print("===================================")
print("       CropIQ Raspberry Pi")
print("===================================")
print("Connecting to Render backend...")
print("===================================")


while True:

    data = check_command()

    if data is not None:

        print("Backend response:")
        print(data)

    time.sleep(5)
