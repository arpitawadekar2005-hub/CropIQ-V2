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

/* =========================================================
   MAIN APP
========================================================= */

.stApp {
    background-color: #f4f7f3;
}

.block-container {
    max-width: 1450px;
    padding: 2rem 3rem 3rem 3rem;
}


/* =========================================================
   HIDE STREAMLIT DEFAULT UI
========================================================= */

#MainMenu {
    visibility: hidden;
}

footer {
    visibility: hidden;
}


/* =========================================================
   HEADER
========================================================= */

.header-box {
    background-color: white;
    border: 1px solid #dfe8e1;
    border-radius: 20px;
    padding: 22px 28px;
    margin-bottom: 28px;
    box-shadow: 0 4px 18px rgba(30, 60, 40, 0.06);
}

.header-title {
    font-size: 34px;
    font-weight: 800;
    color: #173b29;
    margin: 0;
}

.header-subtitle {
    color: #718078;
    font-size: 14px;
    margin-top: 5px;
}


/* =========================================================
   SECTION HEADINGS
========================================================= */

.section-title {
    font-size: 21px;
    font-weight: 800;
    color: #173b29;
    margin-top: 25px;
    margin-bottom: 12px;
}

.small-description {
    color: #718078;
    font-size: 14px;
    margin-bottom: 18px;
}


/* =========================================================
   METRIC CONTAINERS
========================================================= */

[data-testid="stVerticalBlockBorderWrapper"] {
    background-color: white;
    border: 1px solid #dfe8e1;
    border-radius: 16px;
    box-shadow: 0 4px 15px rgba(30, 60, 40, 0.05);
}


/* =========================================================
   METRIC
========================================================= */

[data-testid="stMetric"] {
    padding: 5px;
}

[data-testid="stMetricLabel"] {
    color: #718078 !important;
    font-size: 12px !important;
    font-weight: 700 !important;
}

[data-testid="stMetricValue"] {
    color: #173b29 !important;
    font-size: 25px !important;
    font-weight: 800 !important;
}


/* =========================================================
   IMAGE CONTAINER
========================================================= */

.image-box {
    background-color: white;
    border: 1px solid #dfe8e1;
    border-radius: 18px;
    padding: 18px;
    box-shadow: 0 4px 18px rgba(30, 60, 40, 0.05);
}


/* =========================================================
   CONTROL CONTAINER
========================================================= */

.control-box {
    background-color: white;
    border: 1px solid #dfe8e1;
    border-radius: 18px;
    padding: 22px;
    box-shadow: 0 4px 18px rgba(30, 60, 40, 0.05);
}


/* =========================================================
   BUTTONS
========================================================= */

.stButton > button {
    width: 100%;
    min-height: 48px;
    border-radius: 10px;
    font-weight: 700;
    font-size: 14px;
}


/* =========================================================
   PRIMARY BUTTON
========================================================= */

.stButton > button[kind="primary"] {
    background-color: #1f7a4d;
    border: 1px solid #1f7a4d;
    color: white;
}

.stButton > button[kind="primary"]:hover {
    background-color: #17623d;
    border-color: #17623d;
    color: white;
}


/* =========================================================
   NUMBER INPUT
========================================================= */

[data-testid="stNumberInput"] {
    margin-bottom: 10px;
}


/* =========================================================
   STATUS BOXES
========================================================= */

.ready-box {
    background-color: #ecfdf3;
    border: 1px solid #bbf7d0;
    border-radius: 12px;
    padding: 16px;
    color: #15803d;
    font-weight: 700;
}

.spraying-box {
    background-color: #fff7ed;
    border: 1px solid #fed7aa;
    border-radius: 12px;
    padding: 16px;
    color: #c2410c;
    font-weight: 700;
}

.completed-box {
    background-color: #eff6ff;
    border: 1px solid #bfdbfe;
    border-radius: 12px;
    padding: 16px;
    color: #2563eb;
    font-weight: 700;
}

.offline-box {
    background-color: #fef2f2;
    border: 1px solid #fecaca;
    border-radius: 12px;
    padding: 16px;
    color: #dc2626;
    font-weight: 700;
}


/* =========================================================
   FOOTER
========================================================= */

.footer-text {
    text-align: center;
    color: #89958c;
    font-size: 12px;
    padding-top: 20px;
}


/* =========================================================
   MOBILE
========================================================= */

