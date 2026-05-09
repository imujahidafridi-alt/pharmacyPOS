from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableView,
    QLabel, QLineEdit, QMessageBox, QComboBox, QHeaderView, QFormLayout,
    QDialog, QStyledItemDelegate, QApplication, QTableWidget, QTableWidgetItem
)
from PyQt6.QtCore import Qt, QEvent, QAbstractTableModel, QModelIndex
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

class UnitComboDelegate(QStyledItemDelegate):
    def createEditor(self, parent, option, index):
        combo = QComboBox(parent)
        row = index.model().row_data(index.row())
        for unit in row.get('units', []):
            combo.addItem(unit['name'], unit)
        return combo

    def setEditorData(self, editor, index):
        current_value = index.model().data(index, Qt.ItemDataRole.EditRole)
        for i in range(editor.count()):
            item_data = editor.itemData(i)
            if isinstance(current_value, dict) and isinstance(item_data, dict):
                if item_data.get('id') == current_value.get('id'):
                    editor.setCurrentIndex(i)
                    return
            elif item_data == current_value:
                editor.setCurrentIndex(i)
                return

    def setModelData(self, editor, model, index):
        unit = editor.currentData()
        model.setData(index, unit, Qt.ItemDataRole.EditRole)

class PurchaseTableModel(QAbstractTableModel):
    headers = ["ID", "Item Name", "Unit", "Cost/Unit", "Sale Price", "Qty", "Batch No", "Expiry", "Total"]

    def __init__(self, parent=None):
        super().__init__(parent)
        self._rows = []

    def rowCount(self, parent=QModelIndex()):
        return len(self._rows)

    def columnCount(self, parent=QModelIndex()):
        return len(self.headers)

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None

        row = self._rows[index.row()]
        col = index.column()

        if role == Qt.ItemDataRole.DisplayRole:
            if col == 0:
                return str(row.get('id', ''))
            if col == 1:
                return row.get('name', '')
            if col == 2:
                return row.get('unit', {}).get('name', '')
            if col == 3:
                return f"{row.get('purchase_price', 0.0):.2f}" if row.get('id') is not None else ""
            if col == 4:
                return f"{row.get('sale_price', 0.0):.2f}" if row.get('id') is not None else ""
            if col == 5:
                return str(row.get('qty', '')) if row.get('id') is not None else ""
            if col == 6:
                return row.get('batch_no', '')
            if col == 7:
                return row.get('expiry_date', '')
            if col == 8:
                return f"{row.get('qty', 0) * row.get('purchase_price', 0.0):.2f}" if row.get('id') is not None else ""

        if role == Qt.ItemDataRole.EditRole:
            if col == 2:
                return row.get('unit', {})
            if col == 3:
                return row.get('purchase_price', 0.0)
            if col == 4:
                return row.get('sale_price', 0.0)
            if col == 5:
                return row.get('qty', 0)
            if col == 6:
                return row.get('batch_no', '')
            if col == 7:
                return row.get('expiry_date', '')

        if role == Qt.ItemDataRole.UserRole:
            return row

        return None

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole and orientation == Qt.Orientation.Horizontal:
            return self.headers[section]
        return None

    def flags(self, index):
        if not index.isValid():
            return Qt.ItemFlag.NoItemFlags

        flags = Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable
        row = self._rows[index.row()]
        if row.get('id') is not None and index.column() in [2, 3, 4, 5, 6, 7]:
            flags |= Qt.ItemFlag.ItemIsEditable
        return flags

    def setData(self, index, value, role=Qt.ItemDataRole.EditRole):
        if role != Qt.ItemDataRole.EditRole or not index.isValid():
            return False

        row = self._rows[index.row()]
        col = index.column()

        if col == 3:
            try:
                row['purchase_price'] = float(value)
            except (ValueError, TypeError):
                return False
        elif col == 4:
            try:
                row['sale_price'] = float(value)
            except (ValueError, TypeError):
                return False
        elif col == 5:
            try:
                row['qty'] = int(value)
            except (ValueError, TypeError):
                return False
        elif col == 6:
            row['batch_no'] = str(value)
        elif col == 7:
            row['expiry_date'] = str(value)
        elif col == 2 and isinstance(value, dict):
            row['unit'] = value
        else:
            return False

        self.dataChanged.emit(self.index(index.row(), 0), self.index(index.row(), self.columnCount() - 1), [Qt.ItemDataRole.DisplayRole])
        return True

    def append_blank_row(self):
        self.beginInsertRows(QModelIndex(), self.rowCount(), self.rowCount())
        self._rows.append({'id': None, 'name': '', 'units': [], 'unit': {}, 'purchase_price': 0.0, 'sale_price': 0.0, 'qty': 0, 'batch_no': '', 'expiry_date': '','conversion_to_base': 1})
        self.endInsertRows()

    def add_item(self, med, row=None):
        for idx, existing in enumerate(self._rows):
            if existing.get('id') == med['id']:
                existing['qty'] = existing.get('qty', 0) + 1
                self.dataChanged.emit(self.index(idx, 0), self.index(idx, self.columnCount() - 1), [Qt.ItemDataRole.DisplayRole])
                return idx

        if row is None or row < 0 or row >= self.rowCount() or self._rows[row].get('id') is not None:
            row = self.rowCount()
            self.beginInsertRows(QModelIndex(), row, row)
            self._rows.append({})
            self.endInsertRows()

        units = med.get('units') or [{'id': None, 'name': 'Unit', 'conversion': 1}]
        selected_unit = units[0]
        self._rows[row] = {
            'id': med['id'],
            'name': med['name'],
            'units': units,
            'unit': selected_unit,
            'purchase_price': 0.0,
            'sale_price': med.get('sale_price', 0.0),
            'qty': 1,
            'batch_no': '',
            'expiry_date': '',
            'conversion_to_base': selected_unit.get('conversion', 1)
        }
        self.dataChanged.emit(self.index(row, 0), self.index(row, self.columnCount() - 1), [Qt.ItemDataRole.DisplayRole])
        return row

    def remove_row(self, row):
        if 0 <= row < self.rowCount():
            self.beginRemoveRows(QModelIndex(), row, row)
            self._rows.pop(row)
            self.endRemoveRows()

    def ensure_empty_row(self):
        if self.rowCount() == 0 or self._rows[-1].get('id') is not None:
            self.append_blank_row()

    def get_cart_items(self):
        items = []
        for row in self._rows:
            if row.get('id') is not None and row.get('qty', 0) > 0:
                items.append({
                    'medicine_id': row['id'],
                    'name': row['name'],
                    'quantity': row['qty'],
                    'purchase_price': row['purchase_price'],
                    'sale_price': row['sale_price'],
                    'batch_no': row['batch_no'],
                    'expiry_date': row['expiry_date'],
                    'unit_id': row.get('unit', {}).get('id'),
                    'conversion_to_base': row.get('unit', {}).get('conversion', 1)
                })
        return items

    def clear(self):
        self.beginResetModel()
        self._rows = []
        self.endResetModel()
        self.append_blank_row()

    def row_data(self, row):
        if 0 <= row < self.rowCount():
            return self._rows[row]
        return {}

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
        self.search_results.setHorizontalHeaderLabels(["Name", "Generic Formula", "Available Stock", "Sale Price"])
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
        if len(text) < 2:
            return

        results = self.controller.search_medicines(text)
        self.current_search_results = results
        self.search_results.setRowCount(len(results))
        for i, r in enumerate(results):
            self.search_results.setItem(i, 0, QTableWidgetItem(r['name']))
            self.search_results.setItem(i, 1, QTableWidgetItem(r['generic_name']))
            stock_item = QTableWidgetItem(r.get('human_stock', str(r.get('stock', 0))))
            stock_item.setForeground(Qt.GlobalColor.red if r.get('stock', 0) <= 0 else Qt.GlobalColor.darkGreen)
            self.search_results.setItem(i, 2, stock_item)
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
        self.pos_controller = POSController()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        header_layout = QHBoxLayout()
        title = QLabel("Fast Stock Entry (Model/View Grid)")
        title.setStyleSheet("font-size: 20px; font-weight: bold;")
        header_layout.addWidget(title)

        self.supplier_combo = QComboBox()
        self.supplier_combo.setMinimumWidth(200)
        self.load_suppliers()
        header_layout.addStretch()
        header_layout.addWidget(QLabel("Supplier:"))
        header_layout.addWidget(self.supplier_combo)
        layout.addLayout(header_layout)

        help_text = QLabel("Press ENTER on 'Item Name' row to search. Press TAB to move to the next editable cell.")
        help_text.setStyleSheet("color: gray; font-style: italic;")
        layout.addWidget(help_text)

        self.cart_model = PurchaseTableModel(self)
        self.cart_model.ensure_empty_row()

        self.cart_table = QTableView()
        self.cart_table.setModel(self.cart_model)
        self.cart_table.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self.cart_table.setSelectionMode(QTableView.SelectionMode.SingleSelection)
        self.cart_table.setEditTriggers(QTableView.EditTrigger.SelectedClicked | QTableView.EditTrigger.EditKeyPressed)
        self.cart_table.verticalHeader().setDefaultSectionSize(32)
        self.cart_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.cart_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.cart_table.setItemDelegateForColumn(2, UnitComboDelegate(self.cart_table))
        self.cart_table.setItemDelegateForColumn(3, ExcelDelegate(self.cart_table))
        self.cart_table.setItemDelegateForColumn(4, ExcelDelegate(self.cart_table))
        self.cart_table.setItemDelegateForColumn(5, ExcelDelegate(self.cart_table))
        self.cart_table.installEventFilter(self)
        self.cart_model.dataChanged.connect(self.on_model_data_changed)

        layout.addWidget(self.cart_table)

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
        self.shortcut_search = QShortcut(QKeySequence("F2"), self)
        self.shortcut_search.activated.connect(self.focus_search_cell)
        self.shortcut_new = QShortcut(QKeySequence("Ctrl+N"), self)
        self.shortcut_new.activated.connect(self.clear_all)
        self.shortcut_save_ctrl = QShortcut(QKeySequence("Ctrl+S"), self)
        self.shortcut_save_ctrl.activated.connect(self.save_purchase)

        self.load_suppliers()

    def eventFilter(self, source, event):
        if source is self.cart_table and event.type() == QEvent.Type.KeyPress:
            row = self.cart_table.currentIndex().row()
            col = self.cart_table.currentIndex().column()
            if event.key() in [Qt.Key.Key_Return, Qt.Key.Key_Enter] and col == 1:
                self.open_search_dialog(row)
                return True
            if event.key() in (Qt.Key.Key_Delete, Qt.Key.Key_Backspace) and row >= 0:
                self.cart_model.remove_row(row)
                self.cart_model.ensure_empty_row()
                self.update_totals()
                return True
        return super().eventFilter(source, event)

    def showEvent(self, event):
        super().showEvent(event)
        self.cart_model.ensure_empty_row()
        if self.cart_model.rowCount() > 0:
            self.cart_table.setCurrentIndex(self.cart_model.index(self.cart_model.rowCount() - 1, 1))
            self.cart_table.setFocus()

    def focus_search_cell(self):
        if self.cart_model.rowCount() == 0:
            self.cart_model.ensure_empty_row()
        self.cart_table.setCurrentIndex(self.cart_model.index(self.cart_model.rowCount() - 1, 1))
        self.cart_table.setFocus()

    def load_suppliers(self):
        self.supplier_combo.clear()
        suppliers = self.purchase_controller.get_all_suppliers()
        for s in suppliers:
            self.supplier_combo.addItem(s['name'], s['id'])

    def clear_all(self):
        reply = QMessageBox.question(self, "Clear All", "Are you sure you want to clear all items?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.cart_model.clear()
            self.update_totals()

    def open_search_dialog(self, row):
        dialog = PurchaseMedicineSearchDialog(self.pos_controller, self)
        if dialog.exec() == QDialog.DialogCode.Accepted and dialog.selected_medicine:
            actual_row = self.cart_model.add_item(dialog.selected_medicine, row)
            self.cart_model.ensure_empty_row()
            self.cart_table.setCurrentIndex(self.cart_model.index(actual_row, 3))
            self.cart_table.edit(self.cart_model.index(actual_row, 3))

    def on_model_data_changed(self, top_left, bottom_right, roles=None):
        self.update_totals()

    def update_totals(self):
        total = 0.0
        for item in self.cart_model.get_cart_items():
            total += item['purchase_price'] * item['quantity']
        self.total_lbl.setText(f"Total Invoice Amount: {total:.2f}")

    def save_purchase(self):
        cart_items = self.cart_model.get_cart_items()
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
            self.cart_model.clear()
            self.update_totals()
        else:
            QMessageBox.warning(self, "Error", msg)
