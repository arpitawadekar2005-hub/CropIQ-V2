import streamlit as st
import requests
from datetime import datetime
from textwrap import dedent
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
# HTML HELPER
# IMPORTANT:
# dedent() prevents Streamlit from displaying HTML as code.
# ============================================================

def html(content):
    st.markdown(
        dedent(content),
        unsafe_allow_html=True
    )


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
<style>

@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');


/* ==========================================================
   GLOBAL
   ========================================================== */

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background: #f4f8f5;
    color: #102c26;
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


/* Main content */

.block-container {
    padding-top: 1.5rem;
    padding-bottom: 2rem;
    max-width: 1500px;
}


/* ==========================================================
   SIDEBAR
   ========================================================== */

[data-testid="stSidebar"] {
    background:
        linear-gradient(
            180deg,
            #003f32 0%,
            #004c3d 45%,
            #002f27 100%
        );
    border-right: none;
}

[data-testid="stSidebar"] > div:first-child {
    padding-top: 1.5rem;
    padding-left: 1rem;
    padding-right: 1rem;
}


/* Sidebar brand */

.sidebar-brand {
    text-align: center;
    padding: 10px 5px 25px 5px;
}

.sidebar-logo {
    font-size: 48px;
    line-height: 1;
    margin-bottom: 5px;
}

.sidebar-title {
    color: white;
    font-size: 32px;
    font-weight: 800;
    letter-spacing: -1px;
}

.sidebar-tagline {
    color: #d5eee4;
    font-size: 13px;
    line-height: 1.5;
    margin-top: 10px;
}


/* Sidebar menu */

.menu-label {
    color: #8dc4b5;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 1.5px;
    margin-top: 20px;
    margin-bottom: 12px;
    padding-left: 8px;
}

.sidebar-menu-item {
    color: #e4f5ef;
    padding: 13px 15px;
    margin: 5px 0;
    border-radius: 12px;
    font-size: 14px;
    font-weight: 500;
}

.sidebar-menu-item.active {
    background: linear-gradient(
        90deg,
        #15945b,
        #087b4b
    );
    color: white;
    box-shadow: 0 5px 15px rgba(0,0,0,0.15);
}

.sidebar-menu-icon {
    width: 28px;
    display: inline-block;
    font-size: 19px;
}


/* Sidebar hardware */

.sidebar-hardware {
    margin-top: 35px;
    border: 1px solid rgba(164, 223, 203, 0.35);
    border-radius: 14px;
    padding: 15px;
    background: rgba(0, 30, 23, 0.25);
}

.hardware-title {
    color: white;
    font-size: 12px;
    font-weight: 600;
}

.hardware-online {
    color: #8bea4d;
    font-size: 14px;
    font-weight: 700;
    margin-top: 3px;
}

.hardware-uptime {
    color: #d2e8e0;
    font-size: 12px;
    margin-top: 12px;
}


/* ==========================================================
   TOP HEADER
   ========================================================== */

.top-header {
    background: rgba(255,255,255,0.96);
    border: 1px solid #e5ece8;
    border-radius: 18px;
    padding: 16px 22px;
    box-shadow: 0 8px 30px rgba(20, 70, 55, 0.08);
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 22px;
}

.brand-left {
    display: flex;
    align-items: center;
    gap: 14px;
}

.brand-icon {
    width: 48px;
    height: 48px;
    border-radius: 13px;
    background: #edf7ee;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 27px;
}

.brand-name {
    color: #073d32;
    font-size: 24px;
    font-weight: 800;
}

.brand-subtitle {
    color: #71807d;
    font-size: 12px;
    margin-top: 3px;
}

.top-right {
    display: flex;
    align-items: center;
    gap: 22px;
}

.system-online {
    border: 1px solid #b8ddc8;
    border-radius: 10px;
    padding: 10px 16px;
    color: #167343;
    background: #f5fcf7;
    font-size: 13px;
    font-weight: 600;
}

.green-dot {
    display: inline-block;
    width: 9px;
    height: 9px;
    background: #3dbb58;
    border-radius: 50%;
    margin-right: 7px;
    box-shadow: 0 0 0 3px #e0f5e5;
}

.datetime {
    color: #596663;
    font-size: 13px;
}


/* ==========================================================
   PAGE TITLE
   ========================================================== */

.page-title {
    font-size: 28px;
    font-weight: 800;
    color: #073d32;
    margin-top: 8px;
}

