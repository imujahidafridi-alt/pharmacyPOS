from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableView,
    QLabel, QLineEdit, QMessageBox, QComboBox, QHeaderView, QFormLayout,
    QDialog, QStyledItemDelegate, QApplication, QTableWidget, QTableWidgetItem
)
from PyQt6.QtCore import Qt, QEvent, QAbstractTableModel, QModelIndex
from PyQt6.QtGui import QKeySequence, QShortcut, QKeyEvent
from controllers.pos_controller import POSController
from controllers.customers_controller import CustomersController

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

class CartTableModel(QAbstractTableModel):
    headers = ["Item Name", "Unit", "Sale Price", "Qty", "Total"]

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
                return row.get('name', '')
            if col == 1:
                return row.get('unit', {}).get('name', '')
            if col == 2:
                return f"{row.get('price', 0.0):.2f}" if row.get('id') is not None else ""
            if col == 3:
                return str(row.get('qty', '')) if row.get('id') is not None else ""
            if col == 4:
                return f"{row.get('qty', 0) * row.get('price', 0.0):.2f}" if row.get('id') is not None else ""

        if role == Qt.ItemDataRole.EditRole:
            if col == 1:
                return row.get('unit', {})
            if col == 2:
                return row.get('price', 0.0)
            if col == 3:
                return row.get('qty', 0)

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
        if row.get('id') is not None and index.column() in [1, 2, 3]:
            flags |= Qt.ItemFlag.ItemIsEditable
        return flags

    def setData(self, index, value, role=Qt.ItemDataRole.EditRole):
        if role != Qt.ItemDataRole.EditRole or not index.isValid():
            return False

        row = self._rows[index.row()]
        col = index.column()

        if col == 2:
            try:
                row['price'] = float(value)
            except (ValueError, TypeError):
                return False
        elif col == 3:
            try:
                row['qty'] = int(value)
            except (ValueError, TypeError):
                return False
        elif col == 1 and isinstance(value, dict):
            row['unit'] = value
            row['price'] = row.get('base_price', 0.0) * value.get('conversion', 1)
        else:
            return False

        self.dataChanged.emit(self.index(index.row(), 0), self.index(index.row(), self.columnCount() - 1), [Qt.ItemDataRole.DisplayRole])
        return True

    def append_blank_row(self):
        self.beginInsertRows(QModelIndex(), self.rowCount(), self.rowCount())
        self._rows.append({'id': None, 'name': '', 'units': [], 'unit': {}, 'base_price': 0.0, 'price': 0.0, 'qty': 0, 'is_discountable': 1})
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
            'base_price': med['sale_price'],
            'price': med['sale_price'] * selected_unit.get('conversion', 1),
            'qty': 1,
            'is_discountable': med.get('is_discountable', 1)
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
                    'price': row['price'],
                    'unit_id': row.get('unit', {}).get('id'),
                    'conversion_to_base': row.get('unit', {}).get('conversion', 1),
                    'is_discountable': row.get('is_discountable', 1)
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

