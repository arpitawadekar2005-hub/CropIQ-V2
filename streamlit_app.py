import streamlit as st
import requests
import time
import base64
from io import BytesIO
from PIL import Image
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
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================
# HELPER FUNCTIONS
# ============================================================

def base64_to_image(b64_string):
    """Convert a base64 string back into a PIL Image for Streamlit display."""
    try:
        if "," in b64_string:
            b64_string = b64_string.split(",")[1]
        img_bytes = base64.b64decode(b64_string)
        return Image.open(BytesIO(img_bytes))
    except Exception:
        return None

# ============================================================
# CSS & STYLING
# ============================================================

st.html("""
<style>

html, body {
    font-family: 'Inter', system-ui, -apple-system, sans-serif;
}

#MainMenu, footer {
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

/* SIDEBAR STYLING */
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

.sidebar-brand { text-align: center; padding: 5px 5px 20px 5px; }
.sidebar-logo { font-size: 50px; line-height: 1; }
.sidebar-name { color: white; font-size: 34px; font-weight: 850; letter-spacing: -1px; margin-top: 5px; }
.sidebar-tagline { color: #bddbd2; font-size: 13px; line-height: 1.5; margin-top: 8px; }

section[data-testid="stSidebar"] div[role="radiogroup"] { gap: 6px; }
section[data-testid="stSidebar"] div[role="radiogroup"] > label {
    border-radius: 13px !important; padding: 12px !important; background: transparent !important;
    border: 1px solid transparent !important; transition: 0.2s;
}
section[data-testid="stSidebar"] div[role="radiogroup"] > label:hover { background: rgba(255,255,255,0.08) !important; }
section[data-testid="stSidebar"] div[role="radiogroup"] > label[data-checked="true"],
section[data-testid="stSidebar"] div[role="radiogroup"] > label[aria-checked="true"] {
    background: linear-gradient(90deg, #109b53, #087c41) !important;
    box-shadow: 0 7px 18px rgba(0,0,0,0.20);
}
section[data-testid="stSidebar"] div[role="radiogroup"] > label > div:first-child { display: none !important; }

.sidebar-system { margin-top: 25px; padding: 17px; border-radius: 17px; background: rgba(0,0,0,0.14); border: 1px solid rgba(123,221,169,0.30); }
.sidebar-system-title { color: #c6ded7; font-size: 11px; }
.sidebar-online { color: #5fe68d; font-size: 17px; font-weight: 800; margin-top: 4px; }
.sidebar-status { color: #a8c8c0; font-size: 11px; margin-top: 13px; }
.sidebar-status-value { color: white; font-size: 13px; font-weight: 700; margin-top: 3px; }

/* TOP HEADER */
.top-header { background: rgba(255,255,255,0.96); border: 1px solid #dfe8e3; border-radius: 19px; padding: 17px 22px; min-height: 75px; box-shadow: 0 7px 25px rgba(20,65,45,0.07); }
.header-brand { display: flex; align-items: center; gap: 12px; }
.header-logo { font-size: 38px; }
.header-name { color: #063d31; font-size: 28px; font-weight: 850; }
.header-subtitle { color: #75817c; font-size: 12px; margin-top: 4px; }
.header-right { text-align: right; }
.online-pill { display: inline-block; padding: 8px 14px; border-radius: 22px; background: #effaf3; border: 1px solid #bfe2ca; color: #087b3e; font-size: 11px; font-weight: 800; }
.online-dot { display: inline-block; width: 8px; height: 8px; border-radius: 50%; background: #20aa58; margin-right: 5px; }
.header-date { color: #738079; font-size: 11px; margin-top: 7px; }

/* HERO PANEL */
.hero { position: relative; overflow: hidden; background: linear-gradient(135deg, #edf8ef, #ffffff); border: 1px solid #dce9e1; border-radius: 21px; padding: 23px 27px; margin-top: 17px; margin-bottom: 18px; box-shadow: 0 7px 24px rgba(25,70,50,0.055); }
.hero-title { color: #043d31; font-size: 28px; font-weight: 850; letter-spacing: -0.5px; }
.hero-green { color: #078845; }
.hero-subtitle { color: #6c7a73; font-size: 13px; margin-top: 6px; }

/* CARDS & PANELS */
.panel { background: white; border: 1px solid #dfe8e3; border-radius: 18px; padding: 17px; box-shadow: 0 6px 20px rgba(25,70,48,0.055); margin-bottom: 15px; }
.panel-heading { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
.panel-title { color: #063d31; font-size: 17px; font-weight: 800; }
.live-badge { background: #eafaf0; border: 1px solid #a2e0b6; color: #087d3f; font-size: 11px; font-weight: 800; padding: 4px 10px; border-radius: 12px; }

/* ROVER CONTROL CARD */
.rover-card {
    background: white;
    border: 1px solid #dfe8e3;
    border-radius: 18px;
    padding: 20px;
    box-shadow: 0 6px 20px rgba(25,70,48,0.055);
    margin-bottom: 15px;
}
.rover-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; }
.rover-title { color: #063d31; font-size: 18px; font-weight: 850; }
.status-pill { padding: 4px 12px; border-radius: 12px; font-size: 11px; font-weight: 800; }
.status-pill.offline { background: #fde8e8; border: 1px solid #f8b4b4; color: #9b1c1c; }
.status-pill.online { background: #eafaf0; border: 1px solid #a2e0b6; color: #087d3f; }

/* BUTTON STYLING OVERRIDES */
div.stButton > button {
    border-radius: 12px !important;
    font-weight: 700 !important;
    height: 48px !important;
    transition: all 0.2s ease !important;
    border: 1px solid #109b53 !important;
    background: #ffffff !important;
    color: #063d31 !important;
}
div.stButton > button:hover {
    background: #edf8ef !important;
    border-color: #087c41 !important;
    color: #087c41 !important;
    transform: translateY(-1px);
}
div.stButton > button[kind="primary"] {
    background: linear-gradient(90deg, #109b53, #087c41) !important;
    color: white !important;
    border: none !important;
    box-shadow: 0 4px 14px rgba(16,155,83,0.25) !important;
}
div.stButton > button[kind="primary"]:hover {
    background: linear-gradient(90deg, #0d8848, #066635) !important;
    box-shadow: 0 6px 18px rgba(16,155,83,0.35) !important;
}

/* CONSOLIDATED PLANT ANALYSIS CARD */
.plant-analysis-card {
    background: white;
    border: 1px solid #d8ebd9;
    border-radius: 18px;
    padding: 24px;
    box-shadow: 0 6px 20px rgba(25,70,48,0.05);
    margin-bottom: 15px;
}
.plant-analysis-header { color: #073e33; font-size: 15px; font-weight: 850; letter-spacing: 0.5px; margin-bottom: 4px; }
.plant-analysis-subheader { font-size: 22px; font-weight: 900; margin-bottom: 16px; border-bottom: 1px dashed #c3e2cb; padding-bottom: 10px; }
.analysis-row { display: flex; justify-content: space-between; align-items: center; padding: 7px 0; font-size: 15px; border-bottom: 1px solid #f2f7f4; }
.analysis-label { color: #5d6d66; font-weight: 600; }
.analysis-value { color: #052e25; font-weight: 800; }
.dosage-box { margin-top: 18px; background: linear-gradient(135deg, #eefaf2, #f5fcf7); border: 1px solid #bee5c8; border-radius: 12px; padding: 14px 18px; display: flex; justify-content: space-between; align-items: center; }
.dosage-label { color: #087d3f; font-size: 13px; font-weight: 850; letter-spacing: 0.5px; }
.dosage-value { color: #055e2e; font-size: 24px; font-weight: 900; }

</style>
""")

