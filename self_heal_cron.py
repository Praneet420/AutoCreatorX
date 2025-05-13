# self_heal_cron.py
import os, time, subprocess
try:
    import yaml
except ImportError:
    yaml = None

CONFIG_FILE = "spartan_ai_config.yaml"
LOG_DIR = "logs"
LOG_FILE = os.path.join(LOG_DIR, "self_heal_cron.log")

def log(message):
    """Append a message to the self-heal log and print it."""
    with open(LOG_FILE, 'a') as f:
        f.write(message + "\n")
    print(message)

# Load config to get any necessary parameters
config = {}
if os.path.exists(CONFIG_FILE) and yaml:
    with open(CONFIG_FILE, 'r') as f:
        config = yaml.safe_load(f)

log("=== Self-Healing Cron Job Started ===")

# 1. Run diagnostics to get current health status
diag_status = 0
if os.path.exists("spartan_diagnostics.py"):
    # Run diagnostics as a subprocess to isolate it
    try:
        result = subprocess.run(["python", "spartan_diagnostics.py"], capture_output=True, text=True, timeout=60)
        diag_status = result.returncode
        if diag_status == 0:
            log("[INFO] Diagnostics completed successfully.")
        else:
            log("[WARN] Diagnostics reported issues. Return code: {}".format(diag_status))
            # Capture and log diagnostics output for review
            diag_output = result.stdout.strip()
            if diag_output:
                log("[DIAGNOSTICS OUTPUT] " + diag_output.replace("\n", " | "))
    except Exception as e:
        log(f"[ERROR] Failed to run diagnostics: {e}")
else:
    log("[ERROR] Diagnostics script not found; skipping health check.")

# 2. Maintenance tasks (cleanup and log rotation)
# Example: Delete old log files beyond a retention period
retention_days = 7
now = time.time()
if os.path.isdir(LOG_DIR):
    for fname in os.listdir(LOG_DIR):
        fpath = os.path.join(LOG_DIR, fname)
        if os.path.isfile(fpath):
            age_days = (now - os.path.getmtime(fpath)) / 86400
            if age_days > retention_days:
                try:
                    os.remove(fpath)
                    log(f"[INFO] Removed old log file: {fname} (age {age_days:.1f} days).")
                except Exception as e:
                    log(f"[WARN] Could not remove log file {fname}: {e}")

# (Additional maintenance like clearing cache or temp files can be added here)
temp_dirs = ["cache", "tmp"]
for d in temp_dirs:
    if os.path.isdir(d):
        try:
            for root, dirs, files in os.walk(d):
                for file in files:
                    os.remove(os.path.join(root, file))
            log(f"[INFO] Cleared temporary files in {d}/.")
        except Exception as e:
            log(f"[WARN] Error while clearing {d}/: {e}")

# 3. Auto-restart logic if issues were detected
# If diagnostics returned non-zero or flagged a major issue, attempt to restart services
if diag_status != 0:
    log("[ACTION] Attempting to restart affected modules due to diagnostic issues.")
    # Example: restart entire system or specific services
    # (In a real scenario, this might interface with systemd or application orchestrator)
    try:
        # Here we simulate a simple restart by writing a flag or re-initializing components
        open("restart.flag", 'w').close()  # Create a flag file to signal external supervisor
        log("[INFO] Created restart flag. System supervisor should handle the actual restart.")
    except Exception as e:
        log(f"[ERROR] Failed to initiate restart: {e}")

# 4. Conclude self-healing sequence
log("=== Self-Healing Cron Job Completed ===\n")
