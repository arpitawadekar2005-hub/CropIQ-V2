import streamlit as st
import requests

# =====================================================
# CONFIGURATION
# =====================================================

BACKEND_URL = "https://cropiq-backend-mecl.onrender.com"

st.set_page_config(
    page_title="CropIQ",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS matching exact original CropIQ styling
st.markdown("""
<style>
    /* Dark Green Sidebar */
    [data-testid="stSidebar"] {
        background-color: #0b3b2b;
        color: white;
    }
    [data-testid="stSidebar"] * {
        color: white !important;
    }
    
    /* Global Background */
    .stApp {
        background-color: #f4f7f5;
    }
    
    /* White Card Containers */
    div.stBlock {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }

    /* Target Buttons */
    .stButton>button {
        border-radius: 6px;
        font-weight: 600;
        height: 45px;
    }
    
    /* Red Disease Text */
    .disease-title {
        color: #d93838;
        font-weight: 800;
        font-size: 20px;
        letter-spacing: 0.5px;
    }
</style>
""", unsafe_allow_html=True)

# =====================================================
# SESSION STATES
# =====================================================

if "dash_prediction" not in st.session_state:
    st.session_state["dash_prediction"] = None

if "manual_prediction" not in st.session_state:
    st.session_state["manual_prediction"] = None

if "last_uploaded_name" not in st.session_state:
    st.session_state["last_uploaded_name"] = None

# =====================================================
# SIDEBAR
# =====================================================

with st.sidebar:
    st.markdown("<h1 style='text-align: center; margin-bottom: 0;'>🌿</h1>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center; margin-top: 0;'>CropIQ</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-size: 12px; color: #a3c2b5;'>Precision Farming<br>for a Greener Tomorrow</p>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    page = st.radio(
        "",
        ["🏠 Dashboard", "📷 Live View", "🚜 Rover Control", "💧 Sprayer Control", "🌿 AI Detection", "⚙️ Settings"],
        index=0,
        label_visibility="collapsed"
    )

    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # Raspberry Pi Status Widget
    st.markdown("""
        <div style="background-color: #062b1f; padding: 12px; border-radius: 8px;">
            <p style="font-size: 11px; margin: 0; color: #a3c2b5;">🍓 Raspberry Pi</p>
            <p style="color: #ff4d4d; font-weight: bold; margin: 2px 0;">🔴 OFFLINE</p>
            <p style="font-size: 11px; margin: 0;">System Status: <b style="color: #ffffff;">Disconnected</b></p>
        </div>
    """, unsafe_allow_html=True)

# =====================================================
# PAGE 1: DASHBOARD
# =====================================================

if page == "🏠 Dashboard":
    col1, col2 = st.columns([1.3, 0.7])

    with col1:
        # Camera Feed Block
        st.markdown("### 📷 Live Camera Feed")
        
        # Try loading current Raspberry Pi camera image
        try:
            img_res = requests.get(f"{BACKEND_URL}/latest-image", timeout=3)
            if img_res.status_code == 200:
                st.image(img_res.content, use_container_width=True)
            else:
                st.info("No captured camera stream available.")
        except Exception:
            st.info("Waiting for image from backend...")

        # Action Buttons
        if st.button("📸 CAPTURE PLANT IMAGE", use_container_width=True, type="primary"):
            try:
                requests.post(f"{BACKEND_URL}/capture", timeout=5)
                st.session_state["dash_prediction"] = None  # Reset stale prediction
                st.toast("Capture trigger sent to Pi!")
                st.rerun()
            except Exception as e:
                st.error(f"Error triggering capture: {e}")

        st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)

        if st.button("🔍 RUN AI PREDICTION", use_container_width=True):
            with st.spinner("Analyzing image..."):
                try:
                    res = requests.post(f"{BACKEND_URL}/predict-captured", timeout=20)
                    if res.status_code == 200:
                        st.session_state["dash_prediction"] = res.json()
                        st.rerun()
                    else:
                        st.error("Could not run prediction on captured frame.")
                except Exception as e:
                    st.error(f"Prediction failed: {e}")

    with col2:
        st.markdown("<p style='font-weight: 700; color: #333; margin-bottom: 5px;'>PLANT ANALYSIS</p>", unsafe_allow_html=True)
        
        pred = st.session_state["dash_prediction"]

        if pred:
            is_healthy = "healthy" in pred.get("prediction", "").lower()

            if is_healthy:
                st.markdown("<p style='color: #2e7d32; font-weight: 800; font-size: 20px;'>HEALTHY PLANT</p>", unsafe_allow_html=True)
            else:
                st.markdown("<p class='disease-title'>DISEASE DETECTED</p>", unsafe_allow_html=True)

            st.markdown(f"**Crop:** <span style='float: right;'><b>{pred.get('crop', '-')}</b></span>", unsafe_allow_html=True)
            st.markdown(f"**Disease:** <span style='float: right;'><b>{pred.get('prediction', '-')}</b></span>", unsafe_allow_html=True)
            st.markdown(f"**Confidence:** <span style='float: right;'><b>{pred.get('confidence', 0)}%</b></span>", unsafe_allow_html=True)
            st.markdown(f"**Severity:** <span style='float: right;'><b>{pred.get('disease_area_percentage', 0)}%</b></span>", unsafe_allow_html=True)
            st.markdown(f"**Pesticide:** <span style='float: right;'><b>{pred.get('pesticide_name', '-')}</b></span>", unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)
            
            # Green Dosage Box
            st.markdown(f"""
                <div style="background-color: #eaf5ea; padding: 15px; border-radius: 8px; text-align: center;">
                    <p style="color: #1e5e20; font-weight: 700; font-size: 12px; margin: 0;">RECOMMENDED DOSAGE:</p>
                    <h2 style="color: #1e5e20; font-weight: 900; margin: 0;">{pred.get('recommended_dosage_ml', 0.0)} ml</h2>
                </div>
            """, unsafe_allow_html=True)
        else:
            st.info("Awaiting AI analysis. Click 'RUN AI PREDICTION' to analyze current frame.")

