import streamlit as st
import requests
import time
from datetime import datetime


# ============================================================
# CONFIG
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
# CSS
# IMPORTANT:
# We use st.html() instead of st.markdown() for HTML.
# ============================================================

st.html("""
<style>

html, body {
    font-family: Inter, Arial, sans-serif;
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

.stApp {
    background:
        radial-gradient(
            circle at 15% 10%,
            rgba(76, 175, 105, 0.08),
            transparent 28%
        ),
        linear-gradient(
            135deg,
            #eef5f1 0%,
            #f8fbf9 55%,
            #edf4f0 100%
        );
}

.main .block-container {
    max-width: 1550px;
    padding-top: 1rem;
    padding-bottom: 2rem;
    padding-left: 1.5rem;
    padding-right: 1.5rem;
}


/* ============================================================
   SIDEBAR
   ============================================================ */

section[data-testid="stSidebar"] {
    background:
        radial-gradient(
            circle at 30% 85%,
            rgba(82, 160, 95, 0.15),
            transparent 30%
        ),
        linear-gradient(
            180deg,
            #003d31 0%,
            #004e3e 50%,
            #002d25 100%
        );

    min-width: 285px;
    max-width: 285px;
}

section[data-testid="stSidebar"] > div {
    background: transparent;
}

section[data-testid="stSidebar"] .block-container {
    padding: 1.3rem 0.9rem;
}

section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] span,
section[data-testid="stSidebar"] label {
    color: white !important;
}


/* Sidebar brand */

.sidebar-brand {
    text-align: center;
    padding: 5px 5px 20px 5px;
}

.sidebar-logo {
    font-size: 50px;
    line-height: 1;
}

.sidebar-name {
    color: white;
    font-size: 34px;
    font-weight: 850;
    letter-spacing: -1px;
    margin-top: 5px;
}

.sidebar-tagline {
    color: #bddbd2;
    font-size: 13px;
    line-height: 1.5;
    margin-top: 8px;
}

.sidebar-section {
    color: #7fb9aa;
    font-size: 10px;
    font-weight: 800;
    letter-spacing: 1.7px;
    padding-left: 10px;
    margin-top: 22px;
    margin-bottom: 10px;
}


/* Sidebar radio */

section[data-testid="stSidebar"] div[role="radiogroup"] {
    gap: 6px;
}

section[data-testid="stSidebar"] div[role="radiogroup"] > label {
    border-radius: 13px !important;
    padding: 12px !important;
    background: transparent !important;
    border: 1px solid transparent !important;
    transition: 0.2s;
}

section[data-testid="stSidebar"] div[role="radiogroup"] > label:hover {
    background: rgba(255,255,255,0.08) !important;
}

section[data-testid="stSidebar"] div[role="radiogroup"] > label[data-checked="true"],
section[data-testid="stSidebar"] div[role="radiogroup"] > label[aria-checked="true"] {
    background:
        linear-gradient(
            90deg,
            #109b53,
            #087c41
        ) !important;

    box-shadow:
        0 7px 18px rgba(0,0,0,0.20);
}

section[data-testid="stSidebar"] div[role="radiogroup"] > label > div:first-child {
    display: none !important;
}


/* Sidebar system */

.sidebar-system {
    margin-top: 25px;
    padding: 17px;
    border-radius: 17px;
    background: rgba(0,0,0,0.14);
    border: 1px solid rgba(123,221,169,0.30);
}

.sidebar-system-title {
    color: #c6ded7;
    font-size: 11px;
}

.sidebar-online {
    color: #5fe68d;
    font-size: 17px;
    font-weight: 800;
    margin-top: 4px;
}

.sidebar-status {
    color: #a8c8c0;
    font-size: 11px;
    margin-top: 13px;
}

.sidebar-status-value {
    color: white;
    font-size: 13px;
    font-weight: 700;
    margin-top: 3px;
}


/* ============================================================
   TOP HEADER
   ============================================================ */

.top-header {
    background: rgba(255,255,255,0.96);
    border: 1px solid #dfe8e3;
    border-radius: 19px;
    padding: 17px 22px;
    min-height: 75px;

    box-shadow:
        0 7px 25px rgba(20,65,45,0.07);
}

.header-brand {
    display: flex;
    align-items: center;
    gap: 12px;
}

.header-logo {
    font-size: 38px;
}

.header-name {
    color: #063d31;
    font-size: 28px;
    font-weight: 850;
}

.header-subtitle {
    color: #75817c;
    font-size: 12px;
    margin-top: 4px;
}

.header-right {
    text-align: right;
}

.online-pill {
    display: inline-block;
    padding: 8px 14px;
    border-radius: 22px;
    background: #effaf3;
    border: 1px solid #bfe2ca;
    color: #087b3e;
    font-size: 11px;
    font-weight: 800;
}

.online-dot {
    display: inline-block;
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: #20aa58;
    margin-right: 5px;
}

.header-date {
    color: #738079;
    font-size: 11px;
    margin-top: 7px;
}


/* ============================================================
   HERO
   ============================================================ */

.hero {
    position: relative;
    overflow: hidden;

    background:
        linear-gradient(
            135deg,
            #edf8ef,
            #ffffff
        );

    border: 1px solid #dce9e1;
    border-radius: 21px;

    padding: 23px 27px;
    margin-top: 17px;
    margin-bottom: 18px;

    box-shadow:
        0 7px 24px rgba(25,70,50,0.055);
}

.hero-title {
    color: #043d31;
    font-size: 28px;
    font-weight: 850;
    letter-spacing: -0.5px;
}

.hero-green {
    color: #078845;
}

.hero-subtitle {
    color: #6c7a73;
    font-size: 13px;
    margin-top: 6px;
}


/* ============================================================
   SECTION
   ============================================================ */

.section-title {
    color: #063e32;
    font-size: 20px;
    font-weight: 850;
    margin-top: 18px;
    margin-bottom: 11px;
}


/* ============================================================
   KPI
   ============================================================ */

.kpi-card {
    background: white;
    border-radius: 17px;
    border: 1px solid #dfe8e3;

    padding: 17px;
    min-height: 145px;

    box-shadow:
        0 6px 20px rgba(25,70,48,0.06);
}

.kpi-green-border {
    border-top: 3px solid #39ae68;
}

.kpi-blue-border {
    border-top: 3px solid #45a4eb;
}

.kpi-purple-border {
    border-top: 3px solid #8b62d4;
}

.kpi-icon {
    width: 42px;
    height: 42px;

    display: flex;
    align-items: center;
    justify-content: center;

    border-radius: 50%;

    font-size: 21px;
    margin-bottom: 9px;
}

.icon-green {
    background: #eff9e9;
}

.icon-blue {
    background: #edf6ff;
}

.icon-purple {
    background: #f5efff;
}

.kpi-label {
    color: #74817b;
    font-size: 10px;
    font-weight: 800;
    letter-spacing: 0.5px;
}

.kpi-value {
    font-size: 23px;
    font-weight: 850;
    margin-top: 4px;
}

.green-value {
    color: #087d3f;
}

.blue-value {
    color: #1477cc;
}

.purple-value {
    color: #7042c5;
}

.kpi-description {
    color: #8b9691;
    font-size: 11px;
    margin-top: 5px;
}


/* ============================================================
   PANELS
   ============================================================ */

.panel {
    background: white;
    border: 1px solid #dfe8e3;
    border-radius: 18px;

    padding: 17px;

    box-shadow:
        0 6px 20px rgba(25,70,48,0.055);
}

.panel-heading {
    display: flex;
    justify-content: space-between;
    align-items: center;

    margin-bottom: 12px;
}

.panel-title {
    color: #073e33;
    font-size: 18px;
    font-weight: 850;
}

.panel-subtitle {
    color: #7c8782;
    font-size: 11px;
    margin-top: 4px;
}

.live-badge {
    background: #eaf8ee;
    color: #087c3e;
    border: 1px solid #c8e9d1;

    border-radius: 10px;
    padding: 6px 10px;

    font-size: 10px;
    font-weight: 800;
}


/* ============================================================
   CAMERA
   ============================================================ */

.camera-placeholder {
    min-height: 300px;

    display: flex;
    align-items: center;
    justify-content: center;

    border-radius: 14px;

    background:
        linear-gradient(
            135deg,
            #19352b,
            #0e211b
        );

    color: #c5d6ce;
    text-align: center;
}

.camera-icon {
    font-size: 50px;
}

.camera-caption {
    background: #edf7f1;
    border-radius: 11px;

    padding: 10px 12px;
    margin-top: 9px;

    color: #3e6b5b;
    font-size: 11px;
}


/* ============================================================
   ROVER
   ============================================================ */

.rover-online {
    text-align: center;
    color: #087d3f;
    background: #ecf9f0;
    border: 1px solid #c7e9d1;

    border-radius: 20px;
    padding: 6px 12px;

    width: fit-content;
    margin: 0 auto 8px auto;

    font-size: 10px;
    font-weight: 800;
}

.rover-offline {
    text-align: center;
    color: #b42318;
    background: #fff1ef;
    border: 1px solid #efc7c3;

    border-radius: 20px;
    padding: 6px 12px;

    width: fit-content;
    margin: 0 auto 8px auto;

    font-size: 10px;
    font-weight: 800;
}

.rover-status {
    text-align: center;
    color: #697770;
    font-size: 11px;
    margin-bottom: 8px;
}


/* ============================================================
   SPRAYER
   ============================================================ */

.sprayer-status {
    background:
        linear-gradient(
            135deg,
            #f0faf3,
            #fbfdfb
        );

    border: 1px solid #d6eadc;
    border-radius: 14px;

    padding: 13px;
    margin-bottom: 12px;
}

.sprayer-label {
    color: #66746d;
    font-size: 11px;
    font-weight: 700;
}

.sprayer-value {
    color: #087d3f;
    font-size: 20px;
    font-weight: 850;
    margin-top: 4px;
}

.sprayer-info {
    background: #f1f9f4;
    border: 1px solid #dcebe1;

    border-radius: 12px;
    padding: 11px;

    color: #477064;
    font-size: 11px;
    line-height: 1.5;
    margin-top: 10px;
}


/* ============================================================
   LIVE STATUS
   ============================================================ */

.live-status {
    background:
        linear-gradient(
            135deg,
            #eefaf2,
            white
        );

    border: 1px solid #cee8d6;
    border-radius: 16px;

    padding: 16px;
}

.live-status-title {
    color: #087d3f;
    font-size: 18px;
    font-weight: 850;
}

.live-status-text {
    color: #68766f;
    font-size: 11px;
    margin-top: 5px;
}


/* ============================================================
   AI
   ============================================================ */

.ai-card {
    background: white;
    border: 1px solid #dfe8e3;

    border-radius: 17px;

    padding: 18px;
    min-height: 175px;

    box-shadow:
        0 6px 20px rgba(25,70,48,0.05);
}

.ai-title {
    color: #073d33;
    font-size: 17px;
    font-weight: 850;
}

.ai-label {
    color: #87928d;
    font-size: 10px;
    font-weight: 800;

    margin-top: 14px;
}

.ai-value {
    color: #073e33;
    font-size: 17px;
    font-weight: 800;
    margin-top: 4px;
}

.ai-text {
    color: #75817b;
    font-size: 11px;
    line-height: 1.5;
    margin-top: 7px;
}

.ai-alert {
    background: #fff4f2;
    border-color: #efccc8;
}

.ai-recommend {
    background: #effaf3;
    border-color: #cce8d5;
}


/* ============================================================
   WORKFLOW
   ============================================================ */

.workflow {
    background: white;

    border: 1px solid #dfe8e3;
    border-radius: 18px;

    padding: 19px;

    box-shadow:
        0 6px 20px rgba(25,70,48,0.05);
}

.workflow-step {
    text-align: center;
}

.step-number {
    width: 42px;
    height: 42px;

    border-radius: 50%;

    display: flex;
    align-items: center;
    justify-content: center;

    margin: 0 auto 8px auto;

    background: #eff9e9;
    border: 1px solid #d3e8ce;

    color: #148047;
    font-size: 12px;
    font-weight: 850;
}

.step-icon {
    font-size: 25px;
}

.step-title {
    color: #073e33;
    font-size: 14px;
    font-weight: 850;
    margin-top: 3px;
}

.step-text {
    color: #7c8882;
    font-size: 10px;
    line-height: 1.45;
    margin-top: 4px;
}


/* ============================================================
   STREAMLIT BUTTONS
   ============================================================ */

.stButton > button {
    border-radius: 11px !important;

    min-height: 43px !important;

    font-size: 12px !important;
    font-weight: 750 !important;

    border: 1px solid #d8e4de !important;

    background: white !important;
    color: #173e34 !important;

    transition: 0.18s !important;
}

.stButton > button:hover {
    transform: translateY(-1px);

    box-shadow:
        0 6px 15px rgba(20,70,45,0.10);

    border-color: #8fc7a6 !important;
}

.stButton > button[kind="primary"] {
    background:
        linear-gradient(
            135deg,
            #159550,
            #087c40
        ) !important;

    color: white !important;

    border: none !important;
}


/* ============================================================
   INPUTS
   ============================================================ */

div[data-baseweb="input"],
div[data-baseweb="select"] {
    border-radius: 10px !important;
}

div[data-testid="stNumberInput"] label,
div[data-testid="stSlider"] label {
    font-size: 11px !important;
    font-weight: 700 !important;
    color: #45544d !important;
}


/* ============================================================
   ALERTS
   ============================================================ */

div[data-testid="stAlert"] {
    border-radius: 11px !important;
    font-size: 11px !important;
}


/* ============================================================
   FOOTER
   ============================================================ */

.footer {
    text-align: center;

    color: #89958f;

    font-size: 10px;

    padding: 25px 0 8px 0;
}

</style>
""")


