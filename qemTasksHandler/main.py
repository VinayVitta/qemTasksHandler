# main.py
import sys, argparse

from qemTasksHandler import configParser, utils, backup
from qemTasksHandler.myLogger import get_logger
from restAPI import login, getTaskList, resumeTask, stopTask
import concurrent.futures
import datetime
import csv


def run_tasks(action,  mode=None):
    """
    Run or stop tasks based on action and selection mode.

    :param action: 'resume' or 'stop'
    :param mode: 'S' (selected tasks from YAML) or 'A' (all tasks)
    """
    config = configParser.load_config()
    logger = get_logger(config)
    logger.info("Initiating main tasks with action: %s", action)

    qem_hostname = config['qem_host'].get('qem_hostname')
    qem_user = config['qem_host'].get('qem_user')
    qem_psw = config['qem_host'].get('qem_psw')
    parallel_threads = config.get('parallel_threads', 5)

    login_token = login.login_api(qem_hostname, qem_user, qem_psw)
    if not login_token:
        logger.error("Login failed for host '%s'", qem_hostname)
        return

    # Check for Selective/All tasks RUN from YAML
    yaml_selection_mode = config['settings'].get('mode').upper()

    # Parse CLI arguments
    parser = argparse.ArgumentParser(description="Run or Stop QEM tasks")
    parser.add_argument("--mode", type=str, help="Tasks selection mode: 'S' or 'A'")
    args = parser.parse_args()

    # Decide final mode (CLI overrides YAML)
    tasks_selection_mode = (args.mode or yaml_selection_mode).upper()

    logger.info("Tasks selection mode is: %s", tasks_selection_mode)
    if tasks_selection_mode not in ('S', 'A'):
        logger.error(f"Invalid tasks_selection_mode: {tasks_selection_mode}. Must be 'S' or 'A'.")
        sys.exit(1)  # or `continue` if inside a loop
    action = config['settings'].get('action', '').lower()  # 'resume' or 'stop'

    tasks_to_run = []
    replicate_servers_list = utils.get_replicate_servers(config)

    for replicate_server in replicate_servers_list:
        server_name = replicate_server.get('name')

        # Backup current QEM task status for this server
        replicate_tasks_status_bk = getTaskList.get_task_list(qem_hostname, server_name, login_token)
        backup_file_name = backup.get_backup_filename(config)
        backup.write_task_list_to_csv(replicate_tasks_status_bk, backup_file_name)

        if tasks_selection_mode == 'S':
            # Get tasks from YAML and match against QEM list
            logger.info("Use selective tasks run mode...")
            yaml_task_names = utils.get_tasks_for_server(config, server_name)
            api_task_list_response = getTaskList.get_task_list(qem_hostname, server_name, login_token)
            matching_tasks = utils.validate_tasks_yaml(api_task_list_response, yaml_task_names)

            for task_name in matching_tasks:
                tasks_to_run.append({
                    'server_name': server_name,
                    'task_name': task_name
                })

        elif tasks_selection_mode == 'A':
            # Use all QEM tasks for this server
            logger.info("Use ALL tasks mode...")
            api_task_list_response = getTaskList.get_task_list(qem_hostname, server_name, login_token)
            if not api_task_list_response:
                logger.warning(f"No task list received for server {server_name}, skipping...")
                continue  # or handle differently

            if action == 'stop':
                # Filter only tasks that are running
                running_tasks = [
                    task['name']
                    for task in api_task_list_response.get('taskList', [])
                    if task['state'].upper() == 'RUNNING'
                ]
                for task_name in running_tasks:
                    tasks_to_run.append({
                        'server_name': server_name,
                        'task_name': task_name
                    })
            else:
                # Add all tasks
                for task in api_task_list_response.get('taskList', []):
                    tasks_to_run.append({
                        'server_name': server_name,
                        'task_name': task['name']
                    })
    logger.info("Total tasks to %s: %d on server: %s", action, len(tasks_to_run), server_name)

    # Worker function
    def task_worker(task):
        server = task['server_name']
        task_name = task['task_name']
        try:
            if action == 'resume':
                logger.info("Resuming task '%s' on server '%s'", task_name, server)
                result = resumeTask.resume_task(qem_hostname, server, task_name, login_token)
            else:
                logger.info("Stopping task '%s' on server '%s'", task_name, server)
                result = stopTask.stop_task(qem_hostname, server, task_name, login_token)

            return {'server_name': server, 'task_name': task_name, 'action': action, 'result': result}

        except Exception as e:
            logger.exception("Error executing task '%s' on server '%s': %s", task_name, server, e)
            return {'server_name': server, 'task_name': task_name, 'action': action, 'result': f"ERROR: {e}"}

    # Run in threads
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=parallel_threads) as executor:
        futures = [executor.submit(task_worker, task) for task in tasks_to_run]
        for future in concurrent.futures.as_completed(futures):
            results.append(future.result())

    logger.info("All tasks processed.")


    # Generate CSV report

    output_dir = config['logging']['result_path']
    utils.save_qem_task_report(output_dir, results, action)


    logger.info("CSV report generated. Path: %s", output_dir)
    logger.info("*****************************************************************")
