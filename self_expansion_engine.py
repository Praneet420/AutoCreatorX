# self_expansion_engine.py
import os, json
try:
    import yaml
except ImportError:
    yaml = None

CONFIG_FILE = "spartan_ai_config.yaml"
LOG_FILE = "logs/self_expansion_engine.log"

# Load config and check if this feature is enabled
enabled = False
config = {}
if yaml and os.path.exists(CONFIG_FILE):
    with open(CONFIG_FILE, 'r') as f:
        config = yaml.safe_load(f)
    enabled = config.get("enable_self_expansion_engine", False)

if not enabled:
    # Self-expansion is disabled; exit gracefully
    with open(LOG_FILE, 'a') as logf:
        logf.write("Self-Expansion Engine is disabled by configuration.\n")
    exit(0)

# Self-expansion logic starts here (will only run if enabled)
with open(LOG_FILE, 'a') as logf:
    logf.write("=== Self-Expansion Engine Activated ===\n")

# 1. Identify potential expansion opportunities
opportunities = []
# Example: if a certain domain appears frequently in user requests but no dedicated agent
if yaml and "agents" in config and "domain_map" in config:
    domains_covered = config["domain_map"].keys()
    # Let's pretend we have a way to gather recent prompt topics (could parse context switcher logs or user queries)
    recent_queries_file = "logs/recent_queries.log"
    domains_found = []
    if os.path.exists(recent_queries_file):
        with open(recent_queries_file, 'r') as f:
            data = f.read().lower()
        # simplistic approach: check for keywords in recent queries that match known domains
        for domain in ["finance", "tech", "health", "sports", "entertainment"]:
            if domain in data and domain not in domains_covered:
                domains_found.append(domain)
    if domains_found:
        for domain in set(domains_found):
            opportunities.append(f"Create new agent for domain: {domain}")

# 2. If GPT API is allowed, use it to generate suggestions (optional and offline by default)
if config.get("allow_external_api", False) and config.get("external_api_key"):
    import openai
    openai.api_key = config["external_api_key"]
    try:
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt="Suggest an improvement or new feature for the AutoCreatorX system given its current performance and goals.",
            max_tokens=100
        )
        suggestion = response.choices[0].text.strip()
        opportunities.append(f"GPT-suggested: {suggestion}")
    except Exception as e:
        logf.write(f"[WARN] GPT API call failed or was skipped: {e}\n")

# 3. Act on one of the opportunities (for safety, we log the suggestion and prepare content without enabling)
for opp in opportunities:
    logf.write(f"[OPPORTUNITY] {opp}\n")
    if opp.startswith("Create new agent for domain"):
        domain = opp.split(":")[1].strip()
        agent_name = f"{domain}_agent"
        # Create a skeleton for a new agent configuration
        if yaml:
            config["agents"][agent_name] = {"model": f"{domain}-model.bin", "type": "local", "enabled": True}
            config["domain_map"][domain] = agent_name
            logf.write(f"[ACTION] Added new agent config for '{agent_name}' (domain: {domain}).\n")
# Save updated config with new proposals
if yaml:
    with open(CONFIG_FILE, 'w') as f:
        yaml.safe_dump(config, f)
logf.write("=== Self-Expansion Engine Completed ===\n")