# ============================================================
# BACKEND
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
# STATE
# ============================================================

state = get_state()


if state:

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

    current_speed = esp32.get(
        "speed",
        50
    )

else:

    spray_status = "OFFLINE"
    sprayed_amount = 0.0
    raspberry_online = False
    image_available = False
    esp32_online = False
    rover_status = "UNKNOWN"
    current_speed = 50


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.html("""
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
    """)

    st.html("""
    <div class="sidebar-section">
        MAIN MENU
    </div>
    """)

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

    status_text = (
        "● ONLINE"
        if raspberry_online
        else "● OFFLINE"
    )

    status_color = (
        "#63e995"
        if raspberry_online
        else "#ff7169"
    )

    st.html(f"""
    <div class="sidebar-system">

        <div class="sidebar-system-title">
            🍓 Raspberry Pi
        </div>

        <div class="sidebar-online"
             style="color:{status_color};">
            {status_text}
        </div>

        <div class="sidebar-status">
            System Status
        </div>

        <div class="sidebar-status-value">
            {"Operational" if raspberry_online else "Disconnected"}
        </div>

    </div>
    """)


# ============================================================
# HEADER
# ============================================================

header_left, header_right = st.columns(
    [3, 2]
)


with header_left:

    st.html("""
    <div class="top-header">

        <div class="header-brand">

            <div class="header-logo">
                🌱
            </div>

            <div>

                <div class="header-name">
                    CropIQ
                </div>

                <div class="header-subtitle">
                    Precision Agriculture Intelligence Platform
                </div>

            </div>

        </div>

    </div>
    """)


