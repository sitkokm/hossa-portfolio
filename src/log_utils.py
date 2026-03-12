import os
import datetime
import pandas as pd

import shutil

import config

log_file = config.LOG_FILE
backup_path = config.BACKUP_PATH

wp_folder = config.WP_FOLDER
plots_folder = config.PLOTS_FOLDER

output_path = os.path.join(wp_folder, plots_folder)

def log(msg):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {msg}"
    with open(log_file, "a") as f:
        f.write(line + "\n")
    print(line)
    
def weekly_backup():
    os.makedirs(backup_path, exist_ok=True)
    for file in os.listdir(output_path):
        if file.endswith(".html"):
            src = os.path.join(output_path, file)
            dst = os.path.join(backup_path, file)
            shutil.copy2(src, dst)

    log(f"Weekly backup created: {backup_path}")