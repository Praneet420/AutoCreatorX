# sentiment_deflector.py
import re

# Define a list of toxic or disallowed terms (this can be expanded as needed)
banned_terms = [
    "hate", "kill", "attack", "racist", "offensive_term",  # etc. (add real terms as needed)
    "ignore all rules", "bypass filter"  # include known prompt-injection phrases to catch malicious intents
]

def sanitize_prompt(prompt):
    """Replace characters of detected banned words with asterisks to neutralize the prompt."""
    sanitized = prompt
    for term in banned_terms:
        pattern = re.compile(re.escape(term), re.IGNORECASE)
        sanitized = pattern.sub(lambda m: "*" * len(m.group()), sanitized)
    return sanitized

def check_prompt(prompt, override=False):
    """
    Check the prompt for toxicity. 
    Returns a tuple: (is_flagged, safe_prompt).
    is_flagged = True if prompt is toxic (and override not provided).
    safe_prompt = either the sanitized prompt or original prompt if it's safe or override is allowed.
    """
    lower_prompt = prompt.lower()
    for term in banned_terms:
        if term in lower_prompt:
            if not override:
                # Log the toxic incident (here we simply print, but ideally write to a log file)
                with open("logs/sentiment_deflector.log", 'a') as logf:
                    logf.write(f"[FLAG] Detected toxic term '{term}' in prompt: \"{prompt}\"\n")
                # Return flagged status and sanitized prompt
                return True, sanitize_prompt(prompt)
            else:
                # If override is True, allow the prompt but note it in log
                with open("logs/sentiment_deflector.log", 'a') as logf:
                    logf.write(f"[OVERRIDE] Toxic term '{term}' overridden in prompt: \"{prompt}\"\n")
                return False, prompt
    # If no banned term found, prompt is safe
    return False, prompt

# Example usage:
if __name__ == "__main__":
    user_prompt = "I want to attack the problem with a new strategy."
    flagged, output_prompt = check_prompt(user_prompt, override=False)
    print("Flagged:", flagged)
    print("Output Prompt:", output_prompt)
