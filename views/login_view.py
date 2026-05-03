from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QLineEdit, QPushButton, QMessageBox, QSpacerItem, QSizePolicy, QFrame
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon, QPixmap
from controllers.auth_controller import AuthController

class LoginView(QWidget):
    def __init__(self, auth_controller: AuthController, on_login_success):
        super().__init__()
        self.auth_controller = auth_controller
        self.on_login_success = on_login_success
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Pharmacy POS System - Secure Login")
        self.setFixedSize(800, 500)
        
        # Main Layout (Horizontal split)
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # === Left Panel: Branding / Hero ===
        left_panel = QFrame()
        left_panel.setStyleSheet("""
            QFrame {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #0F172A, stop:1 #0369A1);
            }
        """)
        left_layout = QVBoxLayout(left_panel)
        left_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        logo_lbl = QLabel()
        logo_icon = QIcon("assets/icons/logo.svg").pixmap(80, 80)
        logo_lbl.setPixmap(logo_icon)
        logo_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_lbl.setStyleSheet("background: transparent;")
        left_layout.addWidget(logo_lbl)
        
        title_lbl = QLabel("Pharmacy POS")
        title_lbl.setStyleSheet("color: white; font-size: 32px; font-weight: bold; margin-top: 10px; background: transparent;")
        title_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        left_layout.addWidget(title_lbl)
        
        subtitle_lbl = QLabel("Enterprise Grade Management")
        subtitle_lbl.setStyleSheet("color: #94A3B8; font-size: 16px; background: transparent;")
        subtitle_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        left_layout.addWidget(subtitle_lbl)
        
        main_layout.addWidget(left_panel, stretch=1)
        
        # === Right Panel: Login Form ===
        right_panel = QFrame()
        right_panel.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
            }
        """)
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(60, 60, 60, 60)
        right_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        welcome_lbl = QLabel("Welcome Back")
        welcome_lbl.setStyleSheet("color: #1E293B; font-size: 28px; font-weight: bold; margin-bottom: 5px;")
        welcome_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        right_layout.addWidget(welcome_lbl)
        
        instruction_lbl = QLabel("Please enter your details to sign in.")
        instruction_lbl.setStyleSheet("color: #64748B; font-size: 14px; margin-bottom: 30px;")
        instruction_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        right_layout.addWidget(instruction_lbl)
        
        # Form Container to constrain width
        form_container = QVBoxLayout()
        form_container.setSpacing(15)
        
        # Username Input
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Username")
        self.username_input.setMinimumHeight(45)
        self.username_input.addAction(QIcon("assets/icons/user.svg"), QLineEdit.ActionPosition.LeadingPosition)
        self.username_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid #CBD5E1;
                border-radius: 8px;
                padding-left: 5px;
                font-size: 15px;
                color: #334155;
            }
            QLineEdit:focus {
                border: 2px solid #0369A1;
            }
        """)
        form_container.addWidget(self.username_input)
        
        # Password Input
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setMinimumHeight(45)
        self.password_input.addAction(QIcon("assets/icons/lock.svg"), QLineEdit.ActionPosition.LeadingPosition)
        self.password_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid #CBD5E1;
                border-radius: 8px;
                padding-left: 5px;
                font-size: 15px;
                color: #334155;
            }
            QLineEdit:focus {
                border: 2px solid #0369A1;
            }
        """)
        form_container.addWidget(self.password_input)
        
        # Login Button
        self.login_btn = QPushButton("Sign In")
        self.login_btn.setMinimumHeight(45)
        self.login_btn.setStyleSheet("""
            QPushButton {
                background-color: #0369A1;
                color: white;
                font-size: 16px;
                font-weight: bold;
                border-radius: 8px;
                margin-top: 10px;
                border: none;
            }
            QPushButton:hover {
                background-color: #0284C7;
            }
            QPushButton:pressed {
                background-color: #075985;
            }
        """)
        self.login_btn.clicked.connect(self.handle_login)
        form_container.addWidget(self.login_btn)
        
        right_layout.addLayout(form_container)
        
        main_layout.addWidget(right_panel, stretch=1)
        
        # Allow pressing Enter to login
        self.password_input.returnPressed.connect(self.login_btn.click)
        self.username_input.returnPressed.connect(self.login_btn.click)

    def handle_login(self):
        username = self.username_input.text()
        password = self.password_input.text()

        success, message = self.auth_controller.login(username, password)

        if success:
            self.on_login_success()
        else:
            QMessageBox.warning(self, "Login Failed", message)
