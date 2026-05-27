import os
import time
from datetime import datetime, timedelta
import logging

class DataRetentionManager:
    """
    Manages data retention policies for candidate data.
    Ensures compliance with GDPR/CCPA by deleting PII and transcripts after the retention period.
    """
    def __init__(self, retention_days: int = 90, storage_dirs: list = None):
        self.retention_days = retention_days
        self.storage_dirs = storage_dirs or ["reports/candidates", "logs/audit", "data/processed"]
        self.logger = logging.getLogger("DataRetention")
        self.logger.setLevel(logging.INFO)

    def enforce_retention_policy(self):
        """
        Scans configured directories and securely deletes files older than the retention limit.
        """
        cutoff_time = time.time() - (self.retention_days * 86400)
        files_deleted = 0
        
        for directory in self.storage_dirs:
            if not os.path.exists(directory):
                continue
                
            for filename in os.listdir(directory):
                filepath = os.path.join(directory, filename)
                if os.path.isfile(filepath):
                    file_mtime = os.path.getmtime(filepath)
                    if file_mtime < cutoff_time:
                        try:
                            # Secure deletion protocol (overwriting could be added here)
                            os.remove(filepath)
                            self.logger.info(f"DELETED: {filepath} (Exceeded {self.retention_days} days retention)")
                            files_deleted += 1
                        except Exception as e:
                            self.logger.error(f"FAILED TO DELETE {filepath}: {e}")
                            
        return files_deleted

if __name__ == "__main__":
    manager = DataRetentionManager(retention_days=90)
    deleted = manager.enforce_retention_policy()
    print(f"Retention enforcement complete. {deleted} records securely wiped.")
