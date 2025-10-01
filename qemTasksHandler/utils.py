# Title: helper functions
# Description: Filters for selected tasks
# Author: Vinay Vitta | Qlik PS
# Created: Aug 2025

from qemTasksHandler.myLogger import get_logger
import datetime, os, yaml, csv
from qemTasksHandler import configParser
from restAPI import getTaskDetails

config = configParser.load_config()
logger = get_logger(config)
logger.info("Initiating utils ...")


def get_replicate_servers(config):
    """
    Returns the list of replicate servers from the config.
    """
    try:
        replicate_servers = config.get('replicate_servers', [])
        if not replicate_servers:
            logger.warning("No replicate servers found in config.")
        else:
            logger.info("Found %d replicate servers.", len(replicate_servers))
        return replicate_servers
    except AttributeError as e:
        logger.error("Invalid config format: %s", e)
        return []
    except Exception as e:
        logger.exception("Unexpected error fetching replicate servers: %s", e)
        return []


def get_tasks_for_server(config, replicate_server_name):
    """
    Returns the list of tasks for a specific replicate server.
    """
    try:
        for server in config.get('replicate_servers', []):
            if server.get('name') == replicate_server_name:
                tasks = server.get('tasks', [])
                if not tasks:
                    logger.warning("No tasks found for server '%s'.", replicate_server_name)
                else:
                    logger.info("Found %d tasks for server '%s'.", len(tasks), replicate_server_name)
                return tasks
        logger.warning("Replicate server '%s' not found in config.", replicate_server_name)
        return []
    except AttributeError as e:
        logger.error("Invalid config format: %s", e)
        return []
    except Exception as e:
        logger.exception("Unexpected error fetching tasks for server '%s': %s", replicate_server_name, e)
        return []


def validate_tasks_yaml(api_task_response, yaml_task_names):
    """
    Validate tasks from QEM API against tasks from YAML config.

    Args:
        api_task_response (dict): Response from get_task_list(), expected to contain 'taskList'.
        yaml_task_names (list): List of task names from YAML config.

    Returns:
        list: List of matching task names (case-insensitive).
    """
    try:
        if not api_task_response or 'taskList' not in api_task_response:
            logger.warning("API response is empty or invalid.")
            return []

        # Extract API task names
        api_task_names = [task.get('name', '') for task in api_task_response['taskList']]

        # Convert all names to lowercase for case-insensitive comparison
        api_lower = {name.lower(): name for name in api_task_names}
        yaml_lower = {name.lower(): name for name in yaml_task_names}

        # Find matching tasks
        matching_tasks = [api_lower[name] for name in yaml_lower if name in api_lower]

        # Log tasks in YAML not found in API
        for name in yaml_task_names:
            if name.lower() not in api_lower:
                logger.warning("Task '%s' from YAML not found in API response.", name)

        # Log tasks in API not present in YAML
        for name in api_task_names:
            if name.lower() not in yaml_lower:
                logger.info("Task '%s' from API not present in YAML config.", name)

        return matching_tasks

    except Exception as e:
        logger.exception("Error validating tasks: %s", e)
        return []


def save_qem_task_report(output_dir, data, action):
    """
    Save QEM task report to CSV with descriptive name.

    :param output_dir: Directory to save the report
    :param data: List of dictionaries or list of lists to write
    :param action: 'resume' or 'stop'
    :param server_name: Optional server name to include in filename
    :return: Full path to the saved CSV file
    """
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Build descriptive filename
    timestamp = datetime.datetime.now().strftime("%Y_%m_%dT%H_%M_%S")
    filename = f"Execution_Result_{action.capitalize()}_{timestamp}.csv"
    filepath = os.path.join(output_dir, filename)

    # Write CSV
    if not data:
        raise ValueError("Data for report is empty")

    with open(filepath, mode='w', newline='', encoding='utf-8') as csvfile:
        if isinstance(data[0], dict):
            # Write list of dicts
            writer = csv.DictWriter(csvfile, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)
        else:
            # Write list of lists
            writer = csv.writer(csvfile)
            writer.writerows(data)

    return filepath


