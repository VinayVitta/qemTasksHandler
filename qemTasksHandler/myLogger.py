# Title: logging setup
# Description:  logging setup
# Author: Vinay Vitta | Qlik PS
# Created: Aug 2025

import os
import yaml
import logging
import datetime
from qemTasksHandler import configParser


def get_log_filename(config):
    """
    Constructs the logfile name based on the config and current timestamp.
    """
    try:
        log_dir = config['logging']['log_path']
        # log_dir = os.path.join(log_dir, "replicate")  # Join properly to form path
        log_mode = config['logging']['log_mode']

        # Ensure directory exists
        os.makedirs(log_dir, exist_ok=True)

        date_str = datetime.datetime.now().strftime("%Y_%m_%d")
        logfile_name = f"QEM_TaskHandler_{date_str}.log"
        logfile_path = os.path.join(log_dir, logfile_name)

        return logfile_path, log_mode
    except KeyError as ke:
        print(f"Missing expected logging config key: {ke}")
    except Exception as e:
        print(f"Error creating log filename: {e}")

    # Default fallback
    return "default.log", "INFO"


def setup_logging(logfile_path, log_mode):
    """
    Sets up a logger instance writing to the specified file.
    """
    logger = logging.getLogger(__name__)

    # Convert string log_mode to logging level (default INFO)
    level = getattr(logging, log_mode.upper(), logging.INFO)
    logger.setLevel(level)

    file_handler = logging.FileHandler(logfile_path)
    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s [%(filename)s:%(lineno)d]'
    )
    file_handler.setFormatter(formatter)

    # Avoid adding multiple handlers if called repeatedly
    if not logger.handlers:
        logger.addHandler(file_handler)

    return logger


# Entry point to configure logger
def get_logger():
    config = configParser.load_config()
    if not config:
        raise RuntimeError("Logging config could not be loaded.")

    logfile_path, log_mode = get_log_filename(config)
    logger = setup_logging(logfile_path, log_mode)
    logger.info("----------------------------------------------------------------")
    logger.info(f"Logging initialized with level: {log_mode} and logs path: {logfile_path}")
    return logger


# Example usage when run directly
if __name__ == "__main__":
    try:
        logger = get_logger()
    except Exception as e:
        print(f"Logging setup failed: {e}")
