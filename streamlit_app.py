import streamlit as st
import requests
from datetime import datetime


# ============================================================
# CONFIGURATION
# ============================================================

BACKEND_URL = "https://cropiq-backend-mecl.onrender.com"


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="CropIQ | Smart Spraying",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown("""
<style>

/* ---------------------------------------------------------
   MAIN PAGE
--------------------------------------------------------- */

.stApp {
    background:
        radial-gradient(circle at 10% 10%,
        rgba(34, 197, 94, 0.08),
        transparent 30%),

        radial-gradient(circle at 90% 20%,
        rgba(16, 185, 129, 0.07),
        transparent 25%),

        #f6faf7;
}


/* ---------------------------------------------------------
   REMOVE STREAMLIT DEFAULT TOP SPACE
--------------------------------------------------------- */

.block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
    max-width: 1250px;
}


/* ---------------------------------------------------------
   HEADER
--------------------------------------------------------- */

.crop-header {

    background:
        linear-gradient(
            135deg,
            #064e3b 0%,
            #047857 50%,
            #059669 100%
        );

    padding: 28px 35px;

    border-radius: 22px;

    margin-bottom: 25px;

    box-shadow:
        0 12px 35px rgba(6, 78, 59, 0.20);

    color: white;
}


.crop-title {

    font-size: 42px;

    font-weight: 800;

    margin: 0;

    letter-spacing: -1px;
}


.crop-subtitle {

    font-size: 16px;

    margin-top: 5px;

    opacity: 0.85;
}


/* ---------------------------------------------------------
   SECTION TITLE
--------------------------------------------------------- */

.section-title {

    font-size: 19px;

    font-weight: 700;

    color: #16352b;

    margin-bottom: 12px;
}


/* ---------------------------------------------------------
   CARDS
--------------------------------------------------------- */

.dashboard-card {

    background: rgba(255,255,255,0.95);

    border: 1px solid rgba(15, 118, 86, 0.10);

    border-radius: 20px;

    padding: 22px;

    box-shadow:
        0 8px 30px rgba(0,0,0,0.055);

    transition:
        transform 0.25s ease,
        box-shadow 0.25s ease;

    margin-bottom: 15px;
}


.dashboard-card:hover {

    transform: translateY(-3px);

    box-shadow:
        0 14px 35px rgba(0,0,0,0.09);
}


/* ---------------------------------------------------------
   STATUS BOXES
--------------------------------------------------------- */

.status-ready {

    background:
        linear-gradient(
            135deg,
            #ecfdf5,
            #d1fae5
        );

    border: 1px solid #a7f3d0;

    border-radius: 16px;

    padding: 20px;

    color: #065f46;
}


.status-spraying {

    background:
        linear-gradient(
            135deg,
            #fffbeb,
            #fef3c7
        );

    border: 1px solid #fde68a;

    border-radius: 16px;

    padding: 20px;

    color: #92400e;

    animation: pulse 1.8s infinite;
}


.status-completed {

    background:
        linear-gradient(
            135deg,
            #ecfdf5,
            #bbf7d0
        );

    border: 1px solid #86efac;

    border-radius: 16px;

    padding: 20px;

    color: #166534;
}


.status-error {

    background: #fef2f2;

    border: 1px solid #fecaca;

    border-radius: 16px;

    padding: 20px;

    color: #991b1b;
}


/* ---------------------------------------------------------
   STATUS ANIMATION
--------------------------------------------------------- */

@keyframes pulse {

    0% {
        box-shadow:
            0 0 0 0 rgba(245, 158, 11, 0.25);
    }

    70% {
        box-shadow:
            0 0 0 12px rgba(245, 158, 11, 0);
    }

    100% {
        box-shadow:
            0 0 0 0 rgba(245, 158, 11, 0);
    }
}


/* ---------------------------------------------------------
   STATUS DOT
--------------------------------------------------------- */

.green-dot {

    display: inline-block;

    width: 10px;

    height: 10px;

    background: #22c55e;

    border-radius: 50%;

    margin-right: 8px;

    box-shadow:
        0 0 8px rgba(34,197,94,0.7);
}


.yellow-dot {

    display: inline-block;

    width: 10px;

    height: 10px;

    background: #f59e0b;

    border-radius: 50%;

    margin-right: 8px;
}


.red-dot {

    display: inline-block;

    width: 10px;

    height: 10px;

    background: #ef4444;

    border-radius: 50%;

    margin-right: 8px;
}


/* ---------------------------------------------------------
   BUTTONS
--------------------------------------------------------- */

.stButton > button {

    border-radius: 12px;

    height: 48px;

    font-weight: 700;

    font-size: 15px;

    transition: all 0.2s ease;

    border: none;
}


.stButton > button:hover {

    transform: translateY(-2px);

    box-shadow:
        0 8px 20px rgba(0,0,0,0.12);
}


/* ---------------------------------------------------------
   INPUT
--------------------------------------------------------- */

.stNumberInput input {

    border-radius: 12px !important;

    font-size: 17px !important;

    font-weight: 600 !important;
}


/* ---------------------------------------------------------
   METRIC
--------------------------------------------------------- */

[data-testid="stMetric"] {

    background: white;

    border-radius: 15px;

    padding: 15px;

    border:
        1px solid rgba(15,118,86,0.08);
}


/* ---------------------------------------------------------
   IMAGE
--------------------------------------------------------- */

[data-testid="stImage"] img {

    border-radius: 16px;

    box-shadow:
        0 8px 25px rgba(0,0,0,0.10);
}


/* ---------------------------------------------------------
   FOOTER
--------------------------------------------------------- */

.footer {

    text-align: center;

    color: #718078;

    font-size: 13px;

    margin-top: 35px;

    padding-top: 20px;

    border-top:
        1px solid rgba(0,0,0,0.06);
}


/* ---------------------------------------------------------
   MOBILE
--------------------------------------------------------- */

@media (max-width: 768px) {

    .crop-title {
        font-size: 32px;
    }

    .crop-header {
        padding: 22px;
    }

}

</style>
""", unsafe_allow_html=True)


