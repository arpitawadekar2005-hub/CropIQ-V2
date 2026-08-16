import streamlit as st
import requests


# =====================================================
# CONFIGURATION
# =====================================================

BACKEND_URL = "https://cropiq-backend-mecl.onrender.com"


# =====================================================
# PAGE CONFIG
# =====================================================

st.set_page_config(
    page_title="CropIQ",
    page_icon="🌱",
    layout="centered"
)


# =====================================================
# GET SYSTEM STATE
# =====================================================

def get_state():

    try:

        response = requests.get(
            BACKEND_URL + "/state",
            timeout=10
        )

        if response.status_code == 200:

            return response.json()

    except Exception:

        pass

    return None


# =====================================================
# DISPLAY STATUS
# =====================================================

def show_status():

    state = get_state()

    if state is None:

        st.error(
            "Backend unavailable"
        )

        return

    current_status = state.get(
        "status",
        "Ready"
    )

    sprayed_amount = state.get(
        "sprayed_amount",
        0.0
    )

    if current_status == "Ready":

        st.success(
            "🟢 Ready"
        )

    elif current_status == "Spraying...":

        st.warning(
            "🟡 Spraying..."
        )

        if sprayed_amount > 0:

            st.write(
                f"Dispensed: "
                f"**{sprayed_amount:.2f} ml**"
            )

    elif current_status == "Completed":

        st.success(
            "🟢 Completed"
        )

        st.write(
            f"**{sprayed_amount:.2f} ml sprayed**"
        )

    else:

        st.info(
            current_status
        )


# =====================================================
# TITLE
# =====================================================

st.title("🌱 CropIQ")

st.subheader(
    "Precision Spraying Dashboard"
)


# =====================================================
# BACKEND CONNECTION
# =====================================================

try:

    response = requests.get(
        BACKEND_URL + "/test",
        timeout=10
    )

    if response.status_code == 200:

        st.success(
            "Backend connected successfully ✅"
        )

    else:

        st.error(
            "Backend connection failed"
        )

except Exception:

    st.error(
        "Backend unavailable"
    )


# =====================================================
# PLANT IMAGE
# =====================================================

st.markdown("### 🌿 Plant Image")

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
            "Waiting for Raspberry Pi camera image..."
        )

except Exception:

    st.warning(
        "Unable to load plant image."
    )


# =====================================================
# DOSAGE
# =====================================================

st.markdown("### 💧 Dosage")

dosage = st.number_input(
    "Enter required spray amount (ml)",
    min_value=1.0,
    max_value=500.0,
    value=25.0,
    step=1.0
)


# =====================================================
# SPRAY BUTTON
# =====================================================

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

            st.success(
                f"Spray started: "
                f"{dosage:.0f} ml"
            )

            st.rerun()

        elif response.status_code == 409:

            st.warning(
                "A spray operation is already running."
            )

        else:

            st.error(
                response.text
            )

    except Exception as e:

        st.error(
            f"Backend connection failed: {e}"
        )


# =====================================================
# STATUS
# =====================================================

st.markdown("### 📡 Spray Status")

show_status()
