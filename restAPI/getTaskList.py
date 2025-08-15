# Title: QEM API Calls
# Description: Get Task Details API call
# Author: Vinay Vitta | Qlik PS
# Created: Aug 2025

import json
import warnings
import requests
from qemTasksHandler import configParser
from qemTasksHandler.myLogger import get_logger
from restAPI import login

# Load config and initialize logger
config = configParser.load_config()
logger = get_logger(config)


# Suppress only InsecureRequestWarning when verify=False
warnings.filterwarnings("ignore", category=requests.packages.urllib3.exceptions.InsecureRequestWarning)


def get_task_list(qem_url, server, login_token):
    """
    Fetches the list of tasks for a given QEM server.
    Returns a dictionary if successful, None otherwise.
    """
    logger.info("Initiating QEM REST API getTaskList...")
    try:
        logger.info("Getting task list with status for server '%s' ...", server)
        get_task_list_url = f"https://{qem_url}/attunityenterprisemanager/api/v1/servers/{server}/tasks/"

        response = requests.get(
            url=get_task_list_url,
            headers={'EnterpriseManager.APISessionID': login_token},
            verify=False,
            timeout=30  # optional: set a timeout
        )

        if response.status_code == 200:
            return response.json()
        else:
            try:
                error_code = response.json().get('error_code')
                logger.info("API response error code: %s", error_code)
            except Exception:
                logger.warning("Unable to parse error code from response.")

            logger.error(
                "Get task list API failed for server '%s'. Status: %s, Response: %s",
                server, response.status_code, response.text
            )
            return None

    except requests.exceptions.RequestException as e:
        logger.exception("Request to QEM API failed for server '%s': %s", server, e)
        return None
    except Exception as e:
        logger.exception("Unexpected error while fetching task list for server '%s': %s", server, e)
        return None


if __name__ == "__main__":
    try:
        qem_host = "qmi-di-b45b.qmicloud.com"
        replicate_server = "test_replicate"
        login_token = login.login_api(qem_host, "qmi@QMICLOUD", "cG!!FWW4l00586dP")

        if not login_token:
            logger.error("Login failed for host '%s'", qem_host)
        else:
            logger.info("Successfully logged in to '%s'", qem_host)
            task_list_response = get_task_list(qem_host, replicate_server, login_token)

            if task_list_response and 'taskList' in task_list_response:
                tasks = task_list_response['taskList']
                logger.info("Fetched %d tasks for server '%s'", len(tasks), replicate_server)
                print(tasks)
            else:
                logger.warning("No tasks found or API returned invalid response for server '%s'", replicate_server)

    except Exception as e:
        logger.exception("Unexpected error in main execution: %s", e)
