# smart_scheduler.py

import logging
import time
from datetime import datetime, timedelta

class SmartScheduler:
    def __init__(self):
        self.logger = logging.getLogger("SmartScheduler")
        self.scheduled_tasks = []

    def schedule_task(self, task_fn, best_hour=18):
        now = datetime.now()
        run_time = now.replace(hour=best_hour, minute=0, second=0, microsecond=0)
        if run_time < now:
            run_time += timedelta(days=1)

        self.scheduled_tasks.append((run_time.timestamp(), task_fn))
        self.logger.info(f"Task scheduled for {run_time.strftime('%Y-%m-%d %H:%M:%S')}")

    def run_pending(self):
        current_time = time.time()
        for scheduled_time, task in list(self.scheduled_tasks):
            if current_time >= scheduled_time:
                try:
                    task()
                    self.logger.info("Scheduled task executed successfully.")
                except Exception as e:
                    self.logger.error(f"Scheduled task failed: {e}")
                self.scheduled_tasks.remove((scheduled_time, task))