# ============================================================
# BACKEND FUNCTIONS
# ============================================================

def get_state():
    try:
        response = requests.get(BACKEND_URL + "/state", timeout=REQUEST_TIMEOUT)
        if response.status_code == 200:
            return response.json()
    except Exception:
        pass
    return None

def send_capture():
    try:
        return requests.post(BACKEND_URL + "/capture", timeout=REQUEST_TIMEOUT)
    except Exception as e:
        st.error(f"Backend connection error: {e}")
        return None

def send_spray(amount_ml):
    try:
        return requests.post(BACKEND_URL + "/spray", json={"amount_ml": amount_ml}, timeout=REQUEST_TIMEOUT)
    except Exception as e:
        st.error(f"Backend connection error: {e}")
        return None

def send_rover_command(command, speed):
    try:
        return requests.post(BACKEND_URL + "/rover", json={"command": command, "speed": speed}, timeout=REQUEST_TIMEOUT)
    except Exception as e:
        st.error(f"Backend connection error: {e}")
        return None

def get_latest_image():
    try:
        response = requests.get(BACKEND_URL + "/latest-image", timeout=REQUEST_TIMEOUT)
        if response.status_code == 200:
            return response.content
    except Exception:
        pass
    return None

def predict_manual_image(uploaded_file):
    try:
        image_bytes = uploaded_file.getvalue()
        files = {
            "file": (
                uploaded_file.name,
                image_bytes,
                uploaded_file.type or "image/jpeg"
            )
        }
        response = requests.post(BACKEND_URL + "/predict-manual", files=files, timeout=30)
        return response
    except Exception as e:
        st.error(f"Prediction error: {e}")
    return None

