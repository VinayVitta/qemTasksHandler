
# Title: Email
# Author: Vinay Vitta | Qlik - QDI PS
# Date: August 2025
# Description: Dependency Checker

"""
Dependency checker for QEM Task Handler project.

Checks for:
  - Required external Python packages (installable via pip)
  - Required local modules in the project

Usage:
    python check_dependencies.py
"""

import sys

# External packages (install via pip)
external_packages = [
    "requests",     # HTTP requests
    "yaml",         # From PyYAML package
    "concurrent",   # ThreadPoolExecutor
    "argparse",     # CLI parsing
    "smtplib",      # For Emails
    "email",        # For Emails
    "logging",      # For logging
    "csv",          # For CSV
    "restAPI"       # Using REST API calls
]

# Local project modules (relative imports)
local_modules = [
    "qemTasksHandler.configParser",
    "qemTasksHandler.utils",
    "qemTasksHandler.backup",
    "qemTasksHandler.myLogger",
    "restAPI.login",
    "restAPI.getTaskList",
    "restAPI.resumeTask",
    "restAPI.stopTask",
]

missing = []


def check_import(module_name):
    try:
        __import__(module_name)
        print(f"✔ Module '{module_name}' is present.")
    except ImportError:
        print(f"✘ Module '{module_name}' is MISSING.")
        missing.append(module_name)


def main():
    print("Checking external packages...")
    for pkg in external_packages:
        check_import(pkg)

    print("\nChecking local project modules...")
    for mod in local_modules:
        check_import(mod)

    if missing:
        print("\n❌ Some modules are missing!")
        print("Install missing Python packages with:")
        print(f"  pip install {' '.join(missing)}")
        sys.exit(1)
    else:
        print("\n✅ All dependencies are satisfied.")


if __name__ == "__main__":
    main()