# =====================================================
# PAGE 2: AI DETECTION (MANUAL UPLOAD)
# =====================================================

elif page == "🌿 AI Detection":
    st.markdown("## 🌿 AI Plant Detection & Analysis")
    st.caption("Upload plant leaf images to execute AI diagnosis and automatically derive pesticide treatment dosages.")

    col1, col2 = st.columns([1.3, 0.7])

    with col1:
        st.markdown("### 📷 Upload Plant Image")
        uploaded_file = st.file_uploader("Select a leaf image to run AI analysis.", type=["jpg", "jpeg", "png"])

        if uploaded_file is not None:
            # If new file is uploaded, reset old prediction
            if st.session_state["last_uploaded_name"] != uploaded_file.name:
                st.session_state["last_uploaded_name"] = uploaded_file.name
                st.session_state["manual_prediction"] = None

            image_bytes = uploaded_file.getvalue()
            st.image(image_bytes, use_container_width=True)

            if st.button("🔍 PROCESS AI INFERENCE", type="primary", use_container_width=True):
                with st.spinner("Processing image..."):
                    try:
                        files = {"file": (uploaded_file.name, image_bytes, "image/jpeg")}
                        res = requests.post(f"{BACKEND_URL}/predict-manual", files=files, timeout=20)
                        if res.status_code == 200:
                            st.session_state["manual_prediction"] = res.json()
                            st.rerun()
                        else:
                            st.error("Prediction failed.")
                    except Exception as e:
                        st.error(f"Error connecting to server: {e}")

    with col2:
        st.markdown("<p style='font-weight: 700; color: #333; margin-bottom: 5px;'>PLANT ANALYSIS</p>", unsafe_allow_html=True)

        pred = st.session_state["manual_prediction"]

        if pred:
            is_healthy = "healthy" in pred.get("prediction", "").lower()

            if is_healthy:
                st.markdown("<p style='color: #2e7d32; font-weight: 800; font-size: 20px;'>HEALTHY PLANT</p>", unsafe_allow_html=True)
            else:
                st.markdown("<p class='disease-title'>DISEASE DETECTED</p>", unsafe_allow_html=True)

            st.markdown(f"**Crop:** <span style='float: right;'><b>{pred.get('crop', '-')}</b></span>", unsafe_allow_html=True)
            st.markdown(f"**Disease:** <span style='float: right;'><b>{pred.get('prediction', '-')}</b></span>", unsafe_allow_html=True)
            st.markdown(f"**Confidence:** <span style='float: right;'><b>{pred.get('confidence', 0)}%</b></span>", unsafe_allow_html=True)
            st.markdown(f"**Severity:** <span style='float: right;'><b>{pred.get('disease_area_percentage', 0)}%</b></span>", unsafe_allow_html=True)
            st.markdown(f"**Pesticide:** <span style='float: right;'><b>{pred.get('pesticide_name', '-')}</b></span>", unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            st.markdown(f"""
                <div style="background-color: #eaf5ea; padding: 15px; border-radius: 8px; text-align: center;">
                    <p style="color: #1e5e20; font-weight: 700; font-size: 12px; margin: 0;">RECOMMENDED DOSAGE:</p>
                    <h2 style="color: #1e5e20; font-weight: 900; margin: 0;">{pred.get('recommended_dosage_ml', 0.0)} ml</h2>
                </div>
            """, unsafe_allow_html=True)
        else:
            st.info("Select an image and click 'PROCESS AI INFERENCE'.")
