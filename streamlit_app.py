import streamlit as st
import requests
import time


# ============================================================
# CONFIGURATION
# ============================================================

BACKEND_URL = "https://cropiq-backend-mecl.onrender.com"

REQUEST_TIMEOUT = 15


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="CropIQ",
    page_icon="🌱",
    layout="wide"
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    .main-title {
        font-size: 42px;
        font-weight: 700;
        margin-bottom: 0px;
    }

    .subtitle {
        font-size: 18px;
        color: #777;
        margin-bottom: 25px;
    }

    .status-box {
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #ddd;
        margin-bottom: 10px;
    }

    .online {
        font-weight: bold;
    }

    .offline {
        font-weight: bold;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# TITLE
# ============================================================

st.markdown(
    '<div class="main-title">🌱 CropIQ</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">Precision Agriculture Rover & Plant Monitoring</div>',
    unsafe_allow_html=True
)


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def get_state():

    try:

        response = requests.get(
            BACKEND_URL + "/state",
            timeout=REQUEST_TIMEOUT
        )

        response.raise_for_status()

        return response.json()

    except Exception as e:

        return None


def send_capture():

    try:

        response = requests.post(
            BACKEND_URL + "/capture",
            timeout=REQUEST_TIMEOUT
        )

        return response

    except Exception as e:

        st.error(f"Backend connection error: {e}")

        return None


def send_spray(amount_ml):

    try:

        response = requests.post(
            BACKEND_URL + "/spray",
            json={
                "amount_ml": amount_ml
            },
            timeout=REQUEST_TIMEOUT
        )

        return response

    except Exception as e:

        st.error(f"Backend connection error: {e}")

        return None


def send_rover_command(command, speed):

    try:

        response = requests.post(
            BACKEND_URL + "/rover",
            json={
                "command": command,
                "speed": speed
            },
            timeout=REQUEST_TIMEOUT
        )

        return response

    except Exception as e:

        st.error(f"Backend connection error: {e}")

        return None


def get_latest_image():

    try:

        response = requests.get(
            BACKEND_URL + "/latest-image",
            timeout=REQUEST_TIMEOUT
        )

        if response.status_code == 200:

            return response.content

        return None

    except Exception:

        return None


# ============================================================
# TOP STATUS
# ============================================================

state = get_state()


if state is None:

    st.error("🔴 Cannot connect to CropIQ backend")

else:

    raspberry_state = state.get("raspberry_pi", {})
    esp32_state = state.get("esp32", {})

    spray_status = raspberry_state.get(
        "spray_status",
        "Unknown"
    )

    sprayed_amount = raspberry_state.get(
        "sprayed_amount",
        0.0
    )

    esp32_online = esp32_state.get(
        "online",
        False
    )

    rover_status = esp32_state.get(
        "rover_status",
        "UNKNOWN"
    )

    rover_speed = esp32_state.get(
        "speed",
        50
    )


    # ========================================================
    # STATUS COLUMNS
    # ========================================================

    status1, status2, status3 = st.columns(3)


    with status1:

        st.metric(
            "💧 Spray Status",
            spray_status
        )


    with status2:

        st.metric(
            "💦 Sprayed Amount",
            f"{sprayed_amount:.2f} ml"
        )


    with status3:

        if esp32_online:

            st.metric(
                "🚜 Rover",
                "ONLINE"
            )

        else:

            st.metric(
                "🚜 Rover",
                "OFFLINE"
            )


# ============================================================
# DIVIDER
# ============================================================

st.divider()


# ============================================================
# CAMERA SECTION
# ============================================================

st.header("📷 Plant Monitoring")


camera_col, capture_col = st.columns([3, 1])


with capture_col:

    st.subheader("Camera")

    if st.button(
        "📸 CAPTURE IMAGE",
        use_container_width=True
    ):

        response = send_capture()

        if response is not None:

            if response.status_code == 200:

                st.success(
                    "Capture command sent!"
                )

            else:

                try:
                    error_message = response.json().get(
                        "detail",
                        response.text
                    )
                except Exception:
                    error_message = response.text

                st.error(
                    f"Capture failed: {error_message}"
                )


with camera_col:

    st.subheader("Latest Plant Image")


    # --------------------------------------------------------
    # Automatically refresh image every 2 seconds
    # --------------------------------------------------------

    @st.fragment(run_every="2s")
    def show_latest_image():

        image = get_latest_image()

        if image is not None:

            st.image(
                image,
                caption="Latest captured plant image",
                use_container_width=True
            )

        else:

            st.info(
                "📷 No plant image available yet."
            )


    show_latest_image()


# ============================================================
# SPRAY SECTION
# ============================================================

st.divider()

st.header("💧 Precision Spraying")


spray_col1, spray_col2 = st.columns([2, 1])


with spray_col1:

    dosage = st.number_input(
        "Spray dosage (ml)",
        min_value=1.0,
        max_value=500.0,
        value=20.0,
        step=1.0
    )


with spray_col2:

    st.write("")

    st.write("")

    if st.button(
        "🚿 START SPRAY",
        use_container_width=True
    ):

        response = send_spray(dosage)

        if response is not None:

            if response.status_code == 200:

                st.success(
                    f"Spray command sent: {dosage:.1f} ml"
                )

            else:

                try:
                    error_message = response.json().get(
                        "detail",
                        response.text
                    )
                except Exception:
                    error_message = response.text

                st.error(
                    f"Spray failed: {error_message}"
                )


# ============================================================
# ROVER CONTROL
# ============================================================

st.divider()

st.header("🚜 Rover Control")


# ============================================================
# ROVER STATUS AUTO REFRESH
# ============================================================

@st.fragment(run_every="2s")
def rover_status_display():

    current_state = get_state()

    if current_state is None:

        st.error("Unable to get rover status.")

        return


    esp32 = current_state.get(
        "esp32",
        {}
    )

    online = esp32.get(
        "online",
        False
    )

    status = esp32.get(
        "rover_status",
        "UNKNOWN"
    )

    speed = esp32.get(
        "speed",
        50
    )


    col1, col2, col3 = st.columns(3)


    with col1:

        if online:

            st.success("🟢 ESP32 ONLINE")

        else:

            st.error("🔴 ESP32 OFFLINE")


    with col2:

        st.info(
            f"Rover: **{status}**"
        )


    with col3:

        st.info(
            f"Speed: **{speed}%**"
        )


rover_status_display()


# ============================================================
# SPEED
# ============================================================

speed = st.slider(
    "Rover Speed",
    min_value=0,
    max_value=100,
    value=50,
    step=5
)


# ============================================================
# ROVER BUTTONS
# ============================================================

st.write("### Direction")


# ------------------------------------------------------------
# FORWARD
# ------------------------------------------------------------

row1_col1, row1_col2, row1_col3 = st.columns(3)


with row1_col2:

    if st.button(
        "⬆️ FORWARD",
        use_container_width=True
    ):

        response = send_rover_command(
            "F",
            speed
        )

        if response is not None:

            if response.status_code != 200:

                try:
                    error_message = response.json().get(
                        "detail",
                        response.text
                    )
                except Exception:
                    error_message = response.text

                st.error(
                    f"Forward command failed: {error_message}"
                )


# ------------------------------------------------------------
# LEFT / STOP / RIGHT
# ------------------------------------------------------------

row2_col1, row2_col2, row2_col3 = st.columns(3)


with row2_col1:

    if st.button(
        "⬅️ LEFT",
        use_container_width=True
    ):

        response = send_rover_command(
            "L",
            speed
        )

        if response is not None:

            if response.status_code != 200:

                try:
                    error_message = response.json().get(
                        "detail",
                        response.text
                    )
                except Exception:
                    error_message = response.text

                st.error(
                    f"Left command failed: {error_message}"
                )


with row2_col2:

    if st.button(
        "⛔ STOP",
        use_container_width=True
    ):

        response = send_rover_command(
            "S",
            speed
        )

        if response is not None:

            if response.status_code == 200:

                st.success("Rover stopped.")

            else:

                try:
                    error_message = response.json().get(
                        "detail",
                        response.text
                    )
                except Exception:
                    error_message = response.text

                st.error(
                    f"Stop command failed: {error_message}"
                )


with row2_col3:

    if st.button(
        "➡️ RIGHT",
        use_container_width=True
    ):

        response = send_rover_command(
            "R",
            speed
        )

        if response is not None:

            if response.status_code != 200:

                try:
                    error_message = response.json().get(
                        "detail",
                        response.text
                    )
                except Exception:
                    error_message = response.text

                st.error(
                    f"Right command failed: {error_message}"
                )


# ------------------------------------------------------------
# BACKWARD
# ------------------------------------------------------------

row3_col1, row3_col2, row3_col3 = st.columns(3)


with row3_col2:

    if st.button(
        "⬇️ BACKWARD",
        use_container_width=True
    ):

        response = send_rover_command(
            "B",
            speed
        )

        if response is not None:

            if response.status_code != 200:

                try:
                    error_message = response.json().get(
                        "detail",
                        response.text
                    )
                except Exception:
                    error_message = response.text

                st.error(
                    f"Backward command failed: {error_message}"
                )


# ============================================================
# SYSTEM STATUS
# ============================================================

st.divider()

st.header("🔧 System Status")


@st.fragment(run_every="3s")
def system_status():

    current_state = get_state()

    if current_state is None:

        st.error(
            "🔴 Backend unavailable"
        )

        return


    raspberry = current_state.get(
        "raspberry_pi",
        {}
    )

    esp32 = current_state.get(
        "esp32",
        {}
    )


    col1, col2 = st.columns(2)


    with col1:

        st.subheader("🍓 Raspberry Pi")

        st.write(
            f"Spray status: **{raspberry.get('spray_status', 'Unknown')}**"
        )

        st.write(
            f"Sprayed amount: **{raspberry.get('sprayed_amount', 0):.2f} ml**"
        )

        if raspberry.get(
            "image_available",
            False
        ):

            st.success(
                "📷 Image available"
            )

        else:

            st.info(
                "📷 No image available"
            )


    with col2:

        st.subheader("🚜 ESP32")

        if esp32.get(
            "online",
            False
        ):

            st.success(
                "🟢 ESP32 connected"
            )

        else:

            st.error(
                "🔴 ESP32 disconnected"
            )

        st.write(
            f"Rover status: **{esp32.get('rover_status', 'Unknown')}**"
        )

        st.write(
            f"Speed: **{esp32.get('speed', 0)}%**"
        )


system_status()


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "CropIQ • Precision Agriculture Rover System"
)