.page-description {
    color: #6d7d79;
    font-size: 13px;
    margin-bottom: 22px;
}


/* ==========================================================
   SECTION TITLES
   ========================================================== */

.section-title {
    color: #073d32;
    font-size: 20px;
    font-weight: 800;
    margin-top: 20px;
    margin-bottom: 13px;
}


/* ==========================================================
   KPI CARDS
   ========================================================== */

.kpi-card {
    background: white;
    border: 1px solid #e4ebe7;
    border-radius: 15px;
    padding: 17px;
    min-height: 135px;
    box-shadow: 0 5px 18px rgba(30, 70, 55, 0.06);
    position: relative;
    overflow: hidden;
}

.kpi-card:hover {
    box-shadow: 0 8px 25px rgba(30, 70, 55, 0.10);
    transform: translateY(-1px);
}

.kpi-icon {
    width: 44px;
    height: 44px;
    border-radius: 50%;
    background: #eef8ef;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 22px;
    margin-bottom: 10px;
}

.kpi-label {
    font-size: 10px;
    color: #697672;
    font-weight: 600;
    letter-spacing: 0.5px;
}

.kpi-value {
    font-size: 22px;
    font-weight: 800;
    margin-top: 5px;
    color: #087442;
}

.kpi-description {
    color: #7b8784;
    font-size: 11px;
    margin-top: 7px;
}


/* ==========================================================
   MAIN CARDS
   ========================================================== */

.panel {
    background: white;
    border: 1px solid #e3ebe7;
    border-radius: 16px;
    padding: 18px;
    box-shadow: 0 5px 20px rgba(30,70,55,0.06);
    height: 100%;
}

.panel-title {
    color: #0a322a;
    font-size: 18px;
    font-weight: 800;
    margin-bottom: 14px;
}

.panel-subtitle {
    color: #71807d;
    font-size: 12px;
    line-height: 1.5;
}


/* ==========================================================
   LIVE BADGE
   ========================================================== */

.live-badge {
    display: inline-block;
    background: #eaf8ee;
    color: #187443;
    border: 1px solid #cdebd6;
    padding: 7px 12px;
    border-radius: 9px;
    font-size: 11px;
    font-weight: 700;
}

.live-dot {
    display: inline-block;
    width: 8px;
    height: 8px;
    background: #2fbe50;
    border-radius: 50%;
    margin-right: 5px;
}


/* ==========================================================
   CAMERA
   ========================================================== */

.camera-container {
    background: #0d211c;
    border-radius: 12px;
    overflow: hidden;
    position: relative;
    min-height: 350px;
}

.camera-placeholder {
    min-height: 350px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    color: #d3e4df;
    background:
        linear-gradient(
            135deg,
            #193b30,
            #0b241c
        );
}

.camera-placeholder-icon {
    font-size: 55px;
    margin-bottom: 12px;
}

.camera-placeholder-text {
    font-size: 14px;
}


/* ==========================================================
   ROVER
   ========================================================== */

.mode-container {
    display: flex;
    gap: 8px;
    margin-bottom: 20px;
}

.mode-active {
    background: #15945b;
    color: white;
    padding: 9px 18px;
    border-radius: 22px;
    font-size: 12px;
    font-weight: 700;
}

.mode-inactive {
    background: #f1f4f5;
    color: #596663;
    padding: 9px 18px;
    border-radius: 22px;
    font-size: 12px;
}


.rover-pad {
    width: 245px;
    margin: 12px auto 18px auto;
}

.rover-row {
    display: flex;
    justify-content: center;
    gap: 10px;
    margin: 10px 0;
}

.rover-button {
    width: 70px;
    height: 60px;
    background: #d4f3e2;
    border-radius: 11px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #087442;
    font-size: 25px;
    font-weight: 800;
}

.rover-stop {
    width: 70px;
    height: 70px;
    border-radius: 50%;
    background: #b8ebd1;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #087442;
    font-size: 14px;
    font-weight: 800;
}


/* ==========================================================
   SPRAYER
   ========================================================== */

.sprayer-status {
    background: #f4f7f8;
    border-radius: 12px;
    padding: 14px;
    margin-bottom: 15px;
}

.sprayer-status-label {
    color: #263b37;
    font-size: 13px;
    font-weight: 600;
}

.status-off {
    color: #626e6b;
    font-weight: 700;
}

