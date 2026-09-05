import streamlit as st
import requests
import time
from datetime import datetime
from textwrap import dedent


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
    dedent("""
    <style>

    /* ========================================================
       GLOBAL
       ======================================================== */

    html, body, [class*="css"] {
        font-family: "Inter", "Segoe UI", sans-serif;
    }

    .stApp {
        background:
            radial-gradient(
                circle at 85% 5%,
                rgba(86, 190, 125, 0.10),
                transparent 28%
            ),
            #f3f7f5;
    }

    .main .block-container {
        max-width: 1500px;
        padding-top: 1.2rem;
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

    /* Remove unnecessary Streamlit spacing */

    div[data-testid="stVerticalBlock"] {
        gap: 0.65rem;
    }


    /* ========================================================
       SIDEBAR
       ======================================================== */

    section[data-testid="stSidebar"] {
        background:
            linear-gradient(
                180deg,
                #003f34 0%,
                #004b3d 45%,
                #002d26 100%
            ) !important;

        min-width: 270px !important;
        max-width: 270px !important;

        border-right: 1px solid rgba(255,255,255,0.08);
    }

    section[data-testid="stSidebar"] > div {
        background: transparent !important;
    }

    section[data-testid="stSidebar"] .block-container {
        padding: 1.4rem 0.85rem 1.5rem 0.85rem;
    }

    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] span,
    section[data-testid="stSidebar"] label {
        color: white !important;
    }


    /* Sidebar branding */

    .sidebar-brand {
        text-align: left;
        padding: 0.4rem 0.7rem 1.7rem 0.7rem;
    }

    .sidebar-logo {
        font-size: 43px;
        line-height: 1;
        margin-bottom: 2px;
    }

    .sidebar-name {
        color: white;
        font-size: 31px;
        font-weight: 850;
        letter-spacing: -1px;
        line-height: 1.05;
    }

    .sidebar-tagline {
        color: #c1ddd5;
        font-size: 12px;
        line-height: 1.55;
        margin-top: 9px;
        max-width: 190px;
    }

    .sidebar-section {
        color: #79b9aa;
        font-size: 10px;
        font-weight: 800;
        letter-spacing: 1.7px;
        padding: 0.4rem 0.7rem 0.6rem 0.7rem;
    }


    /* Sidebar navigation */

    section[data-testid="stSidebar"] div[role="radiogroup"] {
        gap: 6px;
        width: 100%;
    }

    section[data-testid="stSidebar"]
    div[role="radiogroup"] > label {
        border-radius: 12px !important;
        padding: 12px 12px !important;
        margin: 0 !important;
        min-height: 43px;
        background: transparent !important;
        transition: all 0.2s ease;
    }

    section[data-testid="stSidebar"]
    div[role="radiogroup"] > label:hover {
        background: rgba(255,255,255,0.08) !important;
    }

    section[data-testid="stSidebar"]
    div[role="radiogroup"] > label[data-checked="true"] {
        background:
            linear-gradient(
                90deg,
                #15964d,
                #087c3d
            ) !important;

        box-shadow:
            0 7px 20px rgba(0,0,0,0.16);
    }

    section[data-testid="stSidebar"]
    div[role="radiogroup"] > label > div:first-child {
        display: none !important;
    }

    section[data-testid="stSidebar"]
    div[role="radiogroup"] label p {
        font-size: 13px !important;
        font-weight: 600 !important;
    }


    /* Sidebar bottom status */

    .sidebar-system {
        margin: 2rem 0.35rem 0 0.35rem;
        padding: 16px;
        border-radius: 16px;
        border: 1px solid rgba(126,220,173,0.35);
        background: rgba(0,0,0,0.15);
    }

    .sidebar-system-top {
        display: flex;
        justify-content: space-between;
        align-items: center;
        color: #d9eee7;
        font-size: 11px;
        font-weight: 600;
    }

    .sidebar-status-online {
        color: #65e991;
        font-size: 17px;
        font-weight: 800;
        margin-top: 5px;
    }

    .sidebar-status-offline {
        color: #ff8f8f;
        font-size: 17px;
        font-weight: 800;
        margin-top: 5px;
    }

    .sidebar-uptime {
        color: #b9d1ca;
        font-size: 11px;
        margin-top: 12px;
        line-height: 1.6;
    }


    /* ========================================================
       TOP HEADER
       ======================================================== */

    .top-header {
        background: rgba(255,255,255,0.94);
        border: 1px solid #dfe9e4;
        border-radius: 19px;
        min-height: 84px;
        padding: 15px 20px;
        box-shadow: 0 7px 25px rgba(24,70,48,0.07);
    }

    .top-brand {
        display: flex;
        align-items: center;
        gap: 13px;
    }

    .top-logo {
        width: 50px;
        height: 50px;
        border-radius: 14px;
        background: linear-gradient(
            135deg,
            #edf8ee,
            #dcefe0
        );
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 30px;
    }

    .top-brand-name {
        color: #063f32;
        font-size: 28px;
        line-height: 1;
        font-weight: 850;
        letter-spacing: -0.8px;
    }

    .top-brand-subtitle {
        color: #71807a;
        font-size: 11px;
        margin-top: 5px;
    }

    .top-right {
        text-align: right;
    }

    .online-pill {
        display: inline-flex;
        align-items: center;
        gap: 7px;
        padding: 8px 13px;
        border-radius: 22px;
        background: #effaf2;
        border: 1px solid #bfe6ca;
        color: #087b3d;
        font-size: 12px;
        font-weight: 800;
    }

    .offline-pill {
        display: inline-flex;
        align-items: center;
        gap: 7px;
        padding: 8px 13px;
        border-radius: 22px;
        background: #fff2f2;
        border: 1px solid #efc7c7;
        color: #b42318;
        font-size: 12px;
        font-weight: 800;
    }

    .green-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: #23a957;
        display: inline-block;
    }

    .red-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: #dc3f3f;
        display: inline-block;
    }

    .datetime {
        color: #78837f;
        font-size: 11px;
        margin-top: 7px;
    }


    /* ========================================================
       HERO
       ======================================================== */

    .hero {
        margin-top: 16px;
        margin-bottom: 15px;
        padding: 21px 23px;
        border-radius: 19px;
        border: 1px solid #d9e9df;
        background:
            linear-gradient(
                120deg,
                #eaf7ed 0%,
                #ffffff 65%
            );
        box-shadow: 0 5px 20px rgba(25,75,50,0.05);
    }

    .hero-title {
        color: #073d32;
        font-size: 27px;
        font-weight: 850;
        letter-spacing: -0.6px;
        line-height: 1.2;
    }

    .hero-highlight {
        color: #15904c;
    }

    .hero-text {
        color: #65736e;
        font-size: 13px;
        margin-top: 7px;
        line-height: 1.5;
    }


    /* ========================================================
       SECTION TITLES
       ======================================================== */

    .section-title {
        color: #073d32;
        font-size: 19px;
        font-weight: 850;
        margin-top: 12px;
        margin-bottom: 9px;
        letter-spacing: -0.3px;
    }


    /* ========================================================
       KPI CARDS
       ======================================================== */

    .kpi-card {
        position: relative;
        overflow: hidden;
        background: #ffffff;
        border: 1px solid #dfe9e4;
        border-radius: 16px;
        padding: 17px;
        min-height: 145px;
        box-shadow: 0 6px 20px rgba(28,74,51,0.055);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }

    .kpi-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 28px rgba(28,74,51,0.09);
    }

    .kpi-top {
        display: flex;
        align-items: center;
        gap: 11px;
    }

    .kpi-icon {
        width: 43px;
        height: 43px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 21px;
        background: #edf8ee;
    }

    .kpi-icon-blue {
        background: #edf5fd;
    }

    .kpi-icon-purple {
        background: #f4effc;
    }

    .kpi-label {
        color: #687670;
        font-size: 10px;
        font-weight: 750;
        letter-spacing: 0.5px;
    }

    .kpi-value {
        color: #073e34;
        font-size: 22px;
        font-weight: 850;
        margin-top: 9px;
    }

    .kpi-green {
        color: #087c3d;
    }

    .kpi-blue {
        color: #1475c7;
    }

    .kpi-purple {
        color: #7042c5;
    }

    .kpi-description {
        color: #89948f;
        font-size: 11px;
        margin-top: 7px;
    }

    .kpi-line {
        position: absolute;
        left: 15px;
        right: 15px;
        bottom: 9px;
        height: 2px;
        border-radius: 4px;
        background: linear-gradient(
            90deg,
            transparent,
            #31a957,
            transparent
        );
        opacity: 0.55;
    }


    /* ========================================================
       PANELS
       ======================================================== */

    .panel {
        background: #ffffff;
        border: 1px solid #dfe9e4;
        border-radius: 17px;
        padding: 17px;
        box-shadow: 0 6px 20px rgba(28,74,51,0.055);
        height: 100%;
    }

    .panel-heading {
        display: flex;
        align-items: center;
        gap: 9px;
        color: #073d32;
        font-size: 18px;
        font-weight: 850;
        margin-bottom: 5px;
    }

    .panel-description {
        color: #77837e;
        font-size: 11px;
        line-height: 1.5;
        margin-bottom: 10px;
    }

    .panel-divider {
        height: 1px;
        background: #e8eeeb;
        margin: 12px 0;
    }


    /* ========================================================
       IMAGE
       ======================================================== */

    [data-testid="stImage"] img {
        border-radius: 13px !important;
        border: 1px solid #dfe8e3;
        max-height: 430px;
        object-fit: cover;
    }


    /* ========================================================
       STREAMLIT BUTTONS
       ======================================================== */

    .stButton > button {
        min-height: 43px;
        border-radius: 11px !important;
        border: 1px solid #d8e5de !important;
        background: #ffffff !important;
        color: #123d32 !important;
        font-weight: 700 !important;
        font-size: 12px !important;
        transition: all 0.18s ease !important;
    }

    .stButton > button:hover {
        border-color: #15904c !important;
        color: #08783c !important;
        box-shadow: 0 5px 14px rgba(22,130,69,0.12) !important;
        transform: translateY(-1px);
    }

    /* Primary buttons */

    .stButton > button[kind="primary"] {
        background: linear-gradient(
            135deg,
            #15934e,
            #08783c
        ) !important;
        color: white !important;
        border: none !important;
        box-shadow: 0 5px 15px rgba(16,128,66,0.2) !important;
    }

    .stButton > button[kind="primary"]:hover {
        color: white !important;
        background: linear-gradient(
            135deg,
            #18a456,
            #087d40
        ) !important;
    }


    /* ========================================================
       INPUTS
       ======================================================== */

    div[data-baseweb="input"],
    div[data-baseweb="select"] {
        border-radius: 10px !important;
    }

    div[data-baseweb="input"] input {
        font-size: 13px !important;
    }

    div[data-baseweb="slider"] {
        margin-top: 3px;
        margin-bottom: 4px;
    }

    label[data-testid="stWidgetLabel"] p {
        font-size: 11px !important;
        font-weight: 700 !important;
        color: #34463f !important;
    }


    /* ========================================================
       STATUS
       ======================================================== */

    .status-ready {
        background: #effbf3;
        border: 1px solid #c5ecd2;
        border-radius: 13px;
        padding: 14px;
        color: #08753b;
    }

    .status-warning {
        background: #fff8e6;
        border: 1px solid #f0dc9d;
        border-radius: 13px;
        padding: 14px;
        color: #946700;
    }

    .status-error {
        background: #fff1f1;
        border: 1px solid #efc5c5;
        border-radius: 13px;
        padding: 14px;
        color: #b42318;
    }

    .status-title {
        font-size: 17px;
        font-weight: 850;
    }

    .status-text {
        font-size: 11px;
        margin-top: 6px;
        line-height: 1.5;
    }


    /* ========================================================
       ROVER CONTROL
       ======================================================== */

    .rover-status {
        background: #f5faf7;
        border: 1px solid #e0ebe5;
        border-radius: 11px;
        padding: 9px;
        text-align: center;
        color: #174b3b;
        font-size: 12px;
        margin-bottom: 9px;
    }

    .rover-online {
        color: #0a843f;
        font-weight: 800;
    }

    .rover-offline {
        color: #c53030;
        font-weight: 800;
    }

    .direction-hint {
        text-align: center;
        color: #87928d;
        font-size: 10px;
        margin-top: 5px;
    }


    /* ========================================================
       SPRAYER
       ======================================================== */

    .sprayer-status {
        display: flex;
        justify-content: space-between;
        align-items: center;
        background: #f5faf7;
        border: 1px solid #e1ebe6;
        border-radius: 12px;
        padding: 12px;
        margin-bottom: 11px;
    }

    .sprayer-status-label {
        color: #52625b;
        font-size: 11px;
        font-weight: 650;
    }

    .sprayer-status-value {
        color: #087c3d;
        font-size: 13px;
        font-weight: 850;
    }


    /* ========================================================
       AI DETECTION
       ======================================================== */

    .detection-card {
        background: #ffffff;
        border: 1px solid #dfe9e4;
        border-radius: 16px;
        padding: 17px;
        min-height: 150px;
        box-shadow: 0 5px 18px rgba(28,74,51,0.045);
    }

    .detection-heading {
        color: #073e34;
        font-size: 16px;
        font-weight: 850;
    }

    .detection-label {
        color: #7a8781;
        font-size: 10px;
        font-weight: 700;
        margin-top: 12px;
    }

    .detection-value {
        color: #073e34;
        font-size: 16px;
        font-weight: 800;
        margin-top: 4px;
    }

    .detection-description {
        color: #78857f;
        font-size: 11px;
        line-height: 1.5;
        margin-top: 5px;
    }


    /* ========================================================
       WORKFLOW
       ======================================================== */

    .workflow-container {
        background: #ffffff;
        border: 1px solid #dfe9e4;
        border-radius: 17px;
        padding: 18px;
        box-shadow: 0 6px 20px rgba(28,74,51,0.05);
    }

    .workflow-card {
        min-height: 110px;
    }

    .step-number {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 35px;
        height: 35px;
        border-radius: 50%;
        background: #e9f7e9;
        color: #128047;
        font-size: 12px;
        font-weight: 850;
    }

    .step-title {
        color: #073e34;
        font-size: 15px;
        font-weight: 850;
        margin-top: 8px;
    }

    .step-description {
        color: #7a8781;
        font-size: 10px;
        line-height: 1.5;
        margin-top: 4px;
    }


    /* ========================================================
       FOOTER
       ======================================================== */

    .footer {
        text-align: center;
        color: #87928d;
        font-size: 10px;
        padding: 20px 0 4px 0;
    }


    /* ========================================================
       MOBILE RESPONSIVE
       ======================================================== */

    @media (max-width: 768px) {

        .main .block-container {
            padding-left: 0.7rem;
            padding-right: 0.7rem;
            padding-top: 0.6rem;
        }

        .top-header {
            padding: 14px;
            border-radius: 15px;
        }

        .top-brand-name {
            font-size: 22px;
        }

        .top-brand-subtitle {
            font-size: 9px;
        }

        .top-logo {
            width: 42px;
            height: 42px;
            font-size: 24px;
        }

        .top-right {
            text-align: left;
        }

        .datetime {
            font-size: 9px;
        }

        .online-pill,
        .offline-pill {
            padding: 6px 9px;
            font-size: 10px;
        }

        .hero {
            padding: 17px;
            margin-top: 10px;
        }

        .hero-title {
            font-size: 21px;
        }

        .hero-text {
            font-size: 11px;
        }

        .section-title {
            font-size: 17px;
            margin-top: 10px;
        }

        .kpi-card {
            min-height: 115px;
            padding: 13px;
        }

        .kpi-icon {
            width: 36px;
            height: 36px;
            font-size: 18px;
        }

        .kpi-label {
            font-size: 9px;
        }

        .kpi-value {
            font-size: 18px;
            margin-top: 6px;
        }

        .kpi-description {
            font-size: 9px;
        }

        .panel {
            padding: 13px;
            border-radius: 14px;
        }

        .panel-heading {
            font-size: 16px;
        }

        .panel-description {
            font-size: 10px;
        }

        .detection-card {
            min-height: 120px;
            padding: 13px;
        }

        .workflow-container {
            padding: 13px;
        }

        .workflow-card {
            min-height: auto;
            padding-bottom: 14px;
        }

        /* Make buttons easier to press on phones */

        .stButton > button {
            min-height: 47px !important;
            font-size: 12px !important;
        }

        /* Prevent oversized images */

        [data-testid="stImage"] img {
            max-height: 330px;
        }

        /* Streamlit sidebar becomes drawer on mobile */

        section[data-testid="stSidebar"] {
            min-width: 280px !important;
            max-width: 280px !important;
        }
    }


    @media (max-width: 480px) {

        .main .block-container {
            padding-left: 0.45rem;
            padding-right: 0.45rem;
        }

        .top-brand-name {
            font-size: 20px;
        }

        .top-brand-subtitle {
            font-size: 8px;
        }

        .top-right {
            margin-top: 7px;
        }

        .hero-title {
            font-size: 19px;
        }

        .hero-text {
            font-size: 10px;
        }

        .section-title {
            font-size: 16px;
        }

        .kpi-card {
            min-height: 105px;
        }

        .kpi-value {
            font-size: 17px;
        }

        .panel-heading {
            font-size: 15px;
        }

        [data-testid="stImage"] img {
            max-height: 270px;
        }
    }

    </style>
    """),
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
# STATE HELPERS
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
        dedent("""
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
        """),
        unsafe_allow_html=True
    )

    st.markdown(
        dedent("""
        <div class="sidebar-section">
            MAIN MENU
        </div>
        """),
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

    if raspberry_online:

        sidebar_status = """
        <div class="sidebar-status-online">
            ● ONLINE
        </div>
        """

    else:

        sidebar_status = """
        <div class="sidebar-status-offline">
            ● OFFLINE
        </div>
        """

    st.markdown(
        dedent(f"""
        <div class="sidebar-system">

            <div class="sidebar-system-top">
                <span>🍓 Raspberry Pi</span>
                <span>●</span>
            </div>

            {sidebar_status}

            <div class="sidebar-uptime">
                System Status<br>
                <b>
                    {"Operational" if raspberry_online else "Disconnected"}
                </b>
            </div>

        </div>
        """),
        unsafe_allow_html=True
    )


# ============================================================
# TOP HEADER
# ============================================================

header_left, header_right = st.columns(
    [3.5, 1.5]
)

with header_left:

    st.markdown(
        dedent("""
        <div class="top-header">

            <div class="top-brand">

                <div class="top-logo">
                    🌱
                </div>

                <div>

                    <div class="top-brand-name">
                        CropIQ
                    </div>

                    <div class="top-brand-subtitle">
                        Precision Agriculture Intelligence Platform
                    </div>

                </div>

            </div>

        </div>
        """),
        unsafe_allow_html=True
    )


with header_right:

    if state is not None:

        status_html = """
        <div class="online-pill">
            <span class="green-dot"></span>
            SYSTEM ONLINE
        </div>
        """

    else:

        status_html = """
        <div class="offline-pill">
            <span class="red-dot"></span>
            SYSTEM OFFLINE
        </div>
        """

    st.markdown(
        dedent(f"""
        <div class="top-header">

            <div class="top-right">

                {status_html}

                <div class="datetime">
                    {datetime.now().strftime("%d %b %Y • %I:%M:%S %p")}
                </div>

            </div>

        </div>
        """),
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
        dedent("""
        <div class="hero">

            <div class="hero-title">
                🌿 Precision
                <span class="hero-highlight">
                    Spraying Control
                </span>
            </div>

            <div class="hero-text">
                Monitor your crop, capture plant images,
                control the rover, configure spray dosage,
                and perform targeted precision spraying.
            </div>

        </div>
        """),
        unsafe_allow_html=True
    )


    # ========================================================
    # SYSTEM OVERVIEW
    # ========================================================

    st.markdown(
        dedent("""
        <div class="section-title">
            System Overview
        </div>
        """),
        unsafe_allow_html=True
    )

    k1, k2, k3, k4 = st.columns(
        4,
        gap="medium"
    )


    # --------------------------------------------------------
    # KPI 1
    # --------------------------------------------------------

    with k1:

        spray_display = str(
            spray_status
        ).upper()

        st.markdown(
            dedent(f"""
            <div class="kpi-card">

                <div class="kpi-top">

                    <div class="kpi-icon">
                        💦
                    </div>

                    <div class="kpi-label">
                        SPRAYER STATUS
                    </div>

                </div>

                <div class="kpi-value kpi-green">
                    {spray_display}
                </div>

                <div class="kpi-description">
                    Current operation
                </div>

                <div class="kpi-line"></div>

            </div>
            """),
            unsafe_allow_html=True
        )


    # --------------------------------------------------------
    # KPI 2
    # --------------------------------------------------------

    with k2:

        try:
            amount = float(sprayed_amount)
        except:
            amount = 0.0

        st.markdown(
            dedent(f"""
            <div class="kpi-card">

                <div class="kpi-top">

                    <div class="kpi-icon kpi-icon-blue">
                        💧
                    </div>

                    <div class="kpi-label">
                        LAST DISPENSED
                    </div>

                </div>

                <div class="kpi-value kpi-blue">
                    {amount:.1f} ml
                </div>

                <div class="kpi-description">
                    Latest spray quantity
                </div>

                <div class="kpi-line"></div>

            </div>
            """),
            unsafe_allow_html=True
        )


    # --------------------------------------------------------
    # KPI 3
    # --------------------------------------------------------

    with k3:

        camera_status = (
            "READY"
            if raspberry_online
            else "OFFLINE"
        )

        st.markdown(
            dedent(f"""
            <div class="kpi-card">

                <div class="kpi-top">

                    <div class="kpi-icon">
                        📷
                    </div>

                    <div class="kpi-label">
                        CAMERA
                    </div>

                </div>

                <div class="kpi-value kpi-green">
                    {camera_status}
                </div>

                <div class="kpi-description">
                    Plant imaging system
                </div>

                <div class="kpi-line"></div>

            </div>
            """),
            unsafe_allow_html=True
        )


    # --------------------------------------------------------
    # KPI 4
    # --------------------------------------------------------

    with k4:

        esp_status = (
            "ONLINE"
            if esp32_online
            else "OFFLINE"
        )

        st.markdown(
            dedent(f"""
            <div class="kpi-card">

                <div class="kpi-top">

                    <div class="kpi-icon kpi-icon-purple">
                        🔌
                    </div>

                    <div class="kpi-label">
                        ESP32 ROVER
                    </div>

                </div>

                <div class="kpi-value kpi-purple">
                    {esp_status}
                </div>

                <div class="kpi-description">
                    Rover hardware connection
                </div>

                <div class="kpi-line"></div>

            </div>
            """),
            unsafe_allow_html=True
        )


    # ========================================================
    # MAIN CONTROL AREA
    # ========================================================

    st.markdown(
        dedent("""
        <div class="section-title">
            Plant Monitoring & Control
        </div>
        """),
        unsafe_allow_html=True
    )


    camera_col, rover_col, spray_col = st.columns(
        [1.35, 1.0, 1.0],
        gap="medium"
    )


    # ========================================================
    # CAMERA PANEL
    # ========================================================

    with camera_col:

        st.markdown(
            dedent("""
            <div class="panel">

                <div class="panel-heading">
                    📷 Live Camera Feed
                </div>

                <div class="panel-description">
                    Latest plant image captured from
                    the Raspberry Pi camera.
                </div>

            </div>
            """),
            unsafe_allow_html=True
        )

        image = get_latest_image()

        if image is not None:

            st.image(
                image,
                use_container_width=True
            )

            st.success(
                "🟢 LIVE • Plant image available"
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

                    time.sleep(0.4)
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
    # ROVER PANEL
    # ========================================================

    with rover_col:

        st.markdown(
            dedent("""
            <div class="panel">

                <div class="panel-heading">
                    🚜 Rover Control
                </div>

                <div class="panel-description">
                    Manually control rover movement
                    through the ESP32.
                </div>

            </div>
            """),
            unsafe_allow_html=True
        )

        if esp32_online:

            st.markdown(
                dedent(f"""
                <div class="rover-status">
                    <span class="rover-online">
                        🟢 ESP32 ONLINE
                    </span>
                    <br>
                    Rover:
                    <b>{rover_status}</b>
                </div>
                """),
                unsafe_allow_html=True
            )

        else:

            st.markdown(
                dedent("""
                <div class="rover-status">
                    <span class="rover-offline">
                        🔴 ESP32 OFFLINE
                    </span>
                    <br>
                    Rover unavailable
                </div>
                """),
                unsafe_allow_html=True
            )


        speed = st.slider(
            "Rover Speed",
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
                key="dashboard_forward"
            ):

                response = send_rover_command(
                    "F",
                    speed
                )

                if response is not None:

                    if response.status_code == 200:
                        st.toast("Rover moving forward")

                    else:
                        st.error(response.text)


        # Left / Stop / Right

        c1, c2, c3 = st.columns(3)

        with c1:

            if st.button(
                "⬅️",
                use_container_width=True,
                key="dashboard_left"
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
                key="dashboard_stop"
            ):

                response = send_rover_command(
                    "S",
                    speed
                )

                if response is not None:

                    if response.status_code == 200:
                        st.toast("Rover stopped")

                    else:
                        st.error(response.text)


        with c3:

            if st.button(
                "➡️",
                use_container_width=True,
                key="dashboard_right"
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
                key="dashboard_backward"
            ):

                response = send_rover_command(
                    "B",
                    speed
                )

                if response is not None:

                    if response.status_code != 200:
                        st.error(response.text)

        st.markdown(
            dedent("""
            <div class="direction-hint">
                ▲ Forward &nbsp; • &nbsp;
                ▼ Reverse &nbsp; • &nbsp;
                ◀ ▶ Turn
            </div>
            """),
            unsafe_allow_html=True
        )


    # ========================================================
    # SPRAYER PANEL
    # ========================================================

    with spray_col:

        st.markdown(
            dedent("""
            <div class="panel">

                <div class="panel-heading">
                    💧 Sprayer Control
                </div>

                <div class="panel-description">
                    Configure dosage and activate
                    the precision sprayer.
                </div>

            </div>
            """),
            unsafe_allow_html=True
        )


        if str(spray_status).upper() in [
            "SPRAYING",
            "SPRAYING..."
        ]:

            status_value = "🟡 ACTIVE"

        else:

            status_value = (
                "🟢 " +
                str(spray_status).upper()
            )


        st.markdown(
            dedent(f"""
            <div class="sprayer-status">

                <div class="sprayer-status-label">
                    Sprayer Status
                </div>

                <div class="sprayer-status-value">
                    {status_value}
                </div>

            </div>
            """),
            unsafe_allow_html=True
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


        st.markdown(
            dedent("""
            <div class="panel-divider"></div>
            """),
            unsafe_allow_html=True
        )


        st.info(
            "💡 The selected dosage will be sent "
            "to the Raspberry Pi sprayer."
        )


    # ========================================================
    # LIVE SPRAY STATUS
    # ========================================================

    st.markdown(
        dedent("""
        <div class="section-title">
            Live Spray Status
        </div>
        """),
        unsafe_allow_html=True
    )


    status_upper = str(
        spray_status
    ).upper()


    if status_upper in [
        "SPRAYING",
        "SPRAYING..."
    ]:

        st.markdown(
            dedent(f"""
            <div class="status-warning">

                <div class="status-title">
                    🟡 SPRAYING
                </div>

                <div class="status-text">
                    {float(sprayed_amount):.1f}
                    ml dispensed.
                    Sprayer operation is currently active.
                </div>

            </div>
            """),
            unsafe_allow_html=True
        )

    elif status_upper in [
        "COMPLETED"
    ]:

        st.markdown(
            dedent(f"""
            <div class="status-ready">

                <div class="status-title">
                    🟢 COMPLETED
                </div>

                <div class="status-text">
                    {float(sprayed_amount):.1f}
                    ml sprayed successfully.
                </div>

            </div>
            """),
            unsafe_allow_html=True
        )

    elif status_upper == "OFFLINE":

        st.markdown(
            dedent("""
            <div class="status-error">

                <div class="status-title">
                    🔴 SYSTEM OFFLINE
                </div>

                <div class="status-text">
                    Raspberry Pi is currently unavailable.
                </div>

            </div>
            """),
            unsafe_allow_html=True
        )

    else:

        st.markdown(
            dedent("""
            <div class="status-ready">

                <div class="status-title">
                    🟢 READY
                </div>

                <div class="status-text">
                    System is ready for the next
                    precision spraying operation.
                </div>

            </div>
            """),
            unsafe_allow_html=True
        )


    # ========================================================
    # AI DETECTION
    # ========================================================

    st.markdown(
        dedent("""
        <div class="section-title">
            🌿 AI Detection
        </div>
        """),
        unsafe_allow_html=True
    )


    detection1, detection2, detection3 = st.columns(
        [1.05, 1.25, 0.9],
        gap="medium"
    )


    with detection1:

        st.markdown(
            dedent("""
            <div class="detection-card">

                <div class="detection-heading">
                    🌿 Plant Analysis
                </div>

                <div class="detection-label">
                    DETECTION STATUS
                </div>

                <div class="detection-value">
                    Awaiting Analysis
                </div>

                <div class="detection-description">
                    Capture a plant image to begin
                    AI-powered analysis.
                </div>

            </div>
            """),
            unsafe_allow_html=True
        )


    with detection2:

        st.markdown(
            dedent("""
            <div class="detection-card">

                <div class="detection-heading">
                    🔬 Disease Detection
                </div>

                <div class="detection-label">
                    DETECTED CONDITION
                </div>

                <div class="detection-value">
                    No analysis available
                </div>

                <div class="detection-description">
                    Your plant disease model can be
                    connected here to display disease,
                    confidence and target area.
                </div>

            </div>
            """),
            unsafe_allow_html=True
        )


    with detection3:

        st.markdown(
            dedent("""
            <div class="detection-card">

                <div class="detection-heading">
                    💡 Recommendation
                </div>

                <div class="detection-label">
                    ACTION
                </div>

                <div class="detection-value">
                    Awaiting Detection
                </div>

                <div class="detection-description">
                    Targeted spray recommendation
                    will appear after AI analysis.
                </div>

            </div>
            """),
            unsafe_allow_html=True
        )


    # ========================================================
    # WORKFLOW
    # ========================================================

    st.markdown(
        dedent("""
        <div class="section-title">
            CropIQ Workflow
        </div>
        """),
        unsafe_allow_html=True
    )


    st.markdown(
        dedent("""
        <div class="workflow-container">
        """),
        unsafe_allow_html=True
    )


    w1, w2, w3, w4 = st.columns(
        4,
        gap="medium"
    )


    workflow = [

        (
            w1,
            "01",
            "📷 Capture",
            "Capture the latest plant image using the Raspberry Pi camera."
        ),

        (
            w2,
            "02",
            "🌿 Analyze",
            "Analyze the captured image using the AI detection system."
        ),

        (
            w3,
            "03",
            "🎯 Target",
            "Determine the treatment area and required spray quantity."
        ),

        (
            w4,
            "04",
            "💧 Spray",
            "Apply the selected dosage to the identified target."
        )
    ]


    for column, number, title, description in workflow:

        with column:

            st.markdown(
                dedent(f"""
                <div class="workflow-card">

                    <div class="step-number">
                        {number}
                    </div>

                    <div class="step-title">
                        {title}
                    </div>

                    <div class="step-description">
                        {description}
                    </div>

                </div>
                """),
                unsafe_allow_html=True
            )


    st.markdown(
        dedent("""
        </div>
        """),
        unsafe_allow_html=True
    )


# ============================================================
# LIVE VIEW PAGE
# ============================================================

elif page == "📷 Live View":

    st.markdown(
        dedent("""
        <div class="hero">

            <div class="hero-title">
                📷 Live Plant Monitoring
            </div>

            <div class="hero-text">
                Monitor the latest image captured
                by the Raspberry Pi camera.
            </div>

        </div>
        """),
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
            "📷 No plant image available."
        )


    if st.button(
        "📸 CAPTURE NEW IMAGE",
        type="primary",
        use_container_width=True,
        key="live_capture"
    ):

        response = send_capture()

        if response is not None:

            if response.status_code == 200:

                st.success(
                    "Capture command sent!"
                )

                time.sleep(0.4)
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
        dedent("""
        <div class="hero">

            <div class="hero-title">
                🚜 Rover Control
            </div>

            <div class="hero-text">
                Control the CropIQ rover using the ESP32.
            </div>

        </div>
        """),
        unsafe_allow_html=True
    )


    if esp32_online:

        st.success(
            "🟢 ESP32 ONLINE"
        )

    else:

        st.error(
            "🔴 ESP32 OFFLINE"
        )


    st.markdown(
        dedent(f"""
        <div class="rover-status">

            Current Rover Status:
            <b>{rover_status}</b>

        </div>
        """),
        unsafe_allow_html=True
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
        dedent("""
        <div class="section-title">
            Direction Control
        </div>
        """),
        unsafe_allow_html=True
    )


    # Forward

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

                if response.status_code == 200:
                    st.success("Forward command sent.")

                else:
                    st.error(response.text)


    # Left / Stop / Right

    c1, c2, c3 = st.columns(3)

    with c1:

        if st.button(
            "⬅️ LEFT",
            use_container_width=True,
            key="page_left"
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
            "⛔ STOP",
            use_container_width=True,
            key="page_stop"
        ):

            response = send_rover_command(
                "S",
                speed
            )

            if response is not None:

                if response.status_code == 200:
                    st.success("Rover stopped.")

                else:
                    st.error(response.text)


    with c3:

        if st.button(
            "➡️ RIGHT",
            use_container_width=True,
            key="page_right"
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
            "⬇️ BACKWARD",
            use_container_width=True,
            key="page_backward"
        ):

            response = send_rover_command(
                "B",
                speed
            )

            if response is not None:

                if response.status_code != 200:
                    st.error(response.text)


# ============================================================
# SPRAYER CONTROL PAGE
# ============================================================

elif page == "💧 Sprayer Control":

    st.markdown(
        dedent("""
        <div class="hero">

            <div class="hero-title">
                💧 Precision Sprayer Control
            </div>

            <div class="hero-text">
                Configure spray dosage and activate
                targeted spraying.
            </div>

        </div>
        """),
        unsafe_allow_html=True
    )


    c1, c2 = st.columns(2)


    with c1:

        st.markdown(
            dedent(f"""
            <div class="kpi-card">

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
            """),
            unsafe_allow_html=True
        )


    with c2:

        st.markdown(
            dedent(f"""
            <div class="kpi-card">

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
            """),
            unsafe_allow_html=True
        )


    st.markdown(
        dedent("""
        <div class="section-title">
            Spray Configuration
        </div>
        """),
        unsafe_allow_html=True
    )


    dosage = st.number_input(
        "Spray dosage (ml)",
        min_value=1.0,
        max_value=500.0,
        value=25.0,
        step=1.0,
        key="sprayer_page_dosage"
    )


    st.caption(
        "Allowed range: 1 – 500 ml"
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
                    f"Spray command sent: "
                    f"{dosage:.1f} ml"
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
        dedent("""
        <div class="hero">

            <div class="hero-title">
                🌿 AI Plant Detection
            </div>

            <div class="hero-text">
                Detect plant diseases and identify
                precise treatment targets.
            </div>

        </div>
        """),
        unsafe_allow_html=True
    )


    image = get_latest_image()


    if image is not None:

        st.image(
            image,
            caption="Latest plant image",
            use_container_width=True
        )

    else:

        st.info(
            "Capture a plant image first."
        )


    d1, d2, d3 = st.columns(3)


    with d1:

        st.markdown(
            dedent("""
            <div class="detection-card">

                <div class="detection-heading">
                    🌿 Plant Analysis
                </div>

                <div class="detection-label">
                    STATUS
                </div>

                <div class="detection-value">
                    Awaiting Analysis
                </div>

                <div class="detection-description">
                    AI analysis will begin once
                    the detection model is connected.
                </div>

            </div>
            """),
            unsafe_allow_html=True
        )


    with d2:

        st.markdown(
            dedent("""
            <div class="detection-card">

                <div class="detection-heading">
                    🔬 Disease Detection
                </div>

                <div class="detection-label">
                    CONDITION
                </div>

                <div class="detection-value">
                    No Analysis Available
                </div>

                <div class="detection-description">
                    Disease name and confidence
                    will appear here.
                </div>

            </div>
            """),
            unsafe_allow_html=True
        )


    with d3:

        st.markdown(
            dedent("""
            <div class="detection-card">

                <div class="detection-heading">
                    🎯 Treatment
                </div>

                <div class="detection-label">
                    RECOMMENDATION
                </div>

                <div class="detection-value">
                    Awaiting Detection
                </div>

                <div class="detection-description">
                    Target zone and spray dosage
                    will be recommended by the AI system.
                </div>

            </div>
            """),
            unsafe_allow_html=True
        )


# ============================================================
# SETTINGS PAGE
# ============================================================

elif page == "⚙️ Settings":

    st.markdown(
        dedent("""
        <div class="hero">

            <div class="hero-title">
                ⚙️ CropIQ Settings
            </div>

            <div class="hero-text">
                View system configuration and
                hardware connectivity.
            </div>

        </div>
        """),
        unsafe_allow_html=True
    )


    st.markdown(
        dedent("""
        <div class="section-title">
            Backend Configuration
        </div>
        """),
        unsafe_allow_html=True
    )


    st.code(
        BACKEND_URL
    )


    st.markdown(
        dedent("""
        <div class="section-title">
            Spray Configuration
        </div>
        """),
        unsafe_allow_html=True
    )


    c1, c2 = st.columns(2)


    with c1:

        st.markdown(
            dedent("""
            <div class="kpi-card">

                <div class="kpi-label">
                    MINIMUM DOSAGE
                </div>

                <div class="kpi-value">
                    1 ml
                </div>

            </div>
            """),
            unsafe_allow_html=True
        )


    with c2:

        st.markdown(
            dedent("""
            <div class="kpi-card">

                <div class="kpi-label">
                    MAXIMUM DOSAGE
                </div>

                <div class="kpi-value">
                    500 ml
                </div>

            </div>
            """),
            unsafe_allow_html=True
        )


    st.markdown(
        dedent("""
        <div class="section-title">
            Hardware Status
        </div>
        """),
        unsafe_allow_html=True
    )


    h1, h2 = st.columns(2)


    with h1:

        if raspberry_online:

            st.success(
                "🍓 Raspberry Pi connected"
            )

        else:

            st.error(
                "🍓 Raspberry Pi unavailable"
            )


    with h2:

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
    dedent("""
    <div class="footer">

        © 2026 CropIQ
        &nbsp; • &nbsp;
        Precision Agriculture
        &nbsp; • &nbsp;
        AI-Powered Targeted Spraying

    </div>
    """),
    unsafe_allow_html=True
)
