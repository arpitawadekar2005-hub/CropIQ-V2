import streamlit as st
import requests

# ============================================================
# CONFIGURATION
# ============================================================

BACKEND_URL = "https://cropiq-backend-mecl.onrender.com"

st.set_page_config(
    page_title="CropIQ | Precision Agriculture",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown("""
<style>

/* ---------- GLOBAL ---------- */

.stApp {
    background: #F5F8F5;
}

.block-container {
    max-width: 1450px;
    padding: 2rem 3rem 3rem 3rem;
}

/* Hide Streamlit branding */
#MainMenu {
    visibility: hidden;
}

footer {
    visibility: hidden;
}

/* ---------- HEADER ---------- */

.cropiq-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    background: #FFFFFF;
    padding: 22px 28px;
    border-radius: 18px;
    border: 1px solid #E2EAE3;
    margin-bottom: 25px;
    box-shadow: 0 4px 18px rgba(31, 55, 40, 0.06);
}

.logo-area {
    display: flex;
    align-items: center;
    gap: 14px;
}

.logo-icon {
    font-size: 42px;
}

.logo-text {
    font-size: 32px;
    font-weight: 800;
    color: #173B29;
    line-height: 1;
}

.logo-subtitle {
    color: #718076;
    font-size: 13px;
    margin-top: 5px;
}

.online-status {
    background: #ECFDF3;
    color: #15803D;
    border: 1px solid #BBF7D0;
    padding: 10px 17px;
    border-radius: 25px;
    font-size: 14px;
    font-weight: 600;
}

/* ---------- PAGE TITLE ---------- */

.page-title {
    font-size: 25px;
    font-weight: 750;
    color: #173B29;
    margin: 5px 0 4px 0;
}

.page-description {
    color: #718076;
    font-size: 14px;
    margin-bottom: 22px;
}

/* ---------- METRIC CARDS ---------- */

.metric-card {
    background: #FFFFFF;
    border: 1px solid #E2EAE3;
    border-radius: 16px;
    padding: 20px;
    min-height: 125px;
    box-shadow: 0 4px 15px rgba(31, 55, 40, 0.05);
}

.metric-top {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.metric-label {
    font-size: 13px;
    color: #718076;
    font-weight: 600;
}

.metric-icon {
    font-size: 24px;
}

.metric-value {
    font-size: 25px;
    font-weight: 750;
    color: #173B29;
    margin-top: 13px;
}

.metric-description {
    font-size: 12px;
    color: #8A978E;
    margin-top: 3px;
}

/* ---------- SECTION TITLES ---------- */

.section-heading {
    color: #173B29;
    font-size: 20px;
    font-weight: 750;
    margin: 28px 0 12px 0;
}

/* ---------- IMAGE PANEL ---------- */

.image-panel {
    background: #FFFFFF;
    border: 1px solid #E2EAE3;
    border-radius: 18px;
    padding: 18px;
    box-shadow: 0 4px 18px rgba(31, 55, 40, 0.05);
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
    font-weight: 700;
}

.live-badge {
    background: #F0FDF4;
    color: #16A34A;
    border-radius: 20px;
    padding: 5px 10px;
    font-size: 11px;
    font-weight: 700;
}

/* ---------- CONTROL PANEL ---------- */

.control-panel {
    background: #FFFFFF;
    border: 1px solid #E2EAE3;
    border-radius: 18px;
    padding: 25px;
    box-shadow: 0 4px 18px rgba(31, 55, 40, 0.05);
    min-height: 100%;
}

.control-title {
    color: #173B29;
    font-size: 19px;
    font-weight: 750;
    margin-bottom: 5px;
}

.control-description {
    color: #718076;
    font-size: 13px;
    line-height: 1.5;
    margin-bottom: 20px;
}

/* ---------- BUTTONS ---------- */

.stButton > button {
    width: 100%;
    border-radius: 11px !important;
    height: 48px !important;
    font-weight: 700 !important;
    font-size: 14px !important;
    transition: all 0.2s ease !important;
}

.stButton > button:hover {
    transform: translateY(-1px);
}

/* ---------- INPUT ---------- */

[data-testid="stNumberInput"] {
    margin-bottom: 15px;
}

[data-testid="stNumberInput"] input {
    font-weight: 600;
}

/* ---------- STATUS ---------- */

.status-panel {
    background: #FFFFFF;
    border: 1px solid #E2EAE3;
    border-radius: 18px;
    padding: 22px 25px;
    box-shadow: 0 4px 18px rgba(31, 55, 40, 0.05);
}

.status-ready {
    background: #ECFDF3;
    border: 1px solid #BBF7D0;
    color: #15803D;
    padding: 13px 16px;
    border-radius: 11px;
    font-weight: 700;
}

.status-spraying {
    background: #FFF7ED;
    border: 1px solid #FED7AA;
    color: #C2410C;
    padding: 13px 16px;
    border-radius: 11px;
    font-weight: 700;
}

.status-completed {
    background: #EFF6FF;
    border: 1px solid #BFDBFE;
    color: #2563EB;
    padding: 13px 16px;
    border-radius: 11px;
    font-weight: 700;
}

.status-offline {
    background: #FEF2F2;
    border: 1px solid #FECACA;
    color: #DC2626;
    padding: 13px 16px;
    border-radius: 11px;
    font-weight: 700;
}

/* ---------- DIVIDER ---------- */

hr {
    border: none;
    border-top: 1px solid #E2EAE3;
    margin: 30px 0;
}

/* ---------- FOOTER ---------- */

.footer {
    text-align: center;
    color: #89958C;
    font-size: 12px;
    padding-top: 20px;
}

/* ---------- MOBILE ---------- */

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
        font-size: 11px;
        padding: 8px 11px;
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
            st.success("📷 Capture command sent to Raspberry Pi.")

        elif response.status_code == 409:
            st.warning("Another command is already pending.")

        else:
            st.error(response.text)

    except Exception as e:
        st.error(f"Backend connection failed: {e}")


def spray(amount):

    try:

        response = requests.post(
            BACKEND_URL + "/spray",
            json={"amount_ml": amount},
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

st.markdown("""
<div class="cropiq-header">

    <div class="logo-area">

        <div class="logo-icon">🌱</div>

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
""", unsafe_allow_html=True)


# ============================================================
# TITLE
# ============================================================

st.markdown(
    '<div class="page-title">Precision Spraying Control</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="page-description">'
    'Monitor the plant, control the sprayer, and perform targeted spraying.'
    '</div>',
    unsafe_allow_html=True
)


# ============================================================
# CURRENT STATE
# ============================================================

state = get_state()

if state:

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
# OVERVIEW CARDS
# ============================================================

st.markdown(
    '<div class="section-heading">System Overview</div>',
    unsafe_allow_html=True
)

col1, col2, col3, col4 = st.columns(4)


with col1:

    status_display = (
        "READY"
        if current_status == "Ready"
        else current_status.upper()
    )

    st.markdown(f"""
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
            {status_display}
        </div>

        <div class="metric-description">
            Current operation
        </div>

    </div>
    """, unsafe_allow_html=True)


with col2:

    st.markdown(f"""
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
    """, unsafe_allow_html=True)


with col3:

    camera_status = "READY" if pi_online else "OFFLINE"

    st.markdown(f"""
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
    """, unsafe_allow_html=True)


with col4:

    device_status = "ONLINE" if pi_online else "OFFLINE"

    st.markdown(f"""
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
    """, unsafe_allow_html=True)


# ============================================================
# MAIN CONTROL AREA
# ============================================================

st.markdown(
    '<div class="section-heading">Plant Monitoring & Control</div>',
    unsafe_allow_html=True
)

image_col, control_col = st.columns(
    [2.1, 1],
    gap="large"
)


# ============================================================
# PLANT IMAGE
# ============================================================

with image_col:

    st.markdown("""
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
    """, unsafe_allow_html=True)


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

    st.markdown("""
    <div class="control-panel">

        <div class="control-title">
            🚿 Precision Spray
        </div>

        <div class="control-description">
            Set the required spray quantity and send
            the command to the precision spraying system.
        </div>

    </div>
    """, unsafe_allow_html=True)


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


    st.caption(
        "Maximum dosage: 500 ml"
    )


# ============================================================
# LIVE STATUS
# ============================================================

st.markdown(
    '<div class="section-heading">Live Spray Status</div>',
    unsafe_allow_html=True
)


@st.fragment(run_every="2s")
def show_status():

    state = get_state()

    if state is None:

        st.markdown("""
        <div class="status-panel">

            <div class="status-offline">
                🔴 Backend unavailable
            </div>

        </div>
        """, unsafe_allow_html=True)

        return


    status = state.get(
        "status",
        "Ready"
    )

    amount = state.get(
        "sprayed_amount",
        0.0
    )


    if status == "Ready":

        st.markdown("""
        <div class="status-panel">

            <div class="status-ready">
                🟢 READY
            </div>

            <p>
                System is ready for the next
                precision spraying operation.
            </p>

        </div>
        """, unsafe_allow_html=True)


    elif status == "Spraying...":

        st.markdown(f"""
        <div class="status-panel">

            <div class="status-spraying">
                🟠 SPRAYING IN PROGRESS
            </div>

            <p>
                Dispensed:
                <strong>{amount:.2f} ml</strong>
            </p>

        </div>
        """, unsafe_allow_html=True)


    elif status == "Completed":

        st.markdown(f"""
        <div class="status-panel">

            <div class="status-completed">
                🔵 SPRAY COMPLETED
            </div>

            <p>
                Total dispensed:
                <strong>{amount:.2f} ml</strong>
            </p>

        </div>
        """, unsafe_allow_html=True)


    else:

        st.info(status)


show_status()


# ============================================================
# FOOTER
# ============================================================

st.markdown("""
<div class="footer">

    🌱 CropIQ &nbsp;•&nbsp;
    Precision Agriculture &nbsp;•&nbsp;
    AI-powered targeted spraying

</div>
""", unsafe_allow_html=True)
