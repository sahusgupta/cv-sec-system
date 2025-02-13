import streamlit as st
import pandas as pd
from datetime import datetime
import re

def parse_event_log(file_path):
    events = []
    with open(file_path, 'r') as f:
        first_timestamp = None
        for line in f:
            match = re.match(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}): (.+)', line.strip())
            if match:
                timestamp = datetime.strptime(match.group(1), '%Y-%m-%d %H:%M:%S')
                if first_timestamp is None:
                    first_timestamp = timestamp
                
                time_since_start = (timestamp - first_timestamp).total_seconds()
                event = match.group(2)
                
                severity = "Low"
                if "ERROR" in event:
                    severity = "High"
                elif "MULTIPLE_DISPLAYS_DETECTED" in event:
                    severity = "High"
                elif "SCREENSHOT_TAKEN" in event:
                    severity = "Medium"
                elif "CLIPBOARD_CHANGE" in event:
                    severity = "Medium"
                
                event_type = "Other"
                if "CTRL +" in event:
                    event_type = "Keyboard"
                elif "CLIPBOARD" in event:
                    event_type = "Clipboard"
                elif "SCREENSHOT" in event:
                    event_type = "Screenshot"
                elif "DISPLAYS" in event:
                    event_type = "System"
                elif "ERROR" in event:
                    event_type = "Error"
                
                events.append({
                    'timestamp': timestamp,
                    'time_since_start': time_since_start,
                    'event': event,
                    'severity': severity,
                    'event_type': event_type
                })
    
    return pd.DataFrame(events)

def format_time(seconds):
    minutes, seconds = divmod(int(seconds), 60)
    hours, minutes = divmod(minutes, 60)
    if hours > 0:
        return f"{hours}h {minutes}m {seconds}s"
    elif minutes > 0:
        return f"{minutes}m {seconds}s"
    else:
        return f"{seconds}s"
import streamlit as st
import pandas as pd
from datetime import datetime
import re
import plotly.graph_objects as go

def create_timeline(df, selected_types, selected_severities):
    if df.empty:
        return None
    
    filtered_df = df.copy()
    if 'All' not in selected_types:
        filtered_df = filtered_df[filtered_df['event_type'].isin(selected_types)]
    if 'All' not in selected_severities:
        filtered_df = filtered_df[filtered_df['severity'].isin(selected_severities)]
    
    colors = {
        'Low': '#00FF00',
        'Medium': '#FFA500',
        'High': '#FF0000'
    }
    
    symbols = {
        'Keyboard': 'circle',
        'Clipboard': 'square',
        'Screenshot': 'diamond',
        'System': 'triangle-up',
        'Error': 'x',
        'Other': 'star'
    }
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=filtered_df['time_since_start'],
        y=[1] * len(filtered_df),
        mode='markers',
        marker=dict(
            symbol=[symbols.get(t, 'circle') for t in filtered_df['event_type']],
            size=15,
            color=[colors.get(sev, '#808080') for sev in filtered_df['severity']],
            line=dict(color='black', width=1)
        ),
        text=[f"<b>{event_type}</b><br>"
              f"Event: {event[:50] + '...' if len(event) > 50 else event}<br>"
              f"Time: {format_time(time)}<br>"
              f"Severity: {sev}" 
              for event, time, sev, event_type in 
              zip(filtered_df['event'], filtered_df['time_since_start'], 
                  filtered_df['severity'], filtered_df['event_type'])],
        hoverinfo='text'
    ))
    
    total_time = filtered_df['time_since_start'].max()
    
    fig.update_layout(
        title='Exam Event Timeline',
        xaxis_title='Time Since Start',
        height=200,
        showlegend=False,
        xaxis=dict(
            ticktext=[format_time(t) for t in range(0, int(total_time) + 60, 60)],
            tickvals=list(range(0, int(total_time) + 60, 60)),
            tickmode='array'
        ),
        yaxis=dict(
            showticklabels=False,
            range=[0.95, 1.05]
        ),
        hovermode='closest'
    )
    
    return fig

def main():
    st.title("Exam Monitoring Timeline")
    
    try:
        df = parse_event_log('C:/Users/DutifulTrack724/OneDrive/Documents/GitHub/cv-sec-system/MVP/eventlog.txt')
    except Exception as e:
        st.error(f"Error loading event log: {e}")
        return
    
    st.sidebar.header("Filters")
    
    event_types = ['All'] + sorted(df['event_type'].unique().tolist())
    selected_type = st.sidebar.multiselect(
        "Event Types",
        event_types,
        default=['All']
    )
    
    severities = ['All'] + sorted(df['severity'].unique().tolist())
    selected_severity = st.sidebar.multiselect(
        "Severity Levels",
        severities,
        default=['All']
    )
    
    timeline_fig = create_timeline(df, selected_type, selected_severity)
    if timeline_fig:
        st.plotly_chart(timeline_fig, use_container_width=True)
    
    legend_cols = st.columns(6)
    with legend_cols[0]:
        st.markdown("🔵 Keyboard")
    with legend_cols[1]:
        st.markdown("⬛ Clipboard")
    with legend_cols[2]:
        st.markdown("💠 Screenshot")
    with legend_cols[3]:
        st.markdown("🔺 System")
    with legend_cols[4]:
        st.markdown("❌ Error")
    with legend_cols[5]:
        st.markdown("⭐ Other")
    
    severity_cols = st.columns(3)
    with severity_cols[0]:
        st.markdown("🟢 Low")
    with severity_cols[1]:
        st.markdown("🟡 Medium")
    with severity_cols[2]:
        st.markdown("🔴 High")
    
    filtered_df = df.copy()
    if 'All' not in selected_type:
        filtered_df = filtered_df[filtered_df['event_type'].isin(selected_type)]
    if 'All' not in selected_severity:
        filtered_df = filtered_df[filtered_df['severity'].isin(selected_severity)]
    
    st.header("Statistics")
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("Events by Type:")
        st.write(filtered_df['event_type'].value_counts())
        
    with col2:
        st.write("Events by Severity:")
        st.write(filtered_df['severity'].value_counts())

    
if __name__ == "__main__":
    main()