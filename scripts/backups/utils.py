import os
import datetime

###############################
#### Logging utilities for backup operations
###############################
LOG_DIR = '/var/log/backups'


# Ensure the log directory exists
def check_log_dir():
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)


# Log a backup operation with a specific level and message
def log_backup(file, level, message):
    check_log_dir()
    log_file = os.path.join(LOG_DIR, file)
    content = f'{datetime.datetime.now()}: [{level}] - {message}'
    with open(log_file, 'a') as f:
        f.write(f'{content}\n')