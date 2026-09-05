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
    page_icon="🌿",
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
        background: #f3f7f5;
    }

    .main .block-container {
        max-width: 1500px;
        padding-top: 1.5rem;
        padding-bottom: 2rem;
        padding-left: 2rem;
        padding-right: 2rem;
    }

    /* Hide Streamlit default elements */

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
            #004d3d 45%,
            #002f27 100%
        );
        min-width: 270px;
        max-width: 270px;
    }

    section[data-testid="stSidebar"] > div {
        background: transparent;
    }

    section[data-testid="stSidebar"] .block-container {
        padding: 1.5rem 1rem;
    }

    /* Sidebar text */

    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] span {
        color: white !important;
    }

    /* Sidebar radio */

    section[data-testid="stSidebar"] div[role="radiogroup"] {
        gap: 8px;
    }

    section[data-testid="stSidebar"] div[role="radiogroup"] > label {
        background: transparent;
        border-radius: 12px;
        padding: 12px 14px;
        transition: 0.2s;
    }

    section[data-testid="stSidebar"] div[role="radiogroup"] > label:hover {
        background: rgba(255,255,255,0.08);
    }

    section[data-testid="stSidebar"] div[role="radiogroup"] > label[data-checked="true"] {
        background: linear-gradient(
            90deg,
            #159447,
            #087c3b
        );
        box-shadow: 0 5px 15px rgba(0,0,0,0.18);
    }

    /* Hide radio circles */

    section[data-testid="stSidebar"] div[role="radiogroup"] > label > div:first-child {
        display: none;
    }


    /* =====================================================
       SIDEBAR BRAND
       ===================================================== */

    .sidebar-brand {
        text-align: center;
        padding: 10px 5px 25px 5px;
    }

    .sidebar-logo {
        font-size: 48px;
        line-height: 1;
    }

    .sidebar-name {
        font-size: 32px;
        font-weight: 800;
        color: white;
        margin-top: 5px;
    }

    .sidebar-tagline {
        color: #c6ddd6;
        font-size: 13px;
        line-height: 1.5;
        margin-top: 8px;
    }

    .sidebar-section {
        color: #8fc8b9;
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 1.5px;
        margin-top: 20px;
        margin-bottom: 8px;
    }


    /* =====================================================
       SIDEBAR SYSTEM CARD
       ===================================================== */

    .sidebar-system {
        margin-top: 30px;
        padding: 18px;
        border-radius: 16px;
        border: 1px solid rgba(125,220,174,0.35);
        background: rgba(0,0,0,0.13);
    }

    .sidebar-system-title {
        color: #d9eee7;
        font-size: 12px;
    }

    .sidebar-online {
        color: #62e88d;
        font-size: 18px;
        font-weight: 700;
        margin-top: 4px;
    }

    .sidebar-uptime {
        color: white;
        font-size: 13px;
        margin-top: 14px;
    }


    /* =====================================================
       TOP HEADER
       ===================================================== */

    .top-header {
        background: white;
        border-radius: 20px;
        padding: 18px 25px;
        box-shadow: 0 5px 25px rgba(25,65,45,0.08);
        border: 1px solid #e2ebe6;
        margin-bottom: 20px;
    }

    .brand-title {
        font-size: 30px;
        font-weight: 800;
        color: #003f32;
        margin: 0;
    }

    .brand-subtitle {
        color: #697772;
        font-size: 14px;
        margin-top: 3px;
    }

    .online-pill {
        display: inline-block;
        background: #e8f8ed;
        color: #087b3d;
        border: 1px solid #b9e5c6;
        border-radius: 25px;
        padding: 9px 16px;
        font-size: 13px;
        font-weight: 700;
    }


    /* =====================================================
       HERO
       ===================================================== */

    .hero {
        background: linear-gradient(
            135deg,
            #eef8f1,
            #ffffff
        );
        border-radius: 20px;
        border: 1px solid #dfeae4;
        padding: 22px 25px;
        margin-bottom: 18px;
    }

    .hero-title {
        font-size: 28px;
        font-weight: 800;
        color: #003f32;
        margin-bottom: 5px;
    }

    .hero-text {
        color: #697772;
        font-size: 14px;
    }


    /* =====================================================
       SECTION TITLE
       ===================================================== */

    .section-title {
        font-size: 21px;
        font-weight: 800;
        color: #073e34;
        margin-top: 18px;
        margin-bottom: 12px;
    }


    /* =====================================================
       KPI CARDS
       ===================================================== */

    .kpi-card {
        background: white;
        border-radius: 17px;
        border: 1px solid #dfe8e3;
        padding: 20px;
        min-height: 145px;
        box-shadow: 0 5px 18px rgba(30,70,50,0.06);
    }

    .kpi-icon {
        font-size: 27px;
        margin-bottom: 5px;
    }

    .kpi-label {
        color: #738079;
        font-size: 12px;
        font-weight: 600;
        letter-spacing: 0.5px;
    }

    .kpi-value {
        color: #073e34;
        font-size: 24px;
        font-weight: 800;
        margin-top: 7px;
    }

    .kpi-green {
        color: #087d3e;
    }

    .kpi-blue {
        color: #1476c9;
    }

    .kpi-purple {
        color: #7141c7;
    }

    .kpi-description {
        color: #8b9691;
        font-size: 12px;
        margin-top: 8px;
    }


    /* =====================================================
       PANELS
       ===================================================== */

    .panel {
        background: white;
        border: 1px solid #dfe8e3;
        border-radius: 18px;
        padding: 18px;
        box-shadow: 0 5px 18px rgba(30,70,50,0.06);
        margin-bottom: 18px;
    }

    .panel-title {
        color: #073e34;
        font-size: 20px;
        font-weight: 800;
        margin-bottom: 5px;
    }

    .panel-description {
        color: #78847f;
        font-size: 13px;
        margin-bottom: 15px;
    }


    /* =====================================================
       IMAGE
       ===================================================== */

    [data-testid="stImage"] img {
        border-radius: 14px;
    }


    /* =====================================================
       BUTTONS
       ===================================================== */

    .stButton > button {
        border-radius: 11px !important;
        min-height: 46px;
        font-weight: 700 !important;
        border: 1px solid #d9e5df !important;
        transition: all 0.2s ease;
    }

    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.10);
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
       ROVER CONTROL
       ===================================================== */

    .rover-circle {
        width: 75px;
        height: 75px;
        background: linear-gradient(
            145deg,
            #d8f6e5,
            #b6ebce
        );
        border-radius: 18px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 28px;
        color: #07583d;
        margin: auto;
    }

    .stop-box {
        width: 85px;
        height: 85px;
        border-radius: 50%;
        background: #b8ebd0;
        display: flex;
        align-items: center;
        justify-content: center;
        margin: auto;
        color: #07583d;
        font-weight: 800;
    }


    /* =====================================================
       STATUS BOX
       ===================================================== */

    .status-ready {
        background: #edfbf2;
        border: 1px solid #c5ecd2;
        border-radius: 14px;
        padding: 18px;
        color: #08753b;
    }

    .status-warning {
        background: #fff8e5;
        border: 1px solid #f1dc9e;
        border-radius: 14px;
        padding: 18px;
        color: #956800;
    }

    .status-error {
        background: #fff0f0;
        border: 1px solid #efc0c0;
        border-radius: 14px;
        padding: 18px;
        color: #b42318;
    }


    /* =====================================================
       AI DETECTION
       ===================================================== */

    .detection-card {
        background: linear-gradient(
            135deg,
            #f6faf7,
            #ffffff
        );
        border: 1px solid #dfe8e3;
        border-radius: 16px;
        padding: 20px;
        min-height: 180px;
    }

    .detection-title {
        color: #063d31;
        font-size: 20px;
        font-weight: 800;
    }

    .detection-label {
        color: #77837e;
        font-size: 12px;
        margin-top: 10px;
    }

    .detection-value {
        color: #073e34;
        font-size: 18px;
        font-weight: 700;
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
        min-height: 130px;
    }

    .step-number {
        color: #128047;
        font-size: 13px;
        font-weight: 800;
    }

    .step-title {
        color: #073e34;
        font-size: 18px;
        font-weight: 800;
        margin-top: 8px;
    }

    .step-description {
        color: #7c8883;
        font-size: 12px;
        line-height: 1.5;
        margin-top: 5px;
    }


    /* =====================================================
       FOOTER
       ===================================================== */

    .footer {
        text-align: center;
        color: #89948f;
        font-size: 12px;
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
# HELPER FUNCTIONS
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

    raspberry = state.get("raspberry_pi", {})
    esp32 = state.get("esp32", {})

    spray_status = raspberry.get(
        "spray_status",
        state.get("status", "READY")
    )

    sprayed_amount = raspberry.get(
        "sprayed_amount",
        state.get("sprayed_amount", 0.0)
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
# GET STATE
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

            <div class="sidebar-logo">🌿</div>

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
                <b>{"Operational" if raspberry_online else "Disconnected"}</b>
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# TOP HEADER
# ============================================================

header_left, header_right = st.columns([4, 2])

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

            <div style="
                color:#6f7c76;
                font-size:12px;
                margin-top:9px;
            ">
                {datetime.now().strftime("%d %b %Y • %I:%M:%S %p")}
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# DASHBOARD PAGE
# ============================================================

if page == "🏠 Dashboard":

    # --------------------------------------------------------
    # HERO
    # --------------------------------------------------------

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


    # --------------------------------------------------------
    # SYSTEM OVERVIEW
    # --------------------------------------------------------

    st.markdown(
        '<div class="section-title">System Overview</div>',
        unsafe_allow_html=True
    )

    k1, k2, k3, k4 = st.columns(4)

    with k1:

        spray_display = str(spray_status).upper()

        st.markdown(
            f"""
            <div class="kpi-card">

                <div class="kpi-icon">💦</div>

                <div class="kpi-label">
                    SPRAYER STATUS
                </div>

                <div class="kpi-value kpi-green">
                    {spray_display}
                </div>

                <div class="kpi-description">
                    Current operation
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )


    with k2:

        st.markdown(
            f"""
            <div class="kpi-card">

                <div class="kpi-icon">💧</div>

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


    with k3:

        camera_status = "READY" if raspberry_online else "OFFLINE"

        st.markdown(
            f"""
            <div class="kpi-card">

                <div class="kpi-icon">📷</div>

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


    with k4:

        esp_status = "ONLINE" if esp32_online else "OFFLINE"

        st.markdown(
            f"""
            <div class="kpi-card">

                <div class="kpi-icon">🔌</div>

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


    # --------------------------------------------------------
    # MAIN CONTROL AREA
    # --------------------------------------------------------

    st.markdown(
        '<div class="section-title">Plant Monitoring & Control</div>',
        unsafe_allow_html=True
    )

    camera_col, rover_col, spray_col = st.columns(
        [1.45, 1, 1]
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
                "📷 No plant image available yet. "
                "Capture an image to begin monitoring."
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
                margin-bottom:10px;
            ">
                Rover: <b>{rover_status}</b>
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

        # Forward

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


        # Left / Stop / Right

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


        # Backward

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

        if spray_status in [
            "Spraying...",
            "SPRAYING",
            "spraying"
        ]:

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

            response = send_spray(dosage)

            if response is not None:

                if response.status_code == 200:

                    st.success(
                        f"Spray command sent: "
                        f"{dosage:.1f} ml"
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
            "💡 The selected dosage will be sent "
            "to the Raspberry Pi sprayer."
        )


    # ========================================================
    # LIVE SPRAY STATUS
    # ========================================================

    st.markdown(
        '<div class="section-title">Live Spray Status</div>',
        unsafe_allow_html=True
    )

    if spray_status in [
        "Spraying...",
        "SPRAYING",
        "spraying"
    ]:

        st.warning(
            f"🟡 SPRAYING • "
            f"{float(sprayed_amount):.1f} ml dispensed"
        )

    elif spray_status in [
        "Completed",
        "COMPLETED",
        "completed"
    ]:

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
# LIVE VIEW PAGE
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
# ROVER CONTROL PAGE
# ============================================================

elif page == "🚜 Rover Control":

    st.markdown(
        '<div class="section-title">🚜 Rover Control</div>',
        unsafe_allow_html=True
    )

    st.info(
        f"ESP32: {'ONLINE' if esp32_online else 'OFFLINE'}"
    )

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
            font-weight:700;
            color:#073e34;
            margin:15px;
        ">
            Current Rover Status: {rover_status}
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

            send_rover_command("F", speed)
            st.success("Forward command sent.")


    c1, c2, c3 = st.columns(3)

    with c1:

        if st.button(
            "⬅️ LEFT",
            use_container_width=True,
            key="page_left"
        ):

            send_rover_command("L", speed)


    with c2:

        if st.button(
            "⛔ STOP",
            use_container_width=True,
            key="page_stop"
        ):

            send_rover_command("S", speed)
            st.success("Rover stopped.")


    with c3:

        if st.button(
            "➡️ RIGHT",
            use_container_width=True,
            key="page_right"
        ):

            send_rover_command("R", speed)


    c1, c2, c3 = st.columns(3)

    with c2:

        if st.button(
            "⬇️ BACKWARD",
            use_container_width=True,
            key="page_backward"
        ):

            send_rover_command("B", speed)


# ============================================================
# SPRAYER CONTROL PAGE
# ============================================================

elif page == "💧 Sprayer Control":

    st.markdown(
        '<div class="section-title">💧 Precision Sprayer Control</div>',
        unsafe_allow_html=True
    )

    st.metric(
        "Sprayer Status",
        str(spray_status).upper()
    )

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

        response = send_spray(dosage)

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
# AI DETECTION PAGE
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
# SETTINGS PAGE
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
