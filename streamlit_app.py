import streamlit as st

st.set_page_config(
    page_title="CropIQ",
    page_icon="🌱",
    layout="wide"
)

st.markdown("""
<style>
.stApp {
    background: #f3f7f5;
}

.test-box {
    background: white;
    border: 2px solid #15934f;
    border-radius: 20px;
    padding: 50px;
    text-align: center;
    margin: 50px auto;
    max-width: 1000px;
}

.test-title {
    font-size: 42px;
    font-weight: 800;
    color: #064b3b;
}

.test-subtitle {
    font-size: 18px;
    color: #687671;
    margin-top: 10px;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="test-box">

    <div class="test-title">
        🌱 CropIQ
    </div>

    <div class="test-subtitle">
        Precision Agriculture Intelligence Platform
    </div>

</div>
""", unsafe_allow_html=True)

st.success("HTML TEST WORKING")
