"""
Dependency checker for QEM Task Handler project.

Checks for presence of required external and local modules.

Usage:
    python check_dependencies.py
"""

import sys

# List external packages to check (those to install via pip)
external_packages = [
    "requests",
    "yaml",  # PyYAML installs this module
]

# List local modules to check (relative imports in your project)
# local_modules = [
#     "qemTasksHandler.myLogger",
#     "qemTasksHandlerqem_task_handler",
# ]

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

    # print("\nChecking local project modules...")
    # for mod in local_modules:
    #    check_import(mod)

    if missing:
        print("\nSome modules are missing!")
        print("Please install missing packages via pip, e.g.:")
        print(f"  pip install {' '.join(missing)}")
        sys.exit(1)
    else:
        print("\nAll dependencies are satisfied.")

if __name__ == "__main__":
    main()