# ============================================================
# AUTO-REFRESH MECHANISM
# ============================================================

if "last_refresh" not in st.session_state:
    st.session_state["last_refresh"] = time.time()

# Check and update background state
state = get_state()

if state:
    raspberry = state.get("raspberry_pi", {})
    esp32 = state.get("esp32", {})

    spray_status = raspberry.get("spray_status", state.get("status", "READY"))
    sprayed_amount = raspberry.get("sprayed_amount", state.get("sprayed_amount", 0.0))
    raspberry_online = raspberry.get("online", False)
    esp32_online = esp32.get("online", False)
    rover_status = esp32.get("rover_status", "STOPPED")
    current_speed = esp32.get("speed", 50)

    # Sync live state from backend unless a manual file is actively uploaded
    if "uploaded_image_bytes" not in st.session_state:
        st.session_state["active_crop"] = raspberry.get("crop", "Guava")
        st.session_state["active_disease"] = raspberry.get("ai_prediction", "Guava fruit fly").replace("_", " ")
        st.session_state["active_confidence"] = float(raspberry.get("ai_confidence", 89.32) or 89.32)
        st.session_state["active_severity"] = float(raspberry.get("disease_area_percentage", 39.24) or 39.24)
        st.session_state["active_pesticide"] = raspberry.get("pesticide_name", "Copper oxychloride")
        st.session_state["active_dosage"] = float(raspberry.get("recommended_dosage_ml", 11.51) or 11.51)
else:
    spray_status = "OFFLINE"
    sprayed_amount = 0.0
    raspberry_online = False
    esp32_online = False
    rover_status = "STOPPED"
    current_speed = 50

    if "active_crop" not in st.session_state:
        st.session_state["active_crop"] = "Guava"
    if "active_disease" not in st.session_state:
        st.session_state["active_disease"] = "Guava fruit fly"
    if "active_confidence" not in st.session_state:
        st.session_state["active_confidence"] = 89.32
    if "active_severity" not in st.session_state:
        st.session_state["active_severity"] = 39.24
    if "active_pesticide" not in st.session_state:
        st.session_state["active_pesticide"] = "Copper oxychloride"
    if "active_dosage" not in st.session_state:
        st.session_state["active_dosage"] = 11.51