@media (max-width: 800px) {

    .block-container {
        padding: 1rem;
    }

    .header-title {
        font-size: 28px;
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
                f"🚿 Spray command sent — "
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
# HEADER
# ============================================================

header_left, header_right = st.columns(
    [4, 1]
)

with header_left:

    st.markdown(
        """
        <div class="header-box">

            <div class="header-title">
                🌱 CropIQ
            </div>

            <div class="header-subtitle">
                Precision Agriculture Intelligence Platform
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )

with header_right:

    st.write("")

    state_header = get_state()

    if state_header is not None:

        st.success("● SYSTEM ONLINE")

    else:

        st.error("● SYSTEM OFFLINE")


# ============================================================
# TITLE
# ============================================================

st.markdown(
    '<div class="section-title">'
    'Precision Spraying Control'
    '</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="small-description">'
    'Monitor the plant, control the sprayer, and perform targeted spraying.'
    '</div>',
    unsafe_allow_html=True
)


# ============================================================
# CURRENT STATE
# ============================================================

state = get_state()

if state is not None:

    current_status = state.get(
        "status",
        "Ready"
    )

    sprayed_amount = state.get(
        "sprayed_amount",
        0.0
    )

    pi_online = True

else:

    current_status = "Offline"

    sprayed_amount = 0.0

    pi_online = False


# ============================================================
# SYSTEM OVERVIEW
# ============================================================

st.markdown(
    '<div class="section-title">'
    'System Overview'
    '</div>',
    unsafe_allow_html=True
)

metric1, metric2, metric3, metric4 = st.columns(
    4,
    gap="medium"
)


# ------------------------------------------------------------
# METRIC 1
# ------------------------------------------------------------

with metric1:

    with st.container(border=True):

        if current_status == "Ready":

            status_text = "READY"

        elif current_status == "Spraying...":

            status_text = "SPRAYING"

        elif current_status == "Completed":

            status_text = "COMPLETED"

        else:

            status_text = "OFFLINE"

        st.metric(
            label="🚿 SPRAYER STATUS",
            value=status_text
        )

        st.caption(
            "Current operation"
        )


# ------------------------------------------------------------
# METRIC 2
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
# METRIC 3
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
# METRIC 4
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
# MAIN CONTROL SECTION
# ============================================================

st.markdown(
    '<div class="section-title">'
    'Plant Monitoring & Control'
    '</div>',
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

        title_col, live_col = st.columns(
            [4, 1]
        )

        with title_col:

            st.subheader(
                "🌿 Latest Plant Image"
            )

        with live_col:

            st.success(
                "● LIVE"
            )


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
                        "🌱 No plant image available yet.\n\n"
                        "Use **Capture Plant Image** to capture a new image."
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

        st.write(
            "Set the required spray quantity "
            "and activate the precision sprayer."
        )

        st.divider()

        dosage = st.number_input(
            "Spray dosage",
            min_value=1.0,
            max_value=500.0,
            value=25.0,
            step=1.0,
            format="%.0f",
            help="Enter the required spray amount in millilitres."
        )

        st.caption(
            "Dosage range: 1 – 500 ml"
        )

        st.write("")

        if st.button(
            "📷  CAPTURE PLANT IMAGE",
            use_container_width=True
        ):

            capture_image()


        if st.button(
            "🚿  START PRECISION SPRAY",
            type="primary",
            use_container_width=True
        ):

            spray(dosage)

        st.info(
            "💡 The selected dosage will be sent "
            "to the Raspberry Pi sprayer."
        )


# ============================================================
# LIVE SPRAY STATUS
# ============================================================

st.markdown(
    '<div class="section-title">'
    'Live Spray Status'
    '</div>',
    unsafe_allow_html=True
)


@st.fragment(run_every="2s")
def show_status():

    state = get_state()

    # --------------------------------------------------------
    # OFFLINE
    # --------------------------------------------------------

    if state is None:

        st.markdown(
            """
            <div class="offline-box">
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
    # STATE
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
            <div class="ready-box">
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
            <div class="spraying-box">
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
            <div class="completed-box">
                🔵 SPRAY COMPLETED
            </div>
            """,
            unsafe_allow_html=True
        )

        st.write(
            f"💧 Total dispensed: **{amount:.2f} ml**"
        )


    # --------------------------------------------------------
    # OTHER
    # --------------------------------------------------------

    else:

        st.info(
            f"Current status: {status}"
        )


show_status()


# ============================================================
# PROJECT WORKFLOW
# ============================================================

st.markdown(
    '<div class="section-title">'
    'CropIQ Workflow'
    '</div>',
    unsafe_allow_html=True
)

workflow1, workflow2, workflow3, workflow4 = st.columns(
    4,
    gap="medium"
)

with workflow1:

    with st.container(border=True):

        st.subheader("01")
        st.write("📷")
        st.markdown("**Capture**")
        st.caption(
            "Capture the latest plant image."
        )


with workflow2:

    with st.container(border=True):

        st.subheader("02")
        st.write("🌿")
        st.markdown("**Analyze**")
        st.caption(
            "Analyze the target plant area."
        )


with workflow3:

    with st.container(border=True):

        st.subheader("03")
        st.write("🎯")
        st.markdown("**Target**")
        st.caption(
            "Determine the required treatment."
        )


with workflow4:

    with st.container(border=True):

        st.subheader("04")
        st.write("🚿")
        st.markdown("**Spray**")
        st.caption(
            "Apply the selected spray dosage."
        )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.markdown(
    """
    <div class="footer-text">
        🌱 CropIQ &nbsp;•&nbsp;
        Precision Agriculture &nbsp;•&nbsp;
        AI-powered targeted spraying
    </div>
    """,
    unsafe_allow_html=True
)
