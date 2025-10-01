# Title: Email
# Author: Vinay Vitta | Qlik - QDI PS
# Date: August 2025
# Description: Main code

import sys
import csv
import concurrent.futures
from qemTasksHandler import configParser, utils, backup
from qemTasksHandler.myLogger import get_logger
from restAPI import login, getTaskList, resumeTask, stopTask, getTaskDetails


def run_tasks(action, mode=None, file_path=None, override_server=None):
    """
    Executes QEM tasks based on provided action and mode.

    Parameters:
        action (str): 'resume' or 'stop'
        mode (str): 'S' (selected from YAML), 'A' (all), 'F' (file-based list, resume only)
        file_path (str): CSV file path if mode='F'
        override_server (str): Server name override for mode='F'
    """
    # --- Load Config & Logger ---
    config = configParser.load_config()
    logger = get_logger(config)
    logger.info("_________________________________________________________")
    logger.info("=== Starting QEM Task Handler ===")
    logger.info("Action: %s | Mode: %s", action, mode)

    # --- Extract QEM Credentials ---
    qem_hostname = config['qem_host'].get('qem_hostname')
    qem_user = config['qem_host'].get('qem_user')
    qem_psw = config['qem_host'].get('qem_psw')
    parallel_threads = config.get('parallel_threads', 5)

    # --- Validate Mode F requirements ---
    yaml_selection_mode = config['settings'].get('mode', 'S').upper()
    tasks_selection_mode = (mode or yaml_selection_mode).upper()

    if tasks_selection_mode == 'F':
        if action != 'resume':
            logger.error("Mode 'F' is only supported with action='resume'.")
            sys.exit(1)
        if not file_path or not override_server:
            logger.error("Both file_path and override_server must be provided in mode='F'.")
            sys.exit(1)

    # --- Authenticate ---
    logger.info("[1/5] Authenticating with QEM server: %s", qem_hostname)
    login_token = login.login_api(qem_hostname, qem_user, qem_psw)
    if not login_token:
        logger.error("Login failed for host '%s'. Aborting.", qem_hostname)
        sys.exit(1)
    logger.info("Authentication successful.")

    # --- Get Server List ---
    logger.info("[2/5] Retrieving replicate server list from config.")
    replicate_servers_list = utils.get_replicate_servers(config)
    tasks_to_run = []

    # --- Task Selection Loop ---
    logger.info("[3/5] Building task list based on mode: %s", tasks_selection_mode)
    for replicate_server in replicate_servers_list:
        server_name = replicate_server.get('name')

        # Skip non-target servers in File mode
        if tasks_selection_mode == 'F' and server_name != override_server:
            continue

        # Backup task list before processing
        replicate_tasks_status_bk = getTaskList.get_task_list(qem_hostname, server_name, login_token)
        backup_file_name = backup.get_backup_filename(config)
        backup.write_task_list_to_csv(replicate_tasks_status_bk, backup_file_name)
        logger.info("Backup created for server: %s -> %s", server_name, backup_file_name)

        # --- Mode S: Selected from YAML ---
        if tasks_selection_mode == 'S':
            logger.info("Using SELECTED mode for server: %s", server_name)
            yaml_task_names = utils.get_tasks_for_server(config, server_name)
            api_task_list_response = getTaskList.get_task_list(qem_hostname, server_name, login_token)
            matching_tasks = utils.validate_tasks_yaml(api_task_list_response, yaml_task_names)
            for task_name in matching_tasks:
                tasks_to_run.append({'server_name': server_name, 'task_name': task_name})

        # --- Mode A: All tasks ---
        elif tasks_selection_mode == 'A':
            logger.info("Using ALL mode for server: %s", server_name)
            api_task_list_response = getTaskList.get_task_list(qem_hostname, server_name, login_token)
            if not api_task_list_response:
                logger.warning("No task list for server %s. Skipping.", server_name)
                continue
            if action == 'stop':
                running_tasks = [
                    task['name'] for task in api_task_list_response.get('taskList', [])
                    if task['state'].upper() == 'RUNNING'
                ]
                for task_name in running_tasks:
                    tasks_to_run.append({'server_name': server_name, 'task_name': task_name})
            else:
                for task in api_task_list_response.get('taskList', []):
                    tasks_to_run.append({'server_name': server_name, 'task_name': task['name']})

        # --- Mode F: File-based selection ---
        elif tasks_selection_mode == 'F':
            logger.info("Using FILE mode for server: %s (override)", override_server)
            try:
                with open(file_path, newline='', encoding='utf-8') as csvfile:
                    reader = csv.DictReader(csvfile)
                    for row in reader:
                        if row.get('state', '').upper() == 'RUNNING':
                            tasks_to_run.append({
                                'server_name': override_server,
                                'task_name': row['name']
                            })
            except FileNotFoundError:
                logger.error("File not found: %s", file_path)
                sys.exit(1)
            except Exception as e:
                logger.exception("Error reading file %s: %s", file_path, e)
                sys.exit(1)

    logger.info("Total tasks queued for %s: %d", action, len(tasks_to_run))

    # --- Pre-check: Stop if any task is still in full load (full_load_completed=False) ---
    logger.info("Performing full load completion check...")
    for task in tasks_to_run:
        server = task['server_name']
        task_name = task['task_name']
        try:
            details = getTaskDetails.get_task_details(qem_hostname, server, task_name, login_token)
            full_load_completed = details.get("full_load_completed", None)

            if not full_load_completed:  # False = active full load
                logger.error(
                    "Task '%s' on server '%s' is still in active full load (full_load_completed=False). Aborting script.",
                    task_name, server
                )
                sys.exit(1)

        except Exception as e:
            logger.exception(
                "Error retrieving details for task '%s' on server '%s': %s",
                task_name, server, e
            )
            sys.exit(1)

    # --- Task Execution ---
    logger.info("[4/5] Executing tasks in parallel (max threads: %d)", parallel_threads)

    def task_worker(task):
        server = task['server_name']
        task_name = task['task_name']
        try:
            if action == 'resume':
                logger.info("Resuming task: '%s' on server: '%s'", task_name, server)
                result = resumeTask.resume_task(qem_hostname, server, task_name, login_token)
            else:
                logger.info("Stopping task: '%s' on server: '%s'", task_name, server)
                result = stopTask.stop_task(qem_hostname, server, task_name, login_token)
            return {'server_name': server, 'task_name': task_name, 'action': action, 'result': result}
        except Exception as e:
            logger.exception("Error executing task '%s' on server '%s': %s", task_name, server, e)
            return {'server_name': server, 'task_name': task_name, 'action': action, 'result': f"ERROR: {e}"}

    results = []

    # Using a dynamic submission loop
    with concurrent.futures.ThreadPoolExecutor(max_workers=parallel_threads) as executor:
        # Convert tasks list to an iterator so we can submit one at a time
        task_iter = iter(tasks_to_run)
        # Submit initial batch equal to max workers
        futures = {executor.submit(task_worker, next(task_iter)): None for _ in range(min(parallel_threads, len(tasks_to_run)))}

        while futures:
            # Wait for any task to complete
            done, _ = concurrent.futures.wait(futures, return_when=concurrent.futures.FIRST_COMPLETED)
            for future in done:
                result = future.result()
                results.append(result)  # Process result immediately
                logger.info("Task completed: %s | Result: %s", result['task_name'], result['result'])
                # Remove completed future
                futures.pop(future)
                # Submit next task if available
                try:
                    next_task = next(task_iter)
                    futures[executor.submit(task_worker, next_task)] = None
                except StopIteration:
                    pass

    # --- Report Generation ---
    logger.info("[5/5] Generating CSV report.")
    output_dir = config['logging']['result_path']
    utils.save_qem_task_report(output_dir, results, action)
    logger.info("CSV report generated. Path: %s", output_dir)
    logger.info("=== QEM Task Handler Completed Successfully ===")

