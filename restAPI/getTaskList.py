# Title: QEM API Calls
# Description: GetTask Details API call
# Author: Vinay Vitta | Qlik PS
# Created: Aug 2025

import base64
import json
import time
import warnings
import requests
from qemTasksHandler import configParser
from qemTasksHandler.myLogger import get_logger
from restAPI import login

logger = get_logger()
logger.info("Initiating QEM REST API calls...")

# Suppress only the single InsecureRequestWarning from urllib3 needed when verify=False in requests
warnings.filterwarnings("ignore", category=requests.packages.urllib3.exceptions.InsecureRequestWarning)

def get_task_list(qem_url, server, login_token):
    logger.info("Getting task list with status for server %s ...", server)
    get_task_list_url = f"{qem_url}servers/{server}/tasks/"
    get_task_list_response = requests.get(
        url=get_task_list_url,
        headers={'EnterpriseManager.APISessionID': login_token},
        verify=False
    )
    if get_task_list_response.status_code == 200:
        return json.loads(get_task_list_response.content)
    else:
        logger.info("response %s", json.loads(get_task_list_response.content)['error_code'])
        logger.error(
            "Get task list API failed for the server %s and response code/content is %s",
            server, get_task_list_response.content
        )
        return None


if __name__ == "__main__":
    # Your code to execute when the script is run directly
    # For example:
    qem_host = "https://qmi-di-b45b.qmicloud.com/attunityenterprisemanager/api/v1/"
    replicate_server = "test_replicate"
    sample_task = "MySQL2Null"
    login_token = login.login_api(qem_host, "qmi@QMICLOUD", "cG!!FWW4l00586dP")
    if login_token:
        print("Successfully Login")
        get_task_list = get_task_list(qem_host, replicate_server, login_token)
        task_list = get_task_list['taskList']
        print(task_list)