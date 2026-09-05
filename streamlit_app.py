import streamlit as st
import requests
from datetime import datetime
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
    page_title="CropIQ | Precision Agriculture",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    /* =====================================================
       GLOBAL
       ===================================================== */

    .stApp {
        background: #eef4f1;
    }

    .main .block-container {
        max-width: 1500px;
        padding-top: 1rem;
        padding-bottom: 2rem;
        padding-left: 1.5rem;
        padding-right: 1.5rem;
    }

    #MainMenu {
        visibility: hidden;
    }

    footer {
        visibility: hidden;
    }

    header {
        background: transparent !important;
    }

    /* =====================================================
       SIDEBAR
       ===================================================== */

    section[data-testid="stSidebar"] {
        background: linear-gradient(
            180deg,
            #003f32 0%,
            #004c3d 50%,
            #002d25 100%
        );

        min-width: 280px;
        max-width: 280px;
    }

    section[data-testid="stSidebar"] > div {
        background: transparent;
    }

    section[data-testid="stSidebar"] .block-container {
        padding: 1.5rem 1rem;
    }

    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] span {
        color: white !important;
    }

    /* =====================================================
       SIDEBAR BRAND
       ===================================================== */

    .sidebar-brand {
        text-align: center;
        padding: 10px 5px 30px 5px;
    }

    .sidebar-logo {
        font-size: 54px;
        line-height: 1;
        margin-bottom: 4px;
    }

    .sidebar-name {
        font-size: 32px;
        font-weight: 800;
        color: white;
        letter-spacing: -1px;
    }

    .sidebar-tagline {
        color: #b8d8ce;
        font-size: 13px;
        line-height: 1.5;
        margin-top: 8px;
    }

    .sidebar-section {
        color: #82b9aa;
        font-size: 10px;
        font-weight: 800;
        letter-spacing: 1.8px;
        margin-top: 15px;
        margin-bottom: 8px;
    }

    /* =====================================================
       SIDEBAR NAVIGATION
       ===================================================== */

    section[data-testid="stSidebar"]
    div[role="radiogroup"] {
        gap: 6px;
    }

    section[data-testid="stSidebar"]
    div[role="radiogroup"] > label {
        background: transparent;
        border-radius: 12px;
        padding: 12px 14px;
        margin-bottom: 3px;
        transition: all 0.2s ease;
    }

    section[data-testid="stSidebar"]
    div[role="radiogroup"] > label:hover {
        background: rgba(255,255,255,0.08);
    }

    section[data-testid="stSidebar"]
    div[role="radiogroup"]
    > label[data-checked="true"] {
        background: linear-gradient(
            90deg,
            #149451,
            #08783e
        );

        box-shadow:
            0 7px 18px rgba(0,0,0,0.18);
    }

    section[data-testid="stSidebar"]
    div[role="radiogroup"]
    > label > div:first-child {
        display: none;
    }

    /* =====================================================
       SIDEBAR SYSTEM CARD
       ===================================================== */

    .sidebar-system {
        margin-top: 35px;
        padding: 18px;
        border-radius: 16px;
        border: 1px solid rgba(120,220,170,0.35);
        background: rgba(0,0,0,0.15);
    }

    .sidebar-system-title {
        color: #cce3db;
        font-size: 12px;
    }

    .sidebar-online {
        color: #64e58b;
        font-size: 18px;
        font-weight: 800;
        margin-top: 5px;
    }

    .sidebar-uptime {
        color: #d0e3dd;
        font-size: 12px;
        margin-top: 13px;
        line-height: 1.7;
    }

    /* =====================================================
       TOP HEADER
       ===================================================== */

    .top-header {
        background: white;
        border-radius: 18px;
        padding: 17px 22px;
        border: 1px solid #dfe9e4;
        box-shadow: 0 5px 20px rgba(25,65,45,0.07);
        min-height: 72px;
    }

    .brand-title {
        font-size: 30px;
        font-weight: 850;
        color: #003f32;
        line-height: 1.1;
    }

    .brand-subtitle {
        color: #718079;
        font-size: 13px;
        margin-top: 4px;
    }

    .online-pill {
        display: inline-block;
        background: #e7f8ed;
        color: #087c3e;
        border: 1px solid #b9e4c7;
        border-radius: 25px;
        padding: 8px 15px;
        font-size: 12px;
        font-weight: 800;
    }

    .datetime {
        color: #6f7c76;
        font-size: 11px;
        margin-top: 8px;
    }

    /* =====================================================
       HERO
       ===================================================== */

    .hero {
        background:
            linear-gradient(
                135deg,
                #eaf7ee,
                #ffffff 70%
            );

        border: 1px solid #dce9e2;
        border-radius: 18px;
        padding: 23px 25px;
        margin-top: 18px;
        margin-bottom: 18px;
    }

    .hero-title {
        font-size: 27px;
        font-weight: 850;
        color: #063d31;
    }

    .hero-text {
        font-size: 13px;
        color: #718079;
        margin-top: 5px;
    }

    /* =====================================================
       SECTION TITLE
       ===================================================== */

    .section-title {
        font-size: 20px;
        font-weight: 850;
        color: #073e34;
        margin-top: 20px;
        margin-bottom: 12px;
    }

    /* =====================================================
       KPI CARDS
       ===================================================== */

    .kpi-card {
        background: white;
        border: 1px solid #dfe8e3;
        border-radius: 17px;
        padding: 19px;
        min-height: 145px;

        box-shadow:
            0 6px 20px rgba(25,65,45,0.06);

        transition: all 0.2s ease;
    }

    .kpi-card:hover {
        transform: translateY(-2px);

        box-shadow:
            0 10px 28px rgba(25,65,45,0.10);
    }

    .kpi-icon {
        font-size: 25px;
        margin-bottom: 7px;
    }

    .kpi-label {
        color: #738079;
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 0.5px;
    }

    .kpi-value {
        font-size: 23px;
        font-weight: 850;
        margin-top: 6px;
    }

    .kpi-green {
        color: #087b3d;
    }

    .kpi-blue {
        color: #1676c9;
    }

    .kpi-purple {
        color: #7041c5;
    }

    .kpi-description {
        color: #8a9690;
        font-size: 11px;
        margin-top: 8px;
    }

    /* =====================================================
       PANELS
       ===================================================== */

    .panel {
        background: white;
        border: 1px solid #dfe8e3;
        border-radius: 18px;
        padding: 19px;
        box-shadow: 0 6px 20px rgba(25,65,45,0.06);
        margin-bottom: 10px;
    }

    .panel-title {
        color: #063d31;
        font-size: 19px;
        font-weight: 850;
    }

    .panel-description {
        color: #78847f;
        font-size: 12px;
        line-height: 1.5;
        margin-top: 5px;
    }

    /* =====================================================
       IMAGE
       ===================================================== */

    [data-testid="stImage"] img {
        border-radius: 14px;
        border: 1px solid #dfe8e3;
    }

    /* =====================================================
       BUTTONS
       ===================================================== */

    .stButton > button {
        border-radius: 11px !important;
        min-height: 45px;
        font-weight: 750 !important;
        border: 1px solid #d7e3dd !important;
        background: white;
        color: #123e33;
        transition: all 0.2s ease;
    }

    .stButton > button:hover {
        transform: translateY(-1px);
        border-color: #159451 !important;
        box-shadow: 0 5px 14px rgba(0,0,0,0.10);
    }

    /* Primary buttons */

    .stButton > button[kind="primary"] {
        background: linear-gradient(
            135deg,
            #159653,
            #087b3e
        ) !important;

        color: white !important;
        border: none !important;
    }

    /* =====================================================
       INPUTS
       ===================================================== */

    div[data-baseweb="input"],
    div[data-baseweb="select"] {
        border-radius: 10px !important;
    }

    div[data-baseweb="slider"] {
        margin-top: 5px;
    }

    /* =====================================================
       STATUS
       ===================================================== */

    .status-ready {
        background: #edfbf2;
        border: 1px solid #c5ecd2;
        border-radius: 14px;
        padding: 17px;
        color: #08753b;
    }

    .status-warning {
        background: #fff8e5;
        border: 1px solid #f1dc9e;
        border-radius: 14px;
        padding: 17px;
        color: #956800;
    }

    .status-error {
        background: #fff0f0;
        border: 1px solid #efc0c0;
        border-radius: 14px;
        padding: 17px;
        color: #b42318;
    }

    /* =====================================================
       ROVER JOYSTICK
       ===================================================== */

    .joystick-button {
        background: linear-gradient(
            145deg,
            #d8f6e5,
            #b8ebd0
        );

        border-radius: 16px;
        height: 62px;

        display: flex;
        align-items: center;
        justify-content: center;

        font-size: 26px;
        color: #07583d;

        border: 1px solid #b6e5cb;
    }

    .joystick-stop {
        background: #b9ebd0;
        width: 82px;
        height: 82px;

        border-radius: 50%;

        display: flex;
        align-items: center;
        justify-content: center;

        margin: auto;

        font-size: 16px;
        font-weight: 850;
        color: #07583d;
    }

    /* =====================================================
       DETECTION
       ===================================================== */

    .detection-card {
        background: linear-gradient(
            135deg,
            #f4faf6,
            #ffffff
        );

        border: 1px solid #dfe8e3;
        border-radius: 16px;

        padding: 19px;

        min-height: 175px;

        box-shadow:
            0 5px 18px rgba(30,70,50,0.04);
    }

    .detection-title {
        color: #063d31;
        font-size: 18px;
        font-weight: 850;
    }

    .detection-label {
        color: #77837e;
        font-size: 11px;
        margin-top: 13px;
    }

    .detection-value {
        color: #073e34;
        font-size: 17px;
        font-weight: 750;
        margin-top: 4px;
    }

    /* =====================================================
       WORKFLOW
       ===================================================== */

    .workflow-card {
        background: white;
        border: 1px solid #dfe8e3;
        border-radius: 16px;

        padding: 18px;

        min-height: 135px;

        box-shadow:
            0 5px 18px rgba(30,70,50,0.05);
    }

    .step-number {
        color: #128047;
        font-size: 12px;
        font-weight: 850;
    }

    .step-title {
        color: #073e34;
        font-size: 17px;
        font-weight: 850;
        margin-top: 7px;
    }

    .step-description {
        color: #7c8883;
        font-size: 11px;
        line-height: 1.5;
        margin-top: 5px;
    }

    /* =====================================================
       FOOTER
       ===================================================== */

    .footer {
        text-align: center;
        color: #89948f;
        font-size: 11px;
        padding: 25px 0 5px 0;
    }

    /* =====================================================
       MOBILE
       ===================================================== */

    @media (max-width: 900px) {

        .main .block-container {
            padding-left: 1rem;
            padding-right: 1rem;
        }

        .hero-title {
            font-size: 23px;
        }

        .brand-title {
            font-size: 24px;
        }
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# BACKEND FUNCTIONS
# ============================================================

def get_state():

    try:

        response = requests.get(
            BACKEND_URL + "/state",
            timeout=REQUEST_TIMEOUT
        )

        if response.status_code == 200:
            return response.json()

    except Exception:
        pass

    return None


def send_capture():

    try:

        return requests.post(
            BACKEND_URL + "/capture",
            timeout=REQUEST_TIMEOUT
        )

    except Exception as e:

        st.error(f"Backend connection error: {e}")

        return None


def send_spray(amount_ml):

    try:

        return requests.post(
            BACKEND_URL + "/spray",
            json={
                "amount_ml": amount_ml
            },
            timeout=REQUEST_TIMEOUT
        )

    except Exception as e:

        st.error(f"Backend connection error: {e}")

        return None


def send_rover_command(command, speed):

    try:

        return requests.post(
            BACKEND_URL + "/rover",
            json={
                "command": command,
                "speed": speed
            },
            timeout=REQUEST_TIMEOUT
        )

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

    except Exception:
        pass

    return None


# ============================================================
# EXTRACT STATE
# ============================================================

def extract_state(state):

    if state is None:

        return {
            "spray_status": "OFFLINE",
            "sprayed_amount": 0.0,
            "raspberry_online": False,
            "image_available": False,
            "esp32_online": False,
            "rover_status": "UNKNOWN",
            "speed": 50
        }

    raspberry = state.get(
        "raspberry_pi",
        {}
    )

    esp32 = state.get(
        "esp32",
        {}
    )

    spray_status = raspberry.get(
        "spray_status",
        state.get(
            "status",
            "READY"
        )
    )

    sprayed_amount = raspberry.get(
        "sprayed_amount",
        state.get(
            "sprayed_amount",
            0.0
        )
    )

    raspberry_online = raspberry.get(
        "online",
        True
    )

    image_available = raspberry.get(
        "image_available",
        False
    )

    esp32_online = esp32.get(
        "online",
        False
    )

    rover_status = esp32.get(
        "rover_status",
        "STOPPED"
    )

    speed = esp32.get(
        "speed",
        50
    )

    return {
        "spray_status": spray_status,
        "sprayed_amount": sprayed_amount,
        "raspberry_online": raspberry_online,
        "image_available": image_available,
        "esp32_online": esp32_online,
        "rover_status": rover_status,
        "speed": speed
    }


# ============================================================
# GET CURRENT STATE
# ============================================================

state = get_state()

info = extract_state(state)

spray_status = info["spray_status"]
sprayed_amount = info["sprayed_amount"]
raspberry_online = info["raspberry_online"]
image_available = info["image_available"]
esp32_online = info["esp32_online"]
rover_status = info["rover_status"]
current_speed = info["speed"]


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown(
        """
        <div class="sidebar-brand">

            <div class="sidebar-logo">
                🌿
            </div>

            <div class="sidebar-name">
                CropIQ
            </div>

            <div class="sidebar-tagline">
                Precision Farming<br>
                for a Greener Tomorrow
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="sidebar-section">MAIN MENU</div>',
        unsafe_allow_html=True
    )

    page = st.radio(
        "Navigation",
        [
            "🏠 Dashboard",
            "📷 Live View",
            "🚜 Rover Control",
            "💧 Sprayer Control",
            "🌿 AI Detection",
            "⚙️ Settings"
        ],
        label_visibility="collapsed"
    )

    st.markdown(
        f"""
        <div class="sidebar-system">

            <div class="sidebar-system-title">
                🍓 Raspberry Pi
            </div>

            <div class="sidebar-online">
                {"● ONLINE" if raspberry_online else "● OFFLINE"}
            </div>

            <div class="sidebar-uptime">
                System Status<br>
                <b>
                    {"Operational" if raspberry_online else "Disconnected"}
                </b>
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# TOP HEADER
# ============================================================

header_left, header_right = st.columns(
    [4, 1.6]
)

with header_left:

    st.markdown(
        """
        <div class="top-header">

            <div class="brand-title">
                🌱 CropIQ
            </div>

            <div class="brand-subtitle">
                Precision Agriculture Intelligence Platform
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )


with header_right:

    st.markdown(
        f"""
        <div class="top-header" style="text-align:center;">

            <div class="online-pill">
                🟢 SYSTEM {"ONLINE" if state is not None else "OFFLINE"}
            </div>

            <div class="datetime">
                {datetime.now().strftime("%d %b %Y • %I:%M:%S %p")}
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# DASHBOARD
# ============================================================

if page == "🏠 Dashboard":

    # ========================================================
    # HERO
    # ========================================================

    st.markdown(
        """
        <div class="hero">

            <div class="hero-title">
                🌿 Precision Spraying Control
            </div>

            <div class="hero-text">
                Monitor the plant, control the rover,
                configure spray dosage, and perform
                precision spraying.
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )


    # ========================================================
    # SYSTEM OVERVIEW
    # ========================================================

    st.markdown(
        '<div class="section-title">System Overview</div>',
        unsafe_allow_html=True
    )

    k1, k2, k3, k4 = st.columns(4)


    # SPRAYER

    with k1:

        st.markdown(
            f"""
            <div class="kpi-card">

                <div class="kpi-icon">
                    💦
                </div>

                <div class="kpi-label">
                    SPRAYER STATUS
                </div>

                <div class="kpi-value kpi-green">
                    {str(spray_status).upper()}
                </div>

                <div class="kpi-description">
                    Current operation
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )


    # LAST DISPENSED

    with k2:

        st.markdown(
            f"""
            <div class="kpi-card">

                <div class="kpi-icon">
                    💧
                </div>

                <div class="kpi-label">
                    LAST DISPENSED
                </div>

                <div class="kpi-value kpi-blue">
                    {float(sprayed_amount):.1f} ml
                </div>

                <div class="kpi-description">
                    Latest spray quantity
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )


    # CAMERA

    with k3:

        camera_status = (
            "READY"
            if raspberry_online
            else "OFFLINE"
        )

        st.markdown(
            f"""
            <div class="kpi-card">

                <div class="kpi-icon">
                    📷
                </div>

                <div class="kpi-label">
                    CAMERA
                </div>

                <div class="kpi-value kpi-green">
                    {camera_status}
                </div>

                <div class="kpi-description">
                    Plant imaging system
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )


    # ESP32

    with k4:

        esp_status = (
            "ONLINE"
            if esp32_online
            else "OFFLINE"
        )

        st.markdown(
            f"""
            <div class="kpi-card">

                <div class="kpi-icon">
                    🔌
                </div>

                <div class="kpi-label">
                    ESP32 ROVER
                </div>

                <div class="kpi-value kpi-purple">
                    {esp_status}
                </div>

                <div class="kpi-description">
                    Rover hardware connection
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )


    # ========================================================
    # MAIN CONTROL AREA
    # ========================================================

    st.markdown(
        '<div class="section-title">Plant Monitoring & Control</div>',
        unsafe_allow_html=True
    )

    camera_col, rover_col, spray_col = st.columns(
        [1.35, 1, 1]
    )


    # ========================================================
    # CAMERA
    # ========================================================

    with camera_col:

        st.markdown(
            """
            <div class="panel">

                <div class="panel-title">
                    📷 Live Camera Feed
                </div>

                <div class="panel-description">
                    Latest image captured from the
                    Raspberry Pi camera.
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )

        image = get_latest_image()

        if image is not None:

            st.image(
                image,
                use_container_width=True
            )

            st.success(
                "🟢 LIVE • Image available"
            )

        else:

            st.info(
                "📷 No plant image available yet."
            )

        if st.button(
            "📸 CAPTURE PLANT IMAGE",
            use_container_width=True,
            key="dashboard_capture"
        ):

            response = send_capture()

            if response is not None:

                if response.status_code == 200:

                    st.success(
                        "Capture command sent to Raspberry Pi."
                    )

                    time.sleep(0.5)
                    st.rerun()

                elif response.status_code == 409:

                    st.warning(
                        "Another command is already pending."
                    )

                else:

                    st.error(
                        f"Capture failed: {response.text}"
                    )


    # ========================================================
    # ROVER
    # ========================================================

    with rover_col:

        st.markdown(
            """
            <div class="panel">

                <div class="panel-title">
                    🚜 Rover Control
                </div>

                <div class="panel-description">
                    Manually control rover movement.
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )

        if esp32_online:
            st.success("🟢 ESP32 ONLINE")
        else:
            st.error("🔴 ESP32 OFFLINE")


        st.markdown(
            f"""
            <div style="
                text-align:center;
                color:#53615b;
                margin:10px 0;
                font-size:13px;
            ">
                Rover:
                <b>{rover_status}</b>
            </div>
            """,
            unsafe_allow_html=True
        )


        speed = st.slider(
            "Speed",
            0,
            100,
            int(current_speed),
            5,
            key="dashboard_speed"
        )


        # FORWARD

        c1, c2, c3 = st.columns(3)

        with c2:

            if st.button(
                "⬆️",
                use_container_width=True,
                key="forward"
            ):

                response = send_rover_command(
                    "F",
                    speed
                )

                if response is not None:

                    if response.status_code == 200:
                        st.success("Forward")

                    else:
                        st.error(response.text)


        # LEFT STOP RIGHT

        c1, c2, c3 = st.columns(3)

        with c1:

            if st.button(
                "⬅️",
                use_container_width=True,
                key="left"
            ):

                response = send_rover_command(
                    "L",
                    speed
                )

                if response is not None:

                    if response.status_code != 200:
                        st.error(response.text)


        with c2:

            if st.button(
                "⛔",
                use_container_width=True,
                key="stop"
            ):

                response = send_rover_command(
                    "S",
                    speed
                )

                if response is not None:

                    if response.status_code == 200:
                        st.success("Stopped")

                    else:
                        st.error(response.text)


        with c3:

            if st.button(
                "➡️",
                use_container_width=True,
                key="right"
            ):

                response = send_rover_command(
                    "R",
                    speed
                )

                if response is not None:

                    if response.status_code != 200:
                        st.error(response.text)


        # BACKWARD

        c1, c2, c3 = st.columns(3)

        with c2:

            if st.button(
                "⬇️",
                use_container_width=True,
                key="backward"
            ):

                response = send_rover_command(
                    "B",
                    speed
                )

                if response is not None:

                    if response.status_code != 200:
                        st.error(response.text)


    # ========================================================
    # SPRAYER
    # ========================================================

    with spray_col:

        st.markdown(
            """
            <div class="panel">

                <div class="panel-title">
                    💧 Sprayer Control
                </div>

                <div class="panel-description">
                    Configure dosage and activate
                    precision spraying.
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )


        if str(spray_status).upper() == "SPRAYING":

            st.warning(
                "🟡 SPRAYER ACTIVE"
            )

        else:

            st.success(
                f"🟢 {str(spray_status).upper()}"
            )


        dosage = st.number_input(
            "Spray dosage (ml)",
            min_value=1.0,
            max_value=500.0,
            value=25.0,
            step=1.0,
            key="dashboard_dosage"
        )


        st.caption(
            "Allowed range: 1 – 500 ml"
        )


        if st.button(
            "🚿 START PRECISION SPRAY",
            type="primary",
            use_container_width=True,
            key="dashboard_spray"
        ):

            response = send_spray(
                dosage
            )

            if response is not None:

                if response.status_code == 200:

                    st.success(
                        f"Spray command sent: {dosage:.1f} ml"
                    )

                elif response.status_code == 409:

                    st.warning(
                        "A spray operation is already running."
                    )

                else:

                    st.error(
                        f"Spray failed: {response.text}"
                    )


        st.info(
            "💡 Selected dosage will be sent "
            "to the Raspberry Pi sprayer."
        )


    # ========================================================
    # LIVE SPRAY STATUS
    # ========================================================

    st.markdown(
        '<div class="section-title">Live Spray Status</div>',
        unsafe_allow_html=True
    )


    if str(spray_status).upper() == "SPRAYING":

        st.warning(
            f"🟡 SPRAYING • "
            f"{float(sprayed_amount):.1f} ml dispensed"
        )

    elif str(spray_status).upper() == "COMPLETED":

        st.success(
            f"🟢 COMPLETED • "
            f"{float(sprayed_amount):.1f} ml sprayed"
        )

    else:

        st.success(
            "🟢 READY • System is ready for the "
            "next precision spraying operation."
        )


    # ========================================================
    # AI DETECTION
    # ========================================================

    st.markdown(
        '<div class="section-title">🌿 AI Detection</div>',
        unsafe_allow_html=True
    )


    detection1, detection2, detection3 = st.columns(
        [1.1, 1.2, 0.8]
    )


    with detection1:

        st.markdown(
            """
            <div class="detection-card">

                <div class="detection-title">
                    🌿 Plant Analysis
                </div>

                <div class="detection-label">
                    DETECTION STATUS
                </div>

                <div class="detection-value">
                    Awaiting Analysis
                </div>

                <div class="detection-label">
                    Capture an image to begin
                    plant analysis.
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )


    with detection2:

        st.markdown(
            """
            <div class="detection-card">

                <div class="detection-title">
                    🔍 Disease Detection
                </div>

                <div class="detection-label">
                    DETECTED CONDITION
                </div>

                <div class="detection-value">
                    No analysis available
                </div>

                <div class="detection-label">
                    AI disease classification will
                    appear here when connected.
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )


    with detection3:

        st.markdown(
            """
            <div class="detection-card">

                <div class="detection-title">
                    💡 Recommendation
                </div>

                <div class="detection-label">
                    ACTION
                </div>

                <div class="detection-value">
                    Awaiting Detection
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )


    # ========================================================
    # WORKFLOW
    # ========================================================

    st.markdown(
        '<div class="section-title">CropIQ Workflow</div>',
        unsafe_allow_html=True
    )


    w1, w2, w3, w4 = st.columns(4)


    workflow = [
        (
            w1,
            "STEP 01",
            "📷 Capture",
            "Capture the latest plant image using the Raspberry Pi camera."
        ),

        (
            w2,
            "STEP 02",
            "🌿 Analyze",
            "Analyze the captured plant image using the AI detection system."
        ),

        (
            w3,
            "STEP 03",
            "🎯 Target",
            "Determine the treatment area and required spray quantity."
        ),

        (
            w4,
            "STEP 04",
            "💧 Spray",
            "Apply the selected spray dosage to the identified target."
        )
    ]


    for column, step, title, description in workflow:

        with column:

            st.markdown(
                f"""
                <div class="workflow-card">

                    <div class="step-number">
                        {step}
                    </div>

                    <div class="step-title">
                        {title}
                    </div>

                    <div class="step-description">
                        {description}
                    </div>

                </div>
                """,
                unsafe_allow_html=True
            )


# ============================================================
# LIVE VIEW
# ============================================================

elif page == "📷 Live View":

    st.markdown(
        '<div class="section-title">📷 Live Plant Monitoring</div>',
        unsafe_allow_html=True
    )


    image = get_latest_image()


    if image is not None:

        st.image(
            image,
            caption="Latest image from Raspberry Pi camera",
            use_container_width=True
        )

    else:

        st.info(
            "No plant image available."
        )


    if st.button(
        "📸 CAPTURE NEW IMAGE",
        type="primary",
        use_container_width=True
    ):

        response = send_capture()

        if response is not None:

            if response.status_code == 200:

                st.success(
                    "Capture command sent!"
                )

                time.sleep(0.5)
                st.rerun()

            else:

                st.error(
                    response.text
                )


# ============================================================
# ROVER CONTROL
# ============================================================

elif page == "🚜 Rover Control":

    st.markdown(
        '<div class="section-title">🚜 Rover Control</div>',
        unsafe_allow_html=True
    )


    if esp32_online:
        st.success("🟢 ESP32 ONLINE")
    else:
        st.error("🔴 ESP32 OFFLINE")


    speed = st.slider(
        "Rover Speed",
        0,
        100,
        int(current_speed),
        5,
        key="rover_page_speed"
    )


    st.markdown(
        f"""
        <div style="
            text-align:center;
            font-size:18px;
            font-weight:750;
            color:#073e34;
            margin:15px;
        ">
            Current Rover Status:
            {rover_status}
        </div>
        """,
        unsafe_allow_html=True
    )


    c1, c2, c3 = st.columns(3)

    with c2:

        if st.button(
            "⬆️ FORWARD",
            use_container_width=True,
            key="page_forward"
        ):

            response = send_rover_command(
                "F",
                speed
            )

            if response is not None:
                st.success("Forward command sent.")


    c1, c2, c3 = st.columns(3)


    with c1:

        if st.button(
            "⬅️ LEFT",
            use_container_width=True,
            key="page_left"
        ):

            send_rover_command(
                "L",
                speed
            )


    with c2:

        if st.button(
            "⛔ STOP",
            use_container_width=True,
            key="page_stop"
        ):

            send_rover_command(
                "S",
                speed
            )

            st.success(
                "Rover stopped."
            )


    with c3:

        if st.button(
            "➡️ RIGHT",
            use_container_width=True,
            key="page_right"
        ):

            send_rover_command(
                "R",
                speed
            )


    c1, c2, c3 = st.columns(3)


    with c2:

        if st.button(
            "⬇️ BACKWARD",
            use_container_width=True,
            key="page_backward"
        ):

            send_rover_command(
                "B",
                speed
            )


# ============================================================
# SPRAYER CONTROL
# ============================================================

elif page == "💧 Sprayer Control":

    st.markdown(
        '<div class="section-title">💧 Precision Sprayer Control</div>',
        unsafe_allow_html=True
    )


    col1, col2 = st.columns(2)


    with col1:

        st.metric(
            "Sprayer Status",
            str(spray_status).upper()
        )


    with col2:

        st.metric(
            "Last Dispensed",
            f"{float(sprayed_amount):.2f} ml"
        )


    dosage = st.number_input(
        "Spray dosage (ml)",
        min_value=1.0,
        max_value=500.0,
        value=25.0,
        step=1.0,
        key="sprayer_page_dosage"
    )


    if st.button(
        "🚿 START PRECISION SPRAY",
        type="primary",
        use_container_width=True,
        key="page_spray"
    ):

        response = send_spray(
            dosage
        )

        if response is not None:

            if response.status_code == 200:

                st.success(
                    f"Spray command sent: {dosage:.1f} ml"
                )

            elif response.status_code == 409:

                st.warning(
                    "Sprayer is already operating."
                )

            else:

                st.error(
                    response.text
                )


# ============================================================
# AI DETECTION
# ============================================================

elif page == "🌿 AI Detection":

    st.markdown(
        '<div class="section-title">🌿 AI Plant Detection</div>',
        unsafe_allow_html=True
    )


    image = get_latest_image()


    if image is not None:

        st.image(
            image,
            caption="Plant image for analysis",
            use_container_width=True
        )

    else:

        st.info(
            "Capture a plant image first."
        )


    st.markdown(
        """
        <div class="detection-card">

            <div class="detection-title">
                🔬 AI Disease Analysis
            </div>

            <div class="detection-label">
                STATUS
            </div>

            <div class="detection-value">
                AI analysis endpoint not connected
            </div>

            <div class="detection-label">
                Connect your plant disease detection
                model here to display disease,
                confidence and treatment recommendation.
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# SETTINGS
# ============================================================

elif page == "⚙️ Settings":

    st.markdown(
        '<div class="section-title">⚙️ CropIQ Settings</div>',
        unsafe_allow_html=True
    )


    st.subheader("Backend")

    st.code(
        BACKEND_URL
    )


    st.subheader("Spray Configuration")

    st.write(
        "Minimum dosage: 1 ml"
    )

    st.write(
        "Maximum dosage: 500 ml"
    )


    st.subheader("Hardware")


    if raspberry_online:

        st.success(
            "🍓 Raspberry Pi connected"
        )

    else:

        st.error(
            "🍓 Raspberry Pi unavailable"
        )


    if esp32_online:

        st.success(
            "🚜 ESP32 connected"
        )

    else:

        st.error(
            "🚜 ESP32 unavailable"
        )


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    """
    <div class="footer">
        © 2026 CropIQ &nbsp; • &nbsp;
        Precision Agriculture &nbsp; • &nbsp;
        AI-Powered Targeted Spraying
    </div>
    """,
    unsafe_allow_html=True
)
