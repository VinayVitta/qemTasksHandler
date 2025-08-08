# 📋 Detailed Pseudocode – QEM Task Handler

## Step-by-step Logic

```python
# Step 1: Read configuration from YAML
config = read_yaml("config.yaml")

# Step 2: Extract details from config
qem_host        = config["qem_host"]
login_user      = config["user"]
login_token     = config["token"]   # or credentials

task_mode       = config["mode"]      # "all" or "selected"
task_list       = config["tasks"]     # List of task names if "selected"

# Resume/Stop config parameters
resume_timeout          = config["resume_timeout"]
resume_check_interval   = config["resume_retry_interval"]
resume_polling_retries  = config["resume_max_polling_retries"]
resume_api_retries      = config["resume_max_api_retries"]

stop_timeout            = config["stop_timeout"]
stop_check_interval     = config["stop_check_interval"]
stop_polling_retries    = config["stop_max_polling_retries"]
stop_api_retries        = config["stop_max_api_retries"]

threads = config["threads"]

# Step 3: Authenticate to QEM
session = login_to_qem(host=qem_host, user=login_user, token=login_token)

if not session.is_valid():
    print("Login failed")
    exit()

# Step 4: Verify if host/server exists
if not check_server_exists(session, qem_host):
    print("Server not found")
    exit()

# Step 5: Get list of currently running tasks
running_tasks = get_running_tasks(session)

# Step 6: Determine tasks to act on
if task_mode == "all":
    tasks_to_process = running_tasks
else:
    tasks_to_process = intersect(task_list, running_tasks)

# Step 7: Save backup of running tasks to CSV
write_to_csv("backup_tasks.csv", tasks_to_process)

# Step 8: Stop tasks in parallel using thread pool
stop_results = parallel_run(
    function=stop_task,
    args=tasks_to_process,
    kwargs={
        "qem_url": qem_host,
        "login_token": login_token,
        "check_interval": stop_check_interval,
        "timeout_minutes": stop_timeout,
        "max_polling_retries": stop_polling_retries,
        "max_stop_api_retries": stop_api_retries
    },
    max_threads=threads
)

# Step 9: Log and verify stopped tasks
log_results("stop_log.csv", stop_results)

# Step 10: Resume tasks in parallel using same logic
resume_results = parallel_run(
    function=resume_task,
    args=tasks_to_process,
    kwargs={
        "qem_url": qem_host,
        "login_token": login_token,
        "check_interval": resume_check_interval,
        "timeout_minutes": resume_timeout,
        "max_polling_retries": resume_polling_retries,
        "max_resume_api_retries": resume_api_retries
    },
    max_threads=threads
)

# Step 11: Log resumed tasks
log_results("resume_log.csv", resume_results)

# Done
print("Task stop/resume operations complete")
