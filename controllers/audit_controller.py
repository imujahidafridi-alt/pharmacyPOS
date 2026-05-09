from core.database import get_db_session
from core.models import AuditLog
import datetime

class AuditController:
    """Handles creating and fetching audit logs."""

    @staticmethod
    def log_action(user_id, action, details=""):
        if not user_id:
            return False
            
        with get_db_session() as db:
            try:
                date_str = datetime.datetime.now()
                log_entry = AuditLog(user_id=user_id, action=action, details=details, timestamp=date_str)
                db.add(log_entry)
                db.commit()
                return True
            except Exception as e:
                db.rollback()
                print(f"Failed to write audit log: {e}")
                return False

    def get_logs(self):
        with get_db_session() as db:
            logs = db.query(AuditLog).order_by(AuditLog.timestamp.desc()).limit(100).all()
            return [{"id": l.id, "user_id": l.user_id, "action": l.action, "details": l.details, "timestamp": l.timestamp} for l in logs]
