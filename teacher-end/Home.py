import streamlit as st

st.set_page_config(layout="wide", page_title="Home - Sys")

st.markdown("""
    <style>
    .stApp {
        background: black;
        color: white;
    }
    .home-container {
        background: #121212;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
        margin-bottom: 20px;
    }
    .home-title {
        font-size: 32px;
        font-weight: bold;
        color: #64B5F6;
        text-align: center;
    }
    .home-subtitle {
        font-size: 18px;
        color: #cccccc;
        text-align: center;
    }
    .metric-card {
        background: #1e1e1e;
        border-radius: 12px;
        padding: 1.2rem;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        color: white;
    }
    .metric-value {
        font-size: 28px;
        font-weight: bold;
        color: #64B5F6;
    }
    .metric-label {
        color: white;
        font-size: 16px;
    }
    .stButton > button {
        background: black;
        color: white;
        border: 1px solid #64B5F6;
        border-radius: 8px;
        padding: 10px;
    }
    .stButton > button:hover {
        background: #64B5F6;
        color: black;
    }
    </style>
""", unsafe_allow_html=True)


st.markdown("<h1 class='home-title'>🏫 Sys </h1>", unsafe_allow_html=True)
st.markdown("<p class='home-subtitle'>Effortlessly manage academic integrity with real-time monitoring, reports, and powerful settings.</p>", unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown("<div class='metric-card'><div class='metric-value'>2</div><div class='metric-label'>Total Districts</div></div>", unsafe_allow_html=True)
with col2:
    st.markdown("<div class='metric-card'><div class='metric-value'>77</div><div class='metric-label'>Total Schools</div></div>", unsafe_allow_html=True)
with col3:
    st.markdown("<div class='metric-card'><div class='metric-value'>95</div><div class='metric-label'>Percent of Cheating Detected</div></div>", unsafe_allow_html=True)
with col4:
    st.markdown("<div class='metric-card'><div class='metric-value'>\inf</div><div class='metric-label'>reasons to invest in Sys</div></div>", unsafe_allow_html=True)

st.markdown("---")

st.subheader("🔗 Quick Access")
col1, col2, col3 = st.columns(3)
with col1:
    if st.button("📋 Manage Classes"):
        st.switch_page("pages/1_Account.py")
with col2:
    if st.button("⚙️ Adjust Settings"):
        st.switch_page("pages/2_Settings.py")
with col3:
    if st.button("💳 View Plans"):
        st.switch_page("pages/3_Plans.py")

st.markdown("---")

st.subheader("📌 Recent Activity")
recent_activities = [
    "🚨 John Doe triggered an alert for tab switching.",
    "📅 New exam 'Algebra Final' scheduled for Feb 15, 2025.",
    "📊 Weekly integrity report generated for 'Physics 101'.",
    "👨‍🏫 Dr. Smith updated class policies for 'Computer Science'."
]
st.header("Example Alerts")
for activity in recent_activities:
    st.markdown(f"✅ {activity}")

st.markdown("---")

st.subheader("📢 Announcements")
st.markdown("""
    - **New Feature**: AI-powered plagiarism detection is now live! 🚀  
    - **Community Feedback**: We’re looking for beta testers for our project. Sign up [here](#).
""")

st.markdown("---")

with st.container():
    st.subheader("💬 Need Help?")
    st.text("Support Email: sahus@sysproctoring.com")
    st.text("Phone: +1-346-434-1402")
    st.button("📧 Contact Support")

