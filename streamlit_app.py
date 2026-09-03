import streamlit as st
import requests
import textwrap

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
# CUSTOM HTML HELPER
# ============================================================

def html(content):
    """
    Render HTML without Streamlit interpreting the indentation
    as a Markdown code block.
    """
    st.markdown(
        textwrap.dedent(content),
        unsafe_allow_html=True
    )


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown("""
<style>

/* ============================================================
   GLOBAL
============================================================ */

.stApp {
    background: #F4F7F3;
}

.block-container {
    max-width: 1450px;
    padding-top: 2rem;
    padding-left: 3rem;
    padding-right: 3rem;
    padding-bottom: 3rem;
}

/* Hide Streamlit default branding */
#MainMenu {
    visibility: hidden;
}

footer {
    visibility: hidden;
}


/* ============================================================
   HEADER
============================================================ */

.cropiq-header {
    background: #FFFFFF;
    border: 1px solid #E1E9E2;
    border-radius: 20px;
    padding: 22px 28px;
    margin-bottom: 28px;

    display: flex;
    justify-content: space-between;
    align-items: center;

    box-shadow: 0 4px 18px rgba(22, 55, 38, 0.06);
}

.logo-area {
    display: flex;
    align-items: center;
    gap: 14px;
}

.logo-icon {
    font-size: 43px;
    line-height: 1;
}

.logo-text {
    font-size: 32px;
    font-weight: 800;
    color: #173B29;
    line-height: 1;
}

.logo-subtitle {
    color: #718078;
    font-size: 13px;
    margin-top: 6px;
}

.online-status {
    background: #ECFDF3;
    border: 1px solid #BBF7D0;
    color: #15803D;

    padding: 10px 17px;
    border-radius: 30px;

    font-size: 13px;
    font-weight: 700;
}


/* ============================================================
   PAGE TITLE
============================================================ */

.page-title {
    color: #173B29;
    font-size: 27px;
    font-weight: 800;
    margin-bottom: 4px;
}

.page-description {
    color: #718078;
    font-size: 14px;
    margin-bottom: 22px;
}


/* ============================================================
   SECTION TITLES
============================================================ */

.section-heading {
    color: #173B29;
    font-size: 20px;
    font-weight: 750;

    margin-top: 28px;
    margin-bottom: 13px;
}


/* ============================================================
   METRIC CARDS
============================================================ */

.metric-card {
    background: #FFFFFF;

    border: 1px solid #E1E9E2;
    border-radius: 17px;

    padding: 20px;

    min-height: 125px;

    box-shadow: 0 4px 16px rgba(22, 55, 38, 0.05);

    transition: all 0.2s ease;
}

.metric-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 7px 22px rgba(22, 55, 38, 0.08);
}

.metric-top {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.metric-label {
    color: #718078;
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 0.5px;
}

.metric-icon {
    font-size: 23px;
}

.metric-value {
    color: #173B29;
    font-size: 25px;
    font-weight: 800;

    margin-top: 13px;
}

.metric-description {
    color: #8A958E;
    font-size: 12px;
    margin-top: 4px;
}


/* ============================================================
   IMAGE PANEL
============================================================ */

.image-panel {
    background: #FFFFFF;

    border: 1px solid #E1E9E2;
    border-radius: 18px;

    padding: 18px;

    box-shadow: 0 4px 18px rgba(22, 55, 38, 0.05);
}

.panel-header {
    display: flex;
    justify-content: space-between;
    align-items: center;

    margin-bottom: 15px;
}

.panel-title {
    color: #173B29;
    font-size: 17px;
    font-weight: 750;
}

.live-badge {
    background: #ECFDF3;
    color: #15803D;

    border: 1px solid #BBF7D0;

    padding: 5px 10px;
    border-radius: 20px;

    font-size: 10px;
    font-weight: 800;
}


/* ============================================================
   CONTROL PANEL
============================================================ */

.control-panel {
    background: #FFFFFF;

    border: 1px solid #E1E9E2;
    border-radius: 18px;

    padding: 25px;

    min-height: 100%;

    box-shadow: 0 4px 18px rgba(22, 55, 38, 0.05);
}

.control-title {
    color: #173B29;
    font-size: 19px;
    font-weight: 800;
    margin-bottom: 7px;
}

.control-description {
    color: #718078;
    font-size: 13px;
    line-height: 1.55;

    margin-bottom: 20px;
}


/* ============================================================
   STREAMLIT BUTTONS
============================================================ */

.stButton > button {
    width: 100%;

    height: 48px;

    border-radius: 11px !important;

    font-weight: 700 !important;
    font-size: 14px !important;

    border: none !important;

    transition: all 0.2s ease !important;
}

.stButton > button:hover {
    transform: translateY(-1px);
}


/* ============================================================
   NUMBER INPUT
============================================================ */

[data-testid="stNumberInput"] {
    margin-bottom: 15px;
}

[data-testid="stNumberInput"] input {
    font-weight: 650;
}


/* ============================================================
   STATUS PANEL
============================================================ */

.status-panel {
    background: #FFFFFF;

    border: 1px solid #E1E9E2;
    border-radius: 18px;

    padding: 22px 25px;

    box-shadow: 0 4px 18px rgba(22, 55, 38, 0.05);
}

.status-panel p {
    color: #66736B;
    font-size: 14px;
    margin-top: 14px;
    margin-bottom: 0;
}

.status-ready {
    background: #ECFDF3;
    border: 1px solid #BBF7D0;

    color: #15803D;

    padding: 13px 16px;

    border-radius: 11px;

    font-weight: 750;
}

.status-spraying {
    background: #FFF7ED;
    border: 1px solid #FED7AA;

    color: #C2410C;

    padding: 13px 16px;

    border-radius: 11px;

    font-weight: 750;
}

.status-completed {
    background: #EFF6FF;
    border: 1px solid #BFDBFE;

    color: #2563EB;

    padding: 13px 16px;

    border-radius: 11px;

    font-weight: 750;
}

.status-offline {
    background: #FEF2F2;
    border: 1px solid #FECACA;

    color: #DC2626;

    padding: 13px 16px;

    border-radius: 11px;

    font-weight: 750;
}


/* ============================================================
   INFO BOX
============================================================ */

.info-box {
    background: #F0F7F1;

    border: 1px solid #D5E5D7;

    border-radius: 12px;

    padding: 13px 15px;

    color: #496052;

    font-size: 12px;

    margin-top: 15px;
}


/* ============================================================
   FOOTER
============================================================ */

.footer {
    text-align: center;

    color: #89958C;

    font-size: 12px;

    padding-top: 25px;
}


/* ============================================================
   MOBILE
============================================================ */

@media (max-width: 800px) {

    .block-container {
        padding: 1rem;
    }

    .cropiq-header {
        padding: 18px;
    }

    .logo-text {
        font-size: 27px;
    }

    .logo-icon {
        font-size: 34px;
    }

    .online-status {
        font-size: 10px;
        padding: 8px 10px;
    }

    .page-title {
        font-size: 23px;
    }

}

</style>
""", unsafe_allow_html=True)


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

