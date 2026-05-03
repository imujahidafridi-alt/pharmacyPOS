from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, 
    QTableWidgetItem, QLabel, QLineEdit, QMessageBox, QComboBox, QHeaderView, QFormLayout
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QKeySequence, QShortcut
from controllers.purchase_controller import PurchaseController
from controllers.inventory_controller import InventoryController

class PurchasesView(QWidget):
    def __init__(self):
        super().__init__()
        self.purchase_controller = PurchaseController()
        self.inventory_controller = InventoryController()
        self.purchase_items = []
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Header controls
        header_layout = QHBoxLayout()
        title = QLabel("Record New Purchase (Stock In)")
        title.setStyleSheet("font-size: 20px; font-weight: bold;")
        header_layout.addWidget(title)
        layout.addLayout(header_layout)
        
        # Top Form
        form_layout = QFormLayout()
        
        self.supplier_combo = QComboBox()
        self.load_suppliers()
        form_layout.addRow("Select Supplier:", self.supplier_combo)
        
        layout.addLayout(form_layout)
        
        # Add Item Form
        add_item_layout = QHBoxLayout()
        
        self.medicine_combo = QComboBox()
        self.load_medicines()
        
        self.batch_input = QLineEdit()
        self.batch_input.setPlaceholderText("Batch No")
        
        self.expiry_input = QLineEdit()
        self.expiry_input.setPlaceholderText("Expiry (YYYY-MM)")
        
        self.qty_input = QLineEdit()
        self.qty_input.setPlaceholderText("Quantity")
        
        self.price_input = QLineEdit()
        self.price_input.setPlaceholderText("Purchase Price")
        
        add_btn = QPushButton("Add to List")
        add_btn.clicked.connect(self.add_item)
        
        add_item_layout.addWidget(self.medicine_combo, stretch=2)
        add_item_layout.addWidget(self.batch_input)
        add_item_layout.addWidget(self.expiry_input)
        add_item_layout.addWidget(self.qty_input)
        add_item_layout.addWidget(self.price_input)
        add_item_layout.addWidget(add_btn)
        
        layout.addLayout(add_item_layout)
        
        # Keyboard workflows
        self.price_input.returnPressed.connect(self.add_item)
        
        # Set Tab Order
        self.setTabOrder(self.supplier_combo, self.medicine_combo)
        self.setTabOrder(self.medicine_combo, self.batch_input)
        self.setTabOrder(self.batch_input, self.expiry_input)
        self.setTabOrder(self.expiry_input, self.qty_input)
        self.setTabOrder(self.qty_input, self.price_input)
        self.setTabOrder(self.price_input, add_btn)
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["Medicine", "Batch", "Expiry", "Qty", "Price", "Total"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.table)
        
        # Bottom controls
        bottom_layout = QHBoxLayout()
        
        self.total_lbl = QLabel("Total Amount: 0.00")
        self.total_lbl.setStyleSheet("font-size: 18px; font-weight: bold;")
        bottom_layout.addWidget(self.total_lbl)
        
        save_btn = QPushButton("Complete Purchase (F12)")
        save_btn.setStyleSheet("background-color: #27ae60; color: white; padding: 10px; font-weight: bold;")
        save_btn.clicked.connect(self.save_purchase)
        bottom_layout.addWidget(save_btn, alignment=Qt.AlignmentFlag.AlignRight)
        
        layout.addLayout(bottom_layout)
        
        # Shortcuts
        self.shortcut_save = QShortcut(QKeySequence("F12"), self)
        self.shortcut_save.activated.connect(self.save_purchase)

    def load_suppliers(self):
        self.supplier_combo.clear()
        suppliers = self.purchase_controller.get_all_suppliers()
        for s in suppliers:
            self.supplier_combo.addItem(s['name'], s['id'])

    def load_medicines(self):
        self.medicine_combo.clear()
        medicines = self.inventory_controller.get_all_medicines()
        for m in medicines:
            self.medicine_combo.addItem(m['name'], m['id'])

    def add_item(self):
        med_id = self.medicine_combo.currentData()
        med_name = self.medicine_combo.currentText()
        batch = self.batch_input.text()
        expiry = self.expiry_input.text()
        
        try:
            qty = int(self.qty_input.text())
            price = float(self.price_input.text())
        except ValueError:
            QMessageBox.warning(self, "Invalid Input", "Quantity and Price must be numbers.")
            return
            
        if not batch or not expiry:
            QMessageBox.warning(self, "Invalid Input", "Batch and Expiry are required.")
            return
            
        self.purchase_items.append({
            'medicine_id': med_id,
            'name': med_name,
            'batch_no': batch,
            'expiry_date': expiry,
            'quantity': qty,
            'purchase_price': price
        })
        
        self.update_table()
        
        # Clear inputs
        self.batch_input.clear()
        self.expiry_input.clear()
        self.qty_input.clear()
        self.price_input.clear()
        
        # Return focus to medicine
        self.medicine_combo.setFocus()

    def update_table(self):
        self.table.setRowCount(len(self.purchase_items))
        total_amount = 0.0
        
        for i, item in enumerate(self.purchase_items):
            self.table.setItem(i, 0, QTableWidgetItem(item['name']))
            self.table.setItem(i, 1, QTableWidgetItem(item['batch_no']))
            self.table.setItem(i, 2, QTableWidgetItem(item['expiry_date']))
            self.table.setItem(i, 3, QTableWidgetItem(str(item['quantity'])))
            self.table.setItem(i, 4, QTableWidgetItem(str(item['purchase_price'])))
            
            row_total = item['quantity'] * item['purchase_price']
            total_amount += row_total
            self.table.setItem(i, 5, QTableWidgetItem(str(row_total)))
            
        self.total_lbl.setText(f"Total Amount: {total_amount:.2f}")

    def save_purchase(self):
        if not self.purchase_items:
            QMessageBox.warning(self, "Empty List", "Please add items to purchase.")
            return
            
        supplier_id = self.supplier_combo.currentData()
        if not supplier_id:
            QMessageBox.warning(self, "No Supplier", "Please select a supplier.")
            return
            
        success, msg = self.purchase_controller.add_purchase(supplier_id, self.purchase_items)
        if success:
            QMessageBox.information(self, "Success", msg)
            self.purchase_items.clear()
            self.update_table()
        else:
            QMessageBox.warning(self, "Error", msg)
