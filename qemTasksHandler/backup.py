# Title: QEM API Calls
# Description: Save running task state to CSV
# Author: Vinay Vitta | Qlik PS
# Created: Aug 2025

from qemTasksHandler.myLogger import get_logger
import datetime, os
from qemTasksHandler import configParser
from restAPI import getTaskList, login
import csv

logger = get_logger()
logger.info("Initiating backup of task status...")


def get_backup_filename(config):
    """
    Constructs the logfile name based on the config and current timestamp.
    """
    try:
        backup_dir = config['backup']['backup_path']
        # backup_dir = os.path.join(backup_dir, "replicate")  # Join properly to form path

        # Ensure directory exists
        os.makedirs(backup_dir, exist_ok=True)

        date_str = datetime.datetime.now().strftime("%Y_%m_%dT%H_%M_%S")
        backup_file_name = f"QEM_TaskList_backup_{date_str}.csv"
        backup_file_path = os.path.join(backup_dir, backup_file_name)

        return backup_file_path
    except KeyError as ke:
        print(f"Missing expected logging config key: {ke}")
    except Exception as e:
        print(f"Error creating log filename: {e}")

    # Default fallback
    return "task_list.csv"


def write_task_list_to_csv(task_data, filename="task_list.csv"):
    """
    Writes the task list JSON to a CSV file.
    Expects JSON in the format:
    {"taskList": [ {task1}, {task2}, ... ]}
    """
    if not task_data or 'taskList' not in task_data:
        logger.error("No valid task list found in the data.")
        return

    task_list = task_data['taskList']

    if not task_list:
        logger.warning("Task list is empty.")
        return

    # Write to CSV
    with open(filename, "w", newline="", encoding="utf-8") as csvfile:
        fieldnames = task_list[0].keys()
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(task_list)

    logger.info("CSV file '%s' created successfully.", filename)


if __name__ == "__main__":
    qem_host = "https://qmi-di-b45b.qmicloud.com/attunityenterprisemanager/api/v1/"
    replicate_server = "test_replicate"
    sample_task = "MySQL2Null"
    login_token = login.login_api(qem_host, "qmi@QMICLOUD", "cG!!FWW4l00586dP")
    config = configParser.load_config()
    if not config:
        raise RuntimeError("Logging config could not be loaded.")

    backup_file_name = get_backup_filename(config)
    print(backup_file_name)
    task_data = getTaskList.get_task_list(qem_host, replicate_server, login_token)
    write_task_list_to_csv(task_data, backup_file_name)

