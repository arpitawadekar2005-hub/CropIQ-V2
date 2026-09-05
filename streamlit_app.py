import streamlit as st

st.set_page_config(
    page_title="CropIQ",
    page_icon="🌱",
    layout="wide"
)

st.markdown(
"""
<style>
body {
    background-color: #eef4f1;
}

.test-box {
    background: white;
    padding: 40px;
    border-radius: 20px;
    border: 2px solid #0b8f4d;
    text-align: center;
}

.test-title {
    color: #064b3c;
    font-size: 40px;
    font-weight: 800;
}
</style>
""",
unsafe_allow_html=True
)

st.markdown(
"""
<div class="test-box">
    <div class="test-title">
        🌱 CropIQ
    </div>
    <p>
        Precision Agriculture Intelligence Platform
    </p>
</div>
""",
unsafe_allow_html=True
)

st.success("HTML TEST WORKING")
