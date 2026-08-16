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

# =====================================================
# PLANT IMAGE
# =====================================================

st.markdown("### 🌿 Plant Image")


# -----------------------------------------
# CAPTURE BUTTON
# -----------------------------------------

if st.button(
    "📷 CAPTURE",
    use_container_width=True
):

    try:

        response = requests.post(
            BACKEND_URL + "/capture",
            timeout=15
        )

        if response.status_code == 200:

            st.success(
                "Capture command sent to Raspberry Pi."
            )

        elif response.status_code == 409:

            st.warning(
                "Another operation is currently running."
            )

        else:

            st.error(
                response.text
            )

    except Exception as e:

        st.error(
            f"Backend connection failed: {e}"
        )


# -----------------------------------------
# DISPLAY LATEST IMAGE
# -----------------------------------------

try:

    image_response = requests.get(
        BACKEND_URL + "/latest-image",
        timeout=10
    )

    if image_response.status_code == 200:

        st.image(
            image_response.content,
            caption="Latest Plant Image",
            use_container_width=True
        )

    else:

        st.info(
            "No plant image captured yet."
        )

except Exception:

    st.warning(
        "Unable to load plant image."
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

    try:

        response = requests.post(
            BACKEND_URL + "/spray",
            json={
                "amount_ml": dosage
            },
            timeout=15
        )

        if response.status_code == 200:

            data = response.json()

            st.success(
                f"Spray command sent: "
                f"{data['amount_ml']:.0f} ml"
            )

        elif response.status_code == 409:

            st.warning(
                "A spray command is already pending."
            )

        else:

            st.error(
                response.text
            )

    except Exception as e:

        st.error(
            f"Backend connection failed: {e}"
        )


# ==========================================
# SPRAY STATUS
# ==========================================

st.markdown("### 📡 Spray Status")

st.success("🟢 Ready")
