import os

class Config:
    # Database Settings
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///database.db")
    
    # Session Settings
    SECRET_KEY = os.getenv("SECRET_KEY", "super-secret-kanban-key-1234")
    SESSION_COOKIE_NAME = "kanban_session"
    
    # Backup Settings
    BACKUP_ENABLED = os.getenv("BACKUP_ENABLED", "true").lower() in ("true", "1", "yes")
    BACKUP_DIR = os.getenv("BACKUP_DIR", "backups")
    # Backup period: 'daily', 'weekly', 'monthly'
    BACKUP_PERIOD = os.getenv("BACKUP_PERIOD", "daily")
    
    # Export Settings
    EXPORT_DIR = os.getenv("EXPORT_DIR", "exports")

# Create required folders
for folder in [Config.BACKUP_DIR, Config.EXPORT_DIR]:
    if not os.path.exists(folder):
        os.makedirs(folder, exist_ok=True)
