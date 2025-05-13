# full_log_viewer.py

import streamlit as st
import os

LOG_PATH = "logs"

st.title("📋 Full System Log Viewer")

selected_file = st.selectbox("Select log file", [f for f in os.listdir(LOG_PATH) if f.endswith(".log")])

if selected_file:
    st.subheader(f"📄 Viewing: {selected_file}")
    with open(os.path.join(LOG_PATH, selected_file), "r") as f:
        lines = f.readlines()[-200:]  # limit view to last 200 lines
        st.text("".join(lines))
