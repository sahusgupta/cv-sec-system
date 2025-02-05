import streamlit as st

# Set page configuration
st.set_page_config(layout="wide", page_title="Settings - Classroom Proctor Hub")

# Custom CSS for dark mode styling
st.markdown("""
    <style>
    .stApp {
        background: black;
        color: white;
    }
    .settings-container {
        background: #121212;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
        margin-bottom: 20px;
    }
    .settings-title {
        font-size: 24px;
        font-weight: bold;
        color: #64B5F6;
    }
    .stSlider, .stCheckbox, .stSelectbox {
        background: #1e1e1e;
        border-radius: 8px;
        padding: 10px;
    }
    .stButton > button {
        background: black;
        color: white;
        border: 1px solid #64B5F6;
    }
    .stButton > button:hover {
        background: #64B5F6;
        color: black;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1 class='settings-title'>⚙️ Settings</h1>", unsafe_allow_html=True)

# General Settings
with st.container():
    st.markdown("<div class='settings-container'>", unsafe_allow_html=True)
    st.subheader("🔧 General Settings")
    dark_mode = st.toggle("🌙 Enable Dark Mode", value=True)
    notifications = st.toggle("🔔 Enable Notifications", value=True)
    language = st.selectbox("🌎 Language", ["English", "Spanish", "French", "German"])
    st.markdown("</div>", unsafe_allow_html=True)

# Proctoring Settings
with st.container():
    st.markdown("<div class='settings-container'>", unsafe_allow_html=True)
    st.subheader("🎥 Proctoring Settings")
    auto_flag = st.toggle("🔍 Auto-flag Suspicious Behavior", value=True)
    sensitivity = st.slider("🎚️ Detection Sensitivity", 1, 5, 3)
    max_tab_switches = st.number_input("📑 Max Tab Switches Allowed", min_value=0, max_value=10, value=3)
    screen_recording = st.toggle("📹 Enable Screen Recording", value=True)
    audio_monitoring = st.toggle("🎙️ Enable Audio Monitoring", value=False)
    st.markdown("</div>", unsafe_allow_html=True)

# Account Settings
with st.container():
    st.markdown("<div class='settings-container'>", unsafe_allow_html=True)
    st.subheader("👤 Account Settings")
    change_email = st.text_input("📧 Change Email")
    change_password = st.text_input("🔑 Change Password", type="password")
    two_factor = st.toggle("🔒 Enable Two-Factor Authentication", value=True)
    st.button("💾 Save Changes")
    st.markdown("</div>", unsafe_allow_html=True)

# Support Section
with st.container():
    st.markdown("<div class='settings-container'>", unsafe_allow_html=True)
    st.subheader("📞 Support")
    st.text("Support Email: support@proctoring.edu")
    st.text("Phone: +1-555-0123")
    st.markdown("</div>", unsafe_allow_html=True)