html("""
<div class="cropiq-header">

    <div class="logo-area">

        <div class="logo-icon">
            🌱
        </div>

        <div>

            <div class="logo-text">
                CropIQ
            </div>

            <div class="logo-subtitle">
                Precision Agriculture Intelligence Platform
            </div>

        </div>

    </div>

    <div class="online-status">
        ● SYSTEM ONLINE
    </div>

</div>
""")


# ============================================================
# PAGE TITLE
# ============================================================

html("""
<div class="page-title">
    Precision Spraying Control
</div>

<div class="page-description">
    Monitor the plant, control the sprayer, and perform targeted spraying.
</div>
""")


# ============================================================
# GET CURRENT STATE
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

html("""
<div class="section-heading">
    System Overview
</div>
""")


col1, col2, col3, col4 = st.columns(4)


# ============================================================
# CARD 1
# ============================================================

with col1:

    if current_status == "Ready":

        display_status = "READY"

    elif current_status == "Spraying...":

        display_status = "SPRAYING"

    elif current_status == "Completed":

        display_status = "COMPLETED"

    else:

        display_status = "OFFLINE"


    html(f"""
    <div class="metric-card">

        <div class="metric-top">

            <div class="metric-label">
                SPRAYER STATUS
            </div>

            <div class="metric-icon">
                🚿
            </div>

        </div>

        <div class="metric-value">
            {display_status}
        </div>

        <div class="metric-description">
            Current operation
        </div>

    </div>
    """)


# ============================================================
# CARD 2
# ============================================================