class MedicineSearchDialog(QDialog):
    def __init__(self, controller, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.selected_medicine = None
        self.current_search_results = []
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Search Medicine")
        self.resize(700, 400)
        layout = QVBoxLayout(self)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Start typing to search medicine...")
        self.search_input.textChanged.connect(self.search_medicines)
        layout.addWidget(self.search_input)

        self.search_results = QTableWidget()
        self.search_results.setColumnCount(4)
        self.search_results.setHorizontalHeaderLabels(["Name", "Generic Formula", "Available Stock", "Price (Rs)"])
        self.search_results.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.search_results.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.search_results.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.search_results.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.search_results.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.search_results.setAlternatingRowColors(True)
        self.search_results.verticalHeader().setDefaultSectionSize(30)
        self.search_results.verticalHeader().setVisible(False)
        self.search_results.setStyleSheet("QTableWidget { outline: none; } QTableWidget::item { outline: none; } QTableWidget::item:selected { background-color: #0369A1; color: #FFFFFF; font-weight: bold; border: none; }")
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

class POSView(QWidget):
    def __init__(self):
        super().__init__()
        self.controller = POSController()
        self.customers_controller = CustomersController()
        self.init_ui()

    def init_ui(self):
        layout = QHBoxLayout(self)

        left_layout = QVBoxLayout()
        title_lbl = QLabel("POS Billing (Excel-Style Grid)")
        title_lbl.setObjectName("pageTitle")
        left_layout.addWidget(title_lbl)

        help_text = QLabel("Press ENTER on the Item Name cell to search. Use arrow keys to navigate and hit ENTER to add the selected medicine.")
        help_text.setStyleSheet("color: gray; font-size: 12px; font-style: italic;")
        left_layout.addWidget(help_text)

        self.cart_model = CartTableModel(self)
        self.cart_model.ensure_empty_row()

        self.cart_table = QTableView()
        self.cart_table.setModel(self.cart_model)
        self.cart_table.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self.cart_table.setSelectionMode(QTableView.SelectionMode.SingleSelection)
        self.cart_table.setEditTriggers(QTableView.EditTrigger.SelectedClicked | QTableView.EditTrigger.EditKeyPressed)
        self.cart_table.verticalHeader().setDefaultSectionSize(32)
        self.cart_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.cart_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.cart_table.setItemDelegateForColumn(1, UnitComboDelegate(self.cart_table))
        self.cart_table.setItemDelegateForColumn(2, ExcelDelegate(self.cart_table))
        self.cart_table.setItemDelegateForColumn(3, ExcelDelegate(self.cart_table))
        self.cart_table.installEventFilter(self)
        self.cart_model.dataChanged.connect(self.on_model_data_changed)

        left_layout.addWidget(self.cart_table)
        layout.addLayout(left_layout, stretch=2)

        right_layout = QVBoxLayout()
        title = QLabel("Checkout")
        title.setObjectName("sectionTitle")
        right_layout.addWidget(title)

        form_layout = QFormLayout()
        self.customer_dropdown = QComboBox()
        self.customer_dropdown.addItem("Walk-in Customer (None)", None)
        form_layout.addRow("Customer:", self.customer_dropdown)
        self.subtotal_lbl = QLabel("0.00")
        form_layout.addRow("Subtotal:", self.subtotal_lbl)
        self.discount_input = QLineEdit("0")
        self.discount_input.setPlaceholderText("Amount or % (Press F3)")
        self.discount_input.textChanged.connect(self.update_totals)
        form_layout.addRow("Discount:", self.discount_input)
        self.total_lbl = QLabel("0.00")
        self.total_lbl.setStyleSheet("font-size: 18px; font-weight: bold; color: green;")
        form_layout.addRow("Grand Total:", self.total_lbl)
        self.payment_method = QComboBox()
        self.payment_method.addItems(["Cash", "Card", "Easypaisa/JazzCash", "Credit (Khata)"])
        self.payment_method.currentTextChanged.connect(self.on_payment_method_changed)
        form_layout.addRow("Payment Method:", self.payment_method)
        self.amount_paid_input = QLineEdit("0.00")
        self.amount_paid_input.setPlaceholderText("Press F4")
        form_layout.addRow("Amount Paid (Rs):", self.amount_paid_input)
        right_layout.addLayout(form_layout)

        clear_btn = QPushButton("Clear Cart")
        clear_btn.setStyleSheet("background-color: #e74c3c; color: white; padding: 10px; font-size: 14px; font-weight: bold;")
        clear_btn.clicked.connect(self.clear_all)
        right_layout.addWidget(clear_btn)

        self.checkout_btn = QPushButton("Complete Sale (F12)")
        self.checkout_btn.setObjectName("successBtn")
        self.checkout_btn.clicked.connect(self.process_sale)
        right_layout.addWidget(self.checkout_btn)
        right_layout.addStretch()
        layout.addLayout(right_layout, stretch=1)

        self.shortcut_discount = QShortcut(QKeySequence("F3"), self)
        self.shortcut_discount.activated.connect(self.focus_discount)
        self.shortcut_amount = QShortcut(QKeySequence("F4"), self)
        self.shortcut_amount.activated.connect(self.focus_amount)
        self.shortcut_checkout = QShortcut(QKeySequence("F12"), self)
        self.shortcut_checkout.activated.connect(self.process_sale)
        self.shortcut_new_sale = QShortcut(QKeySequence("Ctrl+N"), self)
        self.shortcut_new_sale.activated.connect(self.clear_all)
        self.shortcut_save_sale = QShortcut(QKeySequence("Ctrl+S"), self)
        self.shortcut_save_sale.activated.connect(self.process_sale)

        self.load_customers()

    def eventFilter(self, source, event):
        if source is self.cart_table and event.type() == QEvent.Type.KeyPress:
            row = self.cart_table.currentIndex().row()
            col = self.cart_table.currentIndex().column()
            if event.key() in [Qt.Key.Key_Return, Qt.Key.Key_Enter] and col == 0:
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
        self.focus_item_name()

    def load_customers(self):
        self.customer_dropdown.clear()
        self.customer_dropdown.addItem("Walk-in Customer (None)", None)
        customers = self.customers_controller.get_all_customers()
        for c in customers:
            self.customer_dropdown.addItem(f"{c['name']} ({c['phone']})", c['id'])

    def clear_all(self):
        reply = QMessageBox.question(self, "Clear Cart", "Are you sure you want to clear the POS screen?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.cart_model.clear()
            self.update_totals()
            self.discount_input.setText("0")
            self.amount_paid_input.setText("0.00")

    def open_search_dialog(self, row):
        dialog = MedicineSearchDialog(self.controller, self)
        if dialog.exec() == QDialog.DialogCode.Accepted and dialog.selected_medicine:
            actual_row = self.cart_model.add_item(dialog.selected_medicine, row)
            self.cart_model.ensure_empty_row()
            self.cart_table.setCurrentIndex(self.cart_model.index(actual_row, 3))
            self.cart_table.edit(self.cart_model.index(actual_row, 3))

    def on_model_data_changed(self, top_left, bottom_right, roles=None):
        self.update_totals()

    def focus_discount(self):
        self.discount_input.setFocus()
        self.discount_input.selectAll()

    def focus_amount(self):
        self.amount_paid_input.setFocus()
        self.amount_paid_input.selectAll()

    def focus_item_name(self):
        if self.cart_model.rowCount() == 0:
            self.cart_model.ensure_empty_row()
        last_row = self.cart_model.rowCount() - 1
        self.cart_table.setCurrentIndex(self.cart_model.index(last_row, 0))
        self.cart_table.setFocus()

    def on_payment_method_changed(self, method):
        if method == "Credit (Khata)":
            self.amount_paid_input.setText("0.00")
            self.amount_paid_input.setReadOnly(True)
        else:
            self.amount_paid_input.setReadOnly(False)
            self.update_totals()

    def process_sale(self):
        cart_items = self.cart_model.get_cart_items()
        if not cart_items:
            QMessageBox.warning(self, "Empty Cart", "Please add items to cart before checkout.")
            return

        try:
            discount = float(self.discount_input.text() or 0)
            amount_paid = float(self.amount_paid_input.text() or 0)
        except ValueError:
            QMessageBox.warning(self, "Invalid Input", "Discount and Amount Paid must be numbers.")
            return

        payment_method = self.payment_method.currentText()
        customer_id = self.customer_dropdown.currentData()

        if payment_method == "Credit (Khata)" and not customer_id:
            QMessageBox.warning(self, "Customer Required", "Please select a customer for Credit (Khata) sales.")
            return

        success, msg = self.controller.process_sale(cart_items, discount, payment_method, customer_id, amount_paid)
        if success:
            QMessageBox.information(self, "Success", msg)
            self.cart_model.clear()
            self.customer_dropdown.setCurrentIndex(0)
            self.discount_input.setText("0")
            self.amount_paid_input.setText("0.00")
            self.update_totals()
        else:
            QMessageBox.warning(self, "Error", msg)

    def update_totals(self):
        subtotal = 0.0
        for item in self.cart_model.get_cart_items():
            subtotal += item['price'] * item['quantity']

        discount_val = 0.0
        discount_str = self.discount_input.text().strip()
        try:
            if discount_str:
                if discount_str.endswith('%'):
                    perc = float(discount_str.rstrip('%'))
                    discount_val = subtotal * (perc / 100.0)
                else:
                    discount_val = float(discount_str)
            if discount_val > subtotal:
                discount_val = subtotal
        except ValueError:
            discount_val = 0.0

        total = subtotal - discount_val
        self.subtotal_lbl.setText(f"{subtotal:.2f}")
        self.total_lbl.setText(f"{total:.2f}")
        if not self.amount_paid_input.isReadOnly():
            self.amount_paid_input.setText(f"{total:.2f}")
