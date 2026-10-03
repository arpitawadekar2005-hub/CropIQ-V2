import streamlit as st
import requests

# =====================================================
# CONFIGURATION & PAGE SETUP
# =====================================================

BACKEND_URL = "https://cropiq-backend-mecl.onrender.com"

st.set_page_config(
    page_title="CropIQ - Precision Farming",
    page_icon="🌿",
    layout="wide"
)

# Custom CSS styling for CropIQ branding
st.markdown("""
    <style>
    .main {
        background-color: #f8faf9;
    }
    .stButton>button {
        border-radius: 8px;
        font-weight: bold;
    }
    .metric-card {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        border-left: 5px solid #2e7d32;
    }
    </style>
""", unsafe_allow_html=True)

# =====================================================
# SESSION STATE INITIALIZATION
# =====================================================

if "dash_prediction" not in st.session_state:
    st.session_state["dash_prediction"] = None

if "manual_prediction" not in st.session_state:
    st.session_state["manual_prediction"] = None

if "last_manual_file" not in st.session_state:
    st.session_state["last_manual_file"] = None

# =====================================================
# HELPER FUNCTIONS FOR API CALLS
# =====================================================

def fetch_latest_image():
    """Gets the latest Raspberry Pi camera frame from backend."""
    try:
        res = requests.get(f"{BACKEND_URL}/latest-image", timeout=5)
        if res.status_code == 200:
            return res.content
    except Exception:
        pass
    return None

def trigger_pi_capture():
    """Sends command to queue a Pi camera capture."""
    try:
        res = requests.post(f"{BACKEND_URL}/capture", timeout=5)
        return res.status_code == 200
    except Exception:
        return False

def run_pi_prediction():
    """Runs AI inference on the captured Pi image."""
    try:
        res = requests.post(f"{BACKEND_URL}/predict-captured", timeout=30)
        if res.status_code == 200:
            return res.json()
    except Exception as e:
        st.error(f"Prediction failed: {e}")
    return None

def run_manual_prediction(image_bytes, filename):
    """Runs AI inference on manually uploaded file."""
    try:
        files = {"file": (filename, image_bytes, "image/jpeg")}
        res = requests.post(f"{BACKEND_URL}/predict-manual", files=files, timeout=30)
        if res.status_code == 200:
            return res.json()
    except Exception as e:
        st.error(f"Prediction failed: {e}")
    return None

# =====================================================
# SIDEBAR NAVIGATION
# =====================================================

st.sidebar.title("🌿 CropIQ")
st.sidebar.caption("Precision Farming for a Greener Tomorrow")

page = st.sidebar.radio(
    "Navigation", 
    ["🏠 Dashboard", "🌿 AI Detection", "🚜 Rover Control", "⚙️ Settings"]
)

# =====================================================
# PAGE 1: DASHBOARD & RASPBERRY PI CAM
# =====================================================