with col2:

    html(f"""
    <div class="metric-card">

        <div class="metric-top">

            <div class="metric-label">
                LAST DISPENSED
            </div>

            <div class="metric-icon">
                💧
            </div>

        </div>

        <div class="metric-value">
            {sprayed_amount:.1f} ml
        </div>

        <div class="metric-description">
            Latest spray quantity
        </div>

    </div>
    """)


# ============================================================
# CARD 3
# ============================================================

with col3:

    camera_status = "READY" if pi_online else "OFFLINE"

    html(f"""
    <div class="metric-card">

        <div class="metric-top">

            <div class="metric-label">
                CAMERA
            </div>

            <div class="metric-icon">
                📷
            </div>

        </div>

        <div class="metric-value">
            {camera_status}
        </div>

        <div class="metric-description">
            Plant imaging system
        </div>

    </div>
    """)


# ============================================================
# CARD 4
# ============================================================

with col4:

    device_status = "ONLINE" if pi_online else "OFFLINE"

    html(f"""
    <div class="metric-card">

        <div class="metric-top">

            <div class="metric-label">
                RASPBERRY PI
            </div>

            <div class="metric-icon">
                📡
            </div>

        </div>

        <div class="metric-value">
            {device_status}
        </div>

        <div class="metric-description">
            Hardware connection
        </div>

    </div>
    """)


# ============================================================
# MAIN AREA
# ============================================================

html("""
<div class="section-heading">
    Plant Monitoring & Control
</div>
""")


image_col, control_col = st.columns(
    [2.1, 1],
    gap="large"
)


# ============================================================
# PLANT IMAGE
# ============================================================

with image_col:

    html("""
    <div class="image-panel">

        <div class="panel-header">

            <div class="panel-title">
                🌿 Latest Plant Image
            </div>

            <div class="live-badge">
                ● LIVE
            </div>

        </div>

    </div>
    """)


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

with control_col:

    html("""
    <div class="control-panel">

        <div class="control-title">
            🚿 Precision Spray
        </div>

        <div class="control-description">
            Set the required spray quantity and send
            the command to the precision spraying system.
        </div>

    </div>
    """)


    dosage = st.number_input(
        "Spray dosage (ml)",
        min_value=1.0,
        max_value=500.0,
        value=25.0,
        step=1.0
    )


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


    html("""
    <div class="info-box">
        💡 Set the spray quantity according to the
        required treatment amount.
    </div>
    """)


# ============================================================
# LIVE SPRAY STATUS
# ============================================================

html("""
<div class="section-heading">
    Live Spray Status
</div>
""")


@st.fragment(run_every="2s")
def show_status():

    state = get_state()

    # --------------------------------------------------------
    # BACKEND OFFLINE
    # --------------------------------------------------------

    if state is None:

        html("""
        <div class="status-panel">

            <div class="status-offline">
                🔴 BACKEND UNAVAILABLE
            </div>

            <p>
                Unable to communicate with the CropIQ
                control system.
            </p>

        </div>
        """)

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

        html("""
        <div class="status-panel">

            <div class="status-ready">
                🟢 READY
            </div>

            <p>
                System is ready for the next
                precision spraying operation.
            </p>

        </div>
        """)


    # --------------------------------------------------------
    # SPRAYING
    # --------------------------------------------------------

    elif status == "Spraying...":

        html(f"""
        <div class="status-panel">

            <div class="status-spraying">
                🟠 SPRAYING IN PROGRESS
            </div>

            <p>
                Dispensed:
                <strong>{amount:.2f} ml</strong>
            </p>

        </div>
        """)


    # --------------------------------------------------------
    # COMPLETED
    # --------------------------------------------------------

    elif status == "Completed":

        html(f"""
        <div class="status-panel">

            <div class="status-completed">
                🔵 SPRAY COMPLETED
            </div>

            <p>
                Total dispensed:
                <strong>{amount:.2f} ml</strong>
            </p>

        </div>
        """)


    # --------------------------------------------------------
    # OTHER
    # --------------------------------------------------------

    else:

        st.info(status)


show_status()


# ============================================================
# FOOTER
# ============================================================

html("""
<hr>

<div class="footer">
    🌱 CropIQ &nbsp;•&nbsp;
    Precision Agriculture &nbsp;•&nbsp;
    AI-powered targeted spraying
</div>
""")
