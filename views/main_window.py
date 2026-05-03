from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QStackedWidget, QLabel, QPushButton
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon
from controllers.auth_controller import AuthController

class MainWindow(QMainWindow):
    def __init__(self, auth_controller: AuthController, on_logout):
        super().__init__()
        self.auth_controller = auth_controller
        self.on_logout = on_logout
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Pharmacy POS System")
        self.resize(1024, 768)

        # Central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Navbar Container
        self.navbar_container = QWidget()
        self.navbar_container.setFixedHeight(60)
        self.navbar_container.setStyleSheet("""
            QWidget {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0F172A, stop:1 #0369A1);
                border-bottom: 1px solid rgba(255, 255, 255, 0.1);
            }
        """)
        navbar_layout = QHBoxLayout(self.navbar_container)
        navbar_layout.setContentsMargins(20, 0, 20, 0)
        navbar_layout.setSpacing(0)

        # Navbar Header / Logo area
        header_label = QLabel("Pharmacy POS")
        header_label.setStyleSheet("""
            QLabel {
                font-size: 20px;
                font-weight: bold;
                color: #FFFFFF;
                background-color: transparent;
                margin-right: 30px;
            }
        """)
        header_label.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        navbar_layout.addWidget(header_label)

        # Navbar Navigation Layout
        self.nav_layout = QHBoxLayout()
        self.nav_layout.setContentsMargins(0, 0, 0, 0)
        self.nav_layout.setSpacing(10)
        
        # Add items to sidebar
        self.role = self.auth_controller.current_user.get('role', 'Cashier')
        
        all_menu_items = [
            ("Dashboard", 0, "dashboard.svg"),
            ("POS Billing", 1, "pos.svg"),
            ("Inventory", 2, "inventory.svg"),
            ("Purchases", 3, "purchases.svg"),
            ("Suppliers", 4, "suppliers.svg"),
            ("Reports", 5, "reports.svg"),
            ("Customers (Khata)", 6, "customers.svg")
        ]
        
        self.nav_buttons = []
        for name, stack_idx, icon_file in all_menu_items:
            if self.role == 'Cashier' and name not in ["POS Billing", "Inventory", "Customers (Khata)"]:
                continue
                
            btn = QPushButton(f"  {name}")
            btn.setIcon(QIcon(f"assets/icons/{icon_file}"))
            btn.setIconSize(QSize(20, 20))
            btn.setCheckable(True)
            btn.clicked.connect(lambda checked, idx=stack_idx, b=btn: self.on_nav_button_clicked(idx, b))
            
            btn.setStyleSheet("""
                QPushButton {
                    text-align: center;
                    padding: 8px 16px;
                    border-radius: 6px;
                    color: #CBD5E1;
                    font-size: 14px;
                    font-weight: bold;
                    border: none;
                    background-color: transparent;
                }
                QPushButton:hover {
                    background-color: rgba(255, 255, 255, 0.1);
                    color: #FFFFFF;
                }
                QPushButton:checked {
                    background-color: rgba(255, 255, 255, 0.2);
                    color: #FFFFFF;
                }
            """)
            self.nav_layout.addWidget(btn)
            self.nav_buttons.append(btn)
            
        navbar_layout.addLayout(self.nav_layout)

        # Spacer
        navbar_layout.addStretch()

        # Logout Button
        self.logout_btn = QPushButton(" Logout")
        self.logout_btn.setIcon(QIcon("assets/icons/logout.svg"))
        self.logout_btn.setIconSize(QSize(18, 18))
        self.logout_btn.clicked.connect(lambda: self.switch_screen(-1))
        self.logout_btn.setStyleSheet("""
            QPushButton {
                text-align: center;
                padding: 8px 12px;
                border-radius: 6px;
                color: #FCA5A5;
                font-size: 14px;
                font-weight: bold;
                border: none;
                background-color: transparent;
            }
            QPushButton:hover {
                background-color: rgba(239, 68, 68, 0.2);
                color: #EF4444;
            }
        """)
        navbar_layout.addWidget(self.logout_btn)
        
        main_layout.addWidget(self.navbar_container)

        # Stacked widget for main content area
        self.content_stack = QStackedWidget()
        main_layout.addWidget(self.content_stack)

        # Setup screens
        self.setup_screens()
        
        # Select first available item
        if self.nav_buttons:
            self.nav_buttons[0].setChecked(True)
            # Switch to the first screen corresponding to the role
            self.switch_screen(all_menu_items[0][1] if self.role != 'Cashier' else 1)

    def setup_screens(self):
        from views.dashboard_view import DashboardView
        # Dashboard
        self.dashboard_view = DashboardView()
        self.content_stack.addWidget(self.dashboard_view)

        from views.pos_view import POSView
        # POS
        self.pos_view = POSView()
        self.content_stack.addWidget(self.pos_view)

        from views.inventory_view import InventoryView
        # Inventory
        self.inventory_view = InventoryView()
        self.content_stack.addWidget(self.inventory_view)

        from views.purchases_view import PurchasesView
        # Purchases
        self.purchases_view = PurchasesView()
        self.content_stack.addWidget(self.purchases_view)

        from views.suppliers_view import SuppliersView
        # Suppliers
        self.suppliers_view = SuppliersView()
        self.content_stack.addWidget(self.suppliers_view)

        from views.reports_view import ReportsView
        # Reports
        self.reports_view = ReportsView()
        self.content_stack.addWidget(self.reports_view)

        from views.customers_view import CustomersView
        # Customers
        self.customers_view = CustomersView()
        self.content_stack.addWidget(self.customers_view)

    def on_nav_button_clicked(self, stack_idx, clicked_btn):
        # Uncheck other buttons
        for btn in self.nav_buttons:
            if btn != clicked_btn:
                btn.setChecked(False)
        clicked_btn.setChecked(True)
        self.switch_screen(stack_idx)

    def switch_screen(self, stack_idx):
        if stack_idx == -1:
            self.auth_controller.logout()
            self.on_logout()
        else:
            self.content_stack.setCurrentIndex(stack_idx)
            # Refresh data on the newly selected screen
            current_widget = self.content_stack.currentWidget()
            if hasattr(current_widget, 'load_data'):
                current_widget.load_data()
            if hasattr(current_widget, 'load_suppliers'):
                current_widget.load_suppliers()
            if hasattr(current_widget, 'load_medicines'):
                current_widget.load_medicines()
