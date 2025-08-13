# run.py
"""
Launcher script to start or stop QEM tasks.

Usage examples:
  python run.py --action resume           # uses YAML mode
  python run.py --action stop --mode S    # override mode to 'S'
"""

import argparse
from qemTasksHandler import main, configParser

def main_launcher():
    # Load config
    config = configParser.load_config()
    yaml_mode = config['settings'].get('mode', 'A').upper()  # default 'A'

    # Parse CLI arguments
    parser = argparse.ArgumentParser(description="Run or Stop QEM tasks")
    parser.add_argument(
        "--action",
        type=str,
        choices=["resume", "stop"],
        required=True,
        help="Action to perform: resume or stop"
    )
    parser.add_argument(
        "--mode",
        type=str,
        choices=["S", "A"],
        default=yaml_mode,
        help="Tasks selection mode: 'S' (selected tasks) or 'A' (all tasks)"
    )
    args = parser.parse_args()

    main_action = args.action.lower()
    tasks_selection_mode = args.mode.upper()

    print(f"Action: {main_action}, Tasks selection mode: {tasks_selection_mode}")

    # Call main function
    main.run_tasks(action=main_action, mode=tasks_selection_mode)

if __name__ == "__main__":
    main_launcher()
