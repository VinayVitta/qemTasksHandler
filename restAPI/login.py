# Title: QEM API Calls
# Description: Contains all API calls used in the code - login, stop, resume, get task details, get task list
# Author: Vinay Vitta | Qlik PS
# Created: Aug 2025

import base64
import warnings
import requests
from qemTasksHandler.myLogger import get_logger
from qemTasksHandler import  configParser


config = configParser.load_config()
logger = get_logger(config)


# Suppress only the single InsecureRequestWarning from urllib3 needed when verify=False in requests
warnings.filterwarnings("ignore", category=requests.packages.urllib3.exceptions.InsecureRequestWarning)


def encode_credentials(username: str, credentials: str) -> str:
    """
    Encode username and credentials in base64 for Basic Auth header.
    """
    logger.info("Generating login credentials for user: %s", username)
    combined_string = f"{username}:{credentials}"
    encoded_credentials = base64.b64encode(combined_string.encode('utf-8')).decode('utf-8')
    return encoded_credentials


def login_api(url: str, username: str, credentials: str) -> str | None:
    """
    Perform login to QEM REST API, return session ID if successful, else None.
    """
    logger.info("Initiating QEM REST API login...")
    encoded_credentials = encode_credentials(username, credentials)

    headers = {
        "Authorization": f"Basic {encoded_credentials}",
        "Content-Type": "application/json"
    }

    login_url = 'https://' + url.rstrip('/') + '/attunityenterprisemanager/api/v1/login'  # Ensure no double slash

    logger.info("Logging in to QEM server at %s with user %s", login_url, username)
    try:
        response = requests.get(login_url, headers=headers, verify=False)
        response.raise_for_status()

        session_id = response.headers.get('EnterpriseManager.APISessionID')
        if session_id:
            logger.info("Login successful. Session ID received.")
            return session_id
        else:
            logger.error("Login failed: Session ID header missing in response.")
            return None

    except requests.RequestException as e:
        logger.error("Login request failed: %s", e)
        return None


if __name__ == "__main__":
    # Your code to execute when the script is run directly
    # For example:
    qem_host = "qmi-di-b45b.qmicloud.com"
    replicate_server = "test_replicate"
    sample_task = "MySQL2Null"
    login_token = login_api(qem_host, "qmi@QMICLOUD", "cG!!FWW4l00586dP")
    if login_token:
        print("Login Success!")
    else:
        print("Login Failed!")