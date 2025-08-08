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

def get_task_details(qem_url, server, task, login_token):
    logger.info("Getting task details/status for task %s on server %s ...", task, server)
    get_task_details_url = qem_url + "servers/" + server + "/tasks/" + task
    get_task_details_response = requests.get(url=get_task_details_url, headers={'EnterpriseManager.APISessionID': login_token}, verify=False)
    if get_task_details_response.status_code == 200:
        # logger.info(f"Server: {server} Task: '{task}' State: '{json.loads(get_task_details_response.content)["state"]}' Task-Memory-usage: '{json.loads(get_task_details_response.content)["memory_mb"]}'") # Status:  memory usage for task %s is %s", task, json.loads(get_task_details_response.content)["cdc_latency"].get("total_latency"))
        return json.loads(get_task_details_response.content)  # ["cdc_latency"].get("total_latency")
    else:
        logger.info("response %s", json.loads(get_task_details_response.content)['error_code'])
        logger.error("Get task details API failed for the task %s and response code/content is %s", task, get_task_details_response.content)
        return "Task details API failed or No task"


if __name__ == "__main__":
    # Your code to execute when the script is run directly
    # For example:
    qem_host = "https://qmi-di-b45b.qmicloud.com/attunityenterprisemanager/api/v1/"
    replicate_server = "test_replicate"
    sample_task = "MySQL2Null"
    login_token = login.login_api(qem_host, "qmi@QMICLOUD", "cG!!FWW4l00586dP")
    if login_token:
        print("Successfully Login")
        get_task_details = get_task_details(qem_host, replicate_server, sample_task, login_token)
        print(get_task_details)