.status-on {
    color: #087442;
    font-weight: 800;
}

.spray-info {
    background: #effaf2;
    border: 1px solid #d2ecd8;
    border-radius: 11px;
    padding: 13px;
    color: #246443;
    font-size: 12px;
    margin-top: 12px;
}


/* ==========================================================
   AI DETECTION
   ========================================================== */

.detection-panel {
    background: white;
    border: 1px solid #e4ebe7;
    border-radius: 16px;
    padding: 18px;
    box-shadow: 0 5px 20px rgba(30,70,55,0.06);
}

.disease-card {
    background: #fff6f6;
    border-radius: 12px;
    border: 1px solid #f1d7d7;
    padding: 17px;
    margin-bottom: 12px;
}

.disease-title {
    color: #9e1717;
    font-size: 11px;
    font-weight: 700;
}

.disease-name {
    color: #172d29;
    font-size: 20px;
    font-weight: 800;
    margin-top: 4px;
}

.disease-description {
    color: #687571;
    font-size: 12px;
    margin-top: 7px;
}

.recommendation {
    background: #eaf9ef;
    border-radius: 12px;
    border: 1px solid #cdebd5;
    padding: 17px;
}

.recommendation-title {
    color: #11703e;
    font-size: 11px;
    font-weight: 700;
}

.recommendation-name {
    color: #17352d;
    font-size: 18px;
    font-weight: 800;
    margin-top: 4px;
}


/* ==========================================================
   QUOTE CARD
   ========================================================== */

.quote-card {
    height: 100%;
    min-height: 250px;
    background:
        linear-gradient(
            135deg,
            #f6fbf5,
            #edf8ef
        );
    border-radius: 15px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    text-align: center;
    padding: 25px;
}

.quote-icon {
    font-size: 45px;
}

.quote {
    color: #17382f;
    font-size: 19px;
    font-style: italic;
    line-height: 1.5;
    font-weight: 600;
}

.quote-line {
    width: 55px;
    height: 4px;
    border-radius: 5px;
    background: #23a65f;
    margin-top: 15px;
}


/* ==========================================================
   BUTTONS
   ========================================================== */

.stButton > button {
    border-radius: 10px !important;
    min-height: 43px !important;
    font-weight: 600 !important;
    border: 1px solid #dce5e1 !important;
}

.stButton > button:hover {
    border-color: #15945b !important;
}

button[kind="primary"] {
    background: #128a50 !important;
    border-color: #128a50 !important;
    color: white !important;
}


/* ==========================================================
   INPUTS
   ========================================================== */

.stNumberInput input,
.stSelectbox select {
    border-radius: 9px !important;
}

div[data-baseweb="select"] > div {
    border-radius: 9px !important;
}


/* ==========================================================
   SLIDER
   ========================================================== */

.stSlider {
    padding-top: 5px;
}


/* ==========================================================
   FOOTER
   ========================================================== */

.footer {
    text-align: center;
    color: #788681;
    font-size: 11px;
    padding: 22px;
}


/* ==========================================================
   MOBILE
   ========================================================== */

