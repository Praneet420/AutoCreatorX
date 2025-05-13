# dashboard_tabs.py

import streamlit as st
from commander_controls import CommanderControls

TABS = [
    "🧠 Dashboard",
    "📋 Logs",
    "🛡️ Watchman AI",
    "🎥 Media Tools",
    "📈 Analytics",
    "📊 HUD",
    "🧪 Recovery Tools"
]

def register_tabs():
    tab = st.sidebar.radio("🗂️ Select Module Tab", TABS)
    st.session_state["active_tab"] = tab
    return tab

controls = CommanderControls()
active_tab = register_tabs()

if controls.show_debug_controls():
    st.warning("Debug simulation enabled.")
