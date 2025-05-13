# api_key_rotator.py
import os, time
try:
    import yaml
except ImportError:
    yaml = None

CONFIG_FILE = "spartan_ai_config.yaml"
LOG_FILE = "logs/api_key_rotator.log"

# Load configuration
config = {}
if yaml and os.path.exists(CONFIG_FILE):
    with open(CONFIG_FILE, 'r') as f:
        config = yaml.safe_load(f)
else:
    # If YAML not available or config missing, exit
    exit(0)

enabled = config.get("enable_api_key_rotator", False)
if not enabled or not config.get("allow_external_api", False):
    # Feature disabled or external API not in use, nothing to do
    with open(LOG_FILE, 'a') as logf:
        logf.write(f"{time.ctime()}: API Key Rotator is disabled or not needed (offline mode).\n")
    exit(0)

api_keys = config.get("api_keys", [])
current_key = config.get("external_api_key")
if not api_keys or len(api_keys) < 2:
    # Not enough keys to rotate
    with open(LOG_FILE, 'a') as logf:
        logf.write(f"{time.ctime()}: Only one or no API key configured, rotation not applicable.\n")
    exit(0)

# Determine current key index
try:
    current_index = api_keys.index(current_key)
except ValueError:
    current_index = -1  # current key not found in list
# Choose the next key in the list
new_index = (current_index + 1) % len(api_keys) if current_index != -1 else 0
new_key = api_keys[new_index]

# Update the config with new key
config["external_api_key"] = new_key
# Optionally, store the index as well
config["current_api_key_index"] = new_index

# Save the updated config
if yaml:
    with open(CONFIG_FILE, 'w') as f:
        yaml.safe_dump(config, f)

# Log the rotation event
with open(LOG_FILE, 'a') as logf:
    logf.write(f"{time.ctime()}: API key rotated to index {new_index}.\n")
