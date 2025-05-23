import streamlit as st
import json
import os
from datetime import timedelta

DATA_FILE = 'voice_data.json'

def load_data():
    if os.path.exists(DATA_FILE) and os.path.getsize(DATA_FILE) > 0:
        with open(DATA_FILE, 'r') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                st.error("Error decoding the voice data file.")
                return {}
    return {}

def format_duration(seconds):
    return str(timedelta(seconds=int(seconds)))

def main():
    st.set_page_config(page_title="Voice Time Tracker", layout="wide")
    st.title("Discord Voice Time Tracker")

    data = load_data()

    if not data:
        st.warning("No data available.")
        return

    rows = []
    for user_id, info in data.items():
        rows.append({
            "Username": info["username"],
            "Total Time": format_duration(info["total_time"]),
            "Sessions": len(info["sessions"])
        })

    st.dataframe(rows, use_container_width=True)

if __name__ == "__main__":
    main()
