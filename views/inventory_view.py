from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, 
    QTableWidgetItem, QHeaderView, QLabel, QLineEdit, QMessageBox, QFormLayout, QDialog, QFileDialog, QCheckBox
)
from PyQt6.QtCore import Qt
from controllers.inventory_controller import InventoryController

class AddMedicineDialog(QDialog):
    def __init__(self, controller: InventoryController, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.setWindowTitle("Add New Medicine")
        self.resize(300, 250)
        
        layout = QFormLayout(self)
        
        self.name_input = QLineEdit()
        self.generic_input = QLineEdit()
        self.category_input = QLineEdit()
        self.price_input = QLineEdit()
        self.units_input = QLineEdit("1")
        
        layout.addRow("Name *:", self.name_input)
        layout.addRow("Generic Name:", self.generic_input)
        layout.addRow("Category:", self.category_input)
        layout.addRow("Sale Price *:", self.price_input)
        layout.addRow("Units per Box:", self.units_input)
        
        self.discountable_cb = QCheckBox("Is Discountable?")
        self.discountable_cb.setChecked(True)
        layout.addRow(self.discountable_cb)
        
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
        generic = self.generic_input.text()
        category = self.category_input.text()
        price = self.price_input.text()
        units = self.units_input.text()
        is_discountable = 1 if self.discountable_cb.isChecked() else 0
        
        success, msg = self.controller.add_medicine(name, generic, category, price, units, is_discountable)
        if success:
            QMessageBox.information(self, "Success", msg)
            self.accept()
        else:
            QMessageBox.warning(self, "Error", msg)


class InventoryView(QWidget):
    def __init__(self):
        super().__init__()
        self.controller = InventoryController()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Header controls
        header_layout = QHBoxLayout()
        
        title = QLabel("Inventory Management")
        title.setStyleSheet("font-size: 20px; font-weight: bold;")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        import_csv_btn = QPushButton("Import CSV")
        import_csv_btn.setStyleSheet("background-color: #27ae60; color: white; padding: 5px;")
        import_csv_btn.clicked.connect(self.import_csv)
        header_layout.addWidget(import_csv_btn)
        
        add_med_btn = QPushButton("Add New Medicine")
        add_med_btn.setStyleSheet("background-color: #3498db; color: white; padding: 5px;")
        add_med_btn.clicked.connect(self.show_add_medicine_dialog)
        header_layout.addWidget(add_med_btn)
        
        layout.addLayout(header_layout)
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["ID", "Medicine Name", "Batch No", "Expiry Date", "Quantity", "Purchase Price"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.table)
        
        self.load_data()

    def import_csv(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open CSV File", "", "CSV Files (*.csv);;All Files (*)")
        if file_path:
            success, msg = self.controller.import_medicines_csv(file_path)
            if success:
                QMessageBox.information(self, "Success", msg)
                self.load_data()
            else:
                QMessageBox.warning(self, "Error", msg)

    def show_add_medicine_dialog(self):
        dialog = AddMedicineDialog(self.controller, self)
        if dialog.exec():
            self.load_data()

    def load_data(self):
        stock = self.controller.get_inventory_stock()
        self.table.setRowCount(len(stock))
        for row_idx, item in enumerate(stock):
            self.table.setItem(row_idx, 0, QTableWidgetItem(str(item['id'])))
            self.table.setItem(row_idx, 1, QTableWidgetItem(item['name']))
            self.table.setItem(row_idx, 2, QTableWidgetItem(item['batch_no']))
            self.table.setItem(row_idx, 3, QTableWidgetItem(item['expiry_date']))
            self.table.setItem(row_idx, 4, QTableWidgetItem(str(item['quantity'])))
            self.table.setItem(row_idx, 5, QTableWidgetItem(str(item['purchase_price'])))