with header_right:

    system_color = (
        "#20aa58"
        if state
        else "#d13b35"
    )

    system_text = (
        "SYSTEM ONLINE"
        if state
        else "SYSTEM OFFLINE"
    )

    current_time = datetime.now().strftime(
        "%d %b %Y • %I:%M:%S %p"
    )

    st.html(f"""
    <div class="top-header">

        <div class="header-right">

            <div class="online-pill">

                <span class="online-dot"
                      style="background:{system_color};">
                </span>

                {system_text}

            </div>

            <div class="header-date">
                {current_time}
            </div>

        </div>

    </div>
    """)


# ============================================================
# DASHBOARD
# ============================================================

if page == "🏠 Dashboard":

    # --------------------------------------------------------
    # HERO
    # --------------------------------------------------------

    st.html("""
    <div class="hero">

        <div class="hero-title">
            🌿 Precision
            <span class="hero-green">
                Spraying Control
            </span>
        </div>

        <div class="hero-subtitle">
            Monitor the plant, control the rover,
            configure spray dosage, and perform
            precision spraying.
        </div>

    </div>
    """)


    # --------------------------------------------------------
    # SYSTEM OVERVIEW
    # --------------------------------------------------------

    st.html("""
    <div class="section-title">
        System Overview
    </div>
    """)


    k1, k2, k3, k4 = st.columns(4)


    # KPI 1

    with k1:

        st.html(f"""
        <div class="kpi-card kpi-green-border">

            <div class="kpi-icon icon-green">
                💦
            </div>

            <div class="kpi-label">
                SPRAYER STATUS
            </div>

            <div class="kpi-value green-value">
                {str(spray_status).upper()}
            </div>

            <div class="kpi-description">
                Current operation
            </div>

        </div>
        """)


    # KPI 2

    with k2:

        st.html(f"""
        <div class="kpi-card kpi-blue-border">

            <div class="kpi-icon icon-blue">
                💧
            </div>

            <div class="kpi-label">
                LAST DISPENSED
            </div>

            <div class="kpi-value blue-value">
                {float(sprayed_amount):.1f} ml
            </div>

            <div class="kpi-description">
                Latest spray quantity
            </div>

        </div>
        """)


    # KPI 3

    with k3:

        camera_status = (
            "READY"
            if raspberry_online
            else "OFFLINE"
        )

        st.html(f"""
        <div class="kpi-card kpi-green-border">

            <div class="kpi-icon icon-green">
                📷
            </div>

            <div class="kpi-label">
                CAMERA
            </div>

            <div class="kpi-value green-value">
                {camera_status}
            </div>

            <div class="kpi-description">
                Plant imaging system
            </div>

        </div>
        """)


    # KPI 4

    with k4:

        esp_status = (
            "ONLINE"
            if esp32_online
            else "OFFLINE"
        )

        st.html(f"""
        <div class="kpi-card kpi-purple-border">

            <div class="kpi-icon icon-purple">
                🔌
            </div>

            <div class="kpi-label">
                ESP32 ROVER
            </div>

            <div class="kpi-value purple-value">
                {esp_status}
            </div>

            <div class="kpi-description">
                Rover hardware connection
            </div>

        </div>
        """)


    # --------------------------------------------------------
    # MAIN CONTROL
    # --------------------------------------------------------

    st.html("""
    <div class="section-title">
        Plant Monitoring & Control
    </div>
    """)


    camera_col, rover_col, spray_col = st.columns(
        [1.45, 1, 1]
    )


    # ========================================================
    # CAMERA
    # ========================================================

    with camera_col:

        st.html("""
        <div class="panel">

            <div class="panel-heading">

                <div>

                    <div class="panel-title">
                        📷 Live Camera Feed
                    </div>

                    <div class="panel-subtitle">
                        Latest image captured from the
                        Raspberry Pi camera.
                    </div>

                </div>

                <div class="live-badge">
                    ● LIVE
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

            st.html("""
            <div class="camera-caption">
                📷 Live image from Raspberry Pi camera
                <br>
                <span style="color:#83918b;">
                    Capture a new image to update the
                    monitoring view.
                </span>
            </div>
            """)

        else:

            st.html("""
            <div class="camera-placeholder">

                <div>

                    <div class="camera-icon">
                        📷
                    </div>

                    <div>
                        No plant image available
                    </div>

                    <div style="
                        font-size:11px;
                        margin-top:5px;
                        color:#91a49b;
                    ">
                        Capture an image to begin monitoring
                    </div>

                </div>

            </div>
            """)


        st.write("")


        if st.button(
            "📸 CAPTURE PLANT IMAGE",
            use_container_width=True,
            key="capture_dashboard"
        ):

            response = send_capture()

            if response:

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

        st.html("""
        <div class="panel">

            <div class="panel-heading">

                <div>

                    <div class="panel-title">
                        🚜 Rover Control
                    </div>

                    <div class="panel-subtitle">
                        Manual rover movement control.
                    </div>

                </div>

            </div>

        </div>
        """)


        if esp32_online:

            st.html("""
            <div class="rover-online">
                ● ESP32 ONLINE
            </div>
            """)

        else:

            st.html("""
            <div class="rover-offline">
                ● ESP32 OFFLINE
            </div>
            """)


        st.html(f"""
        <div class="rover-status">
            Rover Status:
            <b>{rover_status}</b>
        </div>
        """)


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
                    current_speed
                )

                if response and response.status_code != 200:
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
                    current_speed
                )

                if response and response.status_code != 200:
                    st.error(response.text)


        with c2:

            if st.button(
                "⏹️",
                use_container_width=True,
                key="stop"
            ):

                response = send_rover_command(
                    "S",
                    current_speed
                )

                if response and response.status_code == 200:
                    st.success("Stopped.")


        with c3:

            if st.button(
                "➡️",
                use_container_width=True,
                key="right"
            ):

                response = send_rover_command(
                    "R",
                    current_speed
                )

                if response and response.status_code != 200:
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
                    current_speed
                )

                if response and response.status_code != 200:
                    st.error(response.text)


        speed = st.slider(
            "Rover Speed",
            0,
            100,
            int(current_speed),
            5,
            key="dashboard_speed"
        )


        st.caption(
            f"Current speed: {speed}%"
        )


    # ========================================================
    # SPRAYER
    # ========================================================

    with spray_col:

        st.html("""
        <div class="panel">

            <div class="panel-heading">

                <div>

                    <div class="panel-title">
                        💧 Sprayer Control
                    </div>

                    <div class="panel-subtitle">
                        Configure dosage and activate
                        precision spraying.
                    </div>

                </div>

            </div>

        </div>
        """)


        st.html(f"""
        <div class="sprayer-status">

            <div class="sprayer-label">
                SPRAYER STATUS
            </div>

            <div class="sprayer-value">
                🟢 {str(spray_status).upper()}
            </div>

        </div>
        """)


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

            if response:

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


        st.html("""
        <div class="sprayer-info">
            💡 The selected dosage will be sent
            to the Raspberry Pi sprayer.
        </div>
        """)


    # ========================================================
    # LIVE STATUS
    # ========================================================

    st.html("""
    <div class="section-title">
        Live Spray Status
    </div>
    """)


    spraying = (
        "spray"
        in str(spray_status).lower()
    )


    if spraying:

        st.html(f"""
        <div class="live-status">

            <div class="live-status-title">
                🟡 SPRAYING
            </div>

            <div class="live-status-text">
                {float(sprayed_amount):.1f} ml dispensed.
            </div>

        </div>
        """)

    else:

        st.html("""
        <div class="live-status">

            <div class="live-status-title">
                🟢 READY
            </div>

            <div class="live-status-text">
                System is ready for the next
                precision spraying operation.
            </div>

        </div>
        """)


    # ========================================================
    # AI DETECTION
    # ========================================================

    st.html("""
    <div class="section-title">
        🌿 AI Detection
    </div>
    """)


    ai1, ai2, ai3 = st.columns(
        [1, 1.15, 0.8]
    )


    with ai1:

        st.html("""
        <div class="ai-card">

            <div class="ai-title">
                🌿 Plant Analysis
            </div>

            <div class="ai-label">
                DETECTION STATUS
            </div>

            <div class="ai-value">
                Awaiting Analysis
            </div>

            <div class="ai-text">
                Capture a plant image to begin
                AI-powered plant analysis.
            </div>

        </div>
        """)


    with ai2:

        st.html("""
        <div class="ai-card ai-alert">

            <div class="ai-title">
                🔬 Disease Detection
            </div>

            <div class="ai-label">
                DETECTED CONDITION
            </div>

            <div class="ai-value">
                No analysis available
            </div>

            <div class="ai-text">
                Connect your disease detection
                model to display diagnosis and
                confidence.
            </div>

        </div>
        """)


    with ai3:

        st.html("""
        <div class="ai-card ai-recommend">

            <div class="ai-title">
                💡 Recommendation
            </div>

            <div class="ai-label">
                ACTION
            </div>

            <div class="ai-value">
                Awaiting Detection
            </div>

            <div class="ai-text">
                Treatment recommendations will
                appear after AI detection.
            </div>

        </div>
        """)


    # ========================================================
    # WORKFLOW
    # ========================================================

    st.html("""
    <div class="section-title">
        CropIQ Workflow
    </div>
    """)


    st.html("""
    <div class="workflow">
    """)


    w1, w2, w3, w4 = st.columns(4)


    workflow = [
        (
            w1,
            "01",
            "📷",
            "Capture",
            "Capture the latest plant image using the Raspberry Pi camera."
        ),
        (
            w2,
            "02",
            "🌿",
            "Analyze",
            "Analyze the captured plant image using the AI detection system."
        ),
        (
            w3,
            "03",
            "🎯",
            "Target",
            "Determine the treatment area and required spray quantity."
        ),
        (
            w4,
            "04",
            "💧",
            "Spray",
            "Apply the selected spray dosage to the identified target."
        )
    ]


    for column, number, icon, title, text in workflow:

        with column:

            st.html(f"""
            <div class="workflow-step">

                <div class="step-number">
                    {number}
                </div>

                <div class="step-icon">
                    {icon}
                </div>

                <div class="step-title">
                    {title}
                </div>

                <div class="step-text">
                    {text}
                </div>

            </div>
            """)


    st.html("""
    </div>
    """)


# ============================================================
# LIVE VIEW
# ============================================================

elif page == "📷 Live View":

    st.html("""
    <div class="hero">

        <div class="hero-title">
            📷 Live
            <span class="hero-green">
                Plant Monitoring
            </span>
        </div>

        <div class="hero-subtitle">
            Monitor the latest image from the
            Raspberry Pi camera.
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

        st.info(
            "No plant image available."
        )


    if st.button(
        "📸 CAPTURE NEW IMAGE",
        type="primary",
        use_container_width=True,
        key="live_capture"
    ):

        response = send_capture()

        if response and response.status_code == 200:

            st.success(
                "Capture command sent."
            )

            time.sleep(0.5)
            st.rerun()

        elif response:

            st.error(
                response.text
            )


# ============================================================
# ROVER PAGE
# ============================================================

elif page == "🚜 Rover Control":

    st.html("""
    <div class="hero">

        <div class="hero-title">
            🚜 Rover
            <span class="hero-green">
                Control
            </span>
        </div>

        <div class="hero-subtitle">
            Control the CropIQ rover using ESP32.
        </div>

    </div>
    """)


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


    c1, c2, c3 = st.columns(3)

    with c2:

        if st.button(
            "⬆️ FORWARD",
            use_container_width=True,
            key="page_forward"
        ):

            send_rover_command(
                "F",
                speed
            )


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
# SPRAYER PAGE
# ============================================================

elif page == "💧 Sprayer Control":

    st.html("""
    <div class="hero">

        <div class="hero-title">
            💧 Precision
            <span class="hero-green">
                Sprayer Control
            </span>
        </div>

        <div class="hero-subtitle">
            Configure spray dosage and activate
            precision spraying.
        </div>

    </div>
    """)


    c1, c2 = st.columns(2)


    with c1:

        st.metric(
            "Sprayer Status",
            str(spray_status).upper()
        )


    with c2:

        st.metric(
            "Last Dispensed",
            f"{float(sprayed_amount):.1f} ml"
        )


    dosage = st.number_input(
        "Spray dosage (ml)",
        1.0,
        500.0,
        25.0,
        1.0,
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

        if response and response.status_code == 200:

            st.success(
                f"Spray command sent: {dosage:.1f} ml"
            )

        elif response:

            st.error(
                response.text
            )


# ============================================================
# AI PAGE
# ============================================================

elif page == "🌿 AI Detection":

    st.html("""
    <div class="hero">

        <div class="hero-title">
            🌿 AI Plant
            <span class="hero-green">
                Detection
            </span>
        </div>

        <div class="hero-subtitle">
            AI-powered disease detection and
            targeted treatment recommendation.
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

        st.info(
            "Capture a plant image first."
        )


    a1, a2, a3 = st.columns(3)


    with a1:

        st.html("""
        <div class="ai-card">

            <div class="ai-title">
                🌿 Plant Analysis
            </div>

            <div class="ai-label">
                STATUS
            </div>

            <div class="ai-value">
                Awaiting Analysis
            </div>

            <div class="ai-text">
                AI analysis will appear here
                after image processing.
            </div>

        </div>
        """)


    with a2:

        st.html("""
        <div class="ai-card ai-alert">

            <div class="ai-title">
                🔬 Disease Detection
            </div>

            <div class="ai-label">
                CONDITION
            </div>

            <div class="ai-value">
                No analysis available
            </div>

            <div class="ai-text">
                Connect your disease detection
                model to display diagnosis.
            </div>

        </div>
        """)


    with a3:

        st.html("""
        <div class="ai-card ai-recommend">

            <div class="ai-title">
                💡 Recommendation
            </div>

            <div class="ai-label">
                ACTION
            </div>

            <div class="ai-value">
                Awaiting Detection
            </div>

            <div class="ai-text">
                Treatment recommendation will
                appear here.
            </div>

        </div>
        """)


# ============================================================
# SETTINGS
# ============================================================

elif page == "⚙️ Settings":

    st.html("""
    <div class="hero">

        <div class="hero-title">
            ⚙️ CropIQ
            <span class="hero-green">
                Settings
            </span>
        </div>

        <div class="hero-subtitle">
            System configuration and hardware
            connection information.
        </div>

    </div>
    """)


    st.subheader("Backend")

    st.code(
        BACKEND_URL
    )


    st.subheader("Spray Configuration")

    c1, c2 = st.columns(2)

    with c1:
        st.metric(
            "Minimum Dosage",
            "1 ml"
        )

    with c2:
        st.metric(
            "Maximum Dosage",
            "500 ml"
        )


    st.subheader("Hardware")

    c1, c2 = st.columns(2)


    with c1:

        if raspberry_online:
            st.success("🍓 Raspberry Pi connected")
        else:
            st.error("🍓 Raspberry Pi unavailable")


    with c2:

        if esp32_online:
            st.success("🚜 ESP32 connected")
        else:
            st.error("🚜 ESP32 unavailable")


# ============================================================
# FOOTER
# ============================================================

st.html("""
<div class="footer">
    © 2026 CropIQ
    &nbsp; • &nbsp;
    Precision Agriculture
    &nbsp; • &nbsp;
    AI-Powered Targeted Spraying
</div>
""")
