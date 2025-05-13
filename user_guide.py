"""
AutoCreatorX Dynamic User Guide
Commander Version 1.0

Description:
    Provides modular CLI and Dashboard help system.
"""

class UserGuide:
    @staticmethod
    def display_main_menu():
        print("\n🧠 AutoCreatorX Help Menu:")
        print("  - help               : View this menu")
        print("  - launch dashboard   : Launch the real-time monitoring dashboard")
        print("  - exit               : Exit the system")
        print("\nAdvanced operations and tutorials are available in /docs/tutorials/ folder.")

    @staticmethod
    def module_warning(module_name):
        warnings = {
            "viral_launch": "⚠️ WARNING: Viral Launch is resource-intensive. Ensure your RAM/GPU is sufficient!",
            "honeypot": "⚠️ WARNING: Honeypot traps are aggressive. Activate with caution.",
            "rebranding": "⚠️ WARNING: Stealth Rebranding alters your account signature."
        }
        return warnings.get(module_name.lower(), "⚠️ No special warnings for this module.")
