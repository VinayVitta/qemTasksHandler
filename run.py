# Title: Email
# Author: Vinay Vitta | Qlik - QDI PS
# Date: August 2025
# Description: runner/starter
# run.py
"""
Launcher script to start or stop QEM tasks.

Examples:
    python run.py --action resume
    python run.py --action stop --mode S
    python run.py --action resume --mode F --file tasks.csv --server MyServer
"""

import argparse
from qemTasksHandler import main, configParser


def main_launcher():
    # Load configuration from YAML to get defaults
    config = configParser.load_config()
    yaml_mode = config['settings'].get('mode', 'A').upper()

    # --- CLI Arguments ---
    parser = argparse.ArgumentParser(description="Run or Stop QEM tasks")
    parser.add_argument(
        "--action", type=str, choices=["resume", "stop"], required=True,
        help="Action to perform: resume or stop"
    )
    parser.add_argument(
        "--mode", type=str, choices=["S", "A", "F"], default=yaml_mode,
        help="Tasks selection mode: S (selected), A (all), F (from CSV file - resume only)"
    )
    parser.add_argument(
        "--file", type=str,
        help="Path to CSV file (required if mode=F)"
    )
    parser.add_argument(
        "--server", type=str,
        help="Replicate server name (required if mode=F)"
    )
    args = parser.parse_args()

    # --- Mode F Validation ---
    if args.mode.upper() == "F":
        if args.action.lower() != "resume":
            parser.error("Mode 'F' is only allowed with --action resume.")
        if not args.file:
            parser.error("--file is required when --mode=F and --action=resume.")
        if not args.server:
            parser.error("--server is required when --mode=F and --action=resume.")
    else:
        # Prevent accidental file/server usage in wrong mode
        if args.file or args.server:
            parser.error("--file and --server can only be used when --mode=F and --action=resume.")

    # --- Summary Output ---
    main_action = args.action.lower()
    tasks_selection_mode = args.mode.upper()
    print("=" * 60)
    print(f" QEM Task Handler Starting")
    print(f" Action: {main_action}")
    print(f" Mode: {tasks_selection_mode}")
    if args.file:
        print(f" Task File: {args.file}")
    if args.server:
        print(f" Target Server Override: {args.server}")
    print("=" * 60)

    # --- Call Main Logic ---
    main.run_tasks(
        action=main_action,
        mode=tasks_selection_mode,
        file_path=args.file,
        override_server=args.server
    )


if __name__ == "__main__":
    main_launcher()
