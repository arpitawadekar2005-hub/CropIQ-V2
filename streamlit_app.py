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
    page_title="CropIQ | Precision Spraying",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =====================================================
# CUSTOM CSS
# =====================================================

st.markdown("""
<style>

    /* ================================
       GLOBAL
    ================================= */

    .stApp {
        background: #F4F7F5;
    }

    .block-container {
        max-width: 1400px;
        padding-top: 2rem;
        padding-left: 3rem;
        padding-right: 3rem;
        padding-bottom: 3rem;
    }

    /* ================================
       SIDEBAR
    ================================= */

    [data-testid="stSidebar"] {
        background: #12372A;
    }

    [data-testid="stSidebar"] * {
        color: white;
    }

    .sidebar-logo {
        font-size: 28px;
        font-weight: 700;
        margin-bottom: 5px;
    }

    .sidebar-subtitle {
        font-size: 13px;
        opacity: 0.75;
        margin-bottom: 30px;
    }

    .sidebar-item {
        padding: 12px;
        border-radius: 10px;
        margin: 5px 0;
        font-size: 15px;
    }

    /* ================================
       HEADER
    ================================= */

    .dashboard-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 25px;
    }

    .brand-title {
        font-size: 38px;
        font-weight: 750;
        color: #12372A;
        margin-bottom: 2px;
    }

    .brand-subtitle {
        color: #6B7280;
        font-size: 15px;
    }

    .connection {
        background: white;
        padding: 10px 18px;
        border-radius: 30px;
        border: 1px solid #DDE5DF;
        font-size: 14px;
    }

    .online-dot {
        color: #16A34A;
        font-size: 12px;
    }

    /* ================================
       CARDS
    ================================= */

    .metric-card {
        background: white;
        padding: 22px;
        border-radius: 16px;
        border: 1px solid #E3EAE5;
        box-shadow: 0 3px 12px rgba(0,0,0,0.04);
        height: 120px;
    }

    .metric-label {
        color: #6B7280;
        font-size: 13px;
        margin-bottom: 8px;
    }

    .metric-value {
        color: #12372A;
        font-size: 28px;
        font-weight: 700;
    }

    .metric-icon {
        font-size: 22px;
        float: right;
    }

    /* ================================
       SECTION TITLE
    ================================= */

    .section-title {
        font-size: 20px;
        font-weight: 650;
        color: #12372A;
        margin-top: 25px;
        margin-bottom: 12px;
    }

    /* ================================
       IMAGE CARD
    ================================= */

    .image-header {
        background: white;
        padding: 18px 20px 5px 20px;
        border-radius: 16px 16px 0 0;
        border: 1px solid #E3EAE5;
    }

    /* ================================
       STATUS CARD
    ================================= */

    .status-card {
        background: white;
        padding: 25px;
        border-radius: 16px;
        border: 1px solid #E3EAE5;
        box-shadow: 0 3px 12px rgba(0,0,0,0.04);
    }

    .status-ready {
        background: #ECFDF3;
        color: #15803D;
        padding: 12px 18px;
        border-radius: 10px;
        font-weight: 600;
    }

    .status-spraying {
        background: #FFF7ED;
        color: #C2410C;
        padding: 12px 18px;
        border-radius: 10px;
        font-weight: 600;
    }

    .status-completed {
        background: #EFF6FF;
        color: #2563EB;
        padding: 12px 18px;
        border-radius: 10px;
        font-weight: 600;
    }

    /* ================================
       BUTTONS
    ================================= */

    .stButton > button {
        border-radius: 10px;
        font-weight: 650;
        height: 48px;
        border: none;
    }

    /* ================================
       INPUT
    ================================= */

    [data-testid="stNumberInput"] {
        background: white;
        border-radius: 10px;
    }

    /* ================================
       HIDE STREAMLIT UI
    ================================= */

    #MainMenu {
        visibility: hidden;
    }

    footer {
        visibility: hidden;
    }

</style>
""", unsafe_allow_html=True)


# =====================================================
# BACKEND STATE
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
# SIDEBAR
# =====================================================

with st.sidebar:

    st.markdown(
        '<div class="sidebar-logo">🌱 CropIQ</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="sidebar-subtitle">'
        'Precision Agriculture Platform'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="sidebar-item">📊 Dashboard</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="sidebar-item">📷 Plant Capture</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="sidebar-item">🚿 Precision Spraying</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="sidebar-item">📡 System Status</div>',
        unsafe_allow_html=True
    )

    st.markdown("---")

    st.caption("CropIQ v2.0")
    st.caption("AI-powered precision spraying")


# =====================================================
# HEADER
# =====================================================

st.markdown("""
<div class="dashboard-header">

    <div>
        <div class="brand-title">
            CropIQ
        </div>

        <div class="brand-subtitle">
            AI-powered precision spraying dashboard
        </div>
    </div>

    <div class="connection">
        <span class="online-dot">●</span>
        System Connected
    </div>

</div>
""", unsafe_allow_html=True)


