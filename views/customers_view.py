from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, 
    QTableWidgetItem, QLabel, QLineEdit, QMessageBox, QHeaderView, QFormLayout, QSplitter, QFrame, QGridLayout
)
from PyQt6.QtCore import Qt
from controllers.customers_controller import CustomersController
from datetime import datetime

class CustomersView(QWidget):
    def __init__(self):
        super().__init__()
        self.controller = CustomersController()
        self.current_customer_id = None
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)
        
        title = QLabel("Khata / Customers Management")
        title.setObjectName("pageTitle")
        layout.addWidget(title)
        
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setStyleSheet("QSplitter::handle { background-color: #E2E8F0; width: 1px; }")
        
        # --- Left Panel: Add Customer & List ---
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 10, 0)
        
        # Add Customer Card
        add_card = QFrame()
        add_card.setObjectName("card")
        add_card_layout = QVBoxLayout(add_card)
        add_card_title = QLabel("Add New Customer")
        add_card_title.setObjectName("sectionTitle")
        add_card_layout.addWidget(add_card_title)
        
        form_layout = QFormLayout()
        self.name_input = QLineEdit()
        self.phone_input = QLineEdit()
        self.address_input = QLineEdit()
        
        form_layout.addRow("Name:", self.name_input)
        form_layout.addRow("Phone:", self.phone_input)
        form_layout.addRow("Address:", self.address_input)
        
        add_btn = QPushButton("Add Customer")
        add_btn.clicked.connect(self.add_customer)
        
        add_card_layout.addLayout(form_layout)
        add_card_layout.addWidget(add_btn)
        left_layout.addWidget(add_card)
        
        # Search Bar
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by Name or Phone...")
        self.search_input.textChanged.connect(self.filter_customers)
        search_layout.addWidget(self.search_input)
        left_layout.addLayout(search_layout)
        
        # Customer Table
        self.customer_table = QTableWidget()
        self.customer_table.setColumnCount(4)
        self.customer_table.setHorizontalHeaderLabels(["ID", "Name", "Phone", "Balance"])
        self.customer_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.customer_table.itemSelectionChanged.connect(self.on_customer_selected)
        self.customer_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.customer_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.customer_table.setAlternatingRowColors(True)
        left_layout.addWidget(self.customer_table)
        
        splitter.addWidget(left_panel)
        
        # --- Right Panel: Ledger Details ---
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(10, 0, 0, 0)
        
        self.ledger_title = QLabel("Select a customer to view ledger")
        self.ledger_title.setObjectName("sectionTitle")
        right_layout.addWidget(self.ledger_title)
        
        # Summary Dashboard Cards
        self.dashboard_container = QWidget()
        dash_layout = QHBoxLayout(self.dashboard_container)
        dash_layout.setContentsMargins(0, 0, 0, 0)
        
        self.lbl_balance = self.create_metric_card("Current Balance", "Rs. 0.00", "#EF4444")
        self.lbl_sales = self.create_metric_card("Total Sales", "Rs. 0.00", "#0F172A")
        self.lbl_last_txn = self.create_metric_card("Last Transaction", "-", "#64748B")
        
        dash_layout.addWidget(self.lbl_balance)
        dash_layout.addWidget(self.lbl_sales)
        dash_layout.addWidget(self.lbl_last_txn)
        self.dashboard_container.setVisible(False)
        right_layout.addWidget(self.dashboard_container)
        
        # Ledger Table
        self.ledger_table = QTableWidget()
        self.ledger_table.setColumnCount(4)
        self.ledger_table.setHorizontalHeaderLabels(["Date", "Description", "Type", "Amount"])
        self.ledger_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.ledger_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.ledger_table.setAlternatingRowColors(True)
        right_layout.addWidget(self.ledger_table)
        
        # Receive Payment Card
        self.payment_card = QFrame()
        self.payment_card.setVisible(False)
        self.payment_card.setObjectName("paymentCard")
        self.payment_card.setStyleSheet("""
            QFrame#paymentCard {
                background-color: #F8FAFC;
                border: 1px solid #E2E8F0;
                border-radius: 8px;
                padding: 10px;
            }
        """)
        payment_layout = QHBoxLayout(self.payment_card)
        
        pay_lbl = QLabel("Record Payment:")
        pay_lbl.setObjectName("sectionTitle")
        payment_layout.addWidget(pay_lbl)
        
        self.payment_input = QLineEdit()
        self.payment_input.setPlaceholderText("Amount (Rs)")
        payment_layout.addWidget(self.payment_input)
        
        payment_btn = QPushButton("Receive Payment")
        payment_btn.setObjectName("successBtn")
        payment_btn.clicked.connect(self.receive_payment)
        payment_layout.addWidget(payment_btn)
        
        right_layout.addWidget(self.payment_card)
        
        splitter.addWidget(right_panel)
        splitter.setSizes([450, 650])
        
        layout.addWidget(splitter, 1)
        self.load_data()

    def create_metric_card(self, title, value, val_color):
        card = QFrame()
        card.setObjectName("card")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(15, 15, 15, 15)
        
        lbl_title = QLabel(title)
        lbl_title.setStyleSheet("color: #64748B; font-size: 13px; border: none; font-weight: 500;")
        
        lbl_value = QLabel(value)
        lbl_value.setStyleSheet(f"color: {val_color}; font-size: 18px; border: none; font-weight: bold;")
        
        card.value_label = lbl_value 
        card.value_label.default_color = val_color
        
        layout.addWidget(lbl_title)
        layout.addWidget(lbl_value)
        return card

    def format_date(self, date_value):
        if isinstance(date_value, datetime):
            return date_value.strftime("%d %b %Y, %I:%M %p")
        try:
            dt = datetime.strptime(str(date_value), "%Y-%m-%d %H:%M:%S")
            return dt.strftime("%d %b %Y, %I:%M %p")
        except Exception:
            return str(date_value)

    def filter_customers(self, text):
        text = text.lower()
        for row in range(self.customer_table.rowCount()):
            name_item = self.customer_table.item(row, 1)
            phone_item = self.customer_table.item(row, 2)
            
            name = name_item.text().lower() if name_item else ""
            phone = phone_item.text().lower() if phone_item else ""
            
            if text in name or text in phone:
                self.customer_table.setRowHidden(row, False)
            else:
                self.customer_table.setRowHidden(row, True)

    def load_data(self):
        customers = self.controller.get_all_customers()
        self.customer_table.setRowCount(len(customers))
        for i, c in enumerate(customers):
            self.customer_table.setItem(i, 0, QTableWidgetItem(str(c['id'])))
            self.customer_table.setItem(i, 1, QTableWidgetItem(c['name']))
            self.customer_table.setItem(i, 2, QTableWidgetItem(c['phone']))
            balance_item = QTableWidgetItem(f"Rs. {c['balance']:.2f}")
            if c['balance'] > 0:
                balance_item.setForeground(Qt.GlobalColor.red)
            elif c['balance'] < 0:
                balance_item.setForeground(Qt.GlobalColor.green)
            else:
                balance_item.setForeground(Qt.GlobalColor.gray)
            self.customer_table.setItem(i, 3, balance_item)

    def add_customer(self):
        name = self.name_input.text()
        phone = self.phone_input.text()
        address = self.address_input.text()
        
        success, msg = self.controller.add_customer(name, phone, address)
        if success:
            QMessageBox.information(self, "Success", msg)
            self.name_input.clear()
            self.phone_input.clear()
            self.address_input.clear()
            self.load_data()
        else:
            QMessageBox.warning(self, "Error", msg)

    def on_customer_selected(self):
        selected_items = self.customer_table.selectedItems()
        if not selected_items:
            self.current_customer_id = None
            self.ledger_table.setRowCount(0)
            self.ledger_title.setText("Select a customer to view ledger")
            self.dashboard_container.setVisible(False)
            self.payment_card.setVisible(False)
            return
            
        row = selected_items[0].row()
        self.current_customer_id = int(self.customer_table.item(row, 0).text())
        customer_name = self.customer_table.item(row, 1).text()
        self.ledger_title.setText(f"Ledger: {customer_name}")
        self.dashboard_container.setVisible(True)
        self.payment_card.setVisible(True)
        
        self.load_ledger()

    def load_ledger(self):
        if not self.current_customer_id:
            return
            
        ledger_entries = self.controller.get_ledger(self.current_customer_id)
        self.ledger_table.setRowCount(len(ledger_entries))
        
        total_sales = 0.0
        current_balance = 0.0
        last_date = "-"
        
        for i, entry in enumerate(ledger_entries):
            formatted_date = self.format_date(entry['date'])
            if i == len(ledger_entries) - 1:
                last_date = formatted_date
                
            self.ledger_table.setItem(i, 0, QTableWidgetItem(formatted_date))
            self.ledger_table.setItem(i, 1, QTableWidgetItem(entry['description']))
            
            # Badge Styling for Type
            type_lbl = QLabel(f"  {entry['transaction_type']}  ")
            type_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            if entry['transaction_type'] == 'SALE':
                type_lbl.setStyleSheet("background-color: #FEE2E2; color: #DC2626; border-radius: 4px; font-size: 11px; font-weight: bold;")
                total_sales += entry['amount']
                current_balance += entry['amount']
            else:
                type_lbl.setStyleSheet("background-color: #D1FAE5; color: #059669; border-radius: 4px; font-size: 11px; font-weight: bold;")
                current_balance -= abs(entry['amount'])
                
            # Embed the label as a widget
            container = QWidget()
            l_layout = QHBoxLayout(container)
            l_layout.setContentsMargins(5, 2, 5, 2)
            l_layout.addWidget(type_lbl, alignment=Qt.AlignmentFlag.AlignLeft)
            self.ledger_table.setCellWidget(i, 2, container)
            
            amount_item = QTableWidgetItem(f"Rs. {abs(entry['amount']):.2f}")
            if entry['transaction_type'] == 'SALE':
                amount_item.setForeground(Qt.GlobalColor.red)
            else:
                amount_item.setForeground(Qt.GlobalColor.green)
                
            self.ledger_table.setItem(i, 3, amount_item)
            
        # Update Dashboard Cards
        self.lbl_sales.value_label.setText(f"Rs. {total_sales:.2f}")
        self.lbl_last_txn.value_label.setText(last_date)
        
        bal_text = f"Rs. {abs(current_balance):.2f}"
        if current_balance > 0:
            self.lbl_balance.value_label.setStyleSheet("color: #DC2626; font-size: 18px; border: none; font-weight: bold;")
            self.lbl_balance.value_label.setText(f"{bal_text} (Due)")
        elif current_balance < 0:
            self.lbl_balance.value_label.setStyleSheet("color: #059669; font-size: 18px; border: none; font-weight: bold;")
            self.lbl_balance.value_label.setText(f"{bal_text} (Advance)")
        else:
            self.lbl_balance.value_label.setStyleSheet("color: #64748B; font-size: 18px; border: none; font-weight: bold;")
            self.lbl_balance.value_label.setText("Rs. 0.00")

    def receive_payment(self):
        if not self.current_customer_id:
            QMessageBox.warning(self, "Warning", "Please select a customer first.")
            return
            
        amount = self.payment_input.text()
        success, msg = self.controller.receive_payment(self.current_customer_id, amount)
        
        if success:
            QMessageBox.information(self, "Success", msg)
            self.payment_input.clear()
            self.load_data() # Reload left panel to update total balance
            
            # Reselect the customer to reload ledger
            for row in range(self.customer_table.rowCount()):
                if int(self.customer_table.item(row, 0).text()) == self.current_customer_id:
                    self.customer_table.selectRow(row)
                    break
        else:
            QMessageBox.warning(self, "Error", msg)
