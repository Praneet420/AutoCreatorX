# commander_hud.py

import streamlit as st
import time

st.markdown("""
<style>
#hudBox {
    background-color: #111;
    border: 1px solid red;
    padding: 10px;
    font-family: monospace;
    font-size: 13px;
    color: #FF4444;
    position: fixed;
    bottom: 5px;
    right: 10px;
    z-index: 9999;
    box-shadow: 0 0 10px #FF0000;
    border-radius: 5px;
    max-width: 300px;
}
</style>
<div id="hudBox">
    <b>COMMANDER HUD</b><br>
    Status: <span style="color:#0F0">Monitoring</span><br>
    Last Check: {}</div>
""".format(time.strftime("%H:%M:%S")), unsafe_allow_html=True)

# Optional: show warning
if st.session_state.get("override_active"):
    st.error("⚠️ Manual Override Active")
