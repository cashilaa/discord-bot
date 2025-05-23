import streamlit as st
import json
import pandas as pd
import plotly.express as px
import datetime
import os
import subprocess
import sys
import time
from datetime import datetime

# Set page configuration
st.set_page_config(
    page_title="Discord Voice Tracker",
    page_icon="🎤",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Global variable to track bot process
bot_process = None

def run_bot_process():
    """Run the Discord bot in a separate process"""
    global bot_process
    try:
        # Check if bot is already running
        if bot_process and bot_process.poll() is None:
            st.sidebar.warning("Bot is already running!")
            return
        
        # Start the bot process
        if sys.platform == 'win32':
            # Hide console window on Windows
            log_file = open("bot_output.log", "w")
            bot_process = subprocess.Popen(
                ["python", "bot.py"],
                stdout=log_file,
                stderr=log_file,
                creationflags=subprocess.CREATE_NEW_CONSOLE
            )
        else:
            # For non-Windows platforms
            log_file = open("bot_output.log", "w")
            bot_process = subprocess.Popen(
                ["python", "bot.py"],
                stdout=log_file,
                stderr=log_file
            )
        
        st.sidebar.success("Bot started successfully!")
    except Exception as e:
        st.sidebar.error(f"Error starting bot: {str(e)}")

def stop_bot_process():
    """Stop the Discord bot process"""
    global bot_process
    try:
        if bot_process and bot_process.poll() is None:
            bot_process.terminate()
            bot_process = None
            st.sidebar.success("Bot stopped successfully!")
        else:
            st.sidebar.warning("Bot is not running!")
    except Exception as e:
        st.sidebar.error(f"Error stopping bot: {str(e)}")

def check_bot_status():
    """Check if the bot process is running"""
    global bot_process
    if bot_process and bot_process.poll() is None:
        return "Running"
    else:
        return "Stopped"

# Auto-refresh functionality using Streamlit's built-in functionality
# We'll use a simpler approach that doesn't require threading

# Path to the JSON file for storing voice time data
DATA_FILE = 'voice_data.json'

# Load existing data from the JSON file
def load_data():
    if os.path.exists(DATA_FILE) and os.path.getsize(DATA_FILE) > 0:
        with open(DATA_FILE, 'r') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {}
    return {}

# Format time in seconds to hours and minutes
def format_time(seconds):
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{int(hours)} hours and {int(minutes)} minutes"

# Sidebar for bot controls
st.sidebar.title("Bot Controls")
bot_status = check_bot_status()
st.sidebar.markdown(f"**Bot Status:** {bot_status}")

col1, col2 = st.sidebar.columns(2)
with col1:
    if st.button("Start Bot", key="start_bot"):
        run_bot_process()
        st.rerun()
with col2:
    if st.button("Stop Bot", key="stop_bot"):
        stop_bot_process()
        st.rerun()

# Auto-refresh section
st.sidebar.subheader("Data Refresh")

# Manual refresh button
if st.sidebar.button("Refresh Data Now"):
    st.rerun()

# Auto-refresh toggle
auto_refresh = st.sidebar.checkbox("Enable Auto Refresh", value=False)
if auto_refresh:
    refresh_rate = st.sidebar.slider("Refresh rate (seconds)", 
                                    min_value=5, 
                                    max_value=60, 
                                    value=10)
    st.sidebar.info(f"Auto-refreshing every {refresh_rate} seconds")
    
    # This creates a placeholder that updates based on the current time
    # When it changes, Streamlit will rerun the app
    refresh_placeholder = st.sidebar.empty()
    refresh_placeholder.text(f"Last refresh: {datetime.now().strftime('%H:%M:%S')}")
    time.sleep(refresh_rate)
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.info("""
**Note:** Starting the bot from this interface will open a new console window.
The bot needs to be running for voice data to be collected.
""")

# Main app header
st.title("Discord Voice Tracker Dashboard")
st.markdown("### Voice Channel Session History")

# Load the voice data
voice_data = load_data()

# Display data status
if not voice_data:
    st.warning("No voice data found. Make sure the bot is running and users have joined voice channels.")
else:
    st.success(f"Loaded data for {len(voice_data)} users with {sum(len(data['sessions']) for _, data in voice_data.items())} total sessions.")

if not voice_data:
    st.info("No voice channel data recorded yet.")
else:
    # Collect all sessions from all users
    all_sessions = []
    for user_id, data in voice_data.items():
        username = data['username']
        for session in data['sessions']:
            start_time = datetime.fromisoformat(session['start'])
            end_time = datetime.fromisoformat(session['end'])
            
            all_sessions.append({
                "User ID": user_id,
                "Username": username,
                "Channel": session['channel'],
                "Start Time": start_time,
                "End Time": end_time,
                "Duration (seconds)": session['duration'],
                "Duration": format_time(session['duration'])
            })
    
    # Convert to dataframe and sort by start time (most recent first)
    sessions_df = pd.DataFrame(all_sessions)
    sessions_df = sessions_df.sort_values(by="Start Time", ascending=False)
    
    # Date range filter
    if not sessions_df.empty:
        min_date = sessions_df["Start Time"].min().date()
        max_date = sessions_df["End Time"].max().date()
        
        date_range = st.date_input(
            "Filter by date range:",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date
        )
        
        if len(date_range) == 2:
            start_date, end_date = date_range
            filtered_df = sessions_df[
                (sessions_df["Start Time"].dt.date >= start_date) & 
                (sessions_df["End Time"].dt.date <= end_date)
            ]
            
            # User filter
            unique_users = sorted(filtered_df["Username"].unique())
            selected_users = st.multiselect(
                "Filter by users:",
                options=unique_users,
                default=unique_users
            )
            
            if selected_users:
                filtered_df = filtered_df[filtered_df["Username"].isin(selected_users)]
                
                # Display the filtered sessions with enhanced formatting
                st.subheader("Session Details")
                
                # Create columns for metrics
                metric_cols = st.columns(3)
                with metric_cols[0]:
                    total_duration = filtered_df["Duration (seconds)"].sum()
                    st.metric("Total Time", format_time(total_duration))
                with metric_cols[1]:
                    avg_duration = filtered_df["Duration (seconds)"].mean()
                    st.metric("Average Session Length", format_time(avg_duration))
                with metric_cols[2]:
                    st.metric("Number of Sessions", len(filtered_df))
                
                # Format the dataframe for display
                display_df = filtered_df.copy()
                display_df["Start Time"] = display_df["Start Time"].dt.strftime("%Y-%m-%d %H:%M:%S")
                display_df["End Time"] = display_df["End Time"].dt.strftime("%Y-%m-%d %H:%M:%S")
                display_cols = ["Username", "Channel", "Start Time", "End Time", "Duration"]
                
                # Add a search box
                search_term = st.text_input("Search sessions (by username or channel):", "")
                if search_term:
                    display_df = display_df[
                        display_df["Username"].str.contains(search_term, case=False) | 
                        display_df["Channel"].str.contains(search_term, case=False)
                    ]
                
                # Display the dataframe with pagination
                st.dataframe(display_df[display_cols], use_container_width=True)
                
                # Add download button for CSV export
                @st.cache_data
                def convert_df_to_csv(df):
                    return df[display_cols].to_csv(index=False).encode('utf-8')
                
                csv = convert_df_to_csv(display_df)
                st.download_button(
                    label="Download data as CSV",
                    data=csv,
                    file_name='voice_sessions.csv',
                    mime='text/csv',
                )
                
                # Timeline visualization
                st.subheader("Voice Sessions Timeline")
                
                # Add visualization options
                viz_col1, viz_col2 = st.columns(2)
                with viz_col1:
                    group_by = st.radio(
                        "Group timeline by:",
                        ["User and Channel", "User Only", "Channel Only"]
                    )
                with viz_col2:
                    color_by = st.radio(
                        "Color by:",
                        ["Username", "Channel"]
                    )
                
                # Prepare timeline data based on grouping option
                timeline_df = filtered_df.copy()
                if group_by == "User and Channel":
                    timeline_df["Group"] = timeline_df["Username"] + " - " + timeline_df["Channel"]
                elif group_by == "User Only":
                    timeline_df["Group"] = timeline_df["Username"]
                else:  # Channel Only
                    timeline_df["Group"] = timeline_df["Channel"]
                
                # Create the timeline visualization
                fig = px.timeline(
                    timeline_df,
                    x_start="Start Time",
                    x_end="End Time",
                    y="Group",
                    color=color_by,
                    hover_data=["Username", "Channel", "Duration"],
                    title="Voice Channel Sessions Timeline"
                )
                
                # Customize the figure
                fig.update_yaxes(autorange="reversed")
                fig.update_layout(
                    height=600,
                    legend_title_text=color_by,
                    hovermode="closest"
                )
                
                # Display the timeline
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Please select at least one user to display sessions.")
        else:
            st.info("Please select a valid date range.")
    else:
        st.info("No session history available.")

# Footer
st.markdown("---")
st.markdown("Discord Voice Tracker Dashboard - Powered by Streamlit")
