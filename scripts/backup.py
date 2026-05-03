import os
import shutil
import datetime
import subprocess
from dotenv import load_dotenv

# Load environment variables
# Assumes this script is run from the project root
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///pharmacy.db")
BACKUP_DIR = os.path.join(os.path.dirname(__file__), '..', 'backups')

def run_backup():
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    
    if DATABASE_URL.startswith("sqlite"):
        db_path = DATABASE_URL.replace("sqlite:///", "")
        # Resolve to absolute path relative to project root
        project_root = os.path.join(os.path.dirname(__file__), '..')
        db_path = os.path.join(project_root, db_path)
        
        if not os.path.exists(db_path):
            print(f"Error: SQLite database not found at {db_path}")
            return
            
        backup_file = os.path.join(BACKUP_DIR, f"pharmacy_backup_{timestamp}.db")
        try:
            shutil.copy2(db_path, backup_file)
            print(f"SQLite backup successful: {backup_file}")
        except Exception as e:
            print(f"SQLite backup failed: {e}")
            
    elif DATABASE_URL.startswith("postgresql"):
        backup_file = os.path.join(BACKUP_DIR, f"pharmacy_backup_{timestamp}.sql")
        # Ensure pg_dump is in your system PATH
        try:
            # Note: For automated scripts, PGPASSWORD env variable is usually needed if not using .pgpass
            # Extract credentials from DATABASE_URL if necessary or rely on pgpass.
            # Simple subprocess call assuming standard setup:
            subprocess.run(
                ["pg_dump", DATABASE_URL, "-f", backup_file],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            print(f"PostgreSQL backup successful: {backup_file}")
        except subprocess.CalledProcessError as e:
            print(f"PostgreSQL backup failed: {e.stderr.decode()}")
        except Exception as e:
            print(f"Backup failed: {e}")
            
    else:
        print("Unsupported database type for backup.")

if __name__ == "__main__":
    print("Starting automated database backup...")
    run_backup()
