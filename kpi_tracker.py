# kpi_tracker.py

import json
import time
from datetime import datetime

class KPITracker:
    def __init__(self, filepath="logs/kpi_metrics.json"):
        self.filepath = filepath
        self.metrics = self._load()

    def _load(self):
        try:
            with open(self.filepath, 'r') as f:
                return json.load(f)
        except:
            return {
                "revenue": [],
                "views": [],
                "subscribers": []
            }

    def update_kpi(self, metric, value):
        if metric in self.metrics:
            self.metrics[metric].append({"timestamp": time.time(), "value": value})
            self._save()

    def get_latest(self, metric):
        if metric in self.metrics and self.metrics[metric]:
            return self.metrics[metric][-1]['value']
        return 0

    def _save(self):
        with open(self.filepath, 'w') as f:
            json.dump(self.metrics, f, indent=2)
