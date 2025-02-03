
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from datetime import datetime, timedelta

# Set page config
st.set_page_config(layout="wide", page_title="Classroom Proctor Hub", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    .stApp {
        background: black;
        color: white;
    }
    .session-card {
        background: black;
        border-radius: 15px;
        padding: 1.5rem;
        box-shadow: 0 4px 20px rgba(0,0,0,0.2);
        margin: 1rem 0;
        border-left: 5px solid #64B5F6;
        color: white;
    }
    .violation-card {
        background: black;
        border-radius: 12px;
        padding: 1rem;
        margin: 0.5rem 0;
        border-left: 4px solid #ff4444;
        transition: all 0.3s ease;
        color: white;
    }
    .violation-card:hover {
        transform: translateX(5px);
        box-shadow: 0 4px 20px rgba(0,0,0,0.4);
    }
    .metric-card {
        background: black;
        border-radius: 12px;
        padding: 1.2rem;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        color: white;
    }
    .metric-value {
        font-size: 24px;
        font-weight: bold;
        color: #ffffff;
    }
    .metric-label {
        color: white;
        font-size: 14px;
    }
    .custom-tab {
        background: black;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 2px 15px rgba(0,0,0,0.2);
        color: white;
    }
    .welcome-header {
        background: black;
        color: white;
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
    }
    /* Sidebar styling */
    .css-1d391kg {
        background: black;
    }
    .stSidebar {
        background: black;
    }
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        background: black;
        border-radius: 15px;
        padding: 10px;
    }
    .stTabs [data-baseweb="tab"] {
        color: white;
    }
    /* Support contact box */
    div[style*="background: black"] {
        background: black !important;
        color: white;
    }
    /* Additional text color adjustments */
    p, h1, h2, h3, h4, h5, h6 {
        color: white;
    }
    .stMarkdown {
        color: white;
    }
    /* Button styling */
    .stButton > button {
        background: black;
        color: white;
        border: 1px solid #64B5F6;
    }
    .stButton > button:hover {
        background: black;
        border: 1px solid #ffffff;
    }
    </style>
""", unsafe_allow_html=True)


# Welcome Header
st.markdown("""
    <div class="welcome-header">
        <h1>📚 Classroom Proctor Hub</h1>
        <p>Welcome back, Professor! Your virtual classroom assistant is ready.</p>
    </div>
