from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, 
    QTableWidgetItem, QHeaderView, QLabel, QLineEdit, QMessageBox, QFormLayout, QDialog, QFileDialog, QCheckBox, QComboBox, QGridLayout, QGroupBox
)
from PyQt6.QtCore import Qt
from controllers.inventory_controller import InventoryController

class AddMedicineDialog(QDialog):
    def __init__(self, controller: InventoryController, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.setWindowTitle("Add New Item (Inventory & Medicine)")
        self.resize(700, 500)
        
        main_layout = QVBoxLayout(self)
        
        # --- Section 1: General Info ---
        gen_group = QGroupBox("General Information")
        gen_layout = QGridLayout()
        
        self.barcode_input = QLineEdit()
        self.barcode_input.setPlaceholderText("Scan Barcode or type...")
        
        self.name_input = QLineEdit()
        self.generic_input = QLineEdit()
        
        self.category_combo = QComboBox()
        categories = [
            "Tablets / Capsules", 
            "Syrups / Suspensions", 
            "Injections / Drops",
            "Creams / Ointments",
            "Inhalers / Sprays",
            "Surgical & Disposables",
            "Cosmetics / Skincare",
            "Baby Care / Diapers",
            "Nutraceuticals / Vitamins",
            "OTC (Over The Counter)",
            "Herbal / Homeopathic",
            "Consumer Goods / General",
            "Medicine"
        ]
        self.category_combo.addItems(categories)
        self.category_combo.setEditable(True)
        
        self.manufacturer_input = QLineEdit()
        self.location_input = QLineEdit()
        self.location_input.setPlaceholderText("e.g. A-12")
        
        gen_layout.addWidget(QLabel("Barcode:"), 0, 0)
        gen_layout.addWidget(self.barcode_input, 0, 1)
        gen_layout.addWidget(QLabel("Item Name *:"), 0, 2)
        gen_layout.addWidget(self.name_input, 0, 3)
        
        gen_layout.addWidget(QLabel("Generic Name:"), 1, 0)
        gen_layout.addWidget(self.generic_input, 1, 1)
        gen_layout.addWidget(QLabel("Category:"), 1, 2)
        gen_layout.addWidget(self.category_combo, 1, 3)
        
        gen_layout.addWidget(QLabel("Manufacturer:"), 2, 0)
        gen_layout.addWidget(self.manufacturer_input, 2, 1)
        gen_layout.addWidget(QLabel("Shelf Location:"), 2, 2)
        gen_layout.addWidget(self.location_input, 2, 3)
        
        gen_group.setLayout(gen_layout)
        main_layout.addWidget(gen_group)
        
        # --- Section 2: Units & Pricing ---
        price_group = QGroupBox("Units & Pricing")
        price_layout = QGridLayout()
        
        self.units = self.controller.get_all_units()
        
        self.base_unit_combo = QComboBox()
        for u in self.units:
            self.base_unit_combo.addItem(u['name'], u['id'])
            
        self.pack_unit_combo = QComboBox()
        for u in self.units:
            self.pack_unit_combo.addItem(u['name'], u['id'])
            
        self.pack_conversion_input = QLineEdit("1")
        self.pack_conversion_input.setPlaceholderText("Base units per Pack")
        
        self.sale_price_input = QLineEdit()
        self.sale_price_input.setPlaceholderText("Sale Price per BASE unit")
        
        self.purchase_price_input = QLineEdit()
        self.purchase_price_input.setPlaceholderText("Purchase Price per PACK")
        
        price_layout.addWidget(QLabel("Base Unit *:"), 0, 0)
        price_layout.addWidget(self.base_unit_combo, 0, 1)
        price_layout.addWidget(QLabel("Sale Price (Per Base Unit) *:"), 0, 2)
        price_layout.addWidget(self.sale_price_input, 0, 3)
        
        price_layout.addWidget(QLabel("Pack Unit (e.g. Box):"), 1, 0)
        price_layout.addWidget(self.pack_unit_combo, 1, 1)
        price_layout.addWidget(QLabel("Units per Pack:"), 1, 2)
        price_layout.addWidget(self.pack_conversion_input, 1, 3)
        
        self.default_sale_unit_combo = QComboBox()
        self.default_sale_unit_combo.addItem("Base Unit", "base")
        self.default_sale_unit_combo.addItem("Pack Unit", "pack")
        
        price_layout.addWidget(QLabel("Default Sale Unit:"), 2, 0)
        price_layout.addWidget(self.default_sale_unit_combo, 2, 1)
        
        price_layout.addWidget(QLabel("Purchase Price (Per Pack):"), 2, 2)
        price_layout.addWidget(self.purchase_price_input, 2, 3)
        
        price_group.setLayout(price_layout)
        main_layout.addWidget(price_group)
        
        # --- Section 3: Stock Details ---
        stock_group = QGroupBox("Initial Stock Details")
        stock_layout = QGridLayout()
        
        self.current_stock_input = QLineEdit("0")
        self.current_stock_input.setPlaceholderText("Stock in BASE units")
        
        self.min_stock_input = QLineEdit("10")
        
        self.batch_input = QLineEdit()
        self.expiry_input = QLineEdit()
        self.expiry_input.setPlaceholderText("YYYY-MM-DD")
        
        stock_layout.addWidget(QLabel("Current Stock (Base Units):"), 0, 0)
        stock_layout.addWidget(self.current_stock_input, 0, 1)
        stock_layout.addWidget(QLabel("Minimum Stock Level:"), 0, 2)
        stock_layout.addWidget(self.min_stock_input, 0, 3)
        
        stock_layout.addWidget(QLabel("Batch No:"), 1, 0)
        stock_layout.addWidget(self.batch_input, 1, 1)
        stock_layout.addWidget(QLabel("Expiry Date:"), 1, 2)
        stock_layout.addWidget(self.expiry_input, 1, 3)
        
        stock_group.setLayout(stock_layout)
        main_layout.addWidget(stock_group)
        
        # Description
        desc_layout = QHBoxLayout()
        self.desc_input = QLineEdit()
        self.desc_input.setPlaceholderText("Optional description...")
        desc_layout.addWidget(QLabel("Description:"))
        desc_layout.addWidget(self.desc_input)
        main_layout.addLayout(desc_layout)
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        save_btn = QPushButton("Save Item (Enter)")
        save_btn.setStyleSheet("background-color: #2980b9; color: white; padding: 8px 15px; font-weight: bold;")
        save_btn.clicked.connect(self.save)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(save_btn)
        main_layout.addLayout(btn_layout)
        
        # Set Tab Order manually for perfect UX
        QWidget.setTabOrder(self.barcode_input, self.name_input)
        QWidget.setTabOrder(self.name_input, self.generic_input)
        QWidget.setTabOrder(self.generic_input, self.category_combo)
        QWidget.setTabOrder(self.category_combo, self.manufacturer_input)
        QWidget.setTabOrder(self.manufacturer_input, self.location_input)
        QWidget.setTabOrder(self.location_input, self.base_unit_combo)
        QWidget.setTabOrder(self.base_unit_combo, self.sale_price_input)
        QWidget.setTabOrder(self.sale_price_input, self.pack_unit_combo)
        QWidget.setTabOrder(self.pack_unit_combo, self.pack_conversion_input)
        QWidget.setTabOrder(self.pack_conversion_input, self.purchase_price_input)
        QWidget.setTabOrder(self.purchase_price_input, self.current_stock_input)
        QWidget.setTabOrder(self.current_stock_input, self.min_stock_input)
        QWidget.setTabOrder(self.min_stock_input, self.batch_input)
        QWidget.setTabOrder(self.batch_input, self.expiry_input)
        QWidget.setTabOrder(self.expiry_input, self.desc_input)
        QWidget.setTabOrder(self.desc_input, save_btn)

    def save(self):
        data = {
            'barcode': self.barcode_input.text() or None,
            'name': self.name_input.text(),
            'generic_name': self.generic_input.text(),
            'category': self.category_combo.currentText(),
            'manufacturer': self.manufacturer_input.text(),
            'location': self.location_input.text(),
            'base_unit_id': self.base_unit_combo.currentData(),
            'sale_price': self.sale_price_input.text() or 0,
            'pack_unit_id': self.pack_unit_combo.currentData(),
            'pack_conversion': self.pack_conversion_input.text(),
            'default_sale_unit': self.default_sale_unit_combo.currentData(),
            'purchase_price_pack': self.purchase_price_input.text() or 0,
            'current_stock': self.current_stock_input.text() or 0,
            'min_stock_level': self.min_stock_input.text() or 10,
            'batch_no': self.batch_input.text() or 'Unknown',
            'expiry_date': self.expiry_input.text() or '2099-12-31',
            'description': self.desc_input.text()
        }
        
        success, msg = self.controller.add_medicine_full(data)
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
        
        delete_btn = QPushButton("Delete Selected")
        delete_btn.setStyleSheet("background-color: #e74c3c; color: white; padding: 5px;")
        delete_btn.clicked.connect(self.delete_selected)
        header_layout.addWidget(delete_btn)
        
        layout.addLayout(header_layout)
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Medicine Name", "Batch No", "Expiry Date", "Quantity", "Purchase Price"])
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

    def delete_selected(self):
        row = self.table.currentRow()
        if row >= 0:
            med_name_item = self.table.item(row, 0)
            if not med_name_item: return
            med_id = med_name_item.data(Qt.ItemDataRole.UserRole)
            if med_id is None:
                return
            med_name = med_name_item.text()
            
            reply = QMessageBox.question(self, 'Confirm Delete', f"Are you sure you want to delete '{med_name}'?", 
                                         QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)
            
            if reply == QMessageBox.StandardButton.Yes:
                success, msg = self.controller.delete_medicine(med_id)
                if success:
                    QMessageBox.information(self, "Success", msg)
                    self.load_data()
                else:
                    QMessageBox.warning(self, "Error", msg)
        else:
            QMessageBox.warning(self, "Selection Required", "Please select a row from the table to delete.")

    def load_data(self):
        stock = self.controller.get_inventory_stock()
        self.table.setRowCount(len(stock))
        for row_idx, item in enumerate(stock):
            name_item = QTableWidgetItem(item['name'])
            name_item.setData(Qt.ItemDataRole.UserRole, item['id'])
            self.table.setItem(row_idx, 0, name_item)
            self.table.setItem(row_idx, 1, QTableWidgetItem(item['batch_no']))
            self.table.setItem(row_idx, 2, QTableWidgetItem(item['expiry_date']))
            self.table.setItem(row_idx, 3, QTableWidgetItem(str(item['quantity'])))
            self.table.setItem(row_idx, 4, QTableWidgetItem(str(item['purchase_price'])))
