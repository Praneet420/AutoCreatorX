# spartan_diagnostics.py
import os, shutil, platform
import psutil  # psutil is used for system health checks (installed locally)
try:
    import yaml
except ImportError:
    yaml = None  # handle case where PyYAML isn't installed

# Load global config
config_path = "spartan_ai_config.yaml"
if not os.path.exists(config_path):
    print("[ERROR] Global config file missing!")
    exit(1)
with open(config_path, 'r') as f:
    config = yaml.safe_load(f) if yaml else {}  # use yaml if available

# Ensure logs directory exists for logging
log_dir = config.get("log_dir", "logs")
if not os.path.isdir(log_dir):
    os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, "spartan_diagnostics.log")

def log(message):
    """Append a message to the diagnostics log file and print to console."""
    try:
        with open(log_file, 'a') as lf:
            lf.write(message + "\n")
    except Exception as e:
        print(f"[ERROR] Unable to write to log file: {e}")
    print(message)

log("=== Running System Readiness Scanner ===")

# 1. Check model and resource files
all_models_ok = True
if "agents" in config:
    for agent, props in config["agents"].items():
        if props.get("type") == "local":
            model_path = props.get("model")
            if model_path:
                if os.path.exists(model_path):
                    log(f"[OK] Local model for agent '{agent}' found at: {model_path}")
                else:
                    log(f"[ERROR] Required model for agent '{agent}' not found at: {model_path}")
                    all_models_ok = False
            # If no model path specified (could be rule-based agent), skip check
else:
    log("[WARN] No agent definitions found in config to validate models.")

# 2. Check multimedia support if required
audio_required = config.get("audio_support_required", False)
video_required = config.get("video_support_required", False)
if audio_required:
    try:
        import pyttsx3  # Text-to-speech library as an example for audio
        audio_engine = pyttsx3.init()
        log("[OK] Audio support is available (pyttsx3 library initialized).")
    except Exception as e:
        log(f"[ERROR] Audio support required but not available: {e}")
        all_models_ok = False

if video_required:
    ffmpeg_installed = shutil.which("ffmpeg") is not None
    if ffmpeg_installed:
        log("[OK] Video support is available (FFmpeg found).")
    else:
        log("[ERROR] Video support required but FFmpeg is not installed or not in PATH.")
        all_models_ok = False

# 3. System health checks (CPU, Memory, Disk)
health_ok = True
# Check CPU load (should be below 90% at startup ideally)
cpu_load = psutil.cpu_percent(interval=1)
if cpu_load > 90:
    log(f"[WARN] High CPU load detected at startup: {cpu_load}%.")
    # Not critical enough to fail startup, but flagging
    health_ok = health_ok and True
else:
    log(f"[OK] CPU load is normal: {cpu_load}%.")

# Check available memory (should have some free memory to operate)
mem = psutil.virtual_memory()
if mem.available < 200 * 1024 * 1024:  # less than 200MB
    log(f"[ERROR] Low available memory: {mem.available/1024/1024:.1f} MB.")
    health_ok = False
else:
    log(f"[OK] Available memory: {mem.available/1024/1024:.1f} MB.")

# Check disk space (at least 1GB free on current drive)
disk = psutil.disk_usage(os.getcwd())
if disk.free < 1 * 1024 * 1024 * 1024:  # less than 1 GB
    log(f"[ERROR] Low disk space: {disk.free/1024/1024/1024:.2f} GB free.")
    health_ok = False
else:
    log(f"[OK] Sufficient disk space: {disk.free/1024/1024/1024:.2f} GB free.")

# 4. Summarize and trigger events if needed
if all_models_ok and health_ok:
    log("[INFO] System Readiness Check PASSED.")
    # Could trigger a success event (notifying system is ready)
else:
    log("[WARN] System Readiness Check found issues.")
    # If critical issues exist, trigger anomaly or failure event for self-healing
    if not all_models_ok or not health_ok:
        # Here we would integrate with event_map to signal a resource issue
        event = "resource_issue"
        log(f"[ACTION] Triggering event: {event} for self-healing due to diagnostics failure.")
# End of diagnostics
