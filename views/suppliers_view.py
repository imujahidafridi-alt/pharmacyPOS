from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, 
    QTableWidgetItem, QHeaderView, QLabel, QLineEdit, QMessageBox, QFormLayout, QDialog
)
from PyQt6.QtCore import Qt
from controllers.purchase_controller import PurchaseController

class AddSupplierDialog(QDialog):
    def __init__(self, controller: PurchaseController, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.setWindowTitle("Add New Supplier")
        self.resize(300, 200)
        
        layout = QFormLayout(self)
        
        self.name_input = QLineEdit()
        self.phone_input = QLineEdit()
        self.address_input = QLineEdit()
        
        layout.addRow("Name *:", self.name_input)
        layout.addRow("Phone:", self.phone_input)
        layout.addRow("Address:", self.address_input)
        
        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.save)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addRow(btn_layout)

    def save(self):
        name = self.name_input.text()
        phone = self.phone_input.text()
        address = self.address_input.text()
        
        success, msg = self.controller.add_supplier(name, phone, address)
        if success:
            QMessageBox.information(self, "Success", msg)
            self.accept()
        else:
            QMessageBox.warning(self, "Error", msg)


class SuppliersView(QWidget):
    def __init__(self):
        super().__init__()
        self.controller = PurchaseController()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Header controls
        header_layout = QHBoxLayout()
        
        title = QLabel("Suppliers Management")
        title.setStyleSheet("font-size: 20px; font-weight: bold;")
        header_layout.addWidget(title)
        
        add_btn = QPushButton("Add New Supplier")
        add_btn.setStyleSheet("background-color: #3498db; color: white; padding: 5px;")
        add_btn.clicked.connect(self.show_add_dialog)
        header_layout.addWidget(add_btn, alignment=Qt.AlignmentFlag.AlignRight)
        
        layout.addLayout(header_layout)
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["ID", "Name", "Phone", "Address"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.table)
        
        self.load_data()

    def show_add_dialog(self):
        dialog = AddSupplierDialog(self.controller, self)
        if dialog.exec():
            self.load_data()

    def load_data(self):
        suppliers = self.controller.get_all_suppliers()
        self.table.setRowCount(len(suppliers))
        for row_idx, item in enumerate(suppliers):
            self.table.setItem(row_idx, 0, QTableWidgetItem(str(item['id'])))
            self.table.setItem(row_idx, 1, QTableWidgetItem(item['name']))
            self.table.setItem(row_idx, 2, QTableWidgetItem(item['phone'] or ""))
            self.table.setItem(row_idx, 3, QTableWidgetItem(item['address'] or ""))
