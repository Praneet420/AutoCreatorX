# haptic_alert_driver.py

import logging
import platform
import os

class HapticAlertDriver:
    def __init__(self):
        self.logger = logging.getLogger("HapticAlertDriver")
        self.system = platform.system()

    def trigger(self, intensity=1):
        try:
            if self.system == "Windows":
                # Windows fallback (sound + flash)
                self._fallback_beep()
            elif self.system == "Darwin":
                os.system("afplay /System/Library/Sounds/Submarine.aiff")
            elif self.system == "Linux":
                os.system("paplay /usr/share/sounds/freedesktop/stereo/alarm-clock-elapsed.oga")
            self.logger.info(f"Triggered haptic/sound feedback at intensity {intensity}")
        except Exception as e:
            self.logger.error(f"Failed to trigger haptic feedback: {e}")

    def _fallback_beep(self):
        try:
            import winsound
            winsound.Beep(1000, 300)
        except:
            os.system('echo -e "\a"')