@media (max-width: 900px) {

    .top-header {
        flex-direction: column;
        align-items: flex-start;
        gap: 15px;
    }

    .top-right {
        flex-wrap: wrap;
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
# INITIAL STATE
# ============================================================

state = get_state()

if state is None:

    raspberry = {}
    esp32 = {}

else:

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
    "READY"
)

sprayed_amount = raspberry.get(
    "sprayed_amount",
    0.0
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

backend_online = state is not None


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    html("""
    <div class="sidebar-brand">

        <div class="sidebar-logo">
            🌿
        </div>

        <div class="sidebar-title">
            CropIQ
        </div>

        <div class="sidebar-tagline">
            Precision Farming<br>
            for a Greener Tomorrow
        </div>

    </div>
    """)


    st.markdown(
        '<div class="menu-label">MAIN MENU</div>',
        unsafe_allow_html=True
    )


    # Dashboard

    html("""
    <div class="sidebar-menu-item active">
        <span class="sidebar-menu-icon">⌂</span>
        Dashboard
    </div>
    """)


    # Live View

    html("""
    <div class="sidebar-menu-item">
        <span class="sidebar-menu-icon">📷</span>
        Live View
    </div>
    """)


    # Rover

    html("""
    <div class="sidebar-menu-item">
        <span class="sidebar-menu-icon">🎮</span>
        Rover Control
    </div>
    """)


    # Sprayer

    html("""
    <div class="sidebar-menu-item">
        <span class="sidebar-menu-icon">💦</span>
        Sprayer Control
    </div>
    """)


    # AI

    html("""
    <div class="sidebar-menu-item">
        <span class="sidebar-menu-icon">🌿</span>
        AI Detection
    </div>
    """)


    # Settings

    html("""
    <div class="sidebar-menu-item">
        <span class="sidebar-menu-icon">⚙️</span>
        Settings
    </div>
    """)


    # Hardware status

    pi_status = "ONLINE" if backend_online else "OFFLINE"

    html(f"""
    <div class="sidebar-hardware">

        <div style="font-size:22px;">
            📡
        </div>

        <div class="hardware-title">
            Raspberry Pi
        </div>

        <div class="hardware-online">
            ● {pi_status}
        </div>

        <div class="hardware-uptime">
            Uptime<br>
            <strong>--:--:--</strong>
        </div>

    </div>
    """)


# ============================================================
# TOP HEADER
# ============================================================

now = datetime.now()

formatted_date = now.strftime("%a, %d %b %Y")
formatted_time = now.strftime("%I:%M:%S %p")

html(f"""
<div class="top-header">

    <div class="brand-left">

        <div class="brand-icon">
            🌱
        </div>

        <div>
            <div class="brand-name">
                CropIQ
            </div>

            <div class="brand-subtitle">
                Precision Agriculture Intelligence Platform
            </div>
        </div>

    </div>


    <div class="top-right">

        <div class="system-online">

            <span class="green-dot"></span>

            SYSTEM {"ONLINE" if backend_online else "OFFLINE"}

        </div>

        <div class="datetime">

            {formatted_date}
            &nbsp; • &nbsp;
            {formatted_time}

        </div>

        <div style="font-size:22px;">
            🔔
        </div>

    </div>

</div>
""")


# ============================================================
# PAGE TITLE
# ============================================================

html("""
<div class="page-title">
    Welcome to CropIQ
</div>

<div class="page-description">
    AI-Powered Crop Monitoring & Precision Spraying
</div>
""")


# ============================================================
# SYSTEM OVERVIEW
# ============================================================

st.markdown(
    '<div class="section-title">System Overview</div>',
    unsafe_allow_html=True
)

kpi1, kpi2, kpi3, kpi4 = st.columns(4)


# KPI 1

with kpi1:

    html(f"""
    <div class="kpi-card">

        <div class="kpi-icon">
            🚿
        </div>

        <div class="kpi-label">
            SPRAYER STATUS
        </div>

        <div class="kpi-value">
            {str(spray_status).upper()}
        </div>

        <div class="kpi-description">
            Current operation
        </div>

    </div>
    """)


# KPI 2

with kpi2:

    html(f"""
    <div class="kpi-card">

        <div class="kpi-icon">
            💧
        </div>

        <div class="kpi-label">
            LAST DISPENSED
        </div>

        <div class="kpi-value">
            {sprayed_amount:.1f} ml
        </div>

        <div class="kpi-description">
            Latest spray quantity
        </div>

    </div>
    """)


# KPI 3

with kpi3:

    camera_status = "READY" if image_available else "READY"

    html(f"""
    <div class="kpi-card">

        <div class="kpi-icon">
            📷
        </div>

        <div class="kpi-label">
            CAMERA
        </div>

        <div class="kpi-value">
            {camera_status}
        </div>

        <div class="kpi-description">
            Plant imaging system
        </div>

    </div>
    """)


# KPI 4

with kpi4:

    rover_online_text = (
        "ONLINE"
        if esp32_online
        else "OFFLINE"
    )

    html(f"""
    <div class="kpi-card">

        <div class="kpi-icon">
            🎛️
        </div>

        <div class="kpi-label">
            ESP32 ROVER
        </div>

        <div class="kpi-value">
            {rover_online_text}
        </div>

        <div class="kpi-description">
            Rover hardware connection
        </div>

    </div>
    """)


# ============================================================
# MAIN CONTROL AREA
# ============================================================

st.markdown(
    '<div class="section-title">Plant Monitoring & Control</div>',
    unsafe_allow_html=True
)


camera_col, rover_col, spray_col = st.columns(
    [1.35, 1.0, 1.0],
    gap="medium"
)


# ============================================================
# CAMERA PANEL
# ============================================================

with camera_col:

    html("""
    <div class="panel">

        <div style="
            display:flex;
            justify-content:space-between;
            align-items:center;
            margin-bottom:12px;
        ">

            <div class="panel-title">
                📷 Live Camera Feed
            </div>

            <div class="live-badge">
                <span class="live-dot"></span>
                LIVE
            </div>

        </div>

    </div>
    """)


    image = get_latest_image()

    if image is not None:

        st.image(
            image,
            use_container_width=True
        )

    else:

        html("""
        <div class="camera-container">

            <div class="camera-placeholder">

                <div class="camera-placeholder-icon">
                    📷
                </div>

                <div class="camera-placeholder-text">
                    Waiting for Raspberry Pi camera...
                </div>

                <div style="
                    color:#9bb4ac;
                    font-size:11px;
                    margin-top:6px;
                ">
                    Capture an image to begin monitoring
                </div>

            </div>

        </div>
        """)


    st.write("")


    if st.button(
        "📸  CAPTURE PLANT IMAGE",
        use_container_width=True
    ):

        response = send_capture()

        if response is not None:

            if response.status_code == 200:

                st.success(
                    "Capture command sent to Raspberry Pi."
                )

            elif response.status_code == 409:

                st.warning(
                    "Another command is already pending."
                )

            else:

                st.error(
                    response.text
                )


# ============================================================
# ROVER CONTROL PANEL
# ============================================================

with rover_col:

    html("""
    <div class="panel">

        <div class="panel-title">
            🎮 Rover Control
        </div>

    </div>
    """)


    # Mode

    mode1, mode2 = st.columns(2)

    with mode1:

        html("""
        <div class="mode-active">
            Manual Mode
        </div>
        """)

    with mode2:

        html("""
        <div class="mode-inactive">
            ⚪ Autonomous
        </div>
        """)


    st.write("")


    # Direction controls

    c1, c2, c3 = st.columns(3)

    with c2:

        if st.button(
            "▲",
            key="forward",
            use_container_width=True
        ):

            send_rover_command(
                "F",
                st.session_state.get(
                    "speed",
                    50
                )
            )


    c1, c2, c3 = st.columns(3)

    with c1:

        if st.button(
            "◀",
            key="left",
            use_container_width=True
        ):

            send_rover_command(
                "L",
                st.session_state.get(
                    "speed",
                    50
                )
            )

    with c2:

        if st.button(
            "■",
            key="stop",
            use_container_width=True
        ):

            response = send_rover_command(
                "S",
                st.session_state.get(
                    "speed",
                    50
                )
            )

            if response is not None:
                st.toast("Rover stopped.")


    with c3:

        if st.button(
            "▶",
            key="right",
            use_container_width=True
        ):

            send_rover_command(
                "R",
                st.session_state.get(
                    "speed",
                    50
                )
            )


    c1, c2, c3 = st.columns(3)

    with c2:

        if st.button(
            "▼",
            key="backward",
            use_container_width=True
        ):

            send_rover_command(
                "B",
                st.session_state.get(
                    "speed",
                    50
                )
            )


    # Speed

    speed = st.slider(
        "Speed",
        min_value=0,
        max_value=100,
        value=50,
        step=5,
        key="speed"
    )

    st.caption(
        f"Rover status: {rover_status}"
    )


# ============================================================
# SPRAYER CONTROL PANEL
# ============================================================

with spray_col:

    html("""
    <div class="panel">

        <div class="panel-title">
            💦 Sprayer Control
        </div>

    </div>
    """)


    spray_on = (
        str(spray_status).lower()
        in [
            "spraying",
            "spraying...",
            "on"
        ]
    )


    html(f"""
    <div class="sprayer-status">

        <div style="
            display:flex;
            align-items:center;
            justify-content:space-between;
        ">

            <div class="sprayer-status-label">
                Sprayer Status
            </div>

            <div class="
                {'status-on' if spray_on else 'status-off'}
            ">

                {'🟢 ON' if spray_on else '⚪ OFF'}

            </div>

        </div>

    </div>
    """)


    spray1, spray2 = st.columns(2)


    with spray1:

        if st.button(
            "▶ START SPRAYING",
            type="primary",
            use_container_width=True
        ):

            amount = st.session_state.get(
                "spray_amount",
                25.0
            )

            response = send_spray(
                amount
            )

            if response is not None:

                if response.status_code == 200:

                    st.success(
                        f"Spraying {amount:.0f} ml"
                    )

                else:

                    st.error(
                        response.text
                    )


    with spray2:

        if st.button(
            "■ STOP SPRAYING",
            use_container_width=True
        ):

            # Stop through rover endpoint if supported
            response = send_rover_command(
                "S",
                0
            )

            st.info(
                "Stop command sent."
            )


    st.markdown(
        "<hr>",
        unsafe_allow_html=True
    )


    st.markdown(
        "**Spray Settings**"
    )


    zone = st.selectbox(
        "Zone Selection",
        [
            "Zone 1",
            "Zone 2",
            "Zone 3",
            "Zone 4"
        ]
    )


    duration = st.number_input(
        "Duration (seconds)",
        min_value=1,
        max_value=300,
        value=10,
        step=1
    )


    dosage = st.number_input(
        "Dosage (ml)",
        min_value=1.0,
        max_value=500.0,
        value=25.0,
        step=1.0,
        key="spray_amount"
    )


    html(f"""
    <div class="spray-info">

        💡 <strong>{zone}</strong><br><br>

        {dosage:.0f} ml for
        {duration} seconds.

    </div>
    """)


# ============================================================
# AI DETECTION
# ============================================================

st.markdown(
    '<div class="section-title">🌿 AI Detection</div>',
    unsafe_allow_html=True
)


ai_left, ai_middle, ai_right = st.columns(
    [1.05, 1.15, 0.75],
    gap="medium"
)


# ============================================================
# AI IMAGE
# ============================================================

with ai_left:

    image = get_latest_image()

    if image is not None:

        st.image(
            image,
            use_container_width=True
        )

        html("""
        <div style="
            background:#09251c;
            color:white;
            padding:7px 12px;
            border-radius:8px;
            margin-top:-55px;
            margin-left:10px;
            margin-right:10px;
            position:relative;
            font-size:11px;
        ">
            AI Analysis Image
        </div>
        """)

    else:

        html("""
        <div class="camera-container">

            <div class="camera-placeholder">

                <div class="camera-placeholder-icon">
                    🌿
                </div>

                <div class="camera-placeholder-text">
                    No image available
                </div>

            </div>

        </div>
        """)


# ============================================================
# AI RESULT
# ============================================================

with ai_middle:

    html("""
    <div class="detection-panel">

        <div class="disease-card">

            <div class="disease-title">
                ⚠ DISEASE DETECTION
            </div>

            <div class="disease-name">
                Awaiting Analysis
            </div>

            <div class="disease-description">
                Capture a plant image and run the
                AI detection model to identify
                possible crop diseases.
            </div>

        </div>


        <div class="recommendation">

            <div class="recommendation-title">
                💡 RECOMMENDED ACTION
            </div>

            <div class="recommendation-name">
                Precision Monitoring
            </div>

            <div class="disease-description">
                Capture the latest plant image
                before initiating targeted spraying.
            </div>

        </div>

    </div>
    """)


# ============================================================
# QUOTE
# ============================================================

with ai_right:

    html("""
    <div class="quote-card">

        <div class="quote-icon">
            🌱
        </div>

        <div class="quote">
            “Detect Early<br>
            Treat Precisely<br>
            Grow Better”
        </div>

        <div class="quote-line"></div>

    </div>
    """)


# ============================================================
# LIVE SYSTEM STATUS
# ============================================================

st.markdown(
    '<div class="section-title">System Status</div>',
    unsafe_allow_html=True
)


status1, status2, status3, status4 = st.columns(4)


with status1:

    if backend_online:

        st.success("🟢 Backend Online")

    else:

        st.error("🔴 Backend Offline")


with status2:

    if esp32_online:

        st.success("🟢 ESP32 Online")

    else:

        st.warning("🟡 ESP32 Offline")


with status3:

    if image_available:

        st.success("📷 Camera Available")

    else:

        st.info("📷 Camera Waiting")


with status4:

    st.info(
        f"💧 {sprayed_amount:.1f} ml Dispensed"
    )


# ============================================================
# FOOTER
# ============================================================

html("""
<div class="footer">

    © 2026 CropIQ
    &nbsp; • &nbsp;
    Precision Agriculture
    &nbsp; • &nbsp;
    AI-Powered Targeted Spraying

</div>
""")