""", unsafe_allow_html=True)

# Quick Stats Cards
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown("""
        <div class="metric-card">
            <div class="metric-value">2</div>
            <div class="metric-label">Active Sessions</div>
        </div>
    """, unsafe_allow_html=True)
with col2:
    st.markdown("""
        <div class="metric-card">
            <div class="metric-value">77</div>
            <div class="metric-label">Students Online</div>
        </div>
    """, unsafe_allow_html=True)
with col3:
    st.markdown("""
        <div class="metric-card">
            <div class="metric-value">3</div>
            <div class="metric-label">Alerts</div>
        </div>
    """, unsafe_allow_html=True)
with col4:
    st.markdown("""
        <div class="metric-card">
            <div class="metric-value">5</div>
            <div class="metric-label">Upcoming Exams</div>
        </div>
    """, unsafe_allow_html=True)

# Main navigation with enhanced styling
tab1, tab2, tab3 = st.tabs(["🎥 Live Sessions", "📅 Scheduled Exams", "📊 Past Sessions"])

with tab1:
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📍 Active Monitoring")
        
        # Active sessions with enhanced cards
        active_sessions = {
            "Advanced Mathematics Final": {
                "students": 45,
                "time_remaining": "1:30:00",
                "alerts": 2,
                "violations": ["📱 Mobile device detected", "👥 Multiple faces detected"]
            },
            "Physics Midterm": {
                "students": 32,
                "time_remaining": "0:45:00",
                "alerts": 1,
                "violations": ["🔍 Tab switching detected"]
            }
        }
        
        for exam_name, details in active_sessions.items():
            st.markdown(f"""
                <div class="session-card">
                    <h3>{exam_name}</h3>
                    <p>👥 Students: {details['students']} | ⏰ Time Remaining: {details['time_remaining']}</p>
                    <p>🚨 Active Alerts: {details['alerts']}</p>
                    <p>⚠️ Current Violations: {', '.join(details['violations'])}</p>
                </div>
            """, unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.button(f"👁️ Monitor ({exam_name})")
            with col2:
                st.button(f"⚠️ Send Warning ({exam_name})")
            with col3:
                st.button(f"🛑 End Session ({exam_name})")
    
    with col2:
        st.subheader("🚨 Active Alerts")
        for exam_name, details in active_sessions.items():
            for violation in details['violations']:
                st.markdown(f"""
                    <div class="violation-card">
                        <strong>{exam_name}</strong><br/>
                        {violation}
                        <p style="color: #666; font-size: 12px;">2 minutes ago</p>
                    </div>
                """, unsafe_allow_html=True)

with tab2:
    st.subheader("📝 Exam Schedule")
    
    # Enhanced exam scheduling form
    with st.expander("✨ Schedule New Exam"):
        col1, col2 = st.columns(2)
        with col1:
            st.text_input("📚 Exam Title")
            st.date_input("📅 Date")
            st.time_input("⏰ Start Time")
            st.number_input("⌛ Duration (minutes)", min_value=30, max_value=240, value=120)
        with col2:
            st.multiselect("🛠️ Proctoring Features", 
                          ["Face Detection", "Screen Recording", "Browser Lock", 
                           "ID Verification", "Audio Monitoring"])
            st.text_area("📝 Additional Instructions")
            st.button("🎯 Schedule Exam", type="primary")

    # Upcoming exams visualization
    scheduled_exams = pd.DataFrame({
        'Exam': ['Mathematics 101', 'Physics 202', 'Chemistry 303'],
        'Date': pd.date_range(start='2024-02-01', periods=3),
        'Students': [45, 32, 28]
    })
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=scheduled_exams['Date'],
        y=scheduled_exams['Students'],
        mode='markers+lines',
        name='Students',
        marker=dict(size=12, color='#4361ee'),
        line=dict(color='#4361ee', width=2)
    ))
    
    fig.update_layout(
        title='Upcoming Exam Schedule',
        xaxis_title='Date',
        yaxis_title='Number of Students',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        height=300
    )
    
    st.plotly_chart(fig, use_container_width=True)

# Sidebar with enhanced styling
with st.sidebar:
    st.markdown("### 🎓 Professor Dashboard")
    
    # Profile section
    st.markdown("""
        <div style="text-align: center; padding: 1rem;">
            <img src="https://via.placeholder.com/100" style="border-radius: 50%; margin-bottom: 1rem;">
            <h3>Dr. Smith</h3>
            <p style="color: #666;">Computer Science Department</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Quick actions
    st.subheader("⚡ Quick Actions")
    if st.button("🆕 Start New Exam"):
        st.session_state.show_setup = True
    if st.button("📊 Generate Reports"):
        st.session_state.show_reports = True
    if st.button("📧 Contact Support"):
        st.session_state.show_support = True
        
    st.markdown("---")
    
    # Settings with icons
    st.subheader("⚙️ Proctor Settings")
    st.checkbox("🔍 Auto-flag suspicious behavior", value=True)
    st.slider("🎚️ Detection Sensitivity", 1, 5, 3)
    st.number_input("📑 Max tab switches", min_value=0, max_value=10, value=3)
    
    st.markdown("---")
    
    # Support contact
    st.markdown("""
        <div style="background: #f8f9fa; padding: 1rem; border-radius: 10px;">
            <h4>📞 Need Help?</h4>
            <p>Support: +1-555-0123</p>
            <p>Email: support@proctoring.edu</p>
        </div>
    """, unsafe_allow_html=True)