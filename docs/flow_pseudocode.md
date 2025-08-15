# 📋 Detailed Pseudocode – QEM Task Handler

## Step-by-step Logic

```python
# Step 1: Load configuration from YAML
config = load_config("config.yaml")

# Step 2: Extract settings from config
qem_hostname    = config["qem_host"]["qem_hostname"]
qem_user        = config["qem_host"]["qem_user"]
qem_psw         = config["qem_host"]["qem_psw"]

parallel_threads = config.get("parallel_threads", 5)

yaml_mode        = config["settings"]["mode"].upper()   # 'S' or 'A' or 'F'
cli_mode         = mode_arg_from_CLI_or_None
tasks_mode       = (cli_mode or yaml_mode).upper()

action           = config["settings"]["action"].lower() # 'resume' or 'stop'

# Optional advanced settings (timeouts, retries, intervals)
resume_timeout          = config.get("resume_timeout", 0)
resume_check_interval   = config.get("resume_retry_interval", 0)
resume_polling_retries  = config.get("resume_max_polling_retries", 0)
resume_api_retries      = config.get("resume_max_api_retries", 0)

stop_timeout            = config.get("stop_timeout", 0)
stop_check_interval     = config.get("stop_check_interval", 0)
stop_polling_retries    = config.get("stop_max_polling_retries", 0)
stop_api_retries        = config.get("stop_max_api_retries", 0)

# Step 3: Authenticate to QEM API
login_token = login_api(qem_hostname, qem_user, qem_psw)
if not login_token:
    log_error("Login failed")
    exit()

# Step 4: Prepare the list of QEM servers from config
replicate_servers_list = get_replicate_servers(config)

tasks_to_run = []

# Step 5: For each replicate server
for server in replicate_servers_list:
    server_name = server["name"]

    # Step 5.1: Backup current task status
    task_status_list = get_task_list(qem_hostname, server_name, login_token)
    backup_filename = get_backup_filename(config)
    write_task_list_to_csv(task_status_list, backup_filename)

    # Step 5.2: Determine tasks to process
    if tasks_mode == "S":
        yaml_tasks = get_tasks_for_server(config, server_name)
        api_task_list = get_task_list(qem_hostname, server_name, login_token)
        matching_tasks = validate_tasks_yaml(api_task_list, yaml_tasks)
        for t in matching_tasks:
            tasks_to_run.append({"server_name": server_name, "task_name": t})

    elif tasks_mode == "A":
        api_task_list = get_task_list(qem_hostname, server_name, login_token)
        if not api_task_list:
            log_warning(f"No tasks for server {server_name}")
            continue

        if action == "stop":
            running_only = [
                t["name"] for t in api_task_list["taskList"]
                if t["state"].upper() == "RUNNING"
            ]
            for t in running_only:
                tasks_to_run.append({"server_name": server_name, "task_name": t})
        else:
            for t in api_task_list["taskList"]:
                tasks_to_run.append({"server_name": server_name, "task_name": t["name"]})

# Step 6: Process tasks in parallel threads
def task_worker(task):
    if action == "resume":
        return resume_task(qem_hostname, task["server_name"], task["task_name"], login_token)
    else:
        return stop_task(qem_hostname, task["server_name"], task["task_name"], login_token)

results = run_in_thread_pool(task_worker, tasks_to_run, max_workers=parallel_threads)

# Step 7: Save result CSV report
save_qem_task_report(config["logging"]["result_path"], results, action)

# Step 8: Log completion
log_info("All tasks processed and report saved")

