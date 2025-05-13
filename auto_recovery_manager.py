# auto_recovery_manager.py

import os
import logging
import subprocess

class AutoRecoveryManager:
    def __init__(self):
        self.logger = logging.getLogger("AutoRecoveryManager")

    def attempt_restart(self, module_name: str):
        self.logger.warning(f"[Recovery] Attempting to restart module: {module_name}")
        try:
            result = subprocess.run(["python", f"{module_name}.py"], capture_output=True)
            if result.returncode == 0:
                self.logger.info(f"[Recovery] {module_name} restarted successfully.")
            else:
                self.logger.error(f"[Recovery] Failed to restart {module_name}.")
        except Exception as e:
            self.logger.error(f"[Recovery] Exception while restarting {module_name}: {e}")