# =====================================================
# GET CURRENT STATE
# =====================================================

state = get_state()

if state:

    current_status = state.get("status", "Ready")
    sprayed_amount = state.get("sprayed_amount", 0.0)

else:

    current_status = "Offline"
    sprayed_amount = 0.0


# =====================================================
# KPI CARDS
# =====================================================

col1, col2, col3, col4 = st.columns(4)

with col1:

    st.markdown("""
    <div class="metric-card">
        <div class="metric-icon">🚿</div>
        <div class="metric-label">Current Status</div>
        <div class="metric-value">Ready</div>
    </div>
    """, unsafe_allow_html=True)


with col2:

    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-icon">💧</div>
        <div class="metric-label">Last Dispensed</div>
        <div class="metric-value">{sprayed_amount:.1f} ml</div>
    </div>
    """, unsafe_allow_html=True)


with col3:

    st.markdown("""
    <div class="metric-card">
        <div class="metric-icon">📷</div>
        <div class="metric-label">Camera</div>
        <div class="metric-value">LIVE</div>
    </div>
    """, unsafe_allow_html=True)


with col4:

    st.markdown("""
    <div class="metric-card">
        <div class="metric-icon">📡</div>
        <div class="metric-label">Raspberry Pi</div>
        <div class="metric-value">ONLINE</div>
    </div>
    """, unsafe_allow_html=True)


# =====================================================
# MAIN SECTION
# =====================================================

st.markdown(
    '<div class="section-title">🌿 Plant Monitoring</div>',
    unsafe_allow_html=True
)

image_col, control_col = st.columns([2.2, 1])


# =====================================================
# IMAGE
# =====================================================

with image_col:

    st.markdown("""
    <div class="image-header">
        <strong>📷 Latest Plant Image</strong>
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
                    "No plant image available yet."
                )

            else:

                st.warning(
                    "Unable to load latest image."
                )

        except Exception:

            st.warning(
                "Waiting for Raspberry Pi..."
            )


    show_latest_image()


# =====================================================
# CONTROL PANEL
# =====================================================

with control_col:

    st.markdown("""
    <div class="section-title">
        🚿 Spray Control
    </div>
    """, unsafe_allow_html=True)

    st.write(
        "Set the required spray dosage and activate "
        "the precision sprayer."
    )

    dosage = st.number_input(
        "Spray amount (ml)",
        min_value=1.0,
        max_value=500.0,
        value=25.0,
        step=1.0
    )

    st.write("")

    if st.button(
        "📷  CAPTURE PLANT IMAGE",
        use_container_width=True
    ):

        try:

            response = requests.post(
                BACKEND_URL + "/capture",
                timeout=15
            )

            if response.status_code == 200:

                st.success(
                    "Capture command sent."
                )

            elif response.status_code == 409:

                st.warning(
                    "Another command is pending."
                )

            else:

                st.error(response.text)

        except Exception as e:

            st.error(
                f"Backend connection failed: {e}"
            )


    if st.button(
        "🚿  START SPRAY",
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
                    f"{data['amount_ml']:.0f} ml spray started."
                )

            elif response.status_code == 409:

                st.warning(
                    "Spray operation already running."
                )

            else:

                st.error(response.text)

        except Exception as e:

            st.error(
                f"Backend connection failed: {e}"
            )


# =====================================================
# STATUS
# =====================================================

st.markdown(
    '<div class="section-title">📡 Spraying Status</div>',
    unsafe_allow_html=True
)


@st.fragment(run_every="2s")
def show_status():

    state = get_state()

    if state is None:

        st.markdown("""
        <div class="status-card">
            <div class="status-spraying">
                🔴 Backend unavailable
            </div>
        </div>
        """, unsafe_allow_html=True)

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

        st.markdown("""
        <div class="status-card">
            <div class="status-ready">
                🟢 Sprayer Ready
            </div>
            <br>
            System is ready for the next precision spraying operation.
        </div>
        """, unsafe_allow_html=True)

    elif current_status == "Spraying...":

        st.markdown(f"""
        <div class="status-card">
            <div class="status-spraying">
                🟡 Spraying in progress...
            </div>
            <br>
            Dispensed:
            <strong>{sprayed_amount:.2f} ml</strong>
        </div>
        """, unsafe_allow_html=True)

    elif current_status == "Completed":

        st.markdown(f"""
        <div class="status-card">
            <div class="status-completed">
                🟢 Spray Completed
            </div>
            <br>
            Total dispensed:
            <strong>{sprayed_amount:.2f} ml</strong>
        </div>
        """, unsafe_allow_html=True)

    else:

        st.info(current_status)


show_status()


# =====================================================
# FOOTER
# =====================================================

st.markdown("---")

st.caption(
    "CropIQ • Precision Agriculture • "
    "AI-powered targeted spraying"
)
