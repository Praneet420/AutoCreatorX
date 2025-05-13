# context_aware_switcher.py
import re
try:
    import yaml
except ImportError:
    yaml = None

CONFIG_FILE = "spartan_ai_config.yaml"
# Load config for agent info and settings
config = {}
if yaml and os.path.exists(CONFIG_FILE):
    with open(CONFIG_FILE, 'r') as f:
        config = yaml.safe_load(f)

# Extract necessary info from config
allow_external = config.get("allow_external_api", False)
offline_mode = (config.get("mode") == "offline") or not allow_external
agents = config.get("agents", {})
domain_map = config.get("domain_map", {})
urgent_agent = config.get("urgent_agent", None)

def route_prompt(prompt, urgent=False):
    """Determine which agent should handle the given prompt based on domain and urgency."""
    prompt_lower = prompt.lower()
    chosen_agent = None

    # If urgent, use the designated urgent agent (if any)
    if urgent and urgent_agent:
        # Ensure urgent agent is enabled and available
        if urgent_agent in agents and agents[urgent_agent].get("enabled", True):
            # If offline mode and urgent agent is external, we may skip it
            if not offline_mode or agents[urgent_agent]["type"] == "local":
                chosen_agent = urgent_agent

    # Determine domain from keywords if not urgent or no urgent agent selected
    if chosen_agent is None:
        for keyword, agent_key in domain_map.items():
            if re.search(rf"\b{keyword}\b", prompt_lower):
                if agent_key in agents and agents[agent_key].get("enabled", True):
                    # If offline and the mapped agent is external, skip to next
                    if offline_mode and agents[agent_key]["type"] == "external":
                        continue
                    chosen_agent = agent_key
                    break

    # Fallback to default if no specific domain match or chosen agent was skipped
    if chosen_agent is None:
        default_agent = domain_map.get("default", None) or (config.get("fallback_order")[0] if config.get("fallback_order") else None)
        if default_agent:
            # If default is external and offline, try next fallback
            if offline_mode and default_agent in agents and agents[default_agent]["type"] == "external":
                # Use the first local agent in fallback_order
                fallback_list = config.get("fallback_order", [])
                for agent_key in fallback_list:
                    if agent_key in agents and agents[agent_key]["type"] == "local" and agents[agent_key].get("enabled", True):
                        chosen_agent = agent_key
                        break
            else:
                chosen_agent = default_agent

    # Final safety: if chosen agent still None, pick any enabled local agent
    if chosen_agent is None:
        for agent_key, props in agents.items():
            if props.get("enabled", True) and props.get("type") == "local":
                chosen_agent = agent_key
                break

    # At this point, chosen_agent is the key of the agent to handle the prompt
    return chosen_agent

# Example usage:
if __name__ == "__main__":
    test_prompt = "What's the latest update in the stock market?"  # finance-related prompt
    agent = route_prompt(test_prompt, urgent=False)
    print(f"Prompt: {test_prompt}\nRouted to agent: {agent}")
    # If urgent flag is used
    urgent_prompt = "System outage, need immediate assistance!"
    agent2 = route_prompt(urgent_prompt, urgent=True)
    print(f"Prompt: {urgent_prompt}\nRouted to agent: {agent2}")
