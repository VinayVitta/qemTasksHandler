# Title: Email
# Author: Vinay Vitta | Qlik - QDI PS
# Date: August 2025
# Description: Read YAML config - parse

import os, yaml
from qemTasksHandler.myLogger import get_logger


def get_config_path(filename="config.yaml"):
    """
    Returns absolute path to the config file located in 'config' folder
    inside the project root directory.
    Assumes this script is inside qem_task_handler or subfolder.
    """
    # Get directory of current script
    script_dir = os.path.dirname(os.path.realpath(__file__))

    # Project root = one level above qem_task_handler folder
    project_root = os.path.dirname(script_dir)

    # Construct config path
    config_path = os.path.join(project_root, "config", filename)

    # print(f"Resolved config path: {config_path}")
    return config_path


def load_config(filename="config.yaml"):
    """
    Loads and parses the YAML configuration file.
    Returns a dictionary or None on failure.
    """
    config_path = get_config_path(filename)
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Config file not found: {config_path}")
    with open(config_path, 'r') as file:
        return yaml.safe_load(file) or {}


config = load_config()
logger = get_logger(config)
logger.info("Initiating configParser...")
