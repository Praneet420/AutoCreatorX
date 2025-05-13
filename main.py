"""
AutoCreatorX Main Controller
Commander Version 1.0

Author: COMMANDER
Description:
    - Initializes AutoCreatorX systems
    - Launches modules based on user configuration
    - Handles dashboard or CLI interactions
"""

import sys
import os
import argparse
from config.settings import SETTINGS
from user_guide import UserGuide

def setup_environment():
    """Sets up basic environment checks."""
    print("🔧 Setting up AutoCreatorX environment...")
    required_folders = [
        "logs", "deployment", "core", "media", "platform", "monetization",
        "system", "dashboard", "dashboard/templates", "visualizations",
        "intelligence", "tests", "docs/tutorials", "config"
    ]
    for folder in required_folders:
        if not os.path.exists(folder):
            os.makedirs(folder)
            print(f"✅ Created missing folder: {folder}")

def launch_dashboard():
    """Launch the Live Dashboard Server."""
    print("🚀 Launching AutoCreatorX Dashboard...")
    os.system('python dashboard/server.py')

def run_cli_mode():
    """Run in Console Mode."""
    print("🎯 Welcome to AutoCreatorX CLI Command Center.")
    print("Type 'help' to access the Dynamic User Guide.\n")

    while True:
        command = input("Command > ").strip().lower()
        if command == "exit":
            print("⚡ Exiting AutoCreatorX. Goodbye, Commander!")
            break
        elif command == "help":
            UserGuide.display_main_menu()
        elif command == "launch dashboard":
            launch_dashboard()
        else:
            print(f"❌ Unknown Command: {command}. Type 'help'.")

def main():
    """Main function to initialize AutoCreatorX."""
    setup_environment()

    parser = argparse.ArgumentParser(description="AutoCreatorX Launcher")
    parser.add_argument('--dashboard', action='store_true', help="Launch Dashboard Mode directly.")
    args = parser.parse_args()

    if args.dashboard:
        launch_dashboard()
    else:
        run_cli_mode()

if __name__ == "__main__":
    main()
