# QEM Task Handler

## Overview

QEM Task Handler is a Python-based automation tool that stops and resumes tasks on a QEM server using YAML-based configuration.

## Features

- Reads task and system configuration from YAML
- Authenticates to QEM server via token
- Stops/resumes tasks based on selection
- Parallel task execution with retries and timeouts
- Backup task state to CSV
- Logging and email notifications

---

## Pseudocode (High-Level Logic)

1. Load configuration from YAML  
2. Authenticate with QEM  
3. Check if the server exists  
4. Get running tasks  
5. Filter tasks based on mode (all/selected)  
6. Backup running tasks to CSV  
7. Stop tasks in parallel (with retry + timeout)  
8. Resume tasks in parallel  
9. Log all results  

_For detailed pseudocode, refer to `docs/flow_pseudocode.md`._

---

## Project Structure
````
qem-task-handler/
├── qem_task_handler/
│ ├── init.py
│ ├── main.py # 🔹 Main flow orchestrator
│ ├── config.py # 🔹 YAML config parser/validator
│ ├── api_client.py # 🔹 All QEM API calls (login, stop, resume, etc.)
│ ├── task_manager.py # 🔹 Logic: prepare, select, stop/resume tasks
│ ├── thread_pool.py # 🔹 Threading and retry handling
│ ├── logger.py # 🔹 Logging setup
│ ├── notifier.py # 🔹 Email notifications
│ ├── backup.py # 🔹 Save running task state to CSV
│ └── utils.py # 🔹 Generic helpers
│
├── config/
│ └── config.yaml
│
├── logs/
│ └── qem_task_handler.log
│
├── backups/
│ └── tasks_backup.csv
│
├── tests/
│ ├── init.py
│ └── test_task_manager.py
│
├── docs/
│ └── flow_pseudocode.md
│
├── run.py # 🔹 Entry point (calls main.py)
├── requirements.txt
├── README.md
└── .gitignore
````