# Consolidated Plant Analysis Component
def render_plant_analysis():
    active_disease = st.session_state.get("active_disease") or ""
    is_healthy = "healthy" in active_disease.lower()
    
    display_disease = "Healthy" if is_healthy else st.session_state["active_disease"]
    display_header = "HEALTHY PLANT DETECTED" if is_healthy else "DISEASE DETECTED"
    header_color = "#087d3f" if is_healthy else "#d13b35"
    display_severity = 0.00 if is_healthy else st.session_state["active_severity"]
    display_pesticide = "None" if is_healthy else st.session_state["active_pesticide"]

    st.html(f"""
    <div class="plant-analysis-card">
        <div class="plant-analysis-header">PLANT ANALYSIS</div>
        <div class="plant-analysis-subheader" style="color: {header_color};">{display_header}</div>
        <div class="analysis-row">
            <span class="analysis-label">Crop:</span>
            <span class="analysis-value">{st.session_state["active_crop"]}</span>
        </div>
        <div class="analysis-row">
            <span class="analysis-label">Disease:</span>
            <span class="analysis-value">{display_disease}</span>
        </div>
        <div class="analysis-row">
            <span class="analysis-label">Confidence:</span>
            <span class="analysis-value">{st.session_state["active_confidence"]:.2f}%</span>
        </div>
        <div class="analysis-row">
            <span class="analysis-label">Severity:</span>
            <span class="analysis-value">{display_severity:.2f}%</span>
        </div>
        <div class="analysis-row">
            <span class="analysis-label">Pesticide:</span>
            <span class="analysis-value">{display_pesticide}</span>
        </div>
        <div class="dosage-box">
            <span class="dosage-label">RECOMMENDED DOSAGE:</span>
            <span class="dosage-value">{st.session_state["active_dosage"]:.2f} ml</span>
        </div>
    </div>
    """)

# Rover Controller Component
def render_rover_controls(key_prefix="dash"):
    pill_class = "online" if esp32_online else "offline"
    pill_text = "ESP32 ONLINE" if esp32_online else "ESP32 OFFLINE"

    st.html(f"""
    <div class="rover-card">
        <div class="rover-header">
            <div class="rover-title">🚜 Rover Control</div>
            <div class="status-pill {pill_class}">● {pill_text}</div>
        </div>
        <div style="font-size:12px; color:#5d6d66; margin-bottom:8px;">Rover Status: <b>{rover_status}</b></div>
    </div>
    """)

    speed = st.slider("Rover Speed", 0, 100, int(current_speed), 5, key=f"{key_prefix}_speed")

    c1, c2, c3 = st.columns([1, 1, 1])
    with c2:
        if st.button("⬆️ FORWARD", use_container_width=True, key=f"{key_prefix}_fwd"):
            send_rover_command("F", speed)

    c1, c2, c3 = st.columns([1, 1, 1])
    with c1:
        if st.button("⬅️ LEFT", use_container_width=True, key=f"{key_prefix}_left"):
            send_rover_command("L", speed)
    with c2:
        if st.button("⏹️ STOP", type="primary", use_container_width=True, key=f"{key_prefix}_stop"):
            send_rover_command("S", speed)
    with c3:
        if st.button("➡ RIGHT", use_container_width=True, key=f"{key_prefix}_right"):
            send_rover_command("R", speed)

    c1, c2, c3 = st.columns([1, 1, 1])
    with c2:
        if st.button("⬇️ BACKWARD", use_container_width=True, key=f"{key_prefix}_back"):
            send_rover_command("B", speed)

# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:
    st.html("""
    <div class="sidebar-brand">
        <div class="sidebar-logo">🌿</div>
        <div class="sidebar-name">CropIQ</div>
        <div class="sidebar-tagline">Precision Farming<br>for a Greener Tomorrow</div>
    </div>
    """)

    page = st.radio(
        "Navigation",
        ["🏠 Dashboard", "📷 Live View", "🚜 Rover Control", "💧 Sprayer Control", "🌿 AI Detection", "⚙️ Settings"],
        label_visibility="collapsed"
    )

    status_text = "● ONLINE" if raspberry_online else "● OFFLINE"
    status_color = "#63e995" if raspberry_online else "#ff7169"

    st.html(f"""
    <div class="sidebar-system">
        <div class="sidebar-system-title">🍓 Raspberry Pi</div>
        <div class="sidebar-online" style="color:{status_color};">{status_text}</div>
        <div class="sidebar-status">System Status</div>
        <div class="sidebar-status-value">{"Operational" if raspberry_online else "Disconnected"}</div>
    </div>
    """)

