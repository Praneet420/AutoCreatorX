# logs_monitor_panel.py
import os, glob, tailer

LOG_DIR = "logs"
NUM_LINES = 10  # number of recent lines to show per log

if not os.path.isdir(LOG_DIR):
    print(f"No logs directory found at {LOG_DIR}.")
    exit(0)

log_files = sorted(glob.glob(os.path.join(LOG_DIR, "*.log")))

print("=== System Logs Monitor Panel ===")
for log_file in log_files:
    log_name = os.path.basename(log_file)
    print(f"\n--- Showing last {NUM_LINES} lines of {log_name} ---")
    try:
        # Use tailer to get the last N lines for efficiency, if available
        lines = tailer.tail(open(log_file, 'r'), NUM_LINES)
    except Exception as e:
        lines = []
        try:
            # Fallback: read all lines (not efficient for large files, but safe for smaller logs)
            with open(log_file, 'r') as f:
                content = f.readlines()
                lines = content[-NUM_LINES:] if len(content) >= NUM_LINES else content
        except Exception as e2:
            print(f"Could not read {log_name}: {e2}")
            continue
    for line in lines:
        print(line.rstrip())
print("\n=== End of Logs ===")
