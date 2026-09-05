import streamlit as st
import requests
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
    page_title="CropIQ",
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

    .stApp {
        background: #f5f8f6;
    }

    .main .block-container {
        max-width: 1500px;
        padding-top: 1.2rem;
        padding-bottom: 2rem;
        padding-left: 2rem;
        padding-right: 2rem;
    }

    /* Remove unnecessary Streamlit elements */

    #MainMenu {
        visibility: hidden;
    }

    footer {
        visibility: hidden;
    }

    header {
        background: transparent;
    }


    /* ========================================================
       SIDEBAR
       ======================================================== */

    [data-testid="stSidebar"] {
        background: linear-gradient(
            180deg,
            #063b32 0%,
            #06483b 55%,
            #06382f 100%
        );
        min-width: 235px;
        max-width: 235px;
    }

    [data-testid="stSidebar"] > div:first-child {
        padding-top: 1.2rem;
    }

    [data-testid="stSidebar"] * {
        color: white;
    }

    .sidebar-logo {
        text-align: center;
        padding: 8px 0 25px 0;
    }

    .sidebar-logo-icon {
        font-size: 42px;
        line-height: 1;
    }

    .sidebar-logo-text {
        font-size: 28px;
        font-weight: 800;
        letter-spacing: -1px;
        margin-top: 5px;
    }

    .sidebar-version {
        font-size: 11px;
        color: #a8c8be !important;
        margin-top: 2px;
    }

    .sidebar-section {
        color: #91b8ad !important;
        font-size: 10px;
        font-weight: 700;
        letter-spacing: 1.2px;
        margin: 12px 0 8px 4px;
    }

    /* Sidebar buttons */

    [data-testid="stSidebar"] .stButton > button {
        background: transparent;
        border: none;
        color: #e7f3ef;
        text-align: left;
        border-radius: 9px;
        min-height: 43px;
        font-size: 13px;
        font-weight: 500;
        margin-bottom: 3px;
        padding-left: 15px;
    }

    [data-testid="stSidebar"] .stButton > button:hover {
        background: rgba(255,255,255,0.10);
        color: white;
        border: none;
    }

    .sidebar-online {
        border: 1px solid rgba(142, 220, 169, 0.45);
        background: rgba(11, 101, 72, 0.35);
        border-radius: 13px;
        padding: 15px;
        margin-top: 30px;
    }

    .sidebar-online-title {
        font-size: 11px;
        color: #b7d4cc !important;
    }

    .sidebar-online-status {
        font-size: 17px;
        font-weight: 800;
        color: #8be28c !important;
        margin-top: 3px;
    }

    .sidebar-online-detail {
        font-size: 11px;
        color: #b7d4cc !important;
        margin-top: 12px;
    }

    .sidebar-online-value {
        font-size: 14px;
        color: white !important;
        font-weight: 600;
    }


    /* ========================================================
       TOP HEADER
       ======================================================== */

    .top-header {
        background: white;
        border: 1px solid #e3e9e5;
        border-radius: 16px;
        min-height: 78px;
        padding: 15px 22px;
        box-shadow: 0 3px 15px rgba(18, 50, 38, 0.045);
        margin-bottom: 18px;
    }

    .brand-title {
        color: #073c32;
        font-size: 28px;
        font-weight: 800;
        line-height: 1;
        margin-top: 2px;
    }

    .brand-subtitle {
        color: #6c7772;
        font-size: 12px;
        margin-top: 5px;
    }

    .header-online {
        border: 1px solid #b7ddc2;
        background: #f4fcf6;
        color: #16743c;
        border-radius: 9px;
        padding: 10px 15px;
        font-size: 12px;
        font-weight: 700;
        text-align: center;
    }

    .header-offline {
        border: 1px solid #f0c5c5;
        background: #fff6f6;
        color: #c13c3c;
        border-radius: 9px;
        padding: 10px 15px;
        font-size: 12px;
        font-weight: 700;
        text-align: center;
    }

    .header-date {
        color: #66736c;
        font-size: 11px;
        padding-top: 12px;
        text-align: right;
    }


    /* ========================================================
       HERO
       ======================================================== */

    .hero {
        background: linear-gradient(
            90deg,
            #eef7ef 0%,
            #f8fbf8 60%,
            #edf7ef 100%
        );
        border: 1px solid #e0eae2;
        border-radius: 14px;
        padding: 19px 22px;
        margin-bottom: 17px;
    }

    .hero-title {
        color: #092f29;
        font-size: 27px;
        font-weight: 800;
        line-height: 1.15;
    }

    .hero-title-green {
        color: #16784c;
    }

    .hero-subtitle {
        color: #69756f;
        font-size: 12px;
        margin-top: 6px;
    }

    .hero-badge {
        text-align: right;
        color: #27764d;
        font-size: 11px;
        font-weight: 700;
        padding-top: 15px;
    }


    /* ========================================================
       SECTION TITLES
       ======================================================== */

    .section-heading {
        color: #08382f;
        font-size: 17px;
        font-weight: 800;
        margin-top: 12px;
        margin-bottom: 10px;
    }


    /* ========================================================
       KPI CARDS
       ======================================================== */

    .kpi-card {
        background: white;
        border: 1px solid #e0e8e2;
        border-radius: 13px;
        padding: 17px;
        min-height: 125px;
        box-shadow: 0 3px 14px rgba(20, 54, 39, 0.04);
    }

    .kpi-label {
        color: #6c7772;
        font-size: 10px;
        font-weight: 700;
        letter-spacing: 0.5px;
    }

    .kpi-value {
        color: #073c32;
        font-size: 23px;
        font-weight: 800;
        margin-top: 7px;
    }

    .kpi-value-blue {
        color: #0874c9;
    }

    .kpi-value-purple {
        color: #7540bf;
    }

    .kpi-description {
        color: #89928e;
        font-size: 10px;
        margin-top: 5px;
    }

    .kpi-icon {
        font-size: 23px;
        float: right;
    }

    .kpi-green {
        border-top: 3px solid #5bb878;
    }

    .kpi-blue {
        border-top: 3px solid #54a9ec;
    }

    .kpi-purple {
        border-top: 3px solid #9c72df;
    }


    /* ========================================================
       MAIN CARDS
       ======================================================== */

    [data-testid="stVerticalBlockBorderWrapper"] {
        background: white;
        border: 1px solid #e0e8e2;
        border-radius: 14px;
        box-shadow: 0 3px 15px rgba(20, 54, 39, 0.045);
    }


    /* ========================================================
       CARD HEADERS
       ======================================================== */

    .card-title {
        color: #103d34;
        font-size: 17px;
        font-weight: 800;
        margin-bottom: 5px;
    }

    .card-description {
        color: #6d7973;
        font-size: 11px;
        line-height: 1.5;
    }

    .live-badge {
        background: #e9f8ec;
        border: 1px solid #cce9d2;
        color: #208247;
        border-radius: 7px;
        padding: 7px 12px;
        font-size: 10px;
        font-weight: 800;
        text-align: center;
    }


    /* ========================================================
       IMAGE
       ======================================================== */

    .plant-image-container {
        border-radius: 11px;
        overflow: hidden;
        margin-top: 8px;
    }

    [data-testid="stImage"] img {
        border-radius: 10px;
    }

    .image-info {
        background: #eef7ff;
        border: 1px solid #d8eaf8;
        border-radius: 9px;
        padding: 10px 12px;
        color: #27628a;
        font-size: 10px;
        margin-top: 9px;
    }


    /* ========================================================
       INPUTS
       ======================================================== */

    .stNumberInput label,
    .stSlider label {
        color: #173d35 !important;
        font-size: 11px !important;
        font-weight: 700 !important;
    }

    [data-testid="stNumberInput"] input {
        font-weight: 700;
        color: #153a32;
    }


    /* ========================================================
       BUTTONS
       ======================================================== */

    .stButton > button {
        border-radius: 9px;
        min-height: 42px;
        font-size: 11px;
        font-weight: 700;
        border: 1px solid #d7dfda;
        background: white;
        color: #193b34;
    }

    .stButton > button:hover {
        border-color: #288153;
        color: #17653e;
        background: #f5faf6;
    }

    .stButton > button[kind="primary"] {
        background: #19834f;
        border-color: #19834f;
        color: white;
    }

    .stButton > button[kind="primary"]:hover {
        background: #126b40;
        border-color: #126b40;
        color: white;
    }


    /* ========================================================
       INFO BOX
       ======================================================== */

    .spray-info {
        background: #f0faf1;
        border: 1px solid #d6ecd9;
        border-radius: 9px;
        padding: 12px;
        color: #24643d;
        font-size: 10px;
        line-height: 1.5;
        margin-top: 10px;
    }


    /* ========================================================
       STATUS
       ======================================================== */

    .status-box {
        border-radius: 10px;
        padding: 17px;
        background: #f0fbf2;
        border: 1px solid #cfead3;
    }

    .status-title {
        color: #17713b;
        font-size: 18px;
        font-weight: 800;
    }

    .status-description {
        color: #5c6962;
        font-size: 11px;
        margin-top: 5px;
    }

    .status-stat-label {
        color: #68736e;
        font-size: 10px;
    }

    .status-stat-value {
        color: #13733b;
        font-size: 13px;
        font-weight: 800;
    }

    .status-divider {
        border-top: 1px solid #dce8de;
        margin: 13px 0;
    }


    /* ========================================================
       SYSTEM HEALTH
       ======================================================== */

    .health-circle {
        border: 6px solid #26904e;
        width: 68px;
        height: 68px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        color: #17713b;
        font-size: 15px;
        font-weight: 800;
    }


    /* ========================================================
       WORKFLOW
       ======================================================== */

    .workflow-card {
        background: white;
        border: 1px solid #e0e8e2;
        border-radius: 14px;
        padding: 18px;
        box-shadow: 0 3px 15px rgba(20,54,39,0.04);
    }

    .workflow-number {
        background: #edf8ee;
        color: #27824a;
        border-radius: 50%;
        width: 34px;
        height: 34px;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        font-size: 12px;
        font-weight: 800;
    }

    .workflow-title {
        color: #173b34;
        font-size: 14px;
        font-weight: 800;
    }

    .workflow-description {
        color: #78837e;
        font-size: 10px;
        line-height: 1.45;
    }


    /* ========================================================
       ROVER CONTROL
       ======================================================== */

    .rover-status {
        background: #f1faf3;
        border: 1px solid #d4ead8;
        border-radius: 9px;
        padding: 10px;
        color: #1e7841;
        font-size: 11px;
        font-weight: 700;
    }


    /* ========================================================
       FOOTER
       ======================================================== */

    .footer {
        text-align: center;
        color: #7d8782;
        font-size: 10px;
        padding-top: 8px;
    }


    /* ========================================================
       MOBILE
       ======================================================== */

    @media (max-width: 900px) {

        .main .block-container {
            padding-left: 1rem;
            padding-right: 1rem;
        }

        .hero-title {
            font-size: 22px;
        }

        .brand-title {
            font-size: 23px;
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


def get_error_message(response):

    try:

        data = response.json()

        return data.get(
            "detail",
            response.text
        )

    except Exception:

        return response.text


# ============================================================
# GET STATE
# ============================================================

state = get_state()

if state is None:

    raspberry_pi = {}
    esp32 = {}

else:

    raspberry_pi = state.get(
        "raspberry_pi",
        {}
    )

    esp32 = state.get(
        "esp32",
        {}
    )


spray_status = raspberry_pi.get(
    "spray_status",
    "Unknown"
)

sprayed_amount = raspberry_pi.get(
    "sprayed_amount",
    0.0
)

image_available = raspberry_pi.get(
    "image_available",
    False
)

esp32_online = esp32.get(
    "online",
    False
)

rover_status = esp32.get(
    "rover_status",
    "UNKNOWN"
)

backend_online = state is not None


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown(
        """
        <div class="sidebar-logo">

            <div class="sidebar-logo-icon">
                🌱
            </div>

            <div class="sidebar-logo-text">
                CropIQ
            </div>

            <div class="sidebar-version">
                v2.1.0
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="sidebar-section">MAIN MENU</div>',
        unsafe_allow_html=True
    )

    st.button(
        "⌂   Dashboard",
        use_container_width=True
    )

    st.button(
        "♧   Monitoring",
        use_container_width=True
    )

    st.button(
        "🚿   Spray Control",
        use_container_width=True
    )

    st.button(
        "🚜   Rover Control",
        use_container_width=True
    )

    st.button(
        "◷   History",
        use_container_width=True
    )

    st.button(
        "▥   Analytics",
        use_container_width=True
    )

    st.button(
        "♢   Alerts",
        use_container_width=True
    )

    st.button(
        "⚙   Settings",
        use_container_width=True
    )

    st.markdown(
        "<br>",
        unsafe_allow_html=True
    )

    if backend_online:

        st.markdown(
            """
            <div class="sidebar-online">

                <div class="sidebar-online-title">
                    📡 Raspberry Pi
                </div>

                <div class="sidebar-online-status">
                    ● ONLINE
                </div>

                <div class="sidebar-online-detail">
                    System connection
                </div>

                <div class="sidebar-online-value">
                    Active
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )

    else:

        st.markdown(
            """
            <div class="sidebar-online">

                <div class="sidebar-online-title">
                    📡 Raspberry Pi
                </div>

                <div style="
                    color:#ff9a9a;
                    font-size:17px;
                    font-weight:800;
                    margin-top:3px;
                ">
                    ● OFFLINE
                </div>

                <div class="sidebar-online-detail">
                    System connection
                </div>

                <div class="sidebar-online-value">
                    Unavailable
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )


# ============================================================
# TOP HEADER
# ============================================================

header_left, header_status, header_date, header_bell = st.columns(
    [4.5, 1.3, 1.6, 0.4],
    vertical_alignment="center"
)


with header_left:

    st.markdown(
        """
        <div class="brand-title">
            🌱 CropIQ
        </div>

        <div class="brand-subtitle">
            Precision Agriculture Intelligence Platform
        </div>
        """,
        unsafe_allow_html=True
    )


with header_status:

    if backend_online:

        st.markdown(
            """
            <div class="header-online">
                🟢 SYSTEM ONLINE
            </div>
            """,
            unsafe_allow_html=True
        )

    else:

        st.markdown(
            """
            <div class="header-offline">
                🔴 SYSTEM OFFLINE
            </div>
            """,
            unsafe_allow_html=True
        )


with header_date:

    now = datetime.now()

    st.markdown(
        f"""
        <div class="header-date">
            {now.strftime("%b %d, %Y")}<br>
            {now.strftime("%I:%M:%S %p")}
        </div>
        """,
        unsafe_allow_html=True
    )


with header_bell:

    st.markdown(
        "<div style='font-size:22px;text-align:center;'>♧</div>",
        unsafe_allow_html=True
    )


# ============================================================
# HERO
# ============================================================

st.markdown(
    """
    <div class="hero">

        <div class="hero-title">
            Precision <span class="hero-title-green">Spraying Control</span>
        </div>

        <div class="hero-subtitle">
            Monitor the plant, capture images, configure spray dosage,
            and control the precision spraying system.
        </div>

    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# SYSTEM OVERVIEW
# ============================================================

st.markdown(
    '<div class="section-heading">System Overview</div>',
    unsafe_allow_html=True
)


kpi1, kpi2, kpi3, kpi4 = st.columns(
    4,
    gap="medium"
)


# ------------------------------------------------------------
# KPI 1
# ------------------------------------------------------------

with kpi1:

    status_display = spray_status.upper()

    if status_display == "SPRAYING...":
        status_display = "SPRAYING"

    st.markdown(
        f"""
        <div class="kpi-card kpi-green">

            <div class="kpi-icon">
                🚿
            </div>

            <div class="kpi-label">
                SPRAYER STATUS
            </div>

            <div class="kpi-value">
                {status_display}
            </div>

            <div class="kpi-description">
                Current operation
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )


# ------------------------------------------------------------
# KPI 2
# ------------------------------------------------------------

with kpi2:

    st.markdown(
        f"""
        <div class="kpi-card kpi-blue">

            <div class="kpi-icon">
                💧
            </div>

            <div class="kpi-label">
                LAST DISPENSED
            </div>

            <div class="kpi-value kpi-value-blue">
                {sprayed_amount:.1f} ml
            </div>

            <div class="kpi-description">
                Latest spray quantity
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )


# ------------------------------------------------------------
# KPI 3
# ------------------------------------------------------------

with kpi3:

    camera_display = "READY" if backend_online else "OFFLINE"

    st.markdown(
        f"""
        <div class="kpi-card kpi-green">

            <div class="kpi-icon">
                📷
            </div>

            <div class="kpi-label">
                CAMERA
            </div>

            <div class="kpi-value">
                {camera_display}
            </div>

            <div class="kpi-description">
                Plant imaging system
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )


# ------------------------------------------------------------
# KPI 4
# ------------------------------------------------------------

with kpi4:

    pi_display = "ONLINE" if backend_online else "OFFLINE"

    st.markdown(
        f"""
        <div class="kpi-card kpi-purple">

            <div class="kpi-icon">
                🧠
            </div>

            <div class="kpi-label">
                RASPBERRY PI
            </div>

            <div class="kpi-value kpi-value-purple">
                {pi_display}
            </div>

            <div class="kpi-description">
                Hardware connection
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )


st.write("")


# ============================================================
# MAIN MONITORING AREA
# ============================================================

plant_col, spray_col, status_col = st.columns(
    [2.35, 1.05, 1.05],
    gap="medium"
)


# ============================================================
# PLANT MONITORING
# ============================================================

with plant_col:

    with st.container(border=True):

        title_col, live_col = st.columns(
            [4, 1],
            vertical_alignment="center"
        )

        with title_col:

            st.markdown(
                '<div class="card-title">🌿 Plant Monitoring</div>',
                unsafe_allow_html=True
            )

        with live_col:

            st.markdown(
                """
                <div class="live-badge">
                    🟢 LIVE
                </div>
                """,
                unsafe_allow_html=True
            )


        @st.fragment(run_every="2s")
        def plant_monitor():

            image = get_latest_image()

            if image is not None:

                st.image(
                    image,
                    use_container_width=True
                )

                st.markdown(
                    """
                    <div class="image-info">
                        📷 <b>Live image from Raspberry Pi camera.</b><br>
                        Capture a new image to update the monitoring view.
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            else:

                st.info(
                    "📷 No plant image available yet. "
                    "Capture an image to begin monitoring."
                )


        plant_monitor()


# ============================================================
# PRECISION SPRAY
# ============================================================

with spray_col:

    with st.container(border=True):

        st.markdown(
            '<div class="card-title">🚿 Precision Spray</div>',
            unsafe_allow_html=True
        )

        st.markdown(
            """
            <div class="card-description">
                Configure the required spray quantity
                and activate the precision sprayer.
            </div>
            """,
            unsafe_allow_html=True
        )

        st.divider()


        dosage = st.number_input(
            "Spray dosage (ml)",
            min_value=1.0,
            max_value=500.0,
            value=25.0,
            step=1.0,
            format="%.0f"
        )


        st.caption(
            "Allowed range: 1 – 500 ml"
        )


        if st.button(
            "📷  CAPTURE PLANT IMAGE",
            use_container_width=True
        ):

            response = send_capture()

            if response is not None:

                if response.status_code == 200:

                    st.success(
                        "Capture command sent!"
                    )

                else:

                    st.error(
                        f"Capture failed: "
                        f"{get_error_message(response)}"
                    )


        if st.button(
            "🚿  START PRECISION SPRAY",
            type="primary",
            use_container_width=True
        ):

            response = send_spray(dosage)

            if response is not None:

                if response.status_code == 200:

                    st.success(
                        f"Spray command sent: "
                        f"{dosage:.0f} ml"
                    )

                else:

                    st.error(
                        f"Spray failed: "
                        f"{get_error_message(response)}"
                    )


        st.markdown(
            """
            <div class="spray-info">
                💡 The selected dosage will be sent
                to the Raspberry Pi sprayer.
            </div>
            """,
            unsafe_allow_html=True
        )


# ============================================================
# LIVE SPRAY STATUS
# ============================================================

with status_col:

    with st.container(border=True):

        st.markdown(
            '<div class="card-title">〽 Live Spray Status</div>',
            unsafe_allow_html=True
        )


        @st.fragment(run_every="2s")
        def live_status():

            current_state = get_state()

            if current_state is None:

                st.markdown(
                    """
                    <div class="status-box"
                         style="background:#fff5f5;border-color:#f0cccc;">

                        <div class="status-title"
                             style="color:#c03939;">
                            🔴 OFFLINE
                        </div>

                        <div class="status-description">
                            Unable to communicate with the backend.
                        </div>

                    </div>
                    """,
                    unsafe_allow_html=True
                )

                return


            raspberry = current_state.get(
                "raspberry_pi",
                {}
            )

            status = raspberry.get(
                "spray_status",
                "Ready"
            )

            amount = raspberry.get(
                "sprayed_amount",
                0.0
            )


            if status == "Ready":

                title = "🟢 READY"

                description = (
                    "System is ready for the next "
                    "precision spraying operation."
                )

            elif status == "Spraying...":

                title = "🟠 SPRAYING"

                description = (
                    "Precision spraying operation "
                    "is currently in progress."
                )

            elif status == "Completed":

                title = "🔵 COMPLETED"

                description = (
                    "The precision spraying operation "
                    "has been completed."
                )

            else:

                title = f"● {status.upper()}"

                description = (
                    "Current sprayer system status."
                )


            st.markdown(
                f"""
                <div class="status-box">

                    <div class="status-title">
                        {title}
                    </div>

                    <div class="status-description">
                        {description}
                    </div>

                    <div class="status-divider"></div>

                    <div class="status-stat-label">
                        Total Dispensed
                    </div>

                    <div class="status-stat-value">
                        {amount:.1f} ml
                    </div>

                    <div style="height:9px;"></div>

                    <div class="status-stat-label">
                        Last Updated
                    </div>

                    <div class="status-stat-value"
                         style="color:#36443d;">
                        {datetime.now().strftime("%I:%M:%S %p")}
                    </div>

                    <div class="status-divider"></div>

                    <div style="
                        display:flex;
                        align-items:center;
                        gap:12px;
                    ">

                        <div class="health-circle">
                            100%
                        </div>

                        <div>
                            <div style="
                                color:#68736e;
                                font-size:10px;
                            ">
                                All Systems
                            </div>

                            <div style="
                                color:#14743b;
                                font-size:11px;
                                font-weight:800;
                            ">
                                Operational
                            </div>
                        </div>

                    </div>

                </div>
                """,
                unsafe_allow_html=True
            )


        live_status()


# ============================================================
# WORKFLOW
# ============================================================

st.write("")

st.markdown(
    '<div class="section-heading">CropIQ Workflow</div>',
    unsafe_allow_html=True
)


workflow1, workflow2, workflow3, workflow4 = st.columns(
    4,
    gap="medium"
)


# ------------------------------------------------------------
# WORKFLOW 1
# ------------------------------------------------------------

with workflow1:

    with st.container(border=True):

        st.markdown(
            """
            <div class="workflow-number">
                01
            </div>

            <br>

            <div class="workflow-title">
                📷 Capture
            </div>

            <div class="workflow-description">
                Capture the latest plant image
                using the Raspberry Pi camera.
            </div>
            """,
            unsafe_allow_html=True
        )


# ------------------------------------------------------------
# WORKFLOW 2
# ------------------------------------------------------------

with workflow2:

    with st.container(border=True):

        st.markdown(
            """
            <div class="workflow-number">
                02
            </div>

            <br>

            <div class="workflow-title">
                🌿 Analyze
            </div>

            <div class="workflow-description">
                Analyze the captured plant image
                to identify the target.
            </div>
            """,
            unsafe_allow_html=True
        )


# ------------------------------------------------------------
# WORKFLOW 3
# ------------------------------------------------------------

with workflow3:

    with st.container(border=True):

        st.markdown(
            """
            <div class="workflow-number">
                03
            </div>

            <br>

            <div class="workflow-title">
                🎯 Target
            </div>

            <div class="workflow-description">
                Determine the treatment area
                and required spray quantity.
            </div>
            """,
            unsafe_allow_html=True
        )


# ------------------------------------------------------------
# WORKFLOW 4
# ------------------------------------------------------------

with workflow4:

    with st.container(border=True):

        st.markdown(
            """
            <div class="workflow-number">
                04
            </div>

            <br>

            <div class="workflow-title">
                🚿 Spray
            </div>

            <div class="workflow-description">
                Apply the selected spray dosage
                to the target.
            </div>
            """,
            unsafe_allow_html=True
        )


# ============================================================
# ROVER CONTROL
# ============================================================

st.write("")

st.markdown(
    '<div class="section-heading">🚜 Rover Control</div>',
    unsafe_allow_html=True
)


with st.container(border=True):

    rover_head1, rover_head2 = st.columns(
        [4, 1],
        vertical_alignment="center"
    )

    with rover_head1:

        st.markdown(
            """
            <div class="card-title">
                Rover Movement
            </div>

            <div class="card-description">
                Control rover movement using the ESP32.
                Adjust speed and use the directional controls.
            </div>
            """,
            unsafe_allow_html=True
        )

    with rover_head2:

        if esp32_online:

            st.markdown(
                """
                <div class="rover-status">
                    🟢 ESP32 ONLINE
                </div>
                """,
                unsafe_allow_html=True
            )

        else:

            st.markdown(
                """
                <div class="rover-status"
                     style="
                     background:#fff5f5;
                     border-color:#efcccc;
                     color:#bd3838;
                     ">
                    🔴 ESP32 OFFLINE
                </div>
                """,
                unsafe_allow_html=True
            )


    st.divider()


    rover_speed = st.slider(
        "Rover Speed",
        min_value=0,
        max_value=100,
        value=50,
        step=5
    )


    st.markdown(
        """
        <div style="
            text-align:center;
            color:#6d7973;
            font-size:11px;
            margin-bottom:7px;
        ">
            Directional Controls
        </div>
        """,
        unsafe_allow_html=True
    )


    # --------------------------------------------------------
    # FORWARD
    # --------------------------------------------------------

    r1, r2, r3 = st.columns(3)

    with r2:

        if st.button(
            "⬆️ FORWARD",
            use_container_width=True
        ):

            response = send_rover_command(
                "F",
                rover_speed
            )

            if response is not None:

                if response.status_code != 200:

                    st.error(
                        get_error_message(response)
                    )


    # --------------------------------------------------------
    # LEFT STOP RIGHT
    # --------------------------------------------------------

    r1, r2, r3 = st.columns(3)

    with r1:

        if st.button(
            "⬅️ LEFT",
            use_container_width=True
        ):

            response = send_rover_command(
                "L",
                rover_speed
            )

            if response is not None:

                if response.status_code != 200:

                    st.error(
                        get_error_message(response)
                    )


    with r2:

        if st.button(
            "⛔ STOP",
            use_container_width=True
        ):

            response = send_rover_command(
                "S",
                rover_speed
            )

            if response is not None:

                if response.status_code == 200:

                    st.success(
                        "Rover stopped."
                    )

                else:

                    st.error(
                        get_error_message(response)
                    )


    with r3:

        if st.button(
            "➡️ RIGHT",
            use_container_width=True
        ):

            response = send_rover_command(
                "R",
                rover_speed
            )

            if response is not None:

                if response.status_code != 200:

                    st.error(
                        get_error_message(response)
                    )


    # --------------------------------------------------------
    # BACKWARD
    # --------------------------------------------------------

    r1, r2, r3 = st.columns(3)

    with r2:

        if st.button(
            "⬇️ BACKWARD",
            use_container_width=True
        ):

            response = send_rover_command(
                "B",
                rover_speed
            )

            if response is not None:

                if response.status_code != 200:

                    st.error(
                        get_error_message(response)
                    )


# ============================================================
# ROVER LIVE STATUS
# ============================================================

@st.fragment(run_every="2s")
def rover_live_status():

    current_state = get_state()

    if current_state is None:
        return

    esp = current_state.get(
        "esp32",
        {}
    )

    online = esp.get(
        "online",
        False
    )

    status = esp.get(
        "rover_status",
        "UNKNOWN"
    )

    speed = esp.get(
        "speed",
        50
    )

    col1, col2, col3 = st.columns(3)

    with col1:

        if online:

            st.success(
                "🟢 ESP32 ONLINE"
            )

        else:

            st.error(
                "🔴 ESP32 OFFLINE"
            )

    with col2:

        st.info(
            f"🚜 Rover: **{status}**"
        )

    with col3:

        st.info(
            f"⚡ Speed: **{speed}%**"
        )


rover_live_status()


# ============================================================
# FOOTER
# ============================================================

st.write("")

st.markdown(
    """
    <div class="footer">

        © 2026 CropIQ
        &nbsp;&nbsp;•&nbsp;&nbsp;
        Precision Agriculture
        &nbsp;&nbsp;•&nbsp;&nbsp;
        AI-powered targeted spraying

    </div>
    """,
    unsafe_allow_html=True
)
