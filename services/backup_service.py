import os
import shutil
from datetime import datetime
import glob
from config import Config

def create_backup(db_filename: str = "database.db") -> str:
    """Creates a copy of the SQLite database with a timestamp."""
    if not os.path.exists(db_filename):
        return "Source database does not exist yet."
        
    if not os.path.exists(Config.BACKUP_DIR):
        os.makedirs(Config.BACKUP_DIR, exist_ok=True)
        
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_filename = f"backup_{timestamp}.db"
    backup_filepath = os.path.join(Config.BACKUP_DIR, backup_filename)
    
    shutil.copy2(db_filename, backup_filepath)
    print(f"[Backup] Successfully created database backup: {backup_filepath}")
    return backup_filepath

def run_backup_if_needed(db_filename: str = "database.db") -> bool:
    """Checks the backup configurations and runs a backup if the period is reached."""
    if not Config.BACKUP_ENABLED:
        return False
        
    if not os.path.exists(db_filename):
        return False
        
    # Get all backup files
    backup_pattern = os.path.join(Config.BACKUP_DIR, "backup_*.db")
    backup_files = glob.glob(backup_pattern)
    
    if not backup_files:
        # Create first backup immediately
        create_backup(db_filename)
        return True
        
    # Sort backups to find the latest
    backup_files.sort()
    latest_backup = backup_files[-1]
    
    # Get last backup time
    try:
        # Parse timestamp from filename: backup_YYYYMMDD_HHMMSS.db
        basename = os.path.basename(latest_backup)
        time_part = basename.replace("backup_", "").replace(".db", "")
        last_backup_time = datetime.strptime(time_part, "%Y%m%d_%H%M%S")
    except Exception:
        # If filename is unexpected, get file system modification time
        last_backup_time = datetime.fromtimestamp(os.path.getmtime(latest_backup))
        
    now = datetime.now()
    delta = now - last_backup_time
    
    should_backup = False
    if Config.BACKUP_PERIOD == "daily" and delta.days >= 1:
        should_backup = True
    elif Config.BACKUP_PERIOD == "weekly" and delta.days >= 7:
        should_backup = True
    elif Config.BACKUP_PERIOD == "monthly" and delta.days >= 30:
        should_backup = True
        
    if should_backup:
        create_backup(db_filename)
        return True
        
    return False

def list_backups():
    """Returns lists of backups available in the backup directory."""
    if not os.path.exists(Config.BACKUP_DIR):
        return []
    backup_pattern = os.path.join(Config.BACKUP_DIR, "backup_*.db")
    files = glob.glob(backup_pattern)
    files.sort(reverse=True)
    
    backups = []
    for f in files:
        stat = os.stat(f)
        size_kb = round(stat.st_size / 1024, 2)
        mtime = datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
        backups.append({
            "filename": os.path.basename(f),
            "size_kb": size_kb,
            "modified": mtime,
            "path": f
        })
    return backups
