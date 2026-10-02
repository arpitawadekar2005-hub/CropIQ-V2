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
# CSS
# ============================================================

st.html("""
<style>

/* GLOBAL & EXISTING CSS REMAINS SAME */

html, body {
    font-family: Inter, Arial, sans-serif;
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

/* SIDEBAR */
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
.sidebar-section { color: #7fb9aa; font-size: 10px; font-weight: 800; letter-spacing: 1.7px; padding-left: 10px; margin-top: 22px; margin-bottom: 10px; }

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

/* HERO */
.hero { position: relative; overflow: hidden; background: linear-gradient(135deg, #edf8ef, #ffffff); border: 1px solid #dce9e1; border-radius: 21px; padding: 23px 27px; margin-top: 17px; margin-bottom: 18px; box-shadow: 0 7px 24px rgba(25,70,50,0.055); }
.hero-title { color: #043d31; font-size: 28px; font-weight: 850; letter-spacing: -0.5px; }
.hero-green { color: #078845; }
.hero-subtitle { color: #6c7a73; font-size: 13px; margin-top: 6px; }

/* SECTION & KPI */
.section-title { color: #063e32; font-size: 20px; font-weight: 850; margin-top: 18px; margin-bottom: 11px; }
.kpi-card { background: white; border-radius: 17px; border: 1px solid #dfe8e3; padding: 17px; min-height: 145px; box-shadow: 0 6px 20px rgba(25,70,48,0.06); }
.kpi-green-border { border-top: 3px solid #39ae68; }
.kpi-blue-border { border-top: 3px solid #45a4eb; }
.kpi-purple-border { border-top: 3px solid #8b62d4; }
.kpi-icon { width: 42px; height: 42px; display: flex; align-items: center; justify-content: center; border-radius: 50%; font-size: 21px; margin-bottom: 9px; }
.icon-green { background: #eff9e9; }
.icon-blue { background: #edf6ff; }
.icon-purple { background: #f5efff; }
.kpi-label { color: #74817b; font-size: 10px; font-weight: 800; letter-spacing: 0.5px; }
.kpi-value { font-size: 23px; font-weight: 850; margin-top: 4px; }
.green-value { color: #087d3f; }
.blue-value { color: #1477cc; }
.purple-value { color: #7042c5; }
.kpi-description { color: #8b9691; font-size: 11px; margin-top: 5px; }

/* PANELS */
.panel { background: white; border: 1px solid #dfe8e3; border-radius: 18px; padding: 17px; box-shadow: 0 6px 20px rgba(25,70,48,0.055); }
.panel-heading { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }
.panel-title { color: #073e33; font-size: 18px; font-weight: 850; }
.panel-subtitle { color: #7c8782; font-size: 11px; margin-top: 4px; }

/* SPRAYER & LIVE STATUS */
.sprayer-status { background: linear-gradient(135deg, #f0faf3, #fbfdfb); border: 1px solid #d6eadc; border-radius: 14px; padding: 13px; margin-bottom: 12px; }
.sprayer-label { color: #66746d; font-size: 11px; font-weight: 700; }
.sprayer-value { color: #087d3f; font-size: 20px; font-weight: 850; margin-top: 4px; }
.sprayer-info { background: #f1f9f4; border: 1px solid #dcebe1; border-radius: 12px; padding: 11px; color: #477064; font-size: 11px; line-height: 1.5; margin-top: 10px; }

/* AI CARDS */
.ai-card { background: white; border: 1px solid #dfe8e3; border-radius: 17px; padding: 18px; min-height: 175px; box-shadow: 0 6px 20px rgba(25,70,48,0.05); }
.ai-title { color: #073d33; font-size: 17px; font-weight: 850; }
.ai-label { color: #87928d; font-size: 10px; font-weight: 800; margin-top: 14px; }
.ai-value { color: #073e33; font-size: 17px; font-weight: 800; margin-top: 4px; }
.ai-text { color: #75817b; font-size: 11px; line-height: 1.5; margin-top: 7px; }
.ai-alert { background: #fff4f2; border-color: #efccc8; }
.ai-recommend { background: #effaf3; border-color: #cce8d5; }

/* MANUAL PREDICTION */
.manual-upload-card { background: white; border: 1px solid #dfe8e3; border-radius: 18px; padding: 18px; box-shadow: 0 6px 20px rgba(25,70,48,0.05); }
.manual-upload-title { color: #073e33; font-size: 18px; font-weight: 850; margin-bottom: 5px; }
.manual-upload-subtitle { color: #7c8782; font-size: 11px; line-height: 1.5; }
.manual-result { background: linear-gradient(135deg, #eefaf2, #ffffff); border: 1px solid #cce8d5; border-radius: 16px; padding: 18px; }
.manual-result-label { color: #75817b; font-size: 10px; font-weight: 800; letter-spacing: 0.5px; margin-top: 8px; }
.manual-result-value { color: #073e33; font-size: 21px; font-weight: 850; margin-top: 5px; line-height: 1.25; word-break: break-word; }
.manual-confidence { color: #087d3f; font-size: 27px; font-weight: 850; margin-top: 4px; }
.manual-model-note { color: #75817b; font-size: 10px; line-height: 1.5; margin-top: 12px; }

</style>
""")


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
            json={"amount_ml": amount_ml},
            timeout=REQUEST_TIMEOUT
        )
    except Exception as e:
        st.error(f"Backend connection error: {e}")
        return None


