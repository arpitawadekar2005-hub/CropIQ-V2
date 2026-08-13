import streamlit as st
import requests


# ==========================================
# YOUR RENDER BACKEND URL
# ==========================================

BACKEND_URL = "https://cropiq-backend-mecl.onrender.com"


# ==========================================
# PAGE CONFIGURATION
# ==========================================

st.set_page_config(
    page_title="CropIQ",
    page_icon="🌱",
    layout="centered"
)


# ==========================================
# TITLE
# ==========================================

st.title("🌱 CropIQ")

st.subheader("Precision Spraying Dashboard")


# ==========================================
# BACKEND TEST
# ==========================================

st.markdown("### 🔗 Backend Connection")

try:

    response = requests.get(
        BACKEND_URL + "/test",
        timeout=10
    )

    if response.status_code == 200:

        st.success("Backend connected successfully ✅")

    else:

        st.error("Backend returned an error")

except Exception as e:

    st.error(
        "Could not connect to backend"
    )

    st.write(e)


# ==========================================
# PLANT IMAGE
# ==========================================

st.markdown("### 🌿 Plant Image")

st.info(
    "Raspberry Pi camera image will appear here."
)


# ==========================================
# DOSAGE
# ==========================================

st.markdown("### 💧 Dosage")

dosage = st.number_input(
    "Enter required amount (ml)",
    min_value=1.0,
    max_value=500.0,
    value=25.0,
    step=1.0
)

st.write(
    f"Selected dosage: **{dosage:.0f} ml**"
)


# ==========================================
# SPRAY BUTTON
# ==========================================

if st.button(
    "🚿 SPRAY",
    type="primary",
    use_container_width=True
):

    st.info(
        f"Spray button pressed for {dosage:.0f} ml"
    )


# ==========================================
# SPRAY STATUS
# ==========================================

st.markdown("### 📡 Spray Status")

st.success("🟢 Ready")
