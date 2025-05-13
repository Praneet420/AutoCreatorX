# notification_engine.py

import logging
import streamlit as st
from audio_engine import AudioEngine

class NotificationEngine:
    def __init__(self):
        self.logger = logging.getLogger("NotificationEngine")
        self.audio = AudioEngine()

    def notify(self, msg: str, level="info"):
        if level == "info":
            st.toast(f"ℹ️ {msg}")
            self.audio.speak("Notification. " + msg)
        elif level == "warning":
            st.warning(f"⚠️ {msg}")
            self.audio.speak("Warning. " + msg)
        elif level == "error":
            st.error(f"🚨 {msg}")
            self.audio.speak("Critical alert. " + msg)
        else:
            st.info(msg)
            self.audio.speak(msg)
