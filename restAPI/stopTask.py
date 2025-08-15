# Title: QEM API Calls
# Description: Stop Task
# Author: Vinay Vitta | Qlik PS
# Created: Aug 2025


import time
import warnings
import requests
from qemTasksHandler import configParser
from qemTasksHandler.myLogger import get_logger
from restAPI import getTaskDetails, login

config = configParser.load_config()
logger = get_logger(config)


# Suppress only the single InsecureRequestWarning from urllib3 needed when verify=False in requests
warnings.filterwarnings("ignore", category=requests.packages.urllib3.exceptions.InsecureRequestWarning)


def stop_task(qem_url, server, task, login_token):
    """
    Attempts to stop a task on the QEM server if it is currently running.
    Repeatedly sends the stop API request (up to max_stop_api_retries) while polling
    the task status at intervals, until task is confirmed stopped or timeout.

    Args:
        qem_url (str): Base URL for QEM API.
        server (str): Server hosting the task.
        task (str): Task name.
        login_token (str): Authentication token.

    Returns:
        str: "StopSuccess" if stopped successfully, None otherwise.
    """
    logger.info("Initiating QEM REST API STOP task...")
    logger.info(f"Checking status of task '{task}' on server '{server}' before initiating STOP")

    task_details = getTaskDetails.get_task_details(qem_url, server, task, login_token)
    if not task_details or "memory_mb" not in task_details:
        logger.error(f"Failed to retrieve task details for '{task}'. Exiting.")
        return None

    task_mem_usage = task_details["memory_mb"]
    if task_mem_usage == 0:
        logger.info(f"Task '{task}' is already stopped. No action needed.")
        return "Already_in_STOPPED_State"
    else:
        logger.info(f"Task '{task}' is running (Memory usage: {task_mem_usage} MB). Proceeding to STOP.")

    # Load config for intervals and retries
    try:
        config = configParser.load_config()
        check_interval = int(config['settings'].get('stop_check_interval', 30))  # seconds between polls
        timeout_minutes = int(config['settings'].get('stop_timeout', 35))       # total timeout minutes
        max_polling_retries = int(config['settings'].get('stop_max_polling_retries', 70))  # max poll retries
        max_stop_api_retries = int(config['settings'].get('stop_max_api_retries', 3))     # max stop API retries
    except Exception as e:
        logger.warning(f"Invalid stop config values. Using defaults. Error: {e}")
        check_interval = 30
        timeout_minutes = 35
        max_polling_retries = 70
        max_stop_api_retries = 3

    timeout_seconds = timeout_minutes * 60
    stop_task_url = 'https://' + f"{qem_url.rstrip('/')}/attunityenterprisemanager/api/v1/servers/{server}/tasks/{task}?action=stop"

    elapsed_time = 0
    polling_retry_counter = 0
    api_stop_attempts = 0

    while elapsed_time < timeout_seconds and polling_retry_counter < max_polling_retries:
        task_details = getTaskDetails.get_task_details(qem_url, server, task, login_token)
        if task_details and "memory_mb" in task_details:
            task_mem_usage = task_details["memory_mb"]
            task_state = task_details.get("state", "UNKNOWN")

            if task_mem_usage == 0 and task_state != "RUNNING":
                logger.info(f"Task '{task}' has stopped successfully.")
                return "StopSuccess"

            logger.info(f"Task '{task}' still running. Memory: {task_mem_usage} MB, State: {task_state}")

            # If we still have stop API retries left, send stop request again
            if api_stop_attempts < max_stop_api_retries:
                logger.info(f"Sending stop request attempt {api_stop_attempts + 1}/{max_stop_api_retries} for task '{task}'")
                response = requests.post(
                    url=stop_task_url,
                    headers={'EnterpriseManager.APISessionID': login_token},
                    verify=False
                )
                if response.status_code == 200:
                    logger.info(f"Stop request succeeded on attempt {api_stop_attempts + 1} for task '{task}'")
                else:
                    logger.warning(f"Stop request failed on attempt {api_stop_attempts + 1} with status {response.status_code}: {response.content}")
                api_stop_attempts += 1
            else:
                logger.debug(f"Max stop API retries ({max_stop_api_retries}) reached, not sending further stop requests.")
        else:
            logger.warning(f"Could not retrieve task details while waiting for '{task}' to stop.")

        polling_retry_counter += 1
        logger.info(f"Polling retry {polling_retry_counter}/{max_polling_retries} — waiting {check_interval} seconds before next check")
        time.sleep(check_interval)
        elapsed_time += check_interval

    logger.error(f"Task '{task}' did not stop after {timeout_minutes} minutes or {max_polling_retries} polling retries.")
    return None


if __name__ == "__main__":
    # Your code to execute when the script is run directly
    # For example:
    qem_host = "qmi-di-b45b.qmicloud.com"
    replicate_server = "test_replicate"
    sample_task = "MySQL2Null"
    login_token = login.login_api(qem_host, "qmi@QMICLOUD", "cG!!FWW4l00586dP")
    if login_token:
        print("Successfully Login")
        stop_task_req = stop_task(qem_host, replicate_server, sample_task, login_token)
        print(stop_task_req)