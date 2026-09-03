import streamlit as st
import requests


# ============================================================
# CONFIGURATION
# ============================================================

BACKEND_URL = "https://cropiq-backend-mecl.onrender.com"


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="CropIQ | Precision Agriculture",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    /* ========================================================
       GLOBAL
    ======================================================== */

    .stApp {
        background-color: #F4F7F3;
    }

    .block-container {
        max-width: 1450px;
        padding-top: 2rem;
        padding-bottom: 3rem;
        padding-left: 3rem;
        padding-right: 3rem;
    }

    /* Hide Streamlit branding */
    #MainMenu {
        visibility: hidden;
    }

    footer {
        visibility: hidden;
    }


    /* ========================================================
       TITLE
    ======================================================== */

    .cropiq-title {
        color: #173B29;
        font-size: 42px;
        font-weight: 800;
        letter-spacing: -1px;
        margin-bottom: 0;
    }

    .cropiq-subtitle {
        color: #6F7D74;
        font-size: 15px;
        margin-top: -5px;
        margin-bottom: 25px;
    }


    /* ========================================================
       SECTION HEADINGS
    ======================================================== */

    .section-title {
        color: #173B29;
        font-size: 21px;
        font-weight: 750;
        margin-top: 28px;
        margin-bottom: 12px;
    }


    /* ========================================================
       STREAMLIT CONTAINERS
    ======================================================== */

    [data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #FFFFFF;
        border: 1px solid #DFE8E1;
        border-radius: 16px;
        box-shadow: 0 4px 16px rgba(23, 59, 41, 0.05);
    }


    /* ========================================================
       METRICS
    ======================================================== */

    [data-testid="stMetric"] {
        padding: 10px;
    }

    [data-testid="stMetricLabel"] {
        color: #718078 !important;
        font-size: 12px !important;
        font-weight: 700 !important;
    }

    [data-testid="stMetricValue"] {
        color: #173B29 !important;
        font-size: 26px !important;
        font-weight: 800 !important;
    }


    /* ========================================================
       BUTTONS
    ======================================================== */

    .stButton > button {
        width: 100%;
        min-height: 48px;
        border-radius: 10px;
        font-weight: 700;
        font-size: 14px;
    }

    .stButton > button:hover {
        transform: translateY(-1px);
    }


    /* ========================================================
       PRIMARY BUTTON
    ======================================================== */

    .stButton > button[kind="primary"] {
        background-color: #1F7A4D;
        border-color: #1F7A4D;
        color: white;
    }

    .stButton > button[kind="primary"]:hover {
        background-color: #17623D;
        border-color: #17623D;
        color: white;
    }


    /* ========================================================
       STATUS
    ======================================================== */

    .status-ready {
        background-color: #ECFDF3;
        border: 1px solid #BBF7D0;
        color: #15803D;
        border-radius: 10px;
        padding: 14px 16px;
        font-weight: 700;
        font-size: 15px;
    }

    .status-spraying {
        background-color: #FFF7ED;
        border: 1px solid #FED7AA;
        color: #C2410C;
        border-radius: 10px;
        padding: 14px 16px;
        font-weight: 700;
        font-size: 15px;
    }

    .status-completed {
        background-color: #EFF6FF;
        border: 1px solid #BFDBFE;
        color: #2563EB;
        border-radius: 10px;
        padding: 14px 16px;
        font-weight: 700;
        font-size: 15px;
    }

    .status-offline {
        background-color: #FEF2F2;
        border: 1px solid #FECACA;
        color: #DC2626;
        border-radius: 10px;
        padding: 14px 16px;
        font-weight: 700;
        font-size: 15px;
    }


    /* ========================================================
       INFO
    ======================================================== */

    .info-text {
        color: #6F7D74;
        font-size: 13px;
        line-height: 1.5;
    }


    /* ========================================================
       WORKFLOW CARDS
    ======================================================== */

    .workflow-number {
        color: #1F7A4D;
        font-size: 13px;
        font-weight: 800;
    }


    /* ========================================================
       FOOTER
    ======================================================== */

    .footer {
        text-align: center;
        color: #89958C;
        font-size: 12px;
        margin-top: 20px;
    }


    /* ========================================================
       MOBILE
    ======================================================== */

    @media (max-width: 800px) {

        .block-container {
            padding-left: 1rem;
            padding-right: 1rem;
        }

        .cropiq-title {
            font-size: 32px;
        }

    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# BACKEND FUNCTIONS
# ============================================================

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


def capture_image():

    try:

        response = requests.post(
            BACKEND_URL + "/capture",
            timeout=15
        )

        if response.status_code == 200:

            st.success(
                "📷 Capture command sent to Raspberry Pi."
            )

        elif response.status_code == 409:

            st.warning(
                "Another command is already pending."
            )

        else:

            st.error(response.text)

    except Exception as e:

        st.error(
            f"Backend connection failed: {e}"
        )


def spray(amount):

    try:

        response = requests.post(
            BACKEND_URL + "/spray",
            json={
                "amount_ml": amount
            },
            timeout=15
        )

        if response.status_code == 200:

            data = response.json()

            st.success(
                f"🚿 Spray command sent: "
                f"{data['amount_ml']:.0f} ml"
            )

        elif response.status_code == 409:

            st.warning(
                "A spray operation is already running."
            )

        else:

            st.error(response.text)

    except Exception as e:

        st.error(
            f"Backend connection failed: {e}"
        )


# ============================================================
# GET INITIAL STATE
# ============================================================

state = get_state()

if state is not None:

    pi_online = True

    current_status = state.get(
        "status",
        "Ready"
    )

    sprayed_amount = state.get(
        "sprayed_amount",
        0.0
    )

else:

    pi_online = False

    current_status = "Offline"

    sprayed_amount = 0.0


# ============================================================
# HEADER
# ============================================================

header_left, header_right = st.columns(
    [4, 1],
    vertical_alignment="center"
)


with header_left:

    st.markdown(
        """
        <div class="cropiq-title">
            🌱 CropIQ
        </div>

        <div class="cropiq-subtitle">
            Precision Agriculture Intelligence Platform
        </div>
        """,
        unsafe_allow_html=True
    )


with header_right:

    if pi_online:

        st.success(
            "● SYSTEM ONLINE"
        )

    else:

        st.error(
            "● SYSTEM OFFLINE"
        )


# ============================================================
# PAGE INTRODUCTION
# ============================================================

st.markdown(
    """
    <div class="section-title">
        Precision Spraying Control
    </div>

    <div class="info-text">
        Monitor the plant, capture images, configure spray dosage,
        and control the precision spraying system.
    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# SYSTEM OVERVIEW
# ============================================================

st.markdown(
    '<div class="section-title">System Overview</div>',
    unsafe_allow_html=True
)


metric1, metric2, metric3, metric4 = st.columns(
    4,
    gap="medium"
)


# ------------------------------------------------------------
# SPRAYER STATUS
# ------------------------------------------------------------

with metric1:

    with st.container(border=True):

        if current_status == "Ready":

            display_status = "READY"

        elif current_status == "Spraying...":

            display_status = "SPRAYING"

        elif current_status == "Completed":

            display_status = "COMPLETED"

        else:

            display_status = "OFFLINE"

        st.metric(
            label="🚿 SPRAYER STATUS",
            value=display_status
        )

        st.caption(
            "Current operation"
        )


# ------------------------------------------------------------
# LAST DISPENSED
# ------------------------------------------------------------

with metric2:

    with st.container(border=True):

        st.metric(
            label="💧 LAST DISPENSED",
            value=f"{sprayed_amount:.1f} ml"
        )

        st.caption(
            "Latest spray quantity"
        )


# ------------------------------------------------------------
# CAMERA
# ------------------------------------------------------------

with metric3:

    with st.container(border=True):

        camera_status = (
            "READY"
            if pi_online
            else "OFFLINE"
        )

        st.metric(
            label="📷 CAMERA",
            value=camera_status
        )

        st.caption(
            "Plant imaging system"
        )


# ------------------------------------------------------------
# RASPBERRY PI
# ------------------------------------------------------------

with metric4:

    with st.container(border=True):

        device_status = (
            "ONLINE"
            if pi_online
            else "OFFLINE"
        )

        st.metric(
            label="📡 RASPBERRY PI",
            value=device_status
        )

        st.caption(
            "Hardware connection"
        )


# ============================================================
# PLANT MONITORING & CONTROL
# ============================================================

st.markdown(
    '<div class="section-title">Plant Monitoring & Control</div>',
    unsafe_allow_html=True
)


image_column, control_column = st.columns(
    [2.1, 1],
    gap="large"
)


# ============================================================
# PLANT IMAGE
# ============================================================

with image_column:

    with st.container(border=True):

        image_title, image_live = st.columns(
            [4, 1],
            vertical_alignment="center"
        )

        with image_title:

            st.subheader(
                "🌿 Latest Plant Image"
            )

        with image_live:

            if pi_online:
                st.success("LIVE")
            else:
                st.error("OFFLINE")


        @st.fragment(run_every="2s")
        def show_latest_image():

            try:

                response = requests.get(
                    BACKEND_URL + "/latest-image",
                    timeout=10
                )

                if response.status_code == 200:

                    st.image(
                        response.content,
                        use_container_width=True
                    )

                elif response.status_code == 404:

                    st.info(
                        "🌱 No plant image available yet. "
                        "Capture an image to begin monitoring."
                    )

                else:

                    st.warning(
                        "Unable to load the latest plant image."
                    )

            except Exception:

                st.warning(
                    "📡 Waiting for Raspberry Pi..."
                )


        show_latest_image()


# ============================================================
# SPRAY CONTROL
# ============================================================

with control_column:

    with st.container(border=True):

        st.subheader(
            "🚿 Precision Spray"
        )

        st.markdown(
            """
            <div class="info-text">
                Configure the required spray quantity
                and activate the precision sprayer.
            </div>
            """,
            unsafe_allow_html=True
        )

        st.divider()


        dosage = st.number_input(
            "Spray dosage (ml)",
            min_value=1.0,
            max_value=500.0,
            value=25.0,
            step=1.0,
            format="%.0f",
            help="Enter the required spray amount in millilitres."
        )


        st.caption(
            "Allowed range: 1 – 500 ml"
        )


        st.write("")


        # ----------------------------------------------------
        # CAPTURE
        # ----------------------------------------------------

        if st.button(
            "📷  CAPTURE PLANT IMAGE",
            use_container_width=True
        ):

            capture_image()


        # ----------------------------------------------------
        # SPRAY
        # ----------------------------------------------------

        if st.button(
            "🚿  START PRECISION SPRAY",
            type="primary",
            use_container_width=True
        ):

            spray(dosage)


        st.info(
            "The selected dosage will be sent "
            "to the Raspberry Pi sprayer."
        )


# ============================================================
# LIVE SPRAY STATUS
# ============================================================

st.markdown(
    '<div class="section-title">Live Spray Status</div>',
    unsafe_allow_html=True
)


@st.fragment(run_every="2s")
def show_status():

    state = get_state()


    # --------------------------------------------------------
    # BACKEND OFFLINE
    # --------------------------------------------------------

    if state is None:

        st.markdown(
            """
            <div class="status-offline">
                🔴 BACKEND UNAVAILABLE
            </div>
            """,
            unsafe_allow_html=True
        )

        st.caption(
            "Unable to communicate with the CropIQ control system."
        )

        return


    # --------------------------------------------------------
    # CURRENT STATE
    # --------------------------------------------------------

    status = state.get(
        "status",
        "Ready"
    )

    amount = state.get(
        "sprayed_amount",
        0.0
    )


    # --------------------------------------------------------
    # READY
    # --------------------------------------------------------

    if status == "Ready":

        st.markdown(
            """
            <div class="status-ready">
                🟢 READY
            </div>
            """,
            unsafe_allow_html=True
        )

        st.caption(
            "System is ready for the next precision spraying operation."
        )


    # --------------------------------------------------------
    # SPRAYING
    # --------------------------------------------------------

    elif status == "Spraying...":

        st.markdown(
            """
            <div class="status-spraying">
                🟠 SPRAYING IN PROGRESS
            </div>
            """,
            unsafe_allow_html=True
        )

        st.write(
            f"💧 Dispensed: **{amount:.2f} ml**"
        )


    # --------------------------------------------------------
    # COMPLETED
    # --------------------------------------------------------

    elif status == "Completed":

        st.markdown(
            """
            <div class="status-completed">
                🔵 SPRAY COMPLETED
            </div>
            """,
            unsafe_allow_html=True
        )

        st.write(
            f"💧 Total dispensed: **{amount:.2f} ml**"
        )


    # --------------------------------------------------------
    # OTHER STATUS
    # --------------------------------------------------------

    else:

        st.info(
            f"Current status: {status}"
        )


show_status()


# ============================================================
# CROPIQ WORKFLOW
# ============================================================

st.markdown(
    '<div class="section-title">CropIQ Workflow</div>',
    unsafe_allow_html=True
)


workflow1, workflow2, workflow3, workflow4 = st.columns(
    4,
    gap="medium"
)


# ------------------------------------------------------------
# STEP 1
# ------------------------------------------------------------

with workflow1:

    with st.container(border=True):

        st.markdown(
            '<div class="workflow-number">STEP 01</div>',
            unsafe_allow_html=True
        )

        st.subheader("📷 Capture")

        st.caption(
            "Capture the latest plant image using the Raspberry Pi camera."
        )


# ------------------------------------------------------------
# STEP 2
# ------------------------------------------------------------

with workflow2:

    with st.container(border=True):

        st.markdown(
            '<div class="workflow-number">STEP 02</div>',
            unsafe_allow_html=True
        )

        st.subheader("🌿 Analyze")

        st.caption(
            "Analyze the captured plant image to identify the target."
        )


# ------------------------------------------------------------
# STEP 3
# ------------------------------------------------------------

with workflow3:

    with st.container(border=True):

        st.markdown(
            '<div class="workflow-number">STEP 03</div>',
            unsafe_allow_html=True
        )

        st.subheader("🎯 Target")

        st.caption(
            "Determine the treatment area and required spray quantity."
        )


# ------------------------------------------------------------
# STEP 4
# ------------------------------------------------------------

with workflow4:

    with st.container(border=True):

        st.markdown(
            '<div class="workflow-number">STEP 04</div>',
            unsafe_allow_html=True
        )

        st.subheader("🚿 Spray")

        st.caption(
            "Apply the selected spray dosage to the target."
        )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.markdown(
    """
    <div class="footer">
        🌱 CropIQ &nbsp;•&nbsp;
        Precision Agriculture &nbsp;•&nbsp;
        AI-powered targeted spraying
    </div>
    """,
    unsafe_allow_html=True
)
