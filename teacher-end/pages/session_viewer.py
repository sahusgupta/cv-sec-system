import streamlit as st
import pandas as pd
import sys
import os

# Add parent directory to path so we can import MVP
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from MVP.database import get_connection

# Function to format dataframe to prevent comma separators
def format_dataframe(df):
    # Convert ID columns to strings to prevent auto-formatting with commas
    if 'Session ID' in df.columns:
        df['Session ID'] = df['Session ID'].astype(str)
    if 'Student' in df.columns:
        df['Student'] = df['Student'].astype(str)
    if 'Exam ID' in df.columns:
        df['Exam ID'] = df['Exam ID'].astype(str)
    return df

def display_sessions():
    st.title("Exam Session Monitor")
    
    # Create tabs for active and completed sessions
    tab1, tab2 = st.tabs(["Active Sessions", "Completed Sessions"])
    
    conn = get_connection()
    cur = conn.cursor()
    
    with tab1:
        st.header("Active Sessions")
        try:
            cur.execute("""
                SELECT 
                    session_id,
                    student_id,
                    exam_id,
                    start_time,
                    EXTRACT(EPOCH FROM (NOW() - start_time)) as seconds_since_activity
                FROM exam_sessions
                WHERE status = 'active'
                ORDER BY start_time DESC
            """)
            
            active_sessions = cur.fetchall()
            if active_sessions:
                df = pd.DataFrame(active_sessions, columns=[
                    'Session ID', 'Student', 'Exam ID', 'Start Time', 'Seconds Active'
                ])
                # Format the dataframe to prevent comma separators
                df = format_dataframe(df)
                st.dataframe(df)
                
                # Add warning indicators for inactive students
                for _, row in df.iterrows():
                    if row['Seconds Active'] > 1800:  # 30 minutes
                        st.warning(f"Student {row['Student']} has been in the exam for {int(row['Seconds Active']/60)} minutes")
            else:
                st.info("No active sessions")
        except Exception as e:
            st.error(f"Error loading active sessions: {str(e)}")
    
    with tab2:
        st.header("Completed Sessions")
        try:
            cur.execute("""
                SELECT 
                    session_id,
                    student_id,
                    exam_id,
                    start_time,
                    end_time,
                    (
                        SELECT COUNT(*) 
                        FROM session_events 
                        WHERE session_id = e.session_id
                    ) as total_events
                FROM exam_sessions e
                WHERE status = 'completed'
                ORDER BY end_time DESC
            """)
            
            completed_sessions = cur.fetchall()
            if completed_sessions:
                df = pd.DataFrame(completed_sessions, columns=[
                    'Session ID', 'Student', 'Exam ID',
                    'Start Time', 'End Time', 'Events'
                ])
                # Format the dataframe to prevent comma separators
                df = format_dataframe(df)
                st.dataframe(df)
                
                # Add session details expander
                for _, row in df.iterrows():
                    with st.expander(f"Session Details - {row['Session ID']}"):
                        show_session_details(row['Session ID'])
            else:
                st.info("No completed sessions")
        except Exception as e:
            st.error(f"Error loading completed sessions: {str(e)}")
    
    cur.close()
    conn.close()

def show_session_details(session_id):
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("""
            SELECT event_type, event_data, timestamp
            FROM session_events
            WHERE session_id = %s
            ORDER BY timestamp
        """, (session_id,))
        
        events = cur.fetchall()
        if events:
            df = pd.DataFrame(events, columns=['Event Type', 'Details', 'Timestamp'])
            st.dataframe(df)
        else:
            st.info("No events recorded for this session")
    except Exception as e:
        st.error(f"Error loading session details: {str(e)}")
    
    cur.close()
    conn.close()

if __name__ == "__main__":
    display_sessions() 