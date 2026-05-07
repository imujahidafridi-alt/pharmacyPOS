from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, 
    QTableWidgetItem, QLabel, QLineEdit, QMessageBox, QComboBox, QHeaderView, QFormLayout, QDialog, QStyledItemDelegate, QApplication
)
from PyQt6.QtCore import Qt, QEvent
from PyQt6.QtGui import QKeySequence, QShortcut, QKeyEvent
from controllers.purchase_controller import PurchaseController
from controllers.inventory_controller import InventoryController
from controllers.pos_controller import POSController

class ExcelDelegate(QStyledItemDelegate):
    def setEditorData(self, editor, index):
        super().setEditorData(editor, index)
        if hasattr(editor, 'selectAll'):
            editor.selectAll()
            
    def eventFilter(self, editor, event):
        if event.type() == QEvent.Type.KeyPress and event.key() in [Qt.Key.Key_Return, Qt.Key.Key_Enter]:
            tab_event = QKeyEvent(QEvent.Type.KeyPress, Qt.Key.Key_Tab, Qt.KeyboardModifier.NoModifier)
            QApplication.sendEvent(editor, tab_event)
            return True
        return super().eventFilter(editor, event)

class PurchaseMedicineSearchDialog(QDialog):
    def __init__(self, pos_controller: POSController, parent=None):
        super().__init__(parent)
        self.controller = pos_controller
        self.selected_medicine = None
        self.current_search_results = []
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("Search Item for Purchase")
        self.resize(700, 400)
        layout = QVBoxLayout(self)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Start typing to search...")
        self.search_input.textChanged.connect(self.search_medicines)
        layout.addWidget(self.search_input)
        
        self.search_results = QTableWidget()
        self.search_results.setColumnCount(4)
        self.search_results.setHorizontalHeaderLabels(["Name", "Generic Formula", "Available Stock", "Retail Price"])
        self.search_results.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.search_results.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.search_results.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.search_results.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.search_results.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.search_results.setAlternatingRowColors(True)
        self.search_results.verticalHeader().setDefaultSectionSize(30)
        self.search_results.verticalHeader().setVisible(False)
        self.search_results.setStyleSheet("QTableWidget::item:selected { background-color: #0369A1; color: #FFFFFF; font-weight: bold; }")
        self.search_results.cellDoubleClicked.connect(self.select_item_from_click)
        layout.addWidget(self.search_results)
        
        self.search_input.installEventFilter(self)
        self.search_results.installEventFilter(self)
        
    def eventFilter(self, source, event):
        if source is self.search_input and event.type() == QEvent.Type.KeyPress:
            if event.key() == Qt.Key.Key_Down and self.search_results.rowCount() > 0:
                self.search_results.setFocus()
                self.search_results.selectRow(0)
                return True
            elif event.key() in [Qt.Key.Key_Return, Qt.Key.Key_Enter]:
                if self.search_results.rowCount() > 0:
                    self.search_results.selectRow(0)
                    self.select_item_from_table()
                return True
        elif source is self.search_results and event.type() == QEvent.Type.KeyPress:
            if event.key() in [Qt.Key.Key_Return, Qt.Key.Key_Enter]:
                self.select_item_from_table()
                return True
        return super().eventFilter(source, event)
        
    def search_medicines(self, text):
        self.search_results.setRowCount(0)
        self.current_search_results = []
        if len(text) < 2: return
            
        results = self.controller.search_medicines(text)
        self.current_search_results = results
        
        self.search_results.setRowCount(len(results))
        for i, r in enumerate(results):
            self.search_results.setItem(i, 0, QTableWidgetItem(r['name']))
            self.search_results.setItem(i, 1, QTableWidgetItem(r['generic_name']))
            self.search_results.setItem(i, 2, QTableWidgetItem(str(r.get('stock', 0))))
            self.search_results.setItem(i, 3, QTableWidgetItem(f"{r['sale_price']:.2f}"))
            
    def select_item_from_click(self, row, column):
        self.select_item_from_table()
            
    def select_item_from_table(self):
        row = self.search_results.currentRow()
        if row >= 0 and row < len(self.current_search_results):
            self.selected_medicine = self.current_search_results[row]
            self.accept()

