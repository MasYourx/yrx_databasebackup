import os
import time
import subprocess
import datetime
import requests

# Database Configuration
DB_HOST = "localhost"  # Host database
DB_USER = "root"  # Change your database username
DB_PASSWORD = ""  # Change your database password
DB_NAME = "shrpdb"  # Change your database name
BACKUP_DIR = "C:/Users/Administrator/Desktop/backup-sql/sql"  # Change with your local backup directory
MYSQLDUMP_PATH = "C:/Program Files/MySQL/MySQL Server 8.0/bin/mysqldump.exe"  # The mysqldump.exe directory (default)

# Telegram Configuration
TELEGRAM_BOT_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"  # You can found it with botfather (telegram bot)
TELEGRAM_CHAT_ID = "YOUR_CHAT_ID"  # Change with your telegram chat ID
DAYS_TO_KEEP = 7 # Eg. Your local backup will deleted automatically after 7 days

def backup_database():
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = os.path.join(BACKUP_DIR, f"{DB_NAME}_{timestamp}.sql")

    try:
        print("Database Backup Process ...")
        dump_command = [
            MYSQLDUMP_PATH,
            "-h", DB_HOST,
            "-u", DB_USER,
            f"--password={DB_PASSWORD}",
            DB_NAME,
        ]
        with open(backup_file, "w") as file:
            subprocess.run(dump_command, stdout=file, check=True)
        print(f"Backup successfull: {backup_file}")
        return backup_file
    except subprocess.CalledProcessError as e:
        print("Failed to backup:", e)
        return None

def send_to_telegram(file_path):
    with open(file_path, "rb") as file:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendDocument"
        data = {
            "chat_id": TELEGRAM_CHAT_ID,
            "caption": "Backup Successfully Uploaded",
        }
        files = {
            "document": file,
        }
        response = requests.post(url, data=data, files=files)

        if response.status_code == 200:
            print("Failed to upload or backup failed")
        else:
            print("Fail upload to telegram:", response.status_code, response.text)

def cleanup_old_backups(directory, days=DAYS_TO_KEEP):
    now = time.time()
    cutoff = now - (days * 86400)  # 86400 seconds = 1 day

    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        if os.path.isfile(file_path):
            if os.path.getmtime(file_path) < cutoff:
                os.remove(file_path)
                print(f"Older backup has been deleted: {file_path}")

if __name__ == "__main__":
    cleanup_old_backups(BACKUP_DIR)

    backup_file = backup_database()

    if backup_file:
        send_to_telegram(backup_file)
