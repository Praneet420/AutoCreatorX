# agent_scorecard.py
import json, os

scorecard_path = "agent_scorecard.json"

# Initialize scorecard file if not present
if not os.path.exists(scorecard_path):
    initial_data = {}
    with open(scorecard_path, 'w') as f:
        json.dump(initial_data, f)

# Load current scorecard data (structure: {agent: {"success": int, "failure": int, "enabled": bool}})
with open(scorecard_path, 'r') as f:
    scorecard = json.load(f)

def record_success(agent_name):
    """Record a successful outcome for the given agent."""
    if agent_name not in scorecard:
        scorecard[agent_name] = {"success": 0, "failure": 0, "enabled": True}
    scorecard[agent_name]["success"] += 1
    _evaluate_agent(agent_name)

def record_failure(agent_name):
    """Record a failed outcome for the given agent."""
    if agent_name not in scorecard:
        scorecard[agent_name] = {"success": 0, "failure": 0, "enabled": True}
    scorecard[agent_name]["failure"] += 1
    _evaluate_agent(agent_name)

def _evaluate_agent(agent_name):
    """Evaluate the performance of the agent and disable it if below threshold."""
    data = scorecard[agent_name]
    total = data["success"] + data["failure"]
    if total >= 5:  # only evaluate after at least 5 attempts to avoid premature disabling
        success_rate = data["success"] / total
        if success_rate < 0.5 and data["enabled"]:
            # Disable the agent for poor performance
            scorecard[agent_name]["enabled"] = False
            # Log the disabling event
            with open("logs/agent_scorecard.log", 'a') as logf:
                logf.write(f"Agent {agent_name} disabled - success rate {success_rate*100:.1f}% (success: {data['success']}, failure: {data['failure']})\n")
            # Optionally, trigger an event or notify the system (handled elsewhere, e.g., Meta-Learning Observer)
        elif success_rate >= 0.5 and not data["enabled"]:
            # If performance improved (perhaps agent was re-enabled manually), keep it disabled until manual intervention
            # (We don't auto-reenable in this design without human review)
            pass

    # Save the updated scorecard to file for persistence
    with open(scorecard_path, 'w') as f:
        json.dump(scorecard, f, indent=2)

# Example usage: (In practice, these functions would be called by the system when an agent completes a task)
if __name__ == "__main__":
    # Simulate some outcomes
    record_failure("main")
    record_success("main")
    record_failure("main")
    record_failure("main")
    record_failure("main")
    record_failure("main")  # after multiple failures, "main" might be disabled if it was the failing one
    print("Scorecard:", scorecard)