# ============================================================
# HEADER
# ============================================================

header_left, header_right = st.columns([3, 2])

with header_left:
    st.html("""
    <div class="top-header">
        <div class="header-brand">
            <div class="header-logo">🌿</div>
            <div>
                <div class="header-name">CropIQ</div>
                <div class="header-subtitle">Precision Agriculture Intelligence Platform</div>
            </div>
        </div>
    </div>
    """)

with header_right:
    system_color = "#20aa58" if state else "#d13b35"
    system_text = "SYSTEM ONLINE" if state else "SYSTEM OFFLINE"
    current_time = datetime.now().strftime("%d %b %Y • %I:%M:%S %p")

    st.html(f"""
    <div class="top-header">
        <div class="header-right">
            <div class="online-pill"><span class="online-dot" style="background:{system_color};"></span>{system_text}</div>
            <div class="header-date">{current_time}</div>
        </div>
    </div>
    """)

# ============================================================
# DASHBOARD PAGE
# ============================================================

if page == "🏠 Dashboard":

    st.html("""
    <div class="hero">
        <div class="hero-title">🌿 Precision <span class="hero-green">Spraying & Rover Control</span></div>
        <div class="hero-subtitle">Monitor camera stream, control rover movement, and trigger precision pesticide dosage.</div>
    </div>
    """)

    col_left, col_mid, col_right = st.columns([1.1, 1.0, 0.9])

    with col_left:
        st.html("""
        <div class="panel">
            <div class="panel-heading">
                <div class="panel-title">📷 Live Camera Feed</div>
                <div class="live-badge">● LIVE</div>
            </div>
        </div>
        """)

        if "uploaded_image_bytes" in st.session_state:
            st.image(st.session_state["uploaded_image_bytes"], use_container_width=True)
        else:
            current_image = get_latest_image()
            if current_image:
                st.image(current_image, use_container_width=True)
            else:
                st.info("No camera image available.")

        if st.button("📸 CAPTURE PLANT IMAGE", type="primary", use_container_width=True, key="dashboard_capture"):
            if "uploaded_image_bytes" in st.session_state:
                del st.session_state["uploaded_image_bytes"]
            response = send_capture()
            if response and response.status_code == 200:
                st.info("📸 Capturing new image...")
                time.sleep(1)
                st.rerun()

    with col_mid:
        render_rover_controls(key_prefix="dashboard_rover")

    with col_right:
        render_plant_analysis()

        st.html("""
        <div class="panel">
            <div class="panel-heading">
                <div class="panel-title">💧 Precision Sprayer</div>
            </div>
        </div>
        """)

        dosage = st.number_input(
            "Spray dosage (ml)",
            min_value=0.0,
            max_value=5000.0,
            value=float(st.session_state.get("active_dosage", 11.51)),
            step=1.0,
            key="dashboard_dosage"
        )

        if st.button("🚀 START PRECISION SPRAY", type="primary", use_container_width=True, key="dashboard_spray"):
            response = send_spray(dosage)
            if response and response.status_code == 200:
                st.success(f"Precision spraying triggered: {dosage:.2f} ml")

# ============================================================
# ROVER CONTROL PAGE
# ============================================================

elif page == "🚜 Rover Control":

    st.html("""
    <div class="hero">
        <div class="hero-title">🚜 Manual <span class="hero-green">Rover Control</span></div>
        <div class="hero-subtitle">Adjust rover movement speed and navigate field directions manually.</div>
    </div>
    """)

    rover_col, _ = st.columns([1.2, 0.8])
    with rover_col:
        render_rover_controls(key_prefix="standalone_rover")

# ============================================================
# AI DETECTION PAGE
# ============================================================

