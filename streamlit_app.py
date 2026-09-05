import streamlit as st
import requests
import time
from datetime import datetime


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

    /* ========================================================
       GLOBAL
       ======================================================== */

    html, body, [class*="css"] {
        font-family: Inter, -apple-system, BlinkMacSystemFont,
        "Segoe UI", sans-serif;
    }

    .stApp {
        background:
            radial-gradient(
                circle at top left,
                rgba(35, 160, 95, 0.08),
                transparent 35%
            ),
            #f3f7f5;
    }

    .main .block-container {
        max-width: 1550px;
        padding-top: 1.2rem;
        padding-bottom: 2rem;
        padding-left: 1.4rem;
        padding-right: 1.4rem;
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


    /* ========================================================
       SIDEBAR
       ======================================================== */

    section[data-testid="stSidebar"] {
        background:
            linear-gradient(
                180deg,
                #003d31 0%,
                #004b3c 45%,
                #002c24 100%
            ) !important;

        min-width: 275px !important;
        max-width: 275px !important;

        border-right: 1px solid rgba(255,255,255,0.08);
    }

    section[data-testid="stSidebar"] > div {
        background: transparent !important;
    }

    section[data-testid="stSidebar"] .block-container {
        padding: 1.25rem 0.9rem 1.5rem 0.9rem !important;
    }

    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] span {
        color: white !important;
    }


    /* Sidebar brand */

    .sidebar-brand {
        text-align: center;
        padding: 0.4rem 0.3rem 1.3rem 0.3rem;
    }

    .sidebar-logo {
        font-size: 45px;
        line-height: 1;
        margin-bottom: 0.2rem;
    }

    .sidebar-name {
        color: white;
        font-size: 31px;
        font-weight: 800;
        letter-spacing: -0.8px;
    }

    .sidebar-tagline {
        color: #c3ded5;
        font-size: 12px;
        line-height: 1.45;
        margin-top: 7px;
    }

    .sidebar-section {
        color: #85c5b3;
        font-size: 10px;
        font-weight: 800;
        letter-spacing: 1.7px;
        margin-top: 1.3rem;
        margin-bottom: 0.5rem;
        padding-left: 0.5rem;
    }


    /* Sidebar radio navigation */

    section[data-testid="stSidebar"]
    div[role="radiogroup"] {
        gap: 5px;
    }

    section[data-testid="stSidebar"]
    div[role="radiogroup"] > label {
        background: transparent !important;
        border-radius: 12px !important;
        padding: 11px 12px !important;
        margin: 2px 0 !important;
        transition: all 0.2s ease;
        border: 1px solid transparent !important;
    }

    section[data-testid="stSidebar"]
    div[role="radiogroup"] > label:hover {
        background: rgba(255,255,255,0.08) !important;
    }

    section[data-testid="stSidebar"]
    div[role="radiogroup"]
    > label[data-checked="true"] {
        background:
            linear-gradient(
                90deg,
                #15934f,
                #08783d
            ) !important;

        border: 1px solid rgba(125,230,174,0.25) !important;

        box-shadow:
            0 7px 18px rgba(0,0,0,0.18);
    }

    section[data-testid="stSidebar"]
    div[role="radiogroup"]
    > label > div:first-child {
        display: none !important;
    }


    /* Sidebar system card */

    .sidebar-system {
        margin-top: 2rem;
        padding: 16px;
        border-radius: 16px;

        background:
            linear-gradient(
                145deg,
                rgba(0,0,0,0.17),
                rgba(0,0,0,0.08)
            );

        border:
            1px solid rgba(
                120,
                220,
                170,
                0.30
            );
    }

    .sidebar-system-title {
        color: #d7eee6;
        font-size: 11px;
        font-weight: 600;
    }

    .sidebar-online {
        color: #65ec91;
        font-size: 17px;
        font-weight: 800;
        margin-top: 4px;
    }

    .sidebar-uptime {
        color: #c7ddd7;
        font-size: 11px;
        margin-top: 12px;
        line-height: 1.6;
    }

    .sidebar-uptime b {
        color: white;
    }


    /* ========================================================
       TOP HEADER
       ======================================================== */

    .top-header {
        background: rgba(255,255,255,0.95);
        border: 1px solid #e0e9e4;
        border-radius: 18px;

        padding: 14px 20px;

        box-shadow:
            0 8px 30px rgba(24,70,48,0.07);

        min-height: 75px;

        display: flex;
        align-items: center;
    }

    .header-brand {
        display: flex;
        align-items: center;
        gap: 11px;
    }

    .header-logo {
        font-size: 35px;
        line-height: 1;
    }

    .header-name {
        color: #003f32;
        font-size: 27px;
        font-weight: 850;
        line-height: 1.1;
        letter-spacing: -0.7px;
    }

    .header-subtitle {
        color: #6d7974;
        font-size: 11px;
        margin-top: 3px;
    }

    .header-right {
        text-align: right;
    }

    .online-pill {
        display: inline-flex;
        align-items: center;
        gap: 7px;

        color: #08753b;
        background: #edf9f1;

        border: 1px solid #bce4c8;
        border-radius: 30px;

        padding: 7px 12px;

        font-size: 11px;
        font-weight: 800;
    }

    .green-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: #23ad57;
        display: inline-block;
        box-shadow: 0 0 0 3px rgba(35,173,87,0.12);
    }

    .header-date {
        color: #7a8580;
        font-size: 10px;
        margin-top: 5px;
    }


    /* ========================================================
       HERO
       ======================================================== */

    .hero {
        margin-top: 17px;
        margin-bottom: 15px;

        padding: 19px 22px;

        border-radius: 18px;

        background:
            linear-gradient(
                135deg,
                #edf8f1 0%,
                #ffffff 72%
            );

        border: 1px solid #dce9e1;

        box-shadow:
            0 6px 24px rgba(30,80,50,0.045);
    }

    .hero-title {
        color: #043d31;
        font-size: 27px;
        font-weight: 850;
        letter-spacing: -0.5px;
        line-height: 1.2;
    }

    .hero-title-green {
        color: #16854a;
    }

    .hero-text {
        color: #687671;
        font-size: 12px;
        margin-top: 5px;
        line-height: 1.5;
    }


    /* ========================================================
       SECTION TITLES
       ======================================================== */

    .section-title {
        color: #073e34;
        font-size: 19px;
        font-weight: 850;

        margin-top: 17px;
        margin-bottom: 9px;

        letter-spacing: -0.2px;
    }


    /* ========================================================
       KPI CARDS
       ======================================================== */

    .kpi-card {
        position: relative;

        background: white;

        border: 1px solid #dfe8e3;
        border-radius: 15px;

        padding: 16px;

        min-height: 132px;

        box-shadow:
            0 6px 20px rgba(30,70,50,0.055);

        overflow: hidden;

        transition:
            transform 0.2s ease,
            box-shadow 0.2s ease;
    }

    .kpi-card:hover {
        transform: translateY(-2px);

        box-shadow:
            0 10px 25px rgba(30,70,50,0.09);
    }

    .kpi-card::after {
        content: "";
        position: absolute;

        left: 15px;
        right: 15px;
        bottom: 0;

        height: 2px;

        border-radius: 4px;

        background: #28a85d;

        opacity: 0.85;
    }

    .kpi-blue-card::after {
        background: #2f91e5;
    }

    .kpi-purple-card::after {
        background: #8053d6;
    }

    .kpi-icon {
        width: 39px;
        height: 39px;

        border-radius: 50%;

        display: flex;
        align-items: center;
        justify-content: center;

        background: #eef8e9;

        font-size: 19px;

        margin-bottom: 9px;
    }

    .kpi-blue-icon {
        background: #eef6fd;
    }

    .kpi-purple-icon {
        background: #f3effc;
    }

    .kpi-label {
        color: #7a8580;

        font-size: 9px;
        font-weight: 700;

        letter-spacing: 0.7px;
    }

    .kpi-value {
        color: #063e32;

        font-size: 21px;
        font-weight: 850;

        margin-top: 4px;
    }

    .kpi-green {
        color: #087b3e;
    }

    .kpi-blue {
        color: #1476c9;
    }

    .kpi-purple {
        color: #7141c7;
    }

    .kpi-description {
        color: #89948f;

        font-size: 10px;

        margin-top: 4px;
    }


    /* ========================================================
       PANELS
       ======================================================== */

    .panel {
        background: white;

        border: 1px solid #dfe8e3;
        border-radius: 17px;

        padding: 16px;

        box-shadow:
            0 6px 22px rgba(30,70,50,0.055);

        margin-bottom: 0;
    }

    .panel-title {
        color: #073e34;

        font-size: 18px;
        font-weight: 850;

        line-height: 1.25;
    }

    .panel-description {
        color: #75817c;

        font-size: 10px;

        line-height: 1.45;

        margin-top: 5px;
        margin-bottom: 11px;
    }

    .panel-divider {
        height: 1px;
        background: #e6ece8;
        margin: 12px 0;
    }


    /* ========================================================
       CAMERA
       ======================================================== */

    .camera-frame {
        background: #eaf0ec;

        border-radius: 13px;

        overflow: hidden;

        border: 1px solid #dce7e1;

        min-height: 250px;

        display: flex;
        align-items: center;
        justify-content: center;
    }

    .camera-empty {
        text-align: center;
        color: #73817b;
        padding: 30px;
    }

    .camera-empty-icon {
        font-size: 42px;
        margin-bottom: 8px;
    }

    .camera-empty-title {
        font-size: 13px;
        font-weight: 700;
        color: #52615a;
    }

    .camera-empty-text {
        font-size: 10px;
        margin-top: 4px;
    }

    .live-badge {
        display: inline-flex;
        align-items: center;
        gap: 5px;

        background: #eaf8ee;
        color: #08783d;

        border: 1px solid #c6e9d0;

        padding: 5px 8px;

        border-radius: 8px;

        font-size: 9px;
        font-weight: 800;
    }


    /* ========================================================
       STATUS CARDS
       ======================================================== */

    .status-card {
        border-radius: 14px;

        padding: 15px;

        border: 1px solid #dfe8e3;

        background:
            linear-gradient(
                145deg,
                #f8fcf9,
                #ffffff
            );
    }

    .status-card.ready {
        background:
            linear-gradient(
                145deg,
                #effbf3,
                #ffffff
            );

        border-color: #c9ecd3;
    }

    .status-title {
        color: #08763b;

        font-size: 20px;
        font-weight: 850;
    }

    .status-text {
        color: #53615b;

        font-size: 11px;

        line-height: 1.5;

        margin-top: 8px;
    }

    .status-row {
        display: flex;
        justify-content: space-between;

        padding: 9px 0;

        border-bottom: 1px solid #e5ece8;

        color: #65716c;

        font-size: 10px;
    }

    .status-row:last-child {
        border-bottom: none;
    }

    .status-row strong {
        color: #08783d;
    }


    /* ========================================================
       BUTTONS
       ======================================================== */

    .stButton > button {
        min-height: 43px !important;

        border-radius: 10px !important;

        border: 1px solid #d7e4dd !important;

        background: white !important;

        color: #123f34 !important;

        font-weight: 750 !important;

        font-size: 11px !important;

        transition:
            transform 0.15s ease,
            box-shadow 0.15s ease,
            background 0.15s ease;
    }

    .stButton > button:hover {
        transform: translateY(-1px);

        box-shadow:
            0 6px 15px rgba(20,70,45,0.12) !important;

        border-color: #b8d8c7 !important;
    }

    .stButton > button[kind="primary"] {
        background:
            linear-gradient(
                135deg,
                #15934f,
                #08783d
            ) !important;

        color: white !important;

        border: none !important;

        box-shadow:
            0 6px 15px rgba(8,120,61,0.18);
    }


    /* ========================================================
       ROVER
       ======================================================== */

    .rover-status-pill {
        text-align: center;

        background: #edf8f1;

        color: #08763b;

        border: 1px solid #ccebd5;

        border-radius: 10px;

        padding: 7px;

        font-size: 10px;

        font-weight: 750;

        margin-bottom: 9px;
    }

    .rover-controller {
        margin-top: 7px;
    }

    .rover-controller .stButton > button {
        min-height: 53px !important;

        font-size: 20px !important;

        border-radius: 12px !important;

        background:
            linear-gradient(
                145deg,
                #effaf3,
                #d5f3e1
            ) !important;

        border-color: #c4e8d1 !important;

        color: #075c3d !important;
    }

    .rover-controller .stButton > button:hover {
        background:
            linear-gradient(
                145deg,
                #e0f7e8,
                #c9eed9
            ) !important;
    }


    /* ========================================================
       SPRAYER
       ======================================================== */

    .sprayer-active {
        padding: 10px 12px;

        border-radius: 10px;

        background: #fff8e7;

        border: 1px solid #f1dfad;

        color: #916700;

        font-size: 10px;

        font-weight: 750;

        margin-bottom: 9px;
    }

    .sprayer-ready {
        padding: 10px 12px;

        border-radius: 10px;

        background: #edf9f1;

        border: 1px solid #c8ead2;

        color: #08783d;

        font-size: 10px;

        font-weight: 750;

        margin-bottom: 9px;
    }


    /* ========================================================
       AI DETECTION
       ======================================================== */

    .ai-card {
        background:
            linear-gradient(
                145deg,
                #f6faf7,
                #ffffff
            );

        border: 1px solid #dfe8e3;

        border-radius: 15px;

        padding: 16px;

        min-height: 150px;
    }

    .ai-icon {
        font-size: 26px;
        margin-bottom: 7px;
    }

    .ai-title {
        color: #063e32;

        font-size: 16px;
        font-weight: 850;
    }

    .ai-label {
        color: #7c8882;

        font-size: 9px;
        font-weight: 700;

        margin-top: 10px;
    }

    .ai-value {
        color: #073e34;

        font-size: 15px;
        font-weight: 750;

        margin-top: 4px;
    }

    .ai-text {
        color: #7b8782;

        font-size: 10px;

        line-height: 1.5;

        margin-top: 4px;
    }


    /* ========================================================
       WORKFLOW
       ======================================================== */

    .workflow-card {
        background: white;

        border: 1px solid #dfe8e3;

        border-radius: 15px;

        padding: 15px;

        min-height: 120px;

        box-shadow:
            0 5px 16px rgba(30,70,50,0.04);
    }

    .step-number {
        display: inline-flex;

        align-items: center;
        justify-content: center;

        width: 32px;
        height: 32px;

        border-radius: 50%;

        background: #edf8e9;

        color: #168049;

        font-size: 10px;

        font-weight: 850;
    }

    .step-title {
        color: #073e34;

        font-size: 15px;

        font-weight: 850;

        margin-top: 8px;
    }

    .step-description {
        color: #7d8984;

        font-size: 10px;

        line-height: 1.5;

        margin-top: 5px;
    }


    /* ========================================================
       INFO BOX
       ======================================================== */

    .info-box {
        padding: 11px 13px;

        border-radius: 11px;

        background: #eef7fc;

        border: 1px solid #d4e9f5;

        color: #16649a;

        font-size: 10px;

        line-height: 1.45;

        margin-top: 9px;
    }


    /* ========================================================
       FOOTER
       ======================================================== */

    .footer {
        text-align: center;

        color: #89948f;

        font-size: 9px;

        padding: 25px 0 5px;
    }


    /* ========================================================
       MOBILE
       ======================================================== */

    @media screen and (max-width: 768px) {

        .main .block-container {
            max-width: 100% !important;

            padding-top: 0.65rem !important;
            padding-bottom: 1rem !important;

            padding-left: 0.55rem !important;
            padding-right: 0.55rem !important;
        }


        /* Sidebar */

        section[data-testid="stSidebar"] {
            min-width: 255px !important;
            max-width: 255px !important;
        }

        section[data-testid="stSidebar"]
        .block-container {
            padding: 0.8rem 0.65rem !important;
        }


        /* Header */

        .top-header {
            padding: 12px 13px !important;

            min-height: 64px !important;

            border-radius: 14px !important;
        }

        .header-logo {
            font-size: 27px !important;
        }

        .header-name {
            font-size: 21px !important;
        }

        .header-subtitle {
            font-size: 8px !important;
        }

        .online-pill {
            font-size: 8px !important;
            padding: 5px 8px !important;
        }

        .header-date {
            font-size: 8px !important;
        }


        /* Hero */

        .hero {
            margin-top: 9px !important;

            padding: 14px !important;

            border-radius: 14px !important;
        }

        .hero-title {
            font-size: 20px !important;
        }

        .hero-text {
            font-size: 9px !important;
        }


        /* Section */

        .section-title {
            font-size: 16px !important;

            margin-top: 12px !important;
            margin-bottom: 7px !important;
        }


        /* ----------------------------------------------------
           FORCE STREAMLIT COLUMNS TO STACK
           ---------------------------------------------------- */

        [data-testid="stHorizontalBlock"] {
            flex-wrap: wrap !important;

            gap: 0.55rem !important;
        }

        [data-testid="stHorizontalBlock"]
        > [data-testid="column"] {
            width: 100% !important;

            flex: 1 1 100% !important;

            min-width: 100% !important;

            max-width: 100% !important;
        }


        /* KPI */

        .kpi-card {
            min-height: 108px !important;

            padding: 12px !important;

            border-radius: 13px !important;
        }

        .kpi-icon {
            width: 34px !important;
            height: 34px !important;

            font-size: 16px !important;

            margin-bottom: 6px !important;
        }

        .kpi-label {
            font-size: 8px !important;
        }

        .kpi-value {
            font-size: 18px !important;
        }

        .kpi-description {
            font-size: 9px !important;
        }


        /* Panels */

        .panel {
            padding: 12px !important;

            border-radius: 14px !important;
        }

        .panel-title {
            font-size: 16px !important;
        }

        .panel-description {
            font-size: 9px !important;
        }


        /* Camera */

        .camera-frame {
            min-height: 205px !important;

            border-radius: 11px !important;
        }


        /* Rover */

        .rover-controller .stButton > button {
            min-height: 58px !important;

            font-size: 21px !important;
        }


        /* General buttons */

        .stButton > button {
            min-height: 45px !important;

            font-size: 10px !important;
        }


        /* Status */

        .status-card {
            padding: 13px !important;
        }

        .status-title {
            font-size: 18px !important;
        }

        .status-text {
            font-size: 10px !important;
        }


        /* AI */

        .ai-card {
            min-height: auto !important;

            padding: 13px !important;
        }

        .ai-title {
            font-size: 15px !important;
        }

        .ai-value {
            font-size: 14px !important;
        }


        /* Workflow */

        .workflow-card {
            min-height: 105px !important;

            padding: 12px !important;
        }

        .step-title {
            font-size: 14px !important;
        }

        .step-description {
            font-size: 9px !important;
        }


        /* Footer */

        .footer {
            font-size: 8px !important;
        }
    }


    /* ========================================================
       EXTRA SMALL PHONES
       ======================================================== */

    @media screen and (max-width: 480px) {

        .main .block-container {
            padding-left: 0.4rem !important;
            padding-right: 0.4rem !important;
        }

        .header-name {
            font-size: 19px !important;
        }

        .header-subtitle {
            font-size: 7px !important;
        }

        .hero-title {
            font-size: 18px !important;
        }

        .hero-text {
            font-size: 8px !important;
        }

        .kpi-card {
            min-height: 100px !important;
        }

        .kpi-value {
            font-size: 17px !important;
        }

        .camera-frame {
            min-height: 180px !important;
        }

        .rover-controller .stButton > button {
            min-height: 56px !important;

            font-size: 20px !important;
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
# STATE EXTRACTION
# ============================================================

state = get_state()


if state is None:

    spray_status = "OFFLINE"
    sprayed_amount = 0.0

    raspberry_online = False
    image_available = False

    esp32_online = False
    rover_status = "UNKNOWN"
    current_speed = 50

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

    current_speed = esp32.get(
        "speed",
        50
    )


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
        """
        <div class="sidebar-section">
            MAIN MENU
        </div>
        """,
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
    [3, 1.25],
    gap="small"
)


with header_left:

    st.markdown(
        """
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
        """,
        unsafe_allow_html=True
    )


with header_right:

    st.markdown(
        f"""
        <div class="top-header">

            <div style="width:100%;">

                <div class="header-right">

                    <div class="online-pill">

                        <span class="green-dot"></span>

                        SYSTEM
                        {"ONLINE" if state is not None else "OFFLINE"}

                    </div>

                    <div class="header-date">

                        {datetime.now().strftime(
                            "%d %b %Y • %I:%M:%S %p"
                        )}

                    </div>

                </div>

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
                🌿 Precision
                <span class="hero-title-green">
                    Spraying Control
                </span>
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
        """
        <div class="section-title">
            System Overview
        </div>
        """,
        unsafe_allow_html=True
    )


    k1, k2, k3, k4 = st.columns(
        4,
        gap="small"
    )


    # --------------------------------------------------------
    # KPI 1
    # --------------------------------------------------------

    with k1:

        display_status = str(
            spray_status
        ).upper()

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
                    {display_status}
                </div>

                <div class="kpi-description">
                    Current operation
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )


    # --------------------------------------------------------
    # KPI 2
    # --------------------------------------------------------

    with k2:

        st.markdown(
            f"""
            <div class="kpi-card kpi-blue-card">

                <div class="kpi-icon kpi-blue-icon">
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


    # --------------------------------------------------------
    # KPI 4
    # --------------------------------------------------------

    with k4:

        rover_connection = (
            "ONLINE"
            if esp32_online
            else "OFFLINE"
        )

        st.markdown(
            f"""
            <div class="kpi-card kpi-purple-card">

                <div class="kpi-icon kpi-purple-icon">
                    🔌
                </div>

                <div class="kpi-label">
                    ESP32 ROVER
                </div>

                <div class="kpi-value kpi-purple">
                    {rover_connection}
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
        """
        <div class="section-title">
            Plant Monitoring & Control
        </div>
        """,
        unsafe_allow_html=True
    )


    camera_col, rover_col, spray_col = st.columns(
        [1.45, 1, 1],
        gap="small"
    )


    # ========================================================
    # CAMERA PANEL
    # ========================================================

    with camera_col:

        st.markdown(
            """
            <div class="panel">

                <div style="
                    display:flex;
                    justify-content:space-between;
                    align-items:center;
                    gap:10px;
                ">

                    <div class="panel-title">
                        📷 Live Camera Feed
                    </div>

                    <div class="live-badge">
                        <span class="green-dot"></span>
                        LIVE
                    </div>

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

        else:

            st.markdown(
                """
                <div class="camera-frame">

                    <div class="camera-empty">

                        <div class="camera-empty-icon">
                            📷
                        </div>

                        <div class="camera-empty-title">
                            No plant image available
                        </div>

                        <div class="camera-empty-text">
                            Capture an image to begin
                            plant monitoring.
                        </div>

                    </div>

                </div>
                """,
                unsafe_allow_html=True
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

            st.markdown(
                """
                <div class="rover-status-pill">
                    🟢 ESP32 ONLINE
                </div>
                """,
                unsafe_allow_html=True
            )

        else:

            st.markdown(
                """
                <div class="rover-status-pill"
                     style="
                        background:#fff1f1;
                        border-color:#efc7c7;
                        color:#a52222;
                     ">
                    🔴 ESP32 OFFLINE
                </div>
                """,
                unsafe_allow_html=True
            )


        st.markdown(
            f"""
            <div style="
                text-align:center;
                color:#56645e;
                font-size:10px;
                margin-bottom:7px;
            ">
                Rover:
                <b>{rover_status}</b>
            </div>
            """,
            unsafe_allow_html=True
        )


        speed = st.slider(
            "Rover Speed",
            min_value=0,
            max_value=100,
            value=int(current_speed),
            step=5,
            key="dashboard_speed"
        )


        st.markdown(
            '<div class="rover-controller">',
            unsafe_allow_html=True
        )


        # Forward

        r1, r2, r3 = st.columns(3)

        with r2:

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

        r1, r2, r3 = st.columns(3)


        with r1:

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


        with r2:

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
                        st.success("Rover stopped.")

                    else:
                        st.error(response.text)


        with r3:

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

        r1, r2, r3 = st.columns(3)

        with r2:

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


        st.markdown(
            '</div>',
            unsafe_allow_html=True
        )


    # ========================================================
    # SPRAYER PANEL
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

                <div class="panel-divider"></div>

            </div>
            """,
            unsafe_allow_html=True
        )


        active_statuses = [
            "SPRAYING",
            "SPRAYING...",
            "spraying",
            "Spraying..."
        ]


        if spray_status in active_statuses:

            st.markdown(
                """
                <div class="sprayer-active">
                    🟡 SPRAYER ACTIVE
                </div>
                """,
                unsafe_allow_html=True
            )

        else:

            st.markdown(
                f"""
                <div class="sprayer-ready">
                    🟢 {str(spray_status).upper()}
                </div>
                """,
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
            """
            <div class="info-box">
                💡 The selected dosage will be sent
                to the Raspberry Pi sprayer.
            </div>
            """,
            unsafe_allow_html=True
        )


    # ========================================================
    # LIVE SPRAY STATUS
    # ========================================================

    st.markdown(
        """
        <div class="section-title">
            Live Spray Status
        </div>
        """,
        unsafe_allow_html=True
    )


    if spray_status in active_statuses:

        st.markdown(
            f"""
            <div class="status-card"
                 style="
                    background:#fffaf0;
                    border-color:#f0dfae;
                 ">

                <div class="status-title"
                     style="color:#966b00;">

                    🟡 SPRAYING

                </div>

                <div class="status-text">

                    Precision spraying operation
                    is currently active.

                </div>

                <div class="status-row">
                    <span>Dispensed</span>
                    <strong style="color:#966b00;">
                        {float(sprayed_amount):.1f} ml
                    </strong>
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )

    else:

        st.markdown(
            f"""
            <div class="status-card ready">

                <div class="status-title">
                    🟢 READY
                </div>

                <div class="status-text">
                    System is ready for the next
                    precision spraying operation.
                </div>

                <div class="status-row">
                    <span>Total Dispensed</span>
                    <strong>
                        {float(sprayed_amount):.1f} ml
                    </strong>
                </div>

                <div class="status-row">
                    <span>Raspberry Pi</span>
                    <strong>
                        {"ONLINE" if raspberry_online else "OFFLINE"}
                    </strong>
                </div>

                <div class="status-row">
                    <span>ESP32 Rover</span>
                    <strong>
                        {"ONLINE" if esp32_online else "OFFLINE"}
                    </strong>
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )


    # ========================================================
    # AI DETECTION
    # ========================================================

    st.markdown(
        """
        <div class="section-title">
            🌿 AI Detection
        </div>
        """,
        unsafe_allow_html=True
    )


    ai1, ai2, ai3 = st.columns(
        [1, 1, 1],
        gap="small"
    )


    with ai1:

        st.markdown(
            """
            <div class="ai-card">

                <div class="ai-icon">
                    🌿
                </div>

                <div class="ai-title">
                    Plant Analysis
                </div>

                <div class="ai-label">
                    DETECTION STATUS
                </div>

                <div class="ai-value">
                    Awaiting Analysis
                </div>

                <div class="ai-text">
                    Capture a plant image to
                    begin AI-based analysis.
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )


    with ai2:

        st.markdown(
            """
            <div class="ai-card">

                <div class="ai-icon">
                    🔬
                </div>

                <div class="ai-title">
                    Disease Detection
                </div>

                <div class="ai-label">
                    DETECTED CONDITION
                </div>

                <div class="ai-value">
                    No analysis available
                </div>

                <div class="ai-text">
                    Disease classification and
                    confidence will appear here
                    when the AI model is connected.
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )


    with ai3:

        st.markdown(
            """
            <div class="ai-card">

                <div class="ai-icon">
                    💡
                </div>

                <div class="ai-title">
                    Recommendation
                </div>

                <div class="ai-label">
                    ACTION
                </div>

                <div class="ai-value">
                    Awaiting Detection
                </div>

                <div class="ai-text">
                    Targeted treatment recommendations
                    will appear after disease detection.
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )


    # ========================================================
    # WORKFLOW
    # ========================================================

    st.markdown(
        """
        <div class="section-title">
            CropIQ Workflow
        </div>
        """,
        unsafe_allow_html=True
    )


    w1, w2, w3, w4 = st.columns(
        4,
        gap="small"
    )


    workflow_data = [

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
            "Apply the selected spray dosage to the identified target."
        )

    ]


    for column, number, title, description in workflow_data:

        with column:

            st.markdown(
                f"""
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
                """,
                unsafe_allow_html=True
            )


# ============================================================
# LIVE VIEW PAGE
# ============================================================

elif page == "📷 Live View":

    st.markdown(
        """
        <div class="section-title">
            📷 Live Plant Monitoring
        </div>
        """,
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

        st.markdown(
            """
            <div class="camera-frame">

                <div class="camera-empty">

                    <div class="camera-empty-icon">
                        📷
                    </div>

                    <div class="camera-empty-title">
                        No plant image available
                    </div>

                    <div class="camera-empty-text">
                        Capture an image to begin monitoring.
                    </div>

                </div>

            </div>
            """,
            unsafe_allow_html=True
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
        """
        <div class="section-title">
            🚜 Rover Control
        </div>
        """,
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
        f"""
        <div class="status-card">

            <div class="status-title">
                Rover Status
            </div>

            <div class="status-text">
                Current movement:
                <b>{rover_status}</b>
            </div>

        </div>
        """,
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
        """
        <div style="
            max-width:500px;
            margin:20px auto;
        ">
        """,
        unsafe_allow_html=True
    )


    c1, c2, c3 = st.columns(3)

    with c2:

        if st.button(
            "⬆️",
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
            "⬅️",
            use_container_width=True,
            key="page_left"
        ):

            send_rover_command(
                "L",
                speed
            )


    with c2:

        if st.button(
            "⛔",
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
            "➡️",
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
            "⬇️",
            use_container_width=True,
            key="page_backward"
        ):

            send_rover_command(
                "B",
                speed
            )


    st.markdown(
        "</div>",
        unsafe_allow_html=True
    )


# ============================================================
# SPRAYER CONTROL PAGE
# ============================================================

elif page == "💧 Sprayer Control":

    st.markdown(
        """
        <div class="section-title">
            💧 Precision Sprayer Control
        </div>
        """,
        unsafe_allow_html=True
    )


    col1, col2 = st.columns(2)


    with col1:

        st.markdown(
            f"""
            <div class="status-card ready">

                <div class="status-title">
                    {"🟢 READY" if spray_status not in [
                        "SPRAYING",
                        "SPRAYING..."
                    ] else "🟡 SPRAYING"}
                </div>

                <div class="status-text">
                    Current sprayer status
                </div>

                <div class="status-row">
                    <span>Last Dispensed</span>

                    <strong>
                        {float(sprayed_amount):.1f} ml
                    </strong>
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )


    with col2:

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
        """
        <div class="section-title">
            🌿 AI Plant Detection
        </div>
        """,
        unsafe_allow_html=True
    )


    image = get_latest_image()


    if image is not None:

        st.image(
            image,
            caption="Plant image for AI analysis",
            use_container_width=True
        )

    else:

        st.info(
            "📷 Capture a plant image first."
        )


    a1, a2, a3 = st.columns(3)


    with a1:

        st.markdown(
            """
            <div class="ai-card">

                <div class="ai-icon">
                    🔍
                </div>

                <div class="ai-title">
                    Disease Detection
                </div>

                <div class="ai-value">
                    Awaiting Analysis
                </div>

                <div class="ai-text">
                    Connect your disease detection
                    model to display results.
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )


    with a2:

        st.markdown(
            """
            <div class="ai-card">

                <div class="ai-icon">
                    📊
                </div>

                <div class="ai-title">
                    Confidence
                </div>

                <div class="ai-value">
                    --
                </div>

                <div class="ai-text">
                    Model confidence score will
                    appear after detection.
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )


    with a3:

        st.markdown(
            """
            <div class="ai-card">

                <div class="ai-icon">
                    💡
                </div>

                <div class="ai-title">
                    Recommendation
                </div>

                <div class="ai-value">
                    Awaiting Detection
                </div>

                <div class="ai-text">
                    Treatment recommendation will
                    be generated from the detected condition.
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
        """
        <div class="section-title">
            ⚙️ CropIQ Settings
        </div>
        """,
        unsafe_allow_html=True
    )


    st.subheader(
        "Backend Configuration"
    )


    st.code(
        BACKEND_URL
    )


    st.subheader(
        "Spray Configuration"
    )


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


    st.subheader(
        "Hardware Status"
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
    """
    <div class="footer">
        © 2026 CropIQ
        &nbsp; • &nbsp;
        Precision Agriculture
        &nbsp; • &nbsp;
        AI-Powered Targeted Spraying
    </div>
    """,
    unsafe_allow_html=True
)
