import hashlib
import time
from datetime import datetime

import requests
import streamlit as st

# ============================================================
# CONFIGURATION
# ============================================================

BACKEND_URL = "https://cropiq-backend-mecl.onrender.com"
REQUEST_TIMEOUT = 15
CAPTURE_WAIT_SECONDS = 20

st.set_page_config(
    page_title="CropIQ | Precision Agriculture",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================
# CSS
# ============================================================

st.html(
    """
    <style>
    html, body {
        font-family: Inter, system-ui, -apple-system, BlinkMacSystemFont, sans-serif;
    }

    #MainMenu, footer { visibility: hidden; }
    header { background: transparent !important; }

    .stApp {
        background:
            radial-gradient(circle at 15% 10%, rgba(76,175,105,.08), transparent 28%),
            linear-gradient(135deg, #eef5f1 0%, #f8fbf9 55%, #edf4f0 100%);
    }

    .main .block-container {
        max-width: 1550px;
        padding: 1rem 1.5rem 2rem 1.5rem;
    }

    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #003d31 0%, #004e3e 50%, #002d25 100%);
        min-width: 285px;
        max-width: 285px;
    }

    section[data-testid="stSidebar"] > div { background: transparent; }
    section[data-testid="stSidebar"] .block-container { padding: 1.3rem .9rem; }
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] span,
    section[data-testid="stSidebar"] label { color: white !important; }

    section[data-testid="stSidebar"] div[role="radiogroup"] { gap: 6px; }
    section[data-testid="stSidebar"] div[role="radiogroup"] > label {
        border-radius: 13px !important;
        padding: 12px !important;
        background: transparent !important;
        border: 1px solid transparent !important;
    }
    section[data-testid="stSidebar"] div[role="radiogroup"] > label:hover {
        background: rgba(255,255,255,.08) !important;
    }
    section[data-testid="stSidebar"] div[role="radiogroup"] > label[data-checked="true"],
    section[data-testid="stSidebar"] div[role="radiogroup"] > label[aria-checked="true"] {
        background: linear-gradient(90deg, #109b53, #087c41) !important;
    }
    section[data-testid="stSidebar"] div[role="radiogroup"] > label > div:first-child {
        display: none !important;
    }

    .sidebar-brand { text-align: center; padding: 5px 5px 20px; }
    .sidebar-logo { font-size: 50px; line-height: 1; }
    .sidebar-name { color: white; font-size: 34px; font-weight: 850; margin-top: 5px; }
    .sidebar-tagline { color: #bddbd2; font-size: 13px; line-height: 1.5; margin-top: 8px; }

    .sidebar-system {
        margin-top: 25px;
        padding: 17px;
        border-radius: 17px;
        background: rgba(0,0,0,.14);
        border: 1px solid rgba(123,221,169,.30);
    }
    .sidebar-system-title { color: #c6ded7; font-size: 11px; }
    .sidebar-online { font-size: 17px; font-weight: 800; margin-top: 4px; }
    .sidebar-status { color: #a8c8c0; font-size: 11px; margin-top: 13px; }
    .sidebar-status-value { color: white; font-size: 13px; font-weight: 700; margin-top: 3px; }

    .hero {
        background: linear-gradient(135deg, #edf8ef, #ffffff);
        border: 1px solid #dce9e1;
        border-radius: 21px;
        padding: 23px 27px;
        margin: 17px 0 18px;
    }
    .hero-title { color: #043d31; font-size: 28px; font-weight: 850; }
    .hero-green { color: #078845; }
    .hero-subtitle { color: #6c7a73; font-size: 13px; margin-top: 6px; }

    .panel {
        background: white;
        border: 1px solid #dfe8e3;
        border-radius: 18px;
        padding: 18px;
        box-shadow: 0 6px 20px rgba(25,70,48,.055);
        margin-bottom: 15px;
    }
    .panel-title { color: #063d31; font-size: 18px; font-weight: 850; }
    .muted { color: #6c7a73; font-size: 12px; }

    .result-card {
        background: #ffffff;
        border: 2px solid #bfe5c9;
        border-radius: 20px;
        padding: 24px;
        box-shadow: 0 8px 24px rgba(25,70,48,.08);
        margin: 8px 0 18px;
    }
    .result-title {
        color: #073e33;
        font-size: 17px;
        font-weight: 900;
        letter-spacing: .5px;
    }
    .result-status {
        font-size: 27px;
        font-weight: 950;
        margin: 5px 0 16px;
    }
    .result-row {
        display: flex;
        justify-content: space-between;
        gap: 18px;
        padding: 8px 0;
        border-bottom: 1px solid #edf3ef;
        font-size: 15px;
    }
    .result-label { color: #617069; font-weight: 650; }
    .result-value { color: #062f26; font-weight: 850; text-align: right; }
    .dose-box {
        margin-top: 18px;
        border: 1px solid #9fdab0;
        border-radius: 14px;
        padding: 16px 18px;
        background: linear-gradient(135deg, #edf9f1, #f7fcf8);
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 12px;
    }
    .dose-label { color: #087d3f; font-size: 13px; font-weight: 900; }
    .dose-value { color: #055e2e; font-size: 27px; font-weight: 950; }

    .pending-card {
        background: #fffdf6;
        border: 1px solid #ead7a6;
        border-radius: 18px;
        padding: 20px;
        margin: 8px 0 18px;
    }
    .pending-title { color: #7b5b08; font-size: 21px; font-weight: 900; }

    div.stButton > button {
        border-radius: 12px !important;
        font-weight: 750 !important;
        min-height: 46px !important;
        border: 1px solid #109b53 !important;
        background: #ffffff !important;
        color: #063d31 !important;
    }
    div.stButton > button:hover {
        background: #edf8ef !important;
        border-color: #087c41 !important;
        color: #087c41 !important;
    }
    div.stButton > button[kind="primary"] {
        background: linear-gradient(90deg, #109b53, #087c41) !important;
        color: white !important;
        border: none !important;
    }

    .workflow-step {
        text-align: center;
        background: white;
        border: 1px solid #dfe8e3;
        border-radius: 16px;
        padding: 18px 12px;
        height: 100%;
    }
    .step-number {
        width: 38px;
        height: 38px;
        margin: 0 auto 8px;
        border-radius: 50%;
        background: #eef9f0;
        border: 1px solid #c9e9ce;
        display: flex;
        align-items: center;
        justify-content: center;
        color: #087d3f;
        font-weight: 900;
    }
    .step-title { color: #073e33; font-weight: 850; }
    .step-text { color: #6c7a73; font-size: 11px; margin-top: 5px; }
    </style>
    """
)

# ============================================================
# BACKEND HELPERS
# ============================================================

def api_get(path, timeout=REQUEST_TIMEOUT):
    try:
        response = requests.get(f"{BACKEND_URL}{path}", timeout=timeout)
        response.raise_for_status()
        return response
    except requests.RequestException:
        return None


def get_state():
    response = api_get("/state")
    if response is None:
        return None
    try:
        return response.json()
    except ValueError:
        return None


def post_json(path, payload=None, timeout=REQUEST_TIMEOUT):
    try:
        response = requests.post(
            f"{BACKEND_URL}{path}",
            json=payload or {},
            timeout=timeout,
        )
        return response
    except requests.RequestException as exc:
        st.error(f"Backend connection error: {exc}")
        return None


def capture_image():
    return post_json("/capture")


def predict_latest():
    return post_json("/predict-latest", timeout=60)


def send_spray(amount_ml):
    return post_json("/spray", {"amount_ml": float(amount_ml)})


def send_rover_command(command, speed):
    return post_json("/rover", {"command": command, "speed": int(speed)})


def get_latest_image():
    response = api_get("/latest-image", timeout=20)
    return response.content if response is not None else None


def upload_manual_image(uploaded_file):
    try:
        files = {
            "file": (
                uploaded_file.name,
                uploaded_file.getvalue(),
                uploaded_file.type or "image/jpeg",
            )
        }
        response = requests.post(
            f"{BACKEND_URL}/upload-image",
            files=files,
            data={"source": "manual"},
            timeout=30,
        )
        return response
    except requests.RequestException as exc:
        st.error(f"Image upload error: {exc}")
        return None


def wait_for_new_image(previous_version, timeout_seconds=CAPTURE_WAIT_SECONDS):
    end_time = time.time() + timeout_seconds
    placeholder = st.empty()

    while time.time() < end_time:
        state_now = get_state()
        pi = (state_now or {}).get("raspberry_pi", {})
        current_version = int(pi.get("image_version", 0) or 0)

        if current_version > int(previous_version):
            placeholder.empty()
            image = get_latest_image()
            return image, state_now

        remaining = max(0, int(end_time - time.time()))
        placeholder.info(f"Waiting for Raspberry Pi to upload the new image... {remaining}s")
        time.sleep(1)

    placeholder.empty()
    return None, get_state()

# ============================================================
# RESULT DISPLAY
# ============================================================

def healthy_result(pi):
    prediction = str(pi.get("ai_prediction") or "").lower()
    disease = str(pi.get("disease") or "").lower()
    return bool(pi.get("healthy", False)) or "healthy" in prediction or disease == "healthy"


def render_ai_result(pi):
    prediction = pi.get("ai_prediction")
    confidence = float(pi.get("ai_confidence", 0) or 0)
    crop = pi.get("crop")
    disease = pi.get("disease")
    severity = float(pi.get("severity_percent", 0) or 0)
    pesticide = pi.get("pesticide")
    dosage = float(pi.get("recommended_dosage_ml", 0) or 0)
    analyzed = bool(pi.get("analysis_available", False)) or bool(prediction)

    if not analyzed:
        st.html(
            """
            <div class="pending-card">
                <div class="pending-title">🔍 AI PREDICTION PENDING</div>
                <div class="muted" style="font-size:14px;margin-top:7px;">
                    The image is uploaded and ready. Click <b>AI PREDICTION</b> to run the CropIQ AI pipeline.
                </div>
            </div>
            """
        )
        return

    is_healthy = healthy_result(pi)

    if is_healthy:
        st.html(
            f"""
            <div class="result-card">
                <div class="result-title">🌿 PLANT ANALYSIS</div>
                <div class="result-status" style="color:#087d3f;">HEALTHY</div>
                <div class="result-row"><span class="result-label">Crop:</span><span class="result-value">{crop or '—'}</span></div>
                <div class="result-row"><span class="result-label">Disease:</span><span class="result-value">Healthy</span></div>
                <div class="result-row"><span class="result-label">Confidence:</span><span class="result-value">{confidence:.2f}%</span></div>
                <div class="dose-box">
                    <span class="dose-label">TREATMENT</span>
                    <span class="dose-value">NO SPRAY REQUIRED</span>
                </div>
            </div>
            """
        )
        return

    st.html(
        f"""
        <div class="result-card" style="border-color:#e7c6c6;">
            <div class="result-title">🌿 PLANT ANALYSIS</div>
            <div class="result-status" style="color:#c33731;">DISEASE DETECTED</div>
            <div class="result-row"><span class="result-label">Crop:</span><span class="result-value">{crop or '—'}</span></div>
            <div class="result-row"><span class="result-label">Disease:</span><span class="result-value">{disease or prediction or '—'}</span></div>
            <div class="result-row"><span class="result-label">Confidence:</span><span class="result-value">{confidence:.2f}%</span></div>
            <div class="result-row"><span class="result-label">Severity:</span><span class="result-value">{severity:.2f}%</span></div>
            <div class="result-row"><span class="result-label">Pesticide:</span><span class="result-value">{pesticide or '—'}</span></div>
            <div class="dose-box">
                <span class="dose-label">RECOMMENDED DOSAGE</span>
                <span class="dose-value">{dosage:.2f} ml</span>
            </div>
        </div>
        """
    )


def render_sprayer_panel(pi, button_key):
    if not pi or not pi.get("analysis_available"):
        st.info("Run AI Prediction first. The AI-calculated dosage will appear here.")
        return

    if healthy_result(pi):
        st.success("Plant is healthy. No spraying is required.")
        return

    dosage = float(pi.get("recommended_dosage_ml", 0) or 0)
    crop = pi.get("crop") or "—"
    disease = pi.get("disease") or pi.get("ai_prediction") or "—"
    pesticide = pi.get("pesticide") or "—"
    severity = float(pi.get("severity_percent", 0) or 0)

    st.html(
        f"""
        <div class="panel">
            <div class="panel-title">💧 Precision Spray Target</div>
            <div class="result-row"><span class="result-label">Crop:</span><span class="result-value">{crop}</span></div>
            <div class="result-row"><span class="result-label">Disease:</span><span class="result-value">{disease}</span></div>
            <div class="result-row"><span class="result-label">Severity:</span><span class="result-value">{severity:.2f}%</span></div>
            <div class="result-row"><span class="result-label">Pesticide:</span><span class="result-value">{pesticide}</span></div>
            <div class="dose-box">
                <span class="dose-label">AI CALCULATED DOSAGE</span>
                <span class="dose-value">{dosage:.2f} ml</span>
            </div>
        </div>
        """
    )

    if dosage <= 0:
        st.warning("AI did not return a valid spray dosage.")
        return

    if st.button("🚀 START PRECISION SPRAY", type="primary", use_container_width=True, key=button_key):
        response = send_spray(dosage)
        if response and response.status_code == 200:
            st.success(f"Precision spray command sent to Raspberry Pi: {dosage:.2f} ml")
            st.rerun()
        elif response is not None:
            try:
                st.error(response.json().get("detail", response.text))
            except ValueError:
                st.error(response.text)

# ============================================================
# INITIAL BACKEND STATE
# ============================================================

state = get_state()
pi = (state or {}).get("raspberry_pi", {})
esp32 = (state or {}).get("esp32", {})

raspberry_online = bool(pi.get("online", False))
esp32_online = bool(esp32.get("online", False))
rover_status = esp32.get("rover_status", "STOPPED")
current_speed = int(esp32.get("speed", 50) or 50)

# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:
    st.html(
        """
        <div class="sidebar-brand">
            <div class="sidebar-logo">🌿</div>
            <div class="sidebar-name">CropIQ</div>
            <div class="sidebar-tagline">Precision Farming<br>for a Greener Tomorrow</div>
        </div>
        """
    )

    page = st.radio(
        "Navigation",
        [
            "🏠 Dashboard",
            "📷 Live View",
            "🚜 Rover Control",
            "💧 Sprayer Control",
            "🌿 AI Detection",
            "⚙️ Settings",
        ],
        label_visibility="collapsed",
    )

    status_color = "#63e995" if raspberry_online else "#ff7169"
    status_text = "● ONLINE" if raspberry_online else "● OFFLINE"

    st.html(
        f"""
        <div class="sidebar-system">
            <div class="sidebar-system-title">🍓 Raspberry Pi</div>
            <div class="sidebar-online" style="color:{status_color};">{status_text}</div>
            <div class="sidebar-status">System Status</div>
            <div class="sidebar-status-value">{"Operational" if raspberry_online else "Disconnected"}</div>
        </div>
        """
    )

# ============================================================
# TOP HEADER
# ============================================================

header_left, header_right = st.columns([3, 2])
with header_left:
    st.html(
        """
        <div class="panel">
            <div class="panel-title">🌿 CropIQ</div>
            <div class="muted">Precision Agriculture Intelligence Platform</div>
        </div>
        """
    )

with header_right:
    system_text = "SYSTEM ONLINE" if state else "BACKEND OFFLINE"
    st.html(
        f"""
        <div class="panel" style="text-align:right;">
            <div class="panel-title">{system_text}</div>
            <div class="muted">{datetime.now().strftime('%d %b %Y • %I:%M:%S %p')}</div>
        </div>
        """
    )

# ============================================================
# DASHBOARD
# ============================================================

if page == "🏠 Dashboard":
    st.html(
        """
        <div class="hero">
            <div class="hero-title">🌿 Precision <span class="hero-green">Spraying & Rover Control</span></div>
            <div class="hero-subtitle">Capture a new Raspberry Pi image, run AI prediction only when requested, review the result, and manually start precision spraying.</div>
        </div>
        """
    )

    left, right = st.columns([1.55, 1.0])

    with left:
        st.html('<div class="panel"><div class="panel-title">📷 Raspberry Pi Image</div><div class="muted">The latest captured image replaces the previous Raspberry Pi image automatically.</div></div>')

        latest_image = get_latest_image()
        if latest_image:
            st.image(latest_image, use_container_width=True)
        else:
            st.info("No Raspberry Pi image has been uploaded yet.")

        capture_col, predict_col = st.columns(2)

        with capture_col:
            if st.button("📸 CAPTURE NEW IMAGE", type="primary", use_container_width=True, key="dashboard_capture"):
                previous_version = int(pi.get("image_version", 0) or 0)
                response = capture_image()

                if response and response.status_code == 200:
                    st.session_state["capture_notice"] = "Capture command sent."
                    new_image, new_state = wait_for_new_image(previous_version)
                    if new_image is not None:
                        st.success("✅ New Raspberry Pi image uploaded. AI prediction is waiting for your click.")
                    else:
                        st.warning("Capture command was sent, but Raspberry Pi has not uploaded a new image yet. Make sure the Pi is running and polling /command.")
                    st.rerun()
                elif response is not None:
                    try:
                        st.error(response.json().get("detail", response.text))
                    except ValueError:
                        st.error(response.text)

        with predict_col:
            if st.button("🔍 AI PREDICTION", type="primary", use_container_width=True, key="dashboard_predict"):
                with st.spinner("Running CropIQ AI pipeline..."):
                    response = predict_latest()
                if response and response.status_code == 200:
                    st.session_state["last_prediction_source"] = pi.get("image_source")
                    st.success("✅ AI prediction completed.")
                    st.rerun()
                elif response is not None:
                    try:
                        st.error(response.json().get("detail", response.text))
                    except ValueError:
                        st.error(response.text)

    with right:
        st.html('<div class="panel"><div class="panel-title">🌿 AI Detection Result</div><div class="muted">One result for the currently stored image.</div></div>')
        render_ai_result(pi)
        render_sprayer_panel(pi, "dashboard_spray")

    st.subheader("CropIQ Workflow")
    steps = st.columns(4)
    workflow = [
        ("01", "📸", "Capture", "Raspberry Pi captures and uploads the newest image."),
        ("02", "🧠", "Predict", "You click AI Prediction; classification and segmentation run."),
        ("03", "🎯", "Calculate", "Severity, pesticide, and dosage are calculated."),
        ("04", "💧", "Spray", "You manually start the AI-recommended spray."),
    ]
    for col, (num, icon, title, desc) in zip(steps, workflow):
        with col:
            st.html(
                f"""
                <div class="workflow-step">
                    <div class="step-number">{num}</div>
                    <div style="font-size:24px;">{icon}</div>
                    <div class="step-title">{title}</div>
                    <div class="step-text">{desc}</div>
                </div>
                """
            )

# ============================================================
# LIVE VIEW
# ============================================================

elif page == "📷 Live View":
    st.html(
        """
        <div class="hero">
            <div class="hero-title">📷 Live <span class="hero-green">Raspberry Pi View</span></div>
            <div class="hero-subtitle">This page shows the newest image stored by the backend.</div>
        </div>
        """
    )

    latest_image = get_latest_image()
    if latest_image:
        st.image(latest_image, use_container_width=True)
    else:
        st.info("No image available.")

    c1, c2 = st.columns(2)
    with c1:
        if st.button("📸 CAPTURE NEW IMAGE", type="primary", use_container_width=True, key="live_capture"):
            previous_version = int(pi.get("image_version", 0) or 0)
            response = capture_image()
            if response and response.status_code == 200:
                new_image, _ = wait_for_new_image(previous_version)
                if new_image is not None:
                    st.success("New Raspberry Pi image uploaded.")
                else:
                    st.warning("The Pi has not uploaded a new image yet.")
                st.rerun()
    with c2:
        if st.button("🔍 AI PREDICTION", type="primary", use_container_width=True, key="live_predict"):
            response = predict_latest()
            if response and response.status_code == 200:
                st.success("AI prediction completed.")
                st.rerun()

    st.html('<div class="panel"><div class="panel-title">🌿 Current AI Result</div></div>')
    render_ai_result(pi)

# ============================================================
# ROVER CONTROL
# ============================================================

elif page == "🚜 Rover Control":
    st.html(
        """
        <div class="hero">
            <div class="hero-title">🚜 Manual <span class="hero-green">Rover Control</span></div>
            <div class="hero-subtitle">Control the ESP32 rover using the WebSocket connection inherited from the working backend.</div>
        </div>
        """
    )

    if not esp32_online:
        st.warning("ESP32 rover is offline.")
    else:
        st.success(f"ESP32 ONLINE • Rover status: {rover_status}")

    speed = st.slider("Rover Speed", 0, 100, current_speed, 5, key="standalone_speed")

    c1, c2, c3 = st.columns(3)
    with c2:
        if st.button("⬆️ FORWARD", use_container_width=True, key="rover_forward"):
            response = send_rover_command("F", speed)
            if response and response.status_code == 200:
                st.rerun()
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("⬅️ LEFT", use_container_width=True, key="rover_left"):
            response = send_rover_command("L", speed)
            if response and response.status_code == 200:
                st.rerun()
    with c2:
        if st.button("⏹️ STOP", type="primary", use_container_width=True, key="rover_stop"):
            response = send_rover_command("S", speed)
            if response and response.status_code == 200:
                st.rerun()
    with c3:
        if st.button("➡️ RIGHT", use_container_width=True, key="rover_right"):
            response = send_rover_command("R", speed)
            if response and response.status_code == 200:
                st.rerun()
    c1, c2, c3 = st.columns(3)
    with c2:
        if st.button("⬇️ BACKWARD", use_container_width=True, key="rover_backward"):
            response = send_rover_command("B", speed)
            if response and response.status_code == 200:
                st.rerun()

# ============================================================
# SPRAYER CONTROL
# ============================================================

elif page == "💧 Sprayer Control":
    st.html(
        """
        <div class="hero">
            <div class="hero-title">💧 Precision <span class="hero-green">Sprayer Control</span></div>
            <div class="hero-subtitle">The spray quantity is taken directly from the latest completed AI analysis. Spraying is always started manually.</div>
        </div>
        """
    )

    st.html('<div class="panel"><div class="panel-title">🌿 Current AI Analysis</div></div>')
    render_ai_result(pi)
    render_sprayer_panel(pi, "standalone_spray")

    spray_status = pi.get("spray_status", "Ready")
    sprayed_amount = float(pi.get("sprayed_amount", 0) or 0)
    st.html(
        f"""
        <div class="panel">
            <div class="panel-title">Sprayer Status</div>
            <div style="font-size:22px;font-weight:900;color:#087d3f;margin-top:8px;">{spray_status}</div>
            <div class="muted" style="margin-top:5px;">Last reported sprayed amount: {sprayed_amount:.2f} ml</div>
        </div>
        """
    )

# ============================================================
# AI DETECTION
# ============================================================

elif page == "🌿 AI Detection":
    st.html(
        """
        <div class="hero">
            <div class="hero-title">🌿 AI Plant <span class="hero-green">Detection & Analysis</span></div>
            <div class="hero-subtitle">Choose either the latest Raspberry Pi image or a manual image. Upload/capture first, then explicitly click AI Prediction.</div>
        </div>
        """
    )

    pi_col, manual_col = st.columns(2)

    with pi_col:
        st.html('<div class="panel"><div class="panel-title">🍓 Raspberry Pi Image</div><div class="muted">Capture uploads a new image only. AI runs only after pressing the prediction button.</div></div>')
        latest_image = get_latest_image()
        if latest_image:
            st.image(latest_image, caption="Latest Raspberry Pi Image", use_container_width=True)
        else:
            st.info("No Raspberry Pi image available.")

        a, b = st.columns(2)
        with a:
            if st.button("📸 CAPTURE", type="primary", use_container_width=True, key="ai_pi_capture"):
                previous_version = int(pi.get("image_version", 0) or 0)
                response = capture_image()
                if response and response.status_code == 200:
                    new_image, _ = wait_for_new_image(previous_version)
                    if new_image is not None:
                        st.success("New Raspberry Pi image uploaded. Click AI Prediction.")
                    else:
                        st.warning("No new Pi upload received within the wait period.")
                    st.rerun()
        with b:
            if st.button("🔍 AI PREDICTION", type="primary", use_container_width=True, key="ai_pi_predict"):
                response = predict_latest()
                if response and response.status_code == 200:
                    st.success("Raspberry Pi image analyzed successfully.")
                    st.rerun()

    with manual_col:
        st.html('<div class="panel"><div class="panel-title">📤 Manual Image</div><div class="muted">First choose and upload the image. AI Prediction is a separate action.</div></div>')

        uploaded_file = st.file_uploader(
            "Choose an image",
            type=["jpg", "jpeg", "png"],
            key="manual_upload",
        )

        if uploaded_file is not None:
            manual_bytes = uploaded_file.getvalue()
            file_hash = hashlib.sha256(manual_bytes).hexdigest()

            st.image(manual_bytes, caption="Selected Manual Image", use_container_width=True)

            if st.button("📤 UPLOAD IMAGE", type="primary", use_container_width=True, key="manual_upload_button"):
                response = upload_manual_image(uploaded_file)
                if response and response.status_code == 200:
                    st.session_state["manual_uploaded_hash"] = file_hash
                    st.success("✅ Image uploaded. Click AI Prediction to run the AI pipeline.")
                    st.rerun()
                elif response is not None:
                    try:
                        st.error(response.json().get("detail", response.text))
                    except ValueError:
                        st.error(response.text)

            if st.session_state.get("manual_uploaded_hash") == file_hash:
                st.success("Image is uploaded and ready for AI Prediction.")
                if st.button("🧠 AI PREDICTION", type="primary", use_container_width=True, key="manual_predict_button"):
                    with st.spinner("Running CropIQ AI pipeline..."):
                        response = predict_latest()
                    if response and response.status_code == 200:
                        st.success("✅ Manual image analyzed successfully.")
                        st.rerun()
                    elif response is not None:
                        try:
                            st.error(response.json().get("detail", response.text))
                        except ValueError:
                            st.error(response.text)

    st.subheader("Current AI Result")
    render_ai_result(pi)
    render_sprayer_panel(pi, "ai_spray")

# ============================================================
# SETTINGS
# ============================================================

elif page == "⚙️ Settings":
    st.html(
        """
        <div class="hero">
            <div class="hero-title">⚙️ System <span class="hero-green">Settings</span></div>
            <div class="hero-subtitle">Backend and pipeline configuration.</div>
        </div>
        """
    )

    st.subheader("Backend Service Endpoint")
    st.code(BACKEND_URL)

    st.subheader("Current Backend State")
    st.json(state or {"error": "Backend unavailable"})