elif page == "🌿 AI Detection":

    st.html("""
    <div class="hero">
        <div class="hero-title">🌿 AI Plant <span class="hero-green">Detection & Analysis</span></div>
        <div class="hero-subtitle">Upload plant leaf images to execute AI diagnosis and automatically derive pesticide treatment dosages.</div>
    </div>
    """)

    upload_col, result_col = st.columns([1.1, 0.9])

    with upload_col:
        st.html("""
        <div class="panel">
            <div class="panel-title">📷 Upload Plant Image</div>
            <div class="panel-subtitle" style="font-size:12px; color:#5d6d66; margin-top:4px;">Select a leaf image to run AI analysis.</div>
        </div>
        """)

        uploaded_file = st.file_uploader("Choose an image", type=["jpg", "jpeg", "png"], key="ai_detection_upload")

        if uploaded_file is not None:
            image_bytes = uploaded_file.getvalue()
            st.image(image_bytes, caption="Uploaded Plant Image", use_container_width=True)

            if st.button("🔍 PROCESS AI INFERENCE", type="primary", use_container_width=True, key="ai_process_button"):
                st.session_state["uploaded_image_bytes"] = image_bytes

                with st.spinner("Processing plant diagnosis..."):
                    response = predict_manual_image(uploaded_file)

                if response and response.status_code == 200:
                    res = response.json()
                    st.session_state["active_crop"] = res.get("crop", "Guava")
                    st.session_state["active_disease"] = res.get("prediction", "Guava fruit fly").replace("_", " ")
                    st.session_state["active_confidence"] = float(res.get("confidence", 89.32))
                    st.session_state["active_severity"] = float(res.get("disease_area_percentage", 39.24))
                    st.session_state["active_pesticide"] = res.get("pesticide_name", "Copper oxychloride")
                    st.session_state["active_dosage"] = float(res.get("recommended_dosage_ml", 11.51))
                    st.success("✅ Analysis completed successfully!")
                    st.rerun()

    with result_col:
        render_plant_analysis()

# ============================================================
# LIVE VIEW PAGE
# ============================================================

elif page == "📷 Live View":

    st.html("""
    <div class="hero">
        <div class="hero-title">📷 Live <span class="hero-green">Camera Stream</span></div>
        <div class="hero-subtitle">High-resolution camera feed from Raspberry Pi sensor unit.</div>
    </div>
    """)

    if "uploaded_image_bytes" in st.session_state:
        st.image(st.session_state["uploaded_image_bytes"], use_container_width=True)
    else:
        current_image = get_latest_image()
        if current_image:
            st.image(current_image, use_container_width=True)
        else:
            st.info("No camera image available.")

    if st.button("📸 CAPTURE NEW IMAGE", type="primary", use_container_width=True, key="liveview_capture"):
        if "uploaded_image_bytes" in st.session_state:
            del st.session_state["uploaded_image_bytes"]
        send_capture()
        st.rerun()

# ============================================================
# SPRAYER CONTROL PAGE
# ============================================================

elif page == "💧 Sprayer Control":

    st.html("""
    <div class="hero">
        <div class="hero-title">💧 Precision <span class="hero-green">Sprayer Calibration</span></div>
        <div class="hero-subtitle">Configure pesticide liquid dosage and execute target spraying.</div>
    </div>
    """)

    spray_col, _ = st.columns([1.0, 1.0])
    with spray_col:
        dosage = st.number_input(
            "Spray dosage (ml)",
            min_value=0.0,
            max_value=5000.0,
            value=float(st.session_state.get("active_dosage", 11.51)),
            key="standalone_spray_dosage"
        )
        if st.button("🚀 START PRECISION SPRAY", type="primary", use_container_width=True, key="standalone_spray_btn"):
            send_spray(dosage)
            st.success(f"Dispensary activated for {dosage:.2f} ml.")

# ============================================================
# SETTINGS PAGE
# ============================================================

elif page == "⚙️ Settings":

    st.html("""
    <div class="hero">
        <div class="hero-title">⚙️ System <span class="hero-green">Settings</span></div>
        <div class="hero-subtitle">Configuration parameters and connected API endpoint metadata.</div>
    </div>
    """)

    st.subheader("Backend Service Endpoint")
    st.code(BACKEND_URL)

# Auto-refresh trigger every 4 seconds
if time.time() - st.session_state["last_refresh"] > 4:
    st.session_state["last_refresh"] = time.time()
    st.rerun()
