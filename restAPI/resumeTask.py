# Title: QEM API Calls
# Description: Resume Task
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
logger.info("Initiating QEM REST API calls...")

# Suppress only the single InsecureRequestWarning from urllib3 needed when verify=False in requests
warnings.filterwarnings("ignore", category=requests.packages.urllib3.exceptions.InsecureRequestWarning)


def resume_task(qem_url, server, task, login_token):
    """
    Attempts to resume a task on the QEM server if it is not already running.
    Repeatedly sends resume requests while polling the task status until it
    confirms running or retries/timeouts are exhausted.

    Args:
        qem_url (str): Base URL for QEM API.
        server (str): Server hosting the task.
        task (str): Task name to resume.
        login_token (str): Authentication token.

    Returns:
        str: "ResumeSuccess" if task is running or successfully resumed,
             None otherwise.
    """

    logger.info(f"Checking task '{task}' status on server '{server}' before resume...")

    task_details = getTaskDetails.get_task_details(qem_url, server, task, login_token)
    if not task_details or "memory_mb" not in task_details:
        logger.error(f"Unable to retrieve details for task '{task}'. Aborting resume.")
        return None

    task_mem = task_details["memory_mb"]
    if task_mem >= 1:
        logger.info(f"Task '{task}' is already running. Skipping resume.")
        return "Already_in_Running_State"

    logger.info(f"Task '{task}' is not running (Memory: {task_mem} MB). Proceeding to resume.")

    resume_url = 'https://' + f"{qem_url.rstrip('/')}/attunityenterprisemanager/api/v1/servers/{server}/tasks/{task}?action=run&option=RESUME_PROCESSING"

    # Load config values
    try:
        config = configParser.load_config()
        check_interval = int(config['settings'].get('resume_retry_interval', 30))  # seconds between polls
        timeout_minutes = int(config['settings'].get('resume_timeout', 35))        # total timeout in minutes
        max_polling_retries = int(config['settings'].get('resume_max_polling_retries', 70))
        max_resume_api_retries = int(config['settings'].get('resume_max_api_retries', 3))
    except Exception as e:
        logger.warning(f"Invalid resume config values. Using defaults. Error: {e}")
        check_interval = 30
        timeout_minutes = 35
        max_polling_retries = 70
        max_resume_api_retries = 3

    timeout_seconds = timeout_minutes * 60
    elapsed_time = 0
    polling_retry_counter = 0
    api_resume_attempts = 0

    while elapsed_time < timeout_seconds and polling_retry_counter < max_polling_retries:
        task_details = getTaskDetails.get_task_details(qem_url, server, task, login_token)
        if task_details and "memory_mb" in task_details:
            mem_usage = task_details["memory_mb"]
            if mem_usage >= 1:
                logger.info(f"Task '{task}' resumed successfully (Memory: {mem_usage} MB)")
                return "ResumeSuccess"

            logger.info(f"Task '{task}' still not running (Memory: {mem_usage} MB)")

            # Send resume API request if we still have retries left
            if api_resume_attempts < max_resume_api_retries:
                logger.info(f"Sending resume request attempt {api_resume_attempts + 1}/{max_resume_api_retries} for task '{task}'")
                response = requests.post(
                    url=resume_url,
                    headers={"EnterpriseManager.APISessionID": login_token},
                    verify=False
                )
                if response.status_code == 200:
                    logger.info(f"Resume request succeeded on attempt {api_resume_attempts + 1} for task '{task}'")
                else:
                    logger.warning(f"Resume request failed on attempt {api_resume_attempts + 1} with status {response.status_code}: {response.content}")
                api_resume_attempts += 1
            else:
                logger.debug(f"Max resume API retries ({max_resume_api_retries}) reached, not sending further resume requests.")
        else:
            logger.warning(f"Unable to fetch task details for '{task}' while waiting for resume.")

        polling_retry_counter += 1
        logger.info(f"Polling retry {polling_retry_counter}/{max_polling_retries} — waiting {check_interval} seconds before next check")
        time.sleep(check_interval)
        elapsed_time += check_interval

    logger.error(f"Resume failed for task '{task}': timeout ({timeout_minutes} min) or max retries ({max_polling_retries}) reached.")
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
        run_task = resume_task(qem_host, replicate_server, sample_task, login_token)
        print(run_task)