# meta_learning_monitor.py
import os, re
import statistics
try:
    import yaml
except ImportError:
    yaml = None

CONFIG_FILE = "spartan_ai_config.yaml"
LOG_DIR = "logs"
scorecard_file = os.path.join(LOG_DIR, "agent_scorecard.log")
diag_log_file = os.path.join(LOG_DIR, "spartan_diagnostics.log")

# Load current config
config = {}
if os.path.exists(CONFIG_FILE) and yaml:
    with open(CONFIG_FILE, 'r') as f:
        config = yaml.safe_load(f)

# Analyze agent performance from scorecard log (if available)
agent_performance = {}  # {agent: success_rate}
if os.path.exists(scorecard_file):
    with open(scorecard_file, 'r') as f:
        lines = f.readlines()
    # Example log lines expected: "Agent X - success: a, failure: b"
    for line in lines:
        match = re.match(r"Agent (\w+).*success:\s*(\d+).*failure:\s*(\d+)", line)
        if match:
            agent = match.group(1)
            success = int(match.group(2))
            failure = int(match.group(3))
            total = success + failure
            rate = (success / total) if total > 0 else 0.0
            agent_performance[agent] = rate

# If any agent has consistently low success rate, consider disabling it
disabled_agents = []
for agent, rate in agent_performance.items():
    if total > 5 and rate < 0.5:  # more than 5 attempts and <50% success
        if config.get("agents", {}).get(agent, {}).get("enabled", True):
            config["agents"][agent]["enabled"] = False
            disabled_agents.append(agent)

# Analyze recent diagnostics for recurring issues
issues = []
if os.path.exists(diag_log_file):
    with open(diag_log_file, 'r') as f:
        data = f.read()
    # Count occurrences of errors or warnings
    issues += re.findall(r"\[ERROR\]", data)
    issues += re.findall(r"\[WARN\]", data)

# If frequent issues found, consider adjusting retry policy or other parameters
if len(issues) > 5:  # more than 5 warnings/errors in diagnostics log
    old_retries = config.get("max_retries", 3)
    config["max_retries"] = old_retries + 1
    # Ensure not to exceed a reasonable cap
    if config["max_retries"] > 5:
        config["max_retries"] = 5

# If any agent was disabled, log this and (optionally) trigger event
log_file = os.path.join(LOG_DIR, "meta_learning_monitor.log")
with open(log_file, 'a') as lf:
    lf.write("=== Meta-Learning Adjustment Report ===\n")
    if disabled_agents:
        lf.write(f"Disabled agents due to poor performance: {', '.join(disabled_agents)}\n")
        # (Could trigger an 'agent_disabled' event for each)
    if len(issues) > 5:
        lf.write(f"High number of issues detected ({len(issues)}). Increased max_retries to {config.get('max_retries')}.\n")
    lf.write("Updated Config (partial):\n")
    if disabled_agents or len(issues) > 5:
        lf.write(str({k: config[k] for k in ['max_retries', 'agents']}) + "\n")
    else:
        lf.write("No significant changes made.\n")
    lf.write("=== End of Meta-Learning Report ===\n\n")

# Save updated config if changes were made
if yaml and (disabled_agents or len(issues) > 5):
    with open(CONFIG_FILE, 'w') as f:
        yaml.safe_dump(config, f)
