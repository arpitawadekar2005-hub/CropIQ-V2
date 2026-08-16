import streamlit as st
import requests


# =====================================================
# CONFIGURATION
# =====================================================

BACKEND_URL = "https://cropiq-backend-mecl.onrender.com"


# =====================================================
# PAGE CONFIGURATION
# =====================================================

st.set_page_config(
    page_title="CropIQ",
    page_icon="🌱",
    layout="centered"
)


# =====================================================
# TITLE
# =====================================================

st.title("🌱 CropIQ")

st.subheader(
    "Precision Spraying Dashboard"
)


# =====================================================
# BACKEND TEST
# =====================================================

def check_backend():

    try:

        response = requests.get(
            BACKEND_URL + "/test",
            timeout=10
        )

        return response.status_code == 200

    except Exception:

        return False


if check_backend():

    st.success(
        "Backend connected successfully ✅"
    )

else:

    st.error(
        "Backend connection unavailable"
    )


# =====================================================
# CAPTURE SECTION
# =====================================================

st.markdown("### 🌿 Plant Image")


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


# =====================================================
# DOSAGE SECTION
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

            data = response.json()

            st.success(
                f"Spray command sent: "
                f"{data['amount_ml']:.0f} ml"
            )

        elif response.status_code == 409:

            st.warning(
                "Another operation is already running."
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
# LIVE STATUS + IMAGE
# =====================================================

@st.fragment(run_every="2s")
def live_dashboard():

    # ---------------------------------------------
    # GET SYSTEM STATE
    # ---------------------------------------------

    try:

        state_response = requests.get(
            BACKEND_URL + "/state",
            timeout=10
        )

        if state_response.status_code == 200:

            state = state_response.json()

            current_status = state.get(
                "status",
                "Ready"
            )

            sprayed_amount = state.get(
                "sprayed_amount",
                0.0
            )

        else:

            current_status = "Backend unavailable"

            sprayed_amount = 0.0

    except Exception:

        current_status = "Backend unavailable"

        sprayed_amount = 0.0


    # ---------------------------------------------
    # SPRAY STATUS
    # ---------------------------------------------

    st.markdown("### 📡 Spray Status")


    if current_status == "Ready":

        st.success(
            "🟢 Ready"
        )


    elif current_status == "Spraying...":

        st.warning(
            "🟡 Spraying..."
        )

        st.write(
            f"Sprayed: "
            f"**{sprayed_amount:.2f} ml**"
        )


    elif current_status == "Completed":

        st.success(
            "🟢 Completed"
        )

        st.write(
            f"**{sprayed_amount:.2f} ml sprayed**"
        )


    elif current_status == "Backend unavailable":

        st.error(
            "🔴 Backend unavailable"
        )


    else:

        st.info(
            current_status
        )


    # ---------------------------------------------
    # LATEST PLANT IMAGE
    # ---------------------------------------------

    st.markdown("### 🖼️ Latest Plant Image")


    try:

        image_response = requests.get(

            BACKEND_URL + "/latest-image",

            timeout=10
        )

        if image_response.status_code == 200:

            st.image(

                image_response.content,

                caption="Latest captured plant image",

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


# Run live dashboard
live_dashboard()
