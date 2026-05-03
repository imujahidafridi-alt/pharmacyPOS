from core.database import get_db
from core.models import AuditLog
import datetime

class AuditController:
    """Handles creating and fetching audit logs."""

    @staticmethod
    def log_action(user_id, action, details=""):
        if not user_id:
            return False
            
        db = next(get_db())
        try:
            date_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_entry = AuditLog(user_id=user_id, action=action, details=details, timestamp=date_str)
            db.add(log_entry)
            db.commit()
            return True
        except Exception as e:
            db.rollback()
            print(f"Failed to write audit log: {e}")
            return False

    def get_logs(self):
        db = next(get_db())
        logs = db.query(AuditLog).order_by(AuditLog.timestamp.desc()).limit(100).all()
        return [{"id": l.id, "user_id": l.user_id, "action": l.action, "details": l.details, "timestamp": l.timestamp} for l in logs]