class PurchasesView(QWidget):
    def __init__(self):
        super().__init__()
        self.purchase_controller = PurchaseController()
        self.inventory_controller = InventoryController()
        self.pos_controller = POSController() # Needed for medicine search
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Header controls
        header_layout = QHBoxLayout()
        title = QLabel("Fast Stock Entry (Excel-Style Grid)")
        title.setStyleSheet("font-size: 20px; font-weight: bold;")
        header_layout.addWidget(title)
        
        self.supplier_combo = QComboBox()
        self.supplier_combo.setMinimumWidth(200)
        self.load_suppliers()
        header_layout.addStretch()
        header_layout.addWidget(QLabel("Supplier:"))
        header_layout.addWidget(self.supplier_combo)
        
        layout.addLayout(header_layout)
        
        # Help text
        help_text = QLabel("Press ENTER on 'Item Name' column to search. Press TAB to move to next cell.")
        help_text.setStyleSheet("color: gray; font-style: italic;")
        layout.addWidget(help_text)
        
        # Grid Table
        self.cart_table = QTableWidget()
        self.cart_table.setColumnCount(9)
        self.cart_table.setHorizontalHeaderLabels(["ID", "Item Name (Enter to Search)", "Unit", "Cost/Unit", "Retail Price", "Qty", "Batch No", "Expiry", "Total"])
        self.cart_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.cart_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.cart_table.setColumnHidden(0, True) # Hide ID
        self.cart_table.verticalHeader().setDefaultSectionSize(32)
        
        # Delegates
        self.delegate = ExcelDelegate(self.cart_table)
        for col in [3, 4, 5, 6, 7]:
            self.cart_table.setItemDelegateForColumn(col, self.delegate)
            
        self.cart_table.keyPressEvent = self.table_key_press
        self.cart_table.itemChanged.connect(self.on_item_changed)
        
        layout.addWidget(self.cart_table)
        
        # Bottom controls
        bottom_layout = QHBoxLayout()
        
        clear_btn = QPushButton("Clear All")
        clear_btn.setStyleSheet("background-color: #e74c3c; color: white; padding: 10px; font-weight: bold;")
        clear_btn.clicked.connect(self.clear_all)
        bottom_layout.addWidget(clear_btn)
        
        self.total_lbl = QLabel("Total Invoice Amount: 0.00")
        self.total_lbl.setStyleSheet("font-size: 18px; font-weight: bold; color: #27ae60;")
        bottom_layout.addWidget(self.total_lbl)
        
        save_btn = QPushButton("Complete Purchase (F12)")
        save_btn.setStyleSheet("background-color: #27ae60; color: white; padding: 10px; font-weight: bold;")
        save_btn.clicked.connect(self.save_purchase)
        bottom_layout.addWidget(save_btn, alignment=Qt.AlignmentFlag.AlignRight)
        
        layout.addLayout(bottom_layout)
        
        self.shortcut_save = QShortcut(QKeySequence("F12"), self)
        self.shortcut_save.activated.connect(self.save_purchase)
        
        self.ensure_empty_row()

    def showEvent(self, event):
        super().showEvent(event)
        self.ensure_empty_row()
        row_count = self.cart_table.rowCount()
        if row_count > 0:
            self.cart_table.setCurrentCell(row_count - 1, 1)
            self.cart_table.setFocus()

    def load_suppliers(self):
        self.supplier_combo.clear()
        suppliers = self.purchase_controller.get_all_suppliers()
        for s in suppliers:
            self.supplier_combo.addItem(s['name'], s['id'])

    def table_key_press(self, event):
        row = self.cart_table.currentRow()
        col = self.cart_table.currentColumn()
        
        if event.key() == Qt.Key.Key_Delete or event.key() == Qt.Key.Key_Backspace:
            if row >= 0:
                self.cart_table.removeRow(row)
                self.update_totals()
                self.ensure_empty_row()
                return
                
        if event.key() in [Qt.Key.Key_Return, Qt.Key.Key_Enter]:
            if col == 1:
                self.open_search_dialog(row)
                return
        type(self.cart_table).keyPressEvent(self.cart_table, event)

    def clear_all(self):
        reply = QMessageBox.question(self, "Clear All", "Are you sure you want to clear all items?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.cart_table.blockSignals(True)
            self.cart_table.setRowCount(0)
            self.ensure_empty_row()
            self.cart_table.blockSignals(False)
            self.update_totals()

    def ensure_empty_row(self):
        self.cart_table.blockSignals(True)
        row_count = self.cart_table.rowCount()
        last_is_filled = False
        if row_count > 0:
            id_item = self.cart_table.item(row_count - 1, 0)
            if id_item and id_item.text():
                last_is_filled = True
                
        if row_count == 0 or last_is_filled:
            self.cart_table.insertRow(row_count)
            for col in range(9):
                if col == 2: continue # Combobox
                it = QTableWidgetItem("")
                if col in [0, 1, 8]:
                    it.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
                else:
                    it.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsEditable)
                self.cart_table.setItem(row_count, col, it)
        self.cart_table.blockSignals(False)

    def clear_row(self, row):
        self.cart_table.blockSignals(True)
        for col in range(9):
            if col == 2:
                self.cart_table.removeCellWidget(row, 2)
            elif self.cart_table.item(row, col):
                self.cart_table.item(row, col).setText("")
        self.cart_table.blockSignals(False)

    def open_search_dialog(self, row):
        dialog = PurchaseMedicineSearchDialog(self.pos_controller, self)
        if dialog.exec() == QDialog.DialogCode.Accepted and dialog.selected_medicine:
            med = dialog.selected_medicine
            
            self.cart_table.blockSignals(True)
            self.cart_table.setItem(row, 0, QTableWidgetItem(str(med['id'])))
            self.cart_table.setItem(row, 1, QTableWidgetItem(med['name']))
            
            unit_combo = QComboBox()
            units = med.get('units', [])
            for u in units:
                unit_combo.addItem(u['name'], u)
                
            self.cart_table.setCellWidget(row, 2, unit_combo)
            self.cart_table.setItem(row, 3, QTableWidgetItem("0.00")) # Cost
            self.cart_table.setItem(row, 4, QTableWidgetItem(f"{med.get('sale_price', 0):.2f}")) # Retail Price
            self.cart_table.setItem(row, 5, QTableWidgetItem("1")) # Qty
            self.cart_table.setItem(row, 6, QTableWidgetItem("B-001")) # Batch
            self.cart_table.setItem(row, 7, QTableWidgetItem("2025-12-31")) # Expiry
            self.cart_table.setItem(row, 8, QTableWidgetItem("0.00")) # Total
            
            self.cart_table.blockSignals(False)
            
            self.recalculate_row(row)
            self.ensure_empty_row()
            
            # Jump to Cost editing
            self.cart_table.setCurrentCell(row, 3)
            self.cart_table.editItem(self.cart_table.item(row, 3))

    def on_item_changed(self, item):
        if item.column() in [3, 4, 5]: # Cost, Retail, or Qty
            self.recalculate_row(item.row())

    def recalculate_row(self, row):
        self.cart_table.blockSignals(True)
        try:
            price_text = self.cart_table.item(row, 3).text()
            qty_text = self.cart_table.item(row, 5).text()
            
            if price_text and qty_text:
                price = float(price_text)
                qty = int(qty_text)
                total = price * qty
                self.cart_table.item(row, 8).setText(f"{total:.2f}")
                self.ensure_empty_row()
        except (ValueError, TypeError):
            pass
        finally:
            self.cart_table.blockSignals(False)
            self.update_totals()

    def update_totals(self):
        total = 0.0
        for r in range(self.cart_table.rowCount()):
            id_item = self.cart_table.item(r, 0)
            if id_item and id_item.text():
                try:
                    price = float(self.cart_table.item(r, 3).text())
                    qty = int(self.cart_table.item(r, 5).text())
                    total += price * qty
                except (ValueError, AttributeError):
                    pass
        self.total_lbl.setText(f"Total Invoice Amount: {total:.2f}")

    def save_purchase(self):
        cart_items = []
        for r in range(self.cart_table.rowCount()):
            id_item = self.cart_table.item(r, 0)
            if id_item and id_item.text():
                try:
                    med_id = int(id_item.text())
                    name = self.cart_table.item(r, 1).text()
                    cost = float(self.cart_table.item(r, 3).text())
                    retail_price = float(self.cart_table.item(r, 4).text())
                    qty = int(self.cart_table.item(r, 5).text())
                    batch = self.cart_table.item(r, 6).text()
                    expiry = self.cart_table.item(r, 7).text()
                    
                    combo = self.cart_table.cellWidget(r, 2)
                    unit_data = combo.currentData() if combo else None
                    unit_id = unit_data['id'] if unit_data else None
                    conversion_to_base = unit_data['conversion'] if unit_data else 1
                    
                    if qty > 0:
                        cart_items.append({
                            'medicine_id': med_id,
                            'name': name,
                            'quantity': qty,
                            'purchase_price': cost,
                            'sale_price': retail_price,
                            'batch_no': batch,
                            'expiry_date': expiry,
                            'unit_id': unit_id,
                            'conversion_to_base': conversion_to_base
                        })
                except (ValueError, TypeError):
                    pass
                    
        if not cart_items:
            QMessageBox.warning(self, "Empty List", "Please add items to purchase.")
            return
            
        supplier_id = self.supplier_combo.currentData()
        if not supplier_id:
            QMessageBox.warning(self, "No Supplier", "Please select a supplier.")
            return
            
        success, msg = self.purchase_controller.add_purchase(supplier_id, cart_items)
        if success:
            QMessageBox.information(self, "Success", msg)
            self.cart_table.blockSignals(True)
            self.cart_table.setRowCount(0)
            self.ensure_empty_row()
            self.cart_table.blockSignals(False)
            self.update_totals()
        else:
            QMessageBox.warning(self, "Error", msg)