# ============================================================
# FUNCTIONS
# ============================================================

def backend_connected():

    try:

        response = requests.get(
            BACKEND_URL + "/test",
            timeout=8
        )

        return response.status_code == 200

    except Exception:

        return False


def send_capture_command():

    try:

        response = requests.post(
            BACKEND_URL + "/capture",
            timeout=15
        )

        return response

    except Exception:

        return None


def send_spray_command(amount):

    try:

        response = requests.post(

            BACKEND_URL + "/spray",

            json={
                "amount_ml": amount
            },

            timeout=15
        )

        return response

    except Exception:

        return None


# ============================================================
# HEADER
# ============================================================

st.markdown(
    """
    <div class="crop-header">

        <div class="crop-title">
            🌿 CropIQ
        </div>

        <div class="crop-subtitle">
            Intelligent Precision Spraying System
            &nbsp; • &nbsp;
            Raspberry Pi Powered
        </div>

    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# CONNECTION STATUS
# ============================================================

connected = backend_connected()


if connected:

    st.markdown(
        """
        <div style="
            display:flex;
            align-items:center;
            margin-bottom:20px;
            color:#166534;
            font-weight:600;
        ">

            <span class="green-dot"></span>

            System Online

        </div>
        """,
        unsafe_allow_html=True
    )

else:

    st.markdown(
        """
        <div style="
            margin-bottom:20px;
            color:#991b1b;
            font-weight:600;
        ">

            <span class="red-dot"></span>

            Backend Offline

        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# MAIN COLUMNS
# ============================================================

left_column, right_column = st.columns(
    [1.55, 1],
    gap="large"
)


# ============================================================
# LEFT SIDE — CAMERA
# ============================================================

with left_column:

    st.markdown(
        '<div class="section-title">📷 Plant Camera</div>',
        unsafe_allow_html=True
    )


    # --------------------------------------------------------
    # CAPTURE BUTTON
    # --------------------------------------------------------

    if st.button(
        "📸 Capture Plant Image",
        use_container_width=True
    ):

        response = send_capture_command()

        if response is None:

            st.error(
                "Unable to communicate with backend."
            )

        elif response.status_code == 200:

            st.success(
                "Capture command sent to Raspberry Pi."
            )

        elif response.status_code == 409:

            st.warning(
                "Another operation is currently running."
            )

        else:

            st.error(
                "Capture command failed."
            )


    # --------------------------------------------------------
    # LIVE CAMERA IMAGE
    # --------------------------------------------------------

    @st.fragment(run_every="2s")
    def live_image():

        try:

            response = requests.get(

                BACKEND_URL + "/latest-image",

                timeout=8
            )

            if response.status_code == 200:

                st.image(
                    response.content,
                    caption="Latest captured plant image",
                    use_container_width=True
                )

            else:

                st.markdown(
                    """
                    <div class="dashboard-card"
                         style="text-align:center;
                                padding:70px 20px;">

                        <div style="font-size:45px;">
                            🌱
                        </div>

                        <div style="
                            font-size:18px;
                            font-weight:700;
                            margin-top:10px;
                            color:#315b4b;
                        ">
                            No Image Captured
                        </div>

                        <div style="
                            color:#718078;
                            margin-top:5px;
                        ">
                            Press Capture Plant Image
                            to take a photo.
                        </div>

                    </div>
                    """,
                    unsafe_allow_html=True
                )

        except Exception:

            st.warning(
                "Camera image unavailable."
            )


    live_image()


# ============================================================
# RIGHT SIDE — SPRAY CONTROL
# ============================================================

with right_column:

    st.markdown(
        '<div class="section-title">💧 Spray Control</div>',
        unsafe_allow_html=True
    )


    # --------------------------------------------------------
    # DOSAGE
    # --------------------------------------------------------

    dosage = st.number_input(

        "Required Dosage (ml)",

        min_value=1.0,

        max_value=500.0,

        value=25.0,

        step=1.0
    )


    # --------------------------------------------------------
    # SELECTED DOSAGE
    # --------------------------------------------------------

    st.metric(
        label="Selected Dosage",
        value=f"{dosage:.0f} ml"
    )


    st.write("")


    # --------------------------------------------------------
    # SPRAY BUTTON
    # --------------------------------------------------------

    if st.button(

        "🚿 START SPRAY",

        type="primary",

        use_container_width=True
    ):

        response = send_spray_command(
            dosage
        )

        if response is None:

            st.error(
                "Unable to communicate with backend."
            )

        elif response.status_code == 200:

            st.success(
                f"{dosage:.0f} ml spray command sent."
            )

        elif response.status_code == 409:

            st.warning(
                "Another operation is already running."
            )

        else:

            st.error(
                "Spray command failed."
            )


    st.write("")


    # ========================================================
    # LIVE SPRAY STATUS
    # ========================================================

    @st.fragment(run_every="2s")
    def live_status():

        try:

            response = requests.get(

                BACKEND_URL + "/state",

                timeout=8
            )

            if response.status_code != 200:

                st.markdown(
                    """
                    <div class="status-error">

                        <b>
                            <span class="red-dot"></span>
                            System Error
                        </b>

                        <br><br>

                        Unable to retrieve spray status.

                    </div>
                    """,
                    unsafe_allow_html=True
                )

                return


            data = response.json()


            status = data.get(
                "status",
                "Ready"
            )


            sprayed_amount = data.get(
                "sprayed_amount",
                0.0
            )


            # -----------------------------------------------
            # READY
            # -----------------------------------------------

            if status == "Ready":

                st.markdown(
                    """
                    <div class="status-ready">

                        <div style="
                            font-size:17px;
                            font-weight:700;
                        ">

                            <span class="green-dot"></span>

                            Ready

                        </div>

                        <div style="
                            margin-top:8px;
                            font-size:14px;
                        ">

                            System is ready for spraying.

                        </div>

                    </div>
                    """,
                    unsafe_allow_html=True
                )


            # -----------------------------------------------
            # SPRAYING
            # -----------------------------------------------

            elif status == "Spraying...":

                st.markdown(
                    f"""
                    <div class="status-spraying">

                        <div style="
                            font-size:17px;
                            font-weight:700;
                        ">

                            <span class="yellow-dot"></span>

                            Spraying...

                        </div>

                        <div style="
                            margin-top:10px;
                            font-size:14px;
                        ">

                            Pump and flow sensor active

                        </div>

                    </div>
                    """,
                    unsafe_allow_html=True
                )


            # -----------------------------------------------
            # COMPLETED
            # -----------------------------------------------

            elif status == "Completed":

                st.markdown(
                    f"""
                    <div class="status-completed">

                        <div style="
                            font-size:17px;
                            font-weight:700;
                        ">

                            ✓ Completed

                        </div>

                        <div style="
                            margin-top:10px;
                            font-size:22px;
                            font-weight:800;
                        ">

                            {sprayed_amount:.2f} ml

                        </div>

                        <div style="
                            font-size:13px;
                            margin-top:3px;
                        ">

                            successfully sprayed

                        </div>

                    </div>
                    """,
                    unsafe_allow_html=True
                )


            # -----------------------------------------------
            # OTHER
            # -----------------------------------------------

            else:

                st.info(
                    status
                )


        except Exception:

            st.markdown(
                """
                <div class="status-error">

                    <span class="red-dot"></span>

                    Unable to connect to system

                </div>
                """,
                unsafe_allow_html=True
            )


    st.markdown(
        '<div class="section-title">📡 System Status</div>',
        unsafe_allow_html=True
    )

    live_status()


# ============================================================
# SYSTEM INFORMATION
# ============================================================

st.write("")

st.markdown("---")

st.markdown(
    '<div class="section-title">⚙️ System Information</div>',
    unsafe_allow_html=True
)


info1, info2, info3, info4 = st.columns(4)


with info1:

    st.metric(
        "Controller",
        "Pi 3B+"
    )


with info2:

    st.metric(
        "Flow Calibration",
        "47.64 pulse/ml"
    )


with info3:

    st.metric(
        "Camera",
        "USB"
    )


with info4:

    if connected:

        st.metric(
            "Connection",
            "Online"
        )

    else:

        st.metric(
            "Connection",
            "Offline"
        )


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    f"""
    <div class="footer">

        🌿 <b>CropIQ</b>
        &nbsp; • &nbsp;
        Precision Agriculture System

        <br>

        Dashboard updated:
        {datetime.now().strftime("%d %b %Y • %H:%M")}

    </div>
    """,
    unsafe_allow_html=True
)
