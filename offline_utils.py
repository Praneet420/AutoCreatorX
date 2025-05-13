# offline_utils.py

import os
import logging
import shutil
from pathlib import Path

class OfflineUtils:
    def __init__(self):
        self.logger = logging.getLogger("OfflineUtils")

    def safe_copy(self, src, dst):
        try:
            Path(dst).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(src, dst)
            self.logger.info(f"Copied {src} to {dst}")
        except Exception as e:
            self.logger.error(f"Failed to copy {src} to {dst}: {e}")

    def ensure_folders(self, folder_list):
        for folder in folder_list:
            Path(folder).mkdir(parents=True, exist_ok=True)
            self.logger.info(f"Ensured directory: {folder}")

    def scan_for_files(self, directory, pattern=".txt"):
        files = list(Path(directory).rglob(f"*{pattern}"))
        self.logger.info(f"Found {len(files)} '{pattern}' files in {directory}")
        return files