if page == "🏠 Dashboard":
    st.title("🏠 Dashboard & Camera Control")
    st.caption("Monitor camera stream and run real-time AI diagnosis.")

    col1, col2 = st.columns([1.2, 0.8])

    with col1:
        st.subheader("📷 Live Camera Feed")
        
        captured_img = fetch_latest_image()
        
        if captured_img:
            st.image(captured_img, caption="Latest Captured Frame", use_container_width=True)
        else:
            st.info("No captured image available from Raspberry Pi.")

        btn_col1, btn_col2 = st.columns(2)

        with btn_col1:
            if st.button("📸 CAPTURE PLANT IMAGE", use_container_width=True, type="primary"):
                with st.spinner("Triggering Raspberry Pi Camera..."):
                    if trigger_pi_capture():
                        st.session_state["dash_prediction"] = None  # Reset prediction for new image
                        st.success("Capture command sent!")
                        st.rerun()
                    else:
                        st.error("Failed to connect to Raspberry Pi.")

        with btn_col2:
            if st.button("🔍 RUN AI PREDICTION", use_container_width=True):
                if captured_img:
                    with st.spinner("Executing AI Model Inference..."):
                        result = run_pi_prediction()
                        if result:
                            st.session_state["dash_prediction"] = result
                            st.rerun()
                else:
                    st.warning("Please capture an image first!")

    with col2:
        st.subheader("PLANT ANALYSIS")
        
        pred = st.session_state["dash_prediction"]
        
        if pred:
            is_healthy = pred.get("prediction", "").lower() == "healthy"
            
            if is_healthy:
                st.success("### HEALTHY PLANT DETECTED")
            else:
                st.error("### DISEASE DETECTED")

            st.write(f"**Crop:** {pred.get('crop', 'N/A')}")
            st.write(f"**Disease:** {pred.get('prediction', 'N/A')}")
            st.write(f"**Confidence:** {pred.get('confidence', 0)}%")
            st.write(f"**Severity:** {pred.get('disease_area_percentage', 0)}%")
            st.write(f"**Recommended Pesticide:** {pred.get('pesticide_name', 'None')}")

            st.metric(
                label="RECOMMENDED DOSAGE",
                value=f"{pred.get('recommended_dosage_ml', 0.0)} ml"
            )
        else:
            st.info("AWAITING PREDICTION\n\nClick **RUN AI PREDICTION** to evaluate current frame.")

# =====================================================
# PAGE 2: MANUAL AI DETECTION
# =====================================================

elif page == "🌿 AI Detection":
    st.title("🌿 AI Plant Detection & Analysis")
    st.caption("Upload plant leaf images to execute AI diagnosis manually.")

    col1, col2 = st.columns([1.2, 0.8])

    with col1:
        st.subheader("📷 Upload Plant Image")
        uploaded_file = st.file_uploader("Choose a leaf image...", type=["jpg", "jpeg", "png"])

        if uploaded_file is not None:
            # If a new image is uploaded, clear old prediction state
            if st.session_state["last_manual_file"] != uploaded_file.name:
                st.session_state["last_manual_file"] = uploaded_file.name
                st.session_state["manual_prediction"] = None

            image_bytes = uploaded_file.getvalue()
            st.image(image_bytes, caption="Uploaded Leaf Image", use_container_width=True)

            if st.button("🔍 PROCESS AI INFERENCE", type="primary", use_container_width=True):
                with st.spinner("Analyzing uploaded image..."):
                    result = run_manual_prediction(image_bytes, uploaded_file.name)
                    if result:
                        st.session_state["manual_prediction"] = result
                        st.rerun()

    with col2:
        st.subheader("PLANT ANALYSIS")

        pred = st.session_state["manual_prediction"]

        if pred:
            is_healthy = pred.get("prediction", "").lower() == "healthy"

            if is_healthy:
                st.success("### HEALTHY PLANT DETECTED")
            else:
                st.error("### DISEASE DETECTED")

            st.write(f"**Crop:** {pred.get('crop', 'N/A')}")
            st.write(f"**Disease:** {pred.get('prediction', 'N/A')}")
            st.write(f"**Confidence:** {pred.get('confidence', 0)}%")
            st.write(f"**Severity:** {pred.get('disease_area_percentage', 0)}%")
            st.write(f"**Recommended Pesticide:** {pred.get('pesticide_name', 'None')}")

            st.metric(
                label="RECOMMENDED DOSAGE",
                value=f"{pred.get('recommended_dosage_ml', 0.0)} ml"
            )
        else:
            st.info("AWAITING PREDICTION\n\nUpload an image and click **PROCESS AI INFERENCE**.")

# =====================================================
# PAGE 3 & 4: PLACEHOLDERS
# =====================================================

elif page == "🚜 Rover Control":
    st.title("🚜 Rover Controls")
    st.info("Rover movement controls linked to ESP32 WebSocket endpoint.")

elif page == "⚙️ Settings":
    st.title("⚙️ System Settings")
    st.write(f"**Backend Endpoint:** `{BACKEND_URL}`")