def send_rover_command(command, speed):
    try:
        return requests.post(
            BACKEND_URL + "/rover",
            json={"command": command, "speed": speed},
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
        response = requests.post(
            BACKEND_URL + "/predict-manual",
            files=files,
            timeout=30
        )
        return response
    except Exception as e:
        st.error(f"Prediction error: {e}")
    return None


# ============================================================
# CAMERA FRAGMENT
# ============================================================

@st.fragment
def camera_fragment(button_text, button_key, primary=False, show_panel=True):
    if show_panel:
        st.html("""
        <div class="panel">
            <div class="panel-heading">
                <div>
                    <div class="panel-title">📷 Live Camera Feed</div>
                    <div class="panel-subtitle">Latest image captured from the Raspberry Pi camera.</div>
                </div>
                <div class="live-badge">● LIVE</div>
            </div>
        </div>
        """)

    current_image = get_latest_image()
    image_placeholder = st.empty()

    if current_image is not None:
        image_placeholder.image(current_image, use_container_width=True)
    else:
        image_placeholder.info("No camera image available.")

    st.write("")

    if st.button(
        button_text,
        type="primary" if primary else "secondary",
        use_container_width=True,
        key=button_key
    ):
        response = send_capture()
        if response and response.status_code == 200:
            st.info("📸 Capturing new image...")
            time.sleep(2)
            st.rerun()


# ============================================================
# STATE
# ============================================================

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

    # Active AI results from state
    ai_disease = raspberry.get("ai_prediction", "No Detection")
    ai_confidence = float(raspberry.get("ai_confidence", 0) or 0)
    ai_disease_area = float(raspberry.get("disease_area_percentage", 0) or 0)
    ai_recommended_dosage = float(raspberry.get("recommended_dosage_ml", 25.0) or 25.0)
    ai_pesticide_name = raspberry.get("pesticide_name", "N/A")
    ai_segmentation_b64 = raspberry.get("segmentation_overlay")
else:
    spray_status = "OFFLINE"
    sprayed_amount = 0.0
    raspberry_online = False
    esp32_online = False
    rover_status = "UNKNOWN"
    current_speed = 50
    ai_disease = "No Detection"
    ai_confidence = 0.0
    ai_disease_area = 0.0
    ai_recommended_dosage = 25.0
    ai_pesticide_name = "N/A"
    ai_segmentation_b64 = None


# Check for manual prediction override in Session State
if "last_dosage" not in st.session_state:
    st.session_state["last_dosage"] = ai_recommended_dosage


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
# DASHBOARD
# ============================================================

if page == "🏠 Dashboard":

    st.html("""
    <div class="hero">
        <div class="hero-title">🌿 Precision <span class="hero-green">Spraying Control</span></div>
        <div class="hero-subtitle">Monitor plant health, review AI segmentation masks, and execute precision dosage spraying.</div>
    </div>
    """)

    # KPI ROW
    k1, k2, k3, k4 = st.columns(4)

    with k1:
        st.html(f"""
        <div class="kpi-card kpi-green-border">
            <div class="kpi-icon icon-green">💦</div>
            <div class="kpi-label">SPRAYER STATUS</div>
            <div class="kpi-value green-value">{str(spray_status).upper()}</div>
            <div class="kpi-description">Current operation</div>
        </div>
        """)

    with k2:
        st.html(f"""
        <div class="kpi-card kpi-blue-border">
            <div class="kpi-icon icon-blue">💧</div>
            <div class="kpi-label">LAST DISPENSED</div>
            <div class="kpi-value blue-value">{float(sprayed_amount):.1f} ml</div>
            <div class="kpi-description">Latest spray quantity</div>
        </div>
        """)

    with k3:
        camera_status = "READY" if raspberry_online else "OFFLINE"
        st.html(f"""
        <div class="kpi-card kpi-green-border">
            <div class="kpi-icon icon-green">📷</div>
            <div class="kpi-label">CAMERA</div>
            <div class="kpi-value green-value">{camera_status}</div>
            <div class="kpi-description">Plant imaging system</div>
        </div>
        """)

    with k4:
        esp_status = "ONLINE" if esp32_online else "OFFLINE"
        st.html(f"""
        <div class="kpi-card kpi-purple-border">
            <div class="kpi-icon icon-purple">🔌</div>
            <div class="kpi-label">ESP32 ROVER</div>
            <div class="kpi-value purple-value">{esp_status}</div>
            <div class="kpi-description">Rover hardware connection</div>
        </div>
        """)

    # AI DETECTION RESULTS (DASHBOARD)
    st.html("""<div class="section-title">🌿 Latest AI Detection & Segmentation</div>""")

    ai1, ai2, ai3 = st.columns([1, 1.15, 0.85])

    # Column 1: Classification
    with ai1:
        st.html(f"""
        <div class="ai-card">
            <div class="ai-title">🌿 Classification Result</div>
            <div class="ai-label">DETECTED CONDITION</div>
            <div class="ai-value">{ai_disease.replace('_', ' ')}</div>
            <div class="ai-text">
                Confidence: <b>{ai_confidence:.2f}%</b><br>
                Pesticide: <b>{ai_pesticide_name}</b>
            </div>
        </div>
        """)

    # Column 2: Segmentation Mask Visualizer
    with ai2:
        st.html("""
        <div class="ai-card ai-alert">
            <div class="ai-title">🔬 Disease Segmentation</div>
            <div class="ai-label">AFFECTED LEAF AREA</div>
        </div>
        """)
        if ai_segmentation_b64:
            seg_img = base64_to_image(ai_segmentation_b64)
            if seg_img:
                st.image(seg_img, caption=f"UNet++ Mask Area: {ai_disease_area:.2f}%", use_container_width=True)
            else:
                st.caption("No visual mask render available.")
        else:
            st.caption("No active segmentation overlay found.")

    # Column 3: Recommended Action & Dosage Update
    with ai3:
        st.html(f"""
        <div class="ai-card ai-recommend">
            <div class="ai-title">💡 Spray Recommendation</div>
            <div class="ai-label">RECOMMENDED DOSAGE</div>
            <div class="ai-value">{ai_recommended_dosage:.1f} ml</div>
            <div class="ai-text">
                Calculated based on infected leaf coverage area ({ai_disease_area:.2f}%).
            </div>
        </div>
        """)

    # CONTROL SECTION
    st.html("""<div class="section-title">Plant Monitoring & Control</div>""")

    camera_col, rover_col, spray_col = st.columns([1.45, 1, 1])

    with camera_col:
        camera_fragment(button_text="📸 CAPTURE PLANT IMAGE", button_key="capture_dashboard", primary=False, show_panel=True)

    with rover_col:
        st.html("""<div class="panel"><div class="panel-heading"><div class="panel-title">🚜 Rover Control</div></div></div>""")
        speed = st.slider("Speed", 0, 100, int(current_speed), 5, key="dash_speed")
        c1, c2, c3 = st.columns(3)
        with c2:
            if st.button("⬆️", key="fwd"): send_rover_command("F", speed)
        c1, c2, c3 = st.columns(3)
        with c1:
            if st.button("⬅️", key="lft"): send_rover_command("L", speed)
        with c2:
            if st.button("⏹️", key="stp"): send_rover_command("S", speed)
        with c3:
            if st.button("➡️", key="rgt"): send_rover_command("R", speed)

    with spray_col:
        st.html("""<div class="panel"><div class="panel-heading"><div class="panel-title">💧 Precision Sprayer</div></div></div>""")

        # Auto-populate calculated dosage into manual input box
        dosage = st.number_input(
            "Spray dosage (ml)",
            min_value=1.0,
            max_value=500.0,
            value=float(st.session_state.get("last_dosage", ai_recommended_dosage)),
            step=1.0,
            key="dashboard_dosage"
        )

        if st.button("🚿 APPLY PRECISION SPRAY", type="primary", use_container_width=True, key="dashboard_spray"):
            response = send_spray(dosage)
            if response and response.status_code == 200:
                st.success(f"Dispensary activated for {dosage:.1f} ml.")


# ============================================================
# AI DETECTION PAGE
# ============================================================

elif page == "🌿 AI Detection":

    st.html("""
    <div class="hero">
        <div class="hero-title">🌿 AI Plant <span class="hero-green">Detection & Segmentation</span></div>
        <div class="hero-subtitle">Dual-stage UNet++ and EfficientNet AI inference engine for disease diagnosis & targeted dosage estimation.</div>
    </div>
    """)

    st.html("""<div class="section-title">📤 Manual Image Prediction</div>""")

    upload_col, result_col = st.columns([1.15, 0.85])

    with upload_col:
        st.html("""
        <div class="manual-upload-card">
            <div class="manual-upload-title">📷 Upload Leaf Image</div>
            <div class="manual-upload-subtitle">Upload an image to process UNet++ segmentation & EfficientNet classification simultaneously.</div>
        </div>
        """)

        uploaded_file = st.file_uploader("Choose an image", type=["jpg", "jpeg", "png"], key="manual_prediction_upload")

        if uploaded_file is not None:
            st.image(uploaded_file, caption="Original Image", use_container_width=True)

            if st.button("🔍 PROCESS FULL AI INFERENCE", type="primary", use_container_width=True, key="manual_predict_button"):
                with st.spinner("Executing segmentation, classification & dosage engine..."):
                    response = predict_manual_image(uploaded_file)

                if response and response.status_code == 200:
                    res = response.json()
                    st.session_state["manual_prediction"] = res.get("prediction", "Unknown")
                    st.session_state["manual_confidence"] = float(res.get("confidence", 0))
                    st.session_state["manual_disease_area"] = float(res.get("disease_area_percentage", 0))
                    st.session_state["manual_dosage"] = float(res.get("recommended_dosage_ml", 25.0))
                    st.session_state["manual_pesticide"] = res.get("pesticide_name", "N/A")
                    st.session_state["manual_segmentation"] = res.get("segmentation_overlay")

                    # Update overall spray dosage box default
                    st.session_state["last_dosage"] = float(res.get("recommended_dosage_ml", 25.0))
                    st.success("✅ Complete AI analysis finished successfully.")

    with result_col:
        st.html("""<div class="manual-upload-card"><div class="manual-upload-title">🤖 AI Diagnosis & Dosage Output</div></div>""")

        if "manual_prediction" in st.session_state:
            pred = st.session_state["manual_prediction"].replace("_", " ")
            conf = st.session_state["manual_confidence"]
            area = st.session_state.get("manual_disease_area", 0.0)
            dose = st.session_state.get("manual_dosage", 25.0)
            pest = st.session_state.get("manual_pesticide", "N/A")
            seg_mask = st.session_state.get("manual_segmentation")

            st.html(f"""
            <div class="manual-result">
                <div class="manual-result-label">DISEASE CONDITION</div>
                <div class="manual-result-value">{pred}</div>

                <div class="manual-result-label">CONFIDENCE</div>
                <div class="manual-confidence">{conf:.2f}%</div>

                <div class="manual-result-label">DISEASE AREA COVERAGE</div>
                <div class="manual-result-value">{area:.2f}%</div>

                <div class="manual-result-label">RECOMMENDED PESTICIDE</div>
                <div class="manual-result-value">{pest}</div>

                <div class="manual-result-label">CALCULATED SPRAY DOSAGE</div>
                <div class="manual-confidence" style="color: #1477cc;">{dose:.1f} ml</div>
            </div>
            """)

            if seg_mask:
                st.write("")
                st.markdown("**Segmentation Overlay Mask:**")
                mask_img = base64_to_image(seg_mask)
                if mask_img:
                    st.image(mask_img, use_container_width=True)
        else:
            st.info("Upload an image and click 'PROCESS FULL AI INFERENCE'.")


# ============================================================
# OTHER PAGES (LIVE VIEW, ROVER, SPRAYER, SETTINGS)
# ============================================================

elif page == "📷 Live View":
    camera_fragment(button_text="📸 CAPTURE NEW IMAGE", button_key="live_capture", primary=True, show_panel=False)

elif page == "🚜 Rover Control":
    speed = st.slider("Rover Speed", 0, 100, int(current_speed), 5, key="rover_page_speed")
    c1, c2, c3 = st.columns(3)
    with c2:
        if st.button("⬆️ FORWARD", use_container_width=True, key="page_forward"): send_rover_command("F", speed)
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("⬅️ LEFT", use_container_width=True, key="page_left"): send_rover_command("L", speed)
    with c2:
        if st.button("⛔ STOP", use_container_width=True, key="page_stop"): send_rover_command("S", speed)
    with c3:
        if st.button("➡️ RIGHT", use_container_width=True, key="page_right"): send_rover_command("R", speed)

elif page == "💧 Sprayer Control":
    dosage = st.number_input(
        "Spray dosage (ml)",
        min_value=1.0,
        max_value=500.0,
        value=float(st.session_state.get("last_dosage", ai_recommended_dosage)),
        step=1.0,
        key="sprayer_page_dosage"
    )
    if st.button("🚿 START PRECISION SPRAY", type="primary", use_container_width=True, key="page_spray"):
        response = send_spray(dosage)
        if response and response.status_code == 200:
            st.success(f"Spray command dispatched: {dosage:.1f} ml")

elif page == "⚙️ Settings":
    st.subheader("Backend URL")
    st.code(BACKEND_URL)


# ============================================================
# FOOTER
# ============================================================

st.html("""
<div class="footer">
    © 2026 CropIQ • Precision Agriculture • AI-Powered Targeted Spraying
</div>
""")
