# QEM Task Handler

## Overview

QEM Task Handler is a Python automation tool to stop or resume tasks on QEM servers.  
It uses YAML for configuration, supports selective or all-task modes, and can run tasks in parallel.

## Features

- Load configuration from YAML
- QEM API login authentication
- Backup task states to CSV before changes
- Selective (`S`) or all (`A`) or (`F`) for passing file - task modes
- Parallel execution with thread pooling
- Detailed logging to file
- Generates result CSV after execution

---

## Pseudocode (High-Level Logic)

1. Load configuration from YAML and extract settings (host, credentials, mode, action, threads, etc.)  
2. Override mode from CLI arguments if provided  
3. Authenticate to QEM server (login API)  
4. Retrieve list of replicate servers from config  
5. For each server:  
   a. Get current task list from QEM API  
   b. Backup task list to CSV file  
   c. If mode = `S` (selected):  
      - Load task names from YAML for this server  
      - Match against API task list  
   d. If mode = `A` (all):  
      - If action = `stop`, select only tasks in `RUNNING` state  
        - If action = `resume`, select all tasks
   e. If mode = `F` pass file path:  
      - Works only if you pass the file and provide --server `replicate_server_name`
      - If action = `stop`, throws an error 
      - If action = `resume`, select all running tasks from the file
6. Aggregate all tasks to be processed  
7. Process tasks in parallel threads:  
   - If action = `resume`, call resume API for each task  
   - If action = `stop`, call stop API for each task  
8. Save results to a CSV report in the configured output path  
9. Log completion and summary of operations  


_For detailed pseudocode, refer to `docs/flow_pseudocode.md`._

---

## Usage
```bash
python run.py --action resume --mode S

# Resume tasks from a file containing task info
python run.py --action resume --mode F --file ./my_tasks.csv

# Parameters
--action: resume or stop

--mode: S (selected tasks from YAML) or A (all tasks)
# File content must be like backup/below CSV format
name,state,stop_reason,message,assigned_tags
Task1,ERROR,FATAL_ERROR,The task stopped abnormally,[]
Task2,STOPPED,NORMAL,,[]
MyTask3,RUNNING,,,

````
## Project Structure
````
qem-task-handler/
├── qemTasksHandler/
│   ├── main.py
│   ├── configParser.py
│   ├── utils.py
│   ├── backup.py
│   ├── myLogger.py
│   └── ...
├── restAPI/
│   ├── login.py
│   ├── getTaskList.py
│   ├── resumeTask.py
│   ├── stopTask.py
│   └── ...
├── config/
│   └── config.yaml
├── run.py
├── check_dependencies.py
├── requirements.txt
└── README.md
````
## Prerequisite Modules

Before running the QEM Task Handler, ensure the following Python modules are installed:

**External packages (install via `pip`):**
- `requests` – HTTP requests for QEM API communication  
- `PyYAML` (provides the `yaml` module) – YAML configuration parsing  

**Standard library modules (included with Python, no install needed):**
- `concurrent` – ThreadPoolExecutor for parallel execution  
- `argparse` – Command-line argument parsing  
- `smtplib` – Email sending support  
- `email` – Email message formatting and headers  
- `logging` – Application logging  
- `csv` – CSV file read/write support  

**Local project modules:**
- `restAPI` – Internal module containing QEM API functions

To install required external packages:
```bash
pip install requests PyYAML


````
## Enhancements: Below are MUST - 1, 4

1. Handle LogStream tasks first for RESUME and STOP at last - Mandatory
2. Email alert at last with attached status
3. Delete old logs/backups if needed - optional
4. Check for any FULL RELOADS before stopping - Any time if FULL LOAD is running - hold - Mandatory
5. Final validation if all tasks are stopped/resumed. * very useful
6. Do we need to check latency before STOPPING. - Discover team to confirm.