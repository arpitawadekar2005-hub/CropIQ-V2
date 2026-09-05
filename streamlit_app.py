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
                circle at 10% 10%,
                rgba(92, 190, 120, 0.08),
                transparent 30%
            ),
            linear-gradient(
                135deg,
                #eef5f1 0%,
                #f7faf8 45%,
                #edf4f1 100%
            );
    }

    .main .block-container {
        max-width: 1550px;
        padding-top: 1.2rem;
        padding-bottom: 2rem;
        padding-left: 1.5rem;
        padding-right: 1.5rem;
    }


    /* ========================================================
       SIDEBAR
       ======================================================== */

    section[data-testid="stSidebar"] {
        background:
            radial-gradient(
                circle at 20% 80%,
                rgba(70, 150, 90, 0.16),
                transparent 30%
            ),
            linear-gradient(
                180deg,
                #003b30 0%,
                #004c3d 45%,
                #002e27 100%
            );

        min-width: 285px;
        max-width: 285px;
    }

    section[data-testid="stSidebar"] > div {
        background: transparent;
    }

    section[data-testid="stSidebar"] .block-container {
        padding: 1.4rem 1rem;
    }

    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] span,
    section[data-testid="stSidebar"] label {
        color: white !important;
    }


    /* Sidebar brand */

    .sidebar-brand {
        text-align: center;
        padding: 10px 5px 25px 5px;
    }

    .sidebar-logo {
        font-size: 50px;
        line-height: 1;
        margin-bottom: 4px;
    }

    .sidebar-name {
        color: white;
        font-size: 34px;
        font-weight: 850;
        letter-spacing: -1px;
    }

    .sidebar-tagline {
        color: #b9d8cf;
        font-size: 13px;
        line-height: 1.55;
        margin-top: 8px;
    }

    .sidebar-menu-title {
        color: #80bbae;
        font-size: 10px;
        font-weight: 800;
        letter-spacing: 1.8px;
        margin-top: 25px;
        margin-bottom: 10px;
        padding-left: 10px;
    }


    /* Sidebar navigation */

    section[data-testid="stSidebar"] div[role="radiogroup"] {
        gap: 7px;
    }

    section[data-testid="stSidebar"] div[role="radiogroup"] > label {
        border-radius: 13px !important;
        padding: 12px 12px !important;
        margin: 0 !important;
        background: transparent !important;
        border: 1px solid transparent !important;
        transition: all 0.2s ease;
    }

    section[data-testid="stSidebar"] div[role="radiogroup"] > label:hover {
        background: rgba(255,255,255,0.08) !important;
        transform: translateX(2px);
    }

    section[data-testid="stSidebar"] div[role="radiogroup"] > label[data-checked="true"],
    section[data-testid="stSidebar"] div[role="radiogroup"] > label[aria-checked="true"] {
        background:
            linear-gradient(
                90deg,
                #0d9b52,
                #087e42
            ) !important;

        border: 1px solid rgba(255,255,255,0.08) !important;
        box-shadow:
            0 8px 20px rgba(0,0,0,0.20);
    }

    section[data-testid="stSidebar"] div[role="radiogroup"] > label > div:first-child {
        display: none !important;
    }


    /* Sidebar system card */

    .sidebar-system-card {
        margin-top: 28px;
        padding: 18px;
        border-radius: 18px;
        border: 1px solid rgba(129,225,174,0.32);
        background: rgba(0,0,0,0.16);
        box-shadow:
            inset 0 1px rgba(255,255,255,0.04);
    }

    .sidebar-system-label {
        color: #bcdad2;
        font-size: 11px;
        font-weight: 600;
    }

    .sidebar-system-status {
        color: #63e995;
        font-size: 17px;
        font-weight: 800;
        margin-top: 3px;
    }

    .sidebar-uptime-label {
        color: #9ec2b8;
        font-size: 11px;
        margin-top: 15px;
    }

    .sidebar-uptime-value {
        color: white;
        font-size: 14px;
        font-weight: 700;
        margin-top: 2px;
    }


    /* Decorative plant */

    .sidebar-plant {
        text-align: center;
        opacity: 0.15;
        font-size: 110px;
        margin-top: 40px;
    }


    /* ========================================================
       TOP HEADER
       ======================================================== */

    .top-header {
        background: rgba(255,255,255,0.94);
        border: 1px solid #e0e9e4;
        border-radius: 20px;
        min-height: 82px;
        padding: 16px 22px;
        box-shadow:
            0 8px 30px rgba(23,67,48,0.07);
    }

    .top-brand {
        display: flex;
        align-items: center;
        gap: 12px;
    }

    .top-logo {
        font-size: 38px;
        line-height: 1;
    }

    .top-brand-name {
        color: #063e31;
        font-size: 28px;
        font-weight: 850;
        line-height: 1;
    }

    .top-brand-subtitle {
        color: #728079;
        font-size: 12px;
        margin-top: 5px;
    }

    .top-right {
        display: flex;
        justify-content: flex-end;
        align-items: center;
        gap: 18px;
        height: 100%;
    }

    .online-pill {
        display: inline-flex;
        align-items: center;
        gap: 7px;
        padding: 9px 15px;
        border-radius: 22px;
        border: 1px solid #b9dfc7;
        background: #f0fbf4;
        color: #08783e;
        font-size: 12px;
        font-weight: 800;
    }

    .green-dot {
        width: 9px;
        height: 9px;
        border-radius: 50%;
        background: #20a957;
        display: inline-block;
        box-shadow: 0 0 0 3px rgba(32,169,87,0.12);
    }

    .datetime {
        color: #66736d;
        font-size: 12px;
        line-height: 1.5;
        text-align: right;
    }


    /* ========================================================
       HERO
       ======================================================== */

    .hero {
        position: relative;
        overflow: hidden;
        background:
            linear-gradient(
                135deg,
                #edf8ef 0%,
                #ffffff 65%
            );
        border: 1px solid #dce9e1;
        border-radius: 22px;
        padding: 25px 28px;
        margin-top: 18px;
        margin-bottom: 18px;
        box-shadow:
            0 7px 25px rgba(23,67,48,0.055);
    }

    .hero::after {
        content: "🌿";
        position: absolute;
        right: 35px;
        bottom: -30px;
        font-size: 115px;
        opacity: 0.08;
    }

    .hero-title {
        color: #043d31;
        font-size: 29px;
        font-weight: 850;
        letter-spacing: -0.6px;
    }

    .hero-highlight {
        color: #0a8c49;
    }

    .hero-subtitle {
        color: #66756e;
        font-size: 13px;
        margin-top: 6px;
    }


    /* ========================================================
       SECTION TITLES
       ======================================================== */

    .section-title {
        color: #063e32;
        font-size: 20px;
        font-weight: 850;
        margin-top: 18px;
        margin-bottom: 11px;
    }


    /* ========================================================
       KPI CARDS
       ======================================================== */

    .kpi-card {
        position: relative;
        overflow: hidden;
        background: rgba(255,255,255,0.97);
        border: 1px solid #dfe8e3;
        border-radius: 17px;
        min-height: 142px;
        padding: 17px;
        box-shadow:
            0 6px 20px rgba(25,70,48,0.06);
        transition: all 0.2s ease;
    }

    .kpi-card:hover {
        transform: translateY(-2px);
        box-shadow:
            0 10px 28px rgba(25,70,48,0.10);
    }

    .kpi-card-green {
        border-top: 3px solid #35ad65;
    }

    .kpi-card-blue {
        border-top: 3px solid #3c9ee8;
    }

    .kpi-card-purple {
        border-top: 3px solid #8c63d7;
    }

    .kpi-icon-circle {
        width: 42px;
        height: 42px;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 50%;
        font-size: 22px;
        margin-bottom: 10px;
    }

    .icon-green {
        background: #eef8e9;
    }

    .icon-blue {
        background: #edf6ff;
    }

    .icon-purple {
        background: #f5efff;
    }

    .kpi-label {
        color: #718079;
        font-size: 10px;
        font-weight: 800;
        letter-spacing: 0.6px;
    }

    .kpi-value {
        color: #073e33;
        font-size: 23px;
        font-weight: 850;
        margin-top: 4px;
    }

    .value-green {
        color: #087e3f;
    }

    .value-blue {
        color: #1476ca;
    }

    .value-purple {
        color: #7042c5;
    }

    .kpi-description {
        color: #8a9690;
        font-size: 11px;
        margin-top: 5px;
    }


    /* ========================================================
       MAIN PANELS
       ======================================================== */

    .panel {
        background: rgba(255,255,255,0.97);
        border: 1px solid #dfe8e3;
        border-radius: 18px;
        padding: 18px;
        box-shadow:
            0 7px 23px rgba(25,70,48,0.055);
        margin-bottom: 10px;
    }

    .panel-heading {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 13px;
    }

    .panel-title {
        color: #073d33;
        font-size: 19px;
        font-weight: 850;
    }

    .panel-subtitle {
        color: #7b8781;
        font-size: 11px;
        margin-top: 4px;
    }

    .live-badge {
        background: #ecf9ef;
        color: #0a7e3e;
        border: 1px solid #c9e9d1;
        padding: 6px 10px;
        border-radius: 10px;
        font-size: 10px;
        font-weight: 800;
    }


    /* ========================================================
       CAMERA
       ======================================================== */

    .camera-frame {
        background: #102018;
        border-radius: 14px;
        overflow: hidden;
        border: 1px solid #d7e2dc;
        min-height: 300px;
        display: flex;
        align-items: center;
        justify-content: center;
    }

    .camera-placeholder {
        text-align: center;
        padding: 70px 20px;
        color: #c9d7d0;
    }

    .camera-placeholder-icon {
        font-size: 50px;
        margin-bottom: 10px;
    }

    .camera-caption {
        background: #eef7f2;
        border-radius: 11px;
        padding: 10px 13px;
        margin-top: 10px;
        color: #477064;
        font-size: 11px;
    }


    /* ========================================================
       ROVER
       ======================================================== */

    .rover-status {
        display: flex;
        justify-content: center;
        margin-bottom: 12px;
    }

    .status-chip {
        border-radius: 20px;
        padding: 7px 13px;
        font-size: 11px;
        font-weight: 800;
    }

    .status-online {
        color: #087d3f;
        background: #ecfaf0;
        border: 1px solid #c6ead0;
    }

    .status-offline {
        color: #b42318;
        background: #fff0ef;
        border: 1px solid #f1c8c5;
    }

    .rover-center-status {
        text-align: center;
        color: #52625b;
        font-size: 11px;
        margin: 8px 0;
    }

    .speed-label {
        color: #52615b;
        font-size: 11px;
        font-weight: 700;
        margin-top: 8px;
    }


    /* ========================================================
       SPRAYER
       ======================================================== */

    .sprayer-status-box {
        background:
            linear-gradient(
                135deg,
                #f1faf4,
                #f9fcfa
            );
        border: 1px solid #d6eadc;
        border-radius: 14px;
        padding: 13px;
        margin-bottom: 12px;
    }

    .sprayer-status-title {
        color: #52625b;
        font-size: 11px;
        font-weight: 700;
    }

    .sprayer-status-value {
        color: #087b3e;
        font-size: 20px;
        font-weight: 850;
        margin-top: 4px;
    }

    .sprayer-info {
        background: #f4faf6;
        border: 1px solid #dcece1;
        border-radius: 13px;
        padding: 12px;
        color: #477064;
        font-size: 11px;
        line-height: 1.5;
        margin-top: 10px;
    }


    /* ========================================================
       LIVE SPRAY STATUS
       ======================================================== */

    .live-status-card {
        background: linear-gradient(
            135deg,
            #f0fbf4,
            #ffffff
        );
        border: 1px solid #cfe9d7;
        border-radius: 16px;
        padding: 17px;
    }

    .live-status-main {
        color: #087d3f;
        font-size: 18px;
        font-weight: 850;
    }

    .live-status-text {
        color: #64736c;
        font-size: 11px;
        margin-top: 6px;
    }


    /* ========================================================
       AI DETECTION
       ======================================================== */

    .ai-card {
        background: rgba(255,255,255,0.98);
        border: 1px solid #dfe8e3;
        border-radius: 18px;
        padding: 18px;
        min-height: 180px;
        box-shadow:
            0 6px 20px rgba(25,70,48,0.05);
    }

    .ai-title {
        color: #073d33;
        font-size: 18px;
        font-weight: 850;
    }

    .ai-label {
        color: #83908a;
        font-size: 10px;
        font-weight: 800;
        letter-spacing: 0.5px;
        margin-top: 15px;
    }

    .ai-value {
        color: #073e33;
        font-size: 17px;
        font-weight: 800;
        margin-top: 5px;
    }

    .ai-description {
        color: #75827c;
        font-size: 11px;
        line-height: 1.55;
        margin-top: 8px;
    }

    .ai-alert {
        background: #fff3f1;
        border: 1px solid #f0cbc7;
    }

    .ai-recommendation {
        background: #effaf3;
        border: 1px solid #cce9d5;
    }


    /* ========================================================
       WORKFLOW
       ======================================================== */

    .workflow-container {
        background: white;
        border: 1px solid #dfe8e3;
        border-radius: 18px;
        padding: 19px;
        box-shadow:
            0 6px 20px rgba(25,70,48,0.05);
    }

    .workflow-step {
        text-align: center;
        position: relative;
    }

    .step-circle {
        width: 44px;
        height: 44px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 0 auto 9px auto;
        background: #eff9e9;
        border: 1px solid #d2e9cc;
        color: #178246;
        font-weight: 850;
        font-size: 12px;
    }

    .step-icon {
        font-size: 27px;
        margin-bottom: 5px;
    }

    .step-title {
        color: #073e33;
        font-size: 14px;
        font-weight: 850;
    }

    .step-text {
        color: #7c8882;
        font-size: 10px;
        line-height: 1.45;
        margin-top: 4px;
    }


    /* ========================================================
       NATIVE STREAMLIT BUTTONS
       ======================================================== */

    .stButton > button {
        border-radius: 11px !important;
        min-height: 43px !important;
        font-weight: 750 !important;
        font-size: 12px !important;
        border: 1px solid #d8e4de !important;
        background: white !important;
        color: #163f34 !important;
        transition: all 0.18s ease !important;
    }

    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 6px 16px rgba(20,70,45,0.10);
        border-color: #99cdb0 !important;
    }

    .stButton > button[kind="primary"] {
        background:
            linear-gradient(
                135deg,
                #159450,
                #087c40
            ) !important;
        color: white !important;
        border: none !important;
    }


    /* Rover buttons */

    button[key="forward"],
    button[key="backward"],
    button[key="left"],
    button[key="right"] {
        min-height: 52px !important;
        font-size: 21px !important;
        background: #e5f8ec !important;
        border: 1px solid #c5e9d2 !important;
        color: #075d3e !important;
    }


    /* ========================================================
       INPUTS
       ======================================================== */

    div[data-baseweb="input"],
    div[data-baseweb="select"] {
        border-radius: 10px !important;
    }

    .stSlider {
        padding-top: 2px;
    }

    div[data-testid="stNumberInput"] label,
    div[data-testid="stSlider"] label {
        color: #44544d !important;
        font-size: 11px !important;
        font-weight: 700 !important;
    }


    /* ========================================================
       METRICS
       ======================================================== */

    div[data-testid="stMetric"] {
        background: white;
        border-radius: 14px;
        padding: 12px;
        border: 1px solid #dfe8e3;
    }


    /* ========================================================
       ALERTS
       ======================================================== */

    div[data-testid="stAlert"] {
        border-radius: 12px !important;
        font-size: 12px !important;
    }


    /* ========================================================
       FOOTER
       ======================================================== */

    .footer {
        text-align: center;
        color: #8b9791;
        font-size: 10px;
        padding: 25px 0 8px 0;
    }


    /* ========================================================
       MOBILE
       ======================================================== */

    @media (max-width: 900px) {

        section[data-testid="stSidebar"] {
            min-width: 250px;
            max-width: 250px;
        }

        .main .block-container {
            padding-left: 0.8rem;
            padding-right: 0.8rem;
        }

        .hero-title {
            font-size: 23px;
        }

        .top-brand-name {
            font-size: 23px;
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


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown(
        dedent("""
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
        """),
        unsafe_allow_html=True
    )


    st.markdown(
        '<div class="sidebar-menu-title">MAIN MENU</div>',
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


    raspberry_status = (
        "● ONLINE"
        if raspberry_online
        else "● OFFLINE"
    )

    raspberry_status_color = (
        "#63e995"
        if raspberry_online
        else "#ff7b72"
    )

    st.markdown(
        dedent(f"""
        <div class="sidebar-system-card">

            <div class="sidebar-system-label">
                🍓 Raspberry Pi
            </div>

            <div class="sidebar-system-status"
                 style="color:{raspberry_status_color};">
                {raspberry_status}
            </div>

            <div class="sidebar-uptime-label">
                System Status
            </div>

            <div class="sidebar-uptime-value">
                {"Operational" if raspberry_online else "Disconnected"}
            </div>

        </div>

        <div class="sidebar-plant">
            🌱
        </div>
        """),
        unsafe_allow_html=True
    )


# ============================================================
# TOP HEADER
# ============================================================

header_left, header_right = st.columns([3, 2])


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

    online_text = (
        "SYSTEM ONLINE"
        if state is not None
        else "SYSTEM OFFLINE"
    )

    online_color = (
        "#20a957"
        if state is not None
        else "#d33b32"
    )

    now = datetime.now().strftime(
        "%d %b %Y • %I:%M:%S %p"
    )

    st.markdown(
        dedent(f"""
        <div class="top-header">

            <div class="top-right">

                <div class="online-pill">
                    <span class="green-dot"
                          style="background:{online_color};">
                    </span>
                    {online_text}
                </div>

                <div class="datetime">
                    {now}
                </div>

                <div style="font-size:20px;">
                    🔔
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

    # --------------------------------------------------------
    # HERO
    # --------------------------------------------------------

    st.markdown(
        dedent("""
        <div class="hero">

            <div class="hero-title">
                🌿 Precision
                <span class="hero-highlight">
                    Spraying Control
                </span>
            </div>

            <div class="hero-subtitle">
                Monitor the plant, control the rover,
                configure spray dosage, and perform
                precision spraying.
            </div>

        </div>
        """),
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


    # KPI 1

    with k1:

        display_status = str(
            spray_status
        ).upper()

        st.markdown(
            dedent(f"""
            <div class="kpi-card kpi-card-green">

                <div class="kpi-icon-circle icon-green">
                    💦
                </div>

                <div class="kpi-label">
                    SPRAYER STATUS
                </div>

                <div class="kpi-value value-green">
                    {display_status}
                </div>

                <div class="kpi-description">
                    Current operation
                </div>

            </div>
            """),
            unsafe_allow_html=True
        )


    # KPI 2

    with k2:

        st.markdown(
            dedent(f"""
            <div class="kpi-card kpi-card-blue">

                <div class="kpi-icon-circle icon-blue">
                    💧
                </div>

                <div class="kpi-label">
                    LAST DISPENSED
                </div>

                <div class="kpi-value value-blue">
                    {float(sprayed_amount):.1f} ml
                </div>

                <div class="kpi-description">
                    Latest spray quantity
                </div>

            </div>
            """),
            unsafe_allow_html=True
        )


    # KPI 3

    with k3:

        camera_status = (
            "READY"
            if raspberry_online
            else "OFFLINE"
        )

        st.markdown(
            dedent(f"""
            <div class="kpi-card kpi-card-green">

                <div class="kpi-icon-circle icon-green">
                    📷
                </div>

                <div class="kpi-label">
                    CAMERA
                </div>

                <div class="kpi-value value-green">
                    {camera_status}
                </div>

                <div class="kpi-description">
                    Plant imaging system
                </div>

            </div>
            """),
            unsafe_allow_html=True
        )


    # KPI 4

    with k4:

        rover_connection = (
            "ONLINE"
            if esp32_online
            else "OFFLINE"
        )

        st.markdown(
            dedent(f"""
            <div class="kpi-card kpi-card-purple">

                <div class="kpi-icon-circle icon-purple">
                    🔌
                </div>

                <div class="kpi-label">
                    ESP32 ROVER
                </div>

                <div class="kpi-value value-purple">
                    {rover_connection}
                </div>

                <div class="kpi-description">
                    Rover hardware connection
                </div>

            </div>
            """),
            unsafe_allow_html=True
        )


    # --------------------------------------------------------
    # MAIN CONTROL
    # --------------------------------------------------------

    st.markdown(
        '<div class="section-title">Plant Monitoring & Control</div>',
        unsafe_allow_html=True
    )


    camera_col, rover_col, spray_col = st.columns(
        [1.45, 1, 1]
    )


    # ========================================================
    # CAMERA PANEL
    # ========================================================

    with camera_col:

        st.markdown(
            dedent("""
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
            """),
            unsafe_allow_html=True
        )


        image = get_latest_image()


        if image is not None:

            st.image(
                image,
                use_container_width=True
            )

            st.markdown(
                dedent("""
                <div class="camera-caption">
                    📷 Live image from Raspberry Pi camera
                    <br>
                    <span style="color:#82908a;">
                    Capture a new image to update the
                    monitoring view.
                    </span>
                </div>
                """),
                unsafe_allow_html=True
            )

        else:

            st.markdown(
                dedent("""
                <div class="camera-frame">

                    <div class="camera-placeholder">

                        <div class="camera-placeholder-icon">
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
                """),
                unsafe_allow_html=True
            )


        st.write("")


        if st.button(
            "📸  CAPTURE PLANT IMAGE",
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
    # ROVER PANEL
    # ========================================================

    with rover_col:

        st.markdown(
            dedent("""
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
            """),
            unsafe_allow_html=True
        )


        if esp32_online:

            st.markdown(
                '<div class="rover-status">'
                '<div class="status-chip status-online">'
                '● ESP32 ONLINE'
                '</div>'
                '</div>',
                unsafe_allow_html=True
            )

        else:

            st.markdown(
                '<div class="rover-status">'
                '<div class="status-chip status-offline">'
                '● ESP32 OFFLINE'
                '</div>'
                '</div>',
                unsafe_allow_html=True
            )


        st.markdown(
            dedent(f"""
            <div class="rover-center-status">
                Rover Status:
                <b>{rover_status}</b>
            </div>
            """),
            unsafe_allow_html=True
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
                    current_speed
                )

                if response is not None:

                    if response.status_code != 200:
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

                if response is not None:

                    if response.status_code != 200:
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

                if response is not None:

                    if response.status_code == 200:
                        st.success("Rover stopped.")
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
                    current_speed
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
                    current_speed
                )

                if response is not None:

                    if response.status_code != 200:
                        st.error(response.text)


        speed = st.slider(
            "Rover Speed",
            min_value=0,
            max_value=100,
            value=int(current_speed),
            step=5,
            key="dashboard_speed"
        )


        st.caption(
            f"Current speed: {speed}%"
        )


    # ========================================================
    # SPRAYER PANEL
    # ========================================================

    with spray_col:

        st.markdown(
            dedent("""
            <div class="panel">

                <div class="panel-heading">

                    <div>
                        <div class="panel-title">
                            💧 Sprayer Control
                        </div>

                        <div class="panel-subtitle">
                            Configure and activate precision
                            spraying.
                        </div>
                    </div>

                </div>

            </div>
            """),
            unsafe_allow_html=True
        )


        active_status = str(
            spray_status
        ).lower()


        if "spray" in active_status:

            st.markdown(
                dedent("""
                <div class="sprayer-status-box">

                    <div class="sprayer-status-title">
                        SPRAYER STATUS
                    </div>

                    <div class="sprayer-status-value">
                        🟡 SPRAYING
                    </div>

                </div>
                """),
                unsafe_allow_html=True
            )

        else:

            st.markdown(
                dedent(f"""
                <div class="sprayer-status-box">

                    <div class="sprayer-status-title">
                        SPRAYER STATUS
                    </div>

                    <div class="sprayer-status-value">
                        🟢 {str(spray_status).upper()}
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
            "🚿  START PRECISION SPRAY",
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
            <div class="sprayer-info">
                💡 The selected dosage will be sent
                to the Raspberry Pi sprayer.
            </div>
            """),
            unsafe_allow_html=True
        )


    # ========================================================
    # LIVE SPRAY STATUS
    # ========================================================

    st.markdown(
        '<div class="section-title">Live Spray Status</div>',
        unsafe_allow_html=True
    )


    if "spray" in str(spray_status).lower():

        st.markdown(
            dedent(f"""
            <div class="live-status-card">

                <div class="live-status-main">
                    🟡 SPRAYING
                </div>

                <div class="live-status-text">
                    {float(sprayed_amount):.1f} ml
                    currently dispensed.
                </div>

            </div>
            """),
            unsafe_allow_html=True
        )

    else:

        st.markdown(
            dedent(f"""
            <div class="live-status-card">

                <div class="live-status-main">
                    🟢 READY
                </div>

                <div class="live-status-text">
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
        '<div class="section-title">🌿 AI Detection</div>',
        unsafe_allow_html=True
    )


    ai1, ai2, ai3 = st.columns(
        [1, 1.15, 0.8]
    )


    with ai1:

        st.markdown(
            dedent("""
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

                <div class="ai-description">
                    Capture a plant image to begin
                    AI-powered plant analysis.
                </div>

            </div>
            """),
            unsafe_allow_html=True
        )


    with ai2:

        st.markdown(
            dedent("""
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

                <div class="ai-description">
                    AI disease classification will
                    appear here once your detection
                    model is connected.
                </div>

            </div>
            """),
            unsafe_allow_html=True
        )


    with ai3:

        st.markdown(
            dedent("""
            <div class="ai-card ai-recommendation">

                <div class="ai-title">
                    💡 Recommendation
                </div>

                <div class="ai-label">
                    ACTION
                </div>

                <div class="ai-value">
                    Awaiting Detection
                </div>

                <div class="ai-description">
                    Targeted treatment recommendations
                    will appear here.
                </div>

            </div>
            """),
            unsafe_allow_html=True
        )


    # ========================================================
    # WORKFLOW
    # ========================================================

    st.markdown(
        '<div class="section-title">CropIQ Workflow</div>',
        unsafe_allow_html=True
    )


    st.markdown(
        '<div class="workflow-container">',
        unsafe_allow_html=True
    )


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


    for column, number, icon, title, description in workflow:

        with column:

            st.markdown(
                dedent(f"""
                <div class="workflow-step">

                    <div class="step-circle">
                        {number}
                    </div>

                    <div class="step-icon">
                        {icon}
                    </div>

                    <div class="step-title">
                        {title}
                    </div>

                    <div class="step-text">
                        {description}
                    </div>

                </div>
                """),
                unsafe_allow_html=True
            )


    st.markdown(
        '</div>',
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
                📷 Live
                <span class="hero-highlight">
                    Plant Monitoring
                </span>
            </div>

            <div class="hero-subtitle">
                Monitor the latest images captured
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
                    "Capture command sent."
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
        dedent("""
        <div class="hero">

            <div class="hero-title">
                🚜 Rover
                <span class="hero-highlight">
                    Control
                </span>
            </div>

            <div class="hero-subtitle">
                Control the CropIQ rover using ESP32.
            </div>

        </div>
        """),
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
        dedent(f"""
        <div class="panel">

            <div style="
                text-align:center;
                color:#073e33;
                font-size:18px;
                font-weight:800;
            ">
                Rover Status: {rover_status}
            </div>

            <div style="
                text-align:center;
                color:#77847e;
                font-size:11px;
                margin-top:5px;
            ">
                Speed: {speed}%
            </div>

        </div>
        """),
        unsafe_allow_html=True
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
# SPRAYER CONTROL PAGE
# ============================================================

elif page == "💧 Sprayer Control":

    st.markdown(
        dedent("""
        <div class="hero">

            <div class="hero-title">
                💧 Precision
                <span class="hero-highlight">
                    Sprayer Control
                </span>
            </div>

            <div class="hero-subtitle">
                Configure spray dosage and activate
                the precision sprayer.
            </div>

        </div>
        """),
        unsafe_allow_html=True
    )


    c1, c2 = st.columns(2)


    with c1:

        st.markdown(
            dedent(f"""
            <div class="kpi-card kpi-card-green">

                <div class="kpi-icon-circle icon-green">
                    💦
                </div>

                <div class="kpi-label">
                    SPRAYER STATUS
                </div>

                <div class="kpi-value value-green">
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
            <div class="kpi-card kpi-card-blue">

                <div class="kpi-icon-circle icon-blue">
                    💧
                </div>

                <div class="kpi-label">
                    LAST DISPENSED
                </div>

                <div class="kpi-value value-blue">
                    {float(sprayed_amount):.1f} ml
                </div>

                <div class="kpi-description">
                    Latest spray quantity
                </div>

            </div>
            """),
            unsafe_allow_html=True
        )


    st.write("")


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
                🌿 AI Plant
                <span class="hero-highlight">
                    Detection
                </span>
            </div>

            <div class="hero-subtitle">
                AI-powered plant disease detection
                and targeted treatment recommendation.
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


    a1, a2, a3 = st.columns(3)


    with a1:

        st.markdown(
            dedent("""
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

                <div class="ai-description">
                    AI analysis will appear here
                    after image processing.
                </div>

            </div>
            """),
            unsafe_allow_html=True
        )


    with a2:

        st.markdown(
            dedent("""
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

                <div class="ai-description">
                    Connect your disease detection
                    model to display the diagnosis
                    and confidence score.
                </div>

            </div>
            """),
            unsafe_allow_html=True
        )


    with a3:

        st.markdown(
            dedent("""
            <div class="ai-card ai-recommendation">

                <div class="ai-title">
                    💡 Recommendation
                </div>

                <div class="ai-label">
                    ACTION
                </div>

                <div class="ai-value">
                    Awaiting Detection
                </div>

                <div class="ai-description">
                    Treatment recommendations will
                    appear after AI detection.
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
                ⚙️ CropIQ
                <span class="hero-highlight">
                    Settings
                </span>
            </div>

            <div class="hero-subtitle">
                System configuration and hardware
                connection information.
            </div>

        </div>
        """),
        unsafe_allow_html=True
    )


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

            st.success(
                "🍓 Raspberry Pi connected"
            )

        else:

            st.error(
                "🍓 Raspberry Pi unavailable"
            )


    with c2:

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
