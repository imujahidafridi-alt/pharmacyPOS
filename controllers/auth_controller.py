from core.database import get_db
from core.models import User
from core.security import verify_password
from controllers.audit_controller import AuditController

class AuthController:
    """Handles authentication logic."""

    def __init__(self):
        self.current_user = None

    def login(self, username, password) -> tuple[bool, str]:
        if not username or not password:
            return False, "Username and password are required."

        db = next(get_db())
        user = db.query(User).filter(User.username == username).first()

        if user:
            # Verify password
            if verify_password(password, user.password_hash):
                self.current_user = {
                    'id': user.id,
                    'username': user.username,
                    'role': user.role
                }
                AuditController.log_action(user.id, "LOGIN", f"User {username} logged in successfully.")
                return True, "Login successful."
            else:
                return False, "Invalid password."
        else:
            return False, "User not found."

    def logout(self):
        if self.current_user:
            AuditController.log_action(self.current_user['id'], "LOGOUT", f"User {self.current_user['username']} logged out.")
        self.current_user = None
