import sys
from PyQt6.QtWidgets import QApplication
from core.database import init_db
from core.logging import configure_logging
from core.theme import GLOBAL_STYLE
from controllers.auth_controller import AuthController
from views.login_view import LoginView
from views.main_window import MainWindow

class AppController:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setStyleSheet(GLOBAL_STYLE)
        self.auth_controller = AuthController()
        self.login_view = None
        self.main_window = None

    def show_login(self):
        if self.main_window:
            self.main_window.close()
        self.login_view = LoginView(self.auth_controller, self.show_main_window)
        self.login_view.show()

    def show_main_window(self):
        if self.login_view:
            self.login_view.close()
        self.main_window = MainWindow(self.auth_controller, self.show_login)
        self.main_window.show()

    def run(self):
        logger = configure_logging()
        logger.info("Starting Pharmacy POS System...")
        init_db()
        self.show_login()
        sys.exit(self.app.exec())

if __name__ == "__main__":
    app_controller = AppController()
    app_controller.run()

