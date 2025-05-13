# commander_controls.py

import streamlit as st

class CommanderControls:
    def __init__(self):
        self._manual_override_enabled = st.sidebar.checkbox("🕹️ Manual Override Mode")
        self._auto_failback_enabled = st.sidebar.checkbox("🔁 Auto-Failback Active", value=True)
        self._dashboard_refresh = st.sidebar.selectbox("📡 Refresh Rate (sec)", [15, 30, 60], index=1)

    def override_mode(self):
        return self._manual_override_enabled

    def auto_failback(self):
        return self._auto_failback_enabled

    def refresh_rate(self):
        return int(self._dashboard_refresh)

    def show_debug_controls(self):
        st.sidebar.subheader("⚙️ Debug Options")
        if st.sidebar.button("🧪 Simulate Failure"):
            st.warning("[SIMULATION] Critical system module failure triggered.")
            return True
        return False
