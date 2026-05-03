from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, 
    QTableWidgetItem, QLabel, QLineEdit, QMessageBox, QComboBox, QHeaderView, QListWidget, QFormLayout,
    QDialog, QStyledItemDelegate, QApplication
)
from PyQt6.QtCore import Qt, QEvent
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
            # Simulate Tab key press to move right and wrap to next row
            tab_event = QKeyEvent(QEvent.Type.KeyPress, Qt.Key.Key_Tab, Qt.KeyboardModifier.NoModifier)
            QApplication.sendEvent(editor, tab_event)
            return True
        return super().eventFilter(editor, event)

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
        self.search_results.setStyleSheet("""
            QTableWidget {
                outline: none;
            }
            QTableWidget::item {
                outline: none;
            }
            QTableWidget::item:selected {
                background-color: #0369A1;
                color: #FFFFFF;
                font-weight: bold;
                border: none;
            }
        """)
        self.search_results.cellDoubleClicked.connect(self.select_item_from_click)
        layout.addWidget(self.search_results)
        
        # Install event filters after all widgets are created
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
            
            stock_item = QTableWidgetItem(str(r.get('stock', 0)))
            if r.get('stock', 0) <= 0:
                stock_item.setForeground(Qt.GlobalColor.red)
            else:
                stock_item.setForeground(Qt.GlobalColor.darkGreen)
                
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
        
        # Left side: Spreadsheet Cart
        left_layout = QVBoxLayout()
        
        title_lbl = QLabel("POS Billing (Excel-Style Grid)")
        title_lbl.setObjectName("pageTitle")
        left_layout.addWidget(title_lbl)
        
        self.cart_table = QTableWidget()
        self.cart_table.setColumnCount(5)
        self.cart_table.setHorizontalHeaderLabels(["ID", "Item Name (Enter to Search)", "Retail Price", "Qty", "Total"])
        self.cart_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.cart_table.setColumnHidden(0, True) # Hide ID column
        self.cart_table.verticalHeader().setDefaultSectionSize(32)
        
        # Apply custom delegate for auto-select and Enter->Tab behavior
        self.delegate = ExcelDelegate(self.cart_table)
        self.cart_table.setItemDelegateForColumn(2, self.delegate)
        self.cart_table.setItemDelegateForColumn(3, self.delegate)
        
        self.cart_table.keyPressEvent = self.table_key_press
        self.cart_table.itemChanged.connect(self.on_item_changed)
        
        left_layout.addWidget(self.cart_table)
        layout.addLayout(left_layout, stretch=2)
        
        # Right side: Checkout panel
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
        
        self.checkout_btn = QPushButton("Complete Sale (F12)")
        self.checkout_btn.setObjectName("successBtn")
        self.checkout_btn.clicked.connect(self.process_sale)
        right_layout.addWidget(self.checkout_btn)
        
        right_layout.addStretch()
        layout.addLayout(right_layout, stretch=1)

        # Shortcuts
        self.shortcut_discount = QShortcut(QKeySequence("F3"), self)
        self.shortcut_discount.activated.connect(self.focus_discount)

        self.shortcut_amount = QShortcut(QKeySequence("F4"), self)
        self.shortcut_amount.activated.connect(self.focus_amount)

        self.shortcut_checkout = QShortcut(QKeySequence("F12"), self)
        self.shortcut_checkout.activated.connect(self.process_sale)
        
        self.load_customers()
        self.ensure_empty_row()

    def showEvent(self, event):
        super().showEvent(event)
        self.focus_empty_row()
        
    def focus_empty_row(self):
        row_count = self.cart_table.rowCount()
        if row_count > 0:
            self.cart_table.setCurrentCell(row_count - 1, 1)
            self.cart_table.setFocus()

    def load_customers(self):
        self.customer_dropdown.clear()
        self.customer_dropdown.addItem("Walk-in Customer (None)", None)
        customers = self.customers_controller.get_all_customers()
        for c in customers:
            self.customer_dropdown.addItem(f"{c['name']} ({c['phone']})", c['id'])

    def load_data(self):
        self.load_customers()

    def table_key_press(self, event):
        row = self.cart_table.currentRow()
        col = self.cart_table.currentColumn()
        
        if event.key() in [Qt.Key.Key_Return, Qt.Key.Key_Enter]:
            if col == 1:
                self.open_search_dialog(row)
                return
                
        type(self.cart_table).keyPressEvent(self.cart_table, event)

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
            for col in range(5):
                it = QTableWidgetItem("")
                if col in [0, 1, 4]:
                    it.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
                else:
                    it.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsEditable)
                self.cart_table.setItem(row_count, col, it)
        self.cart_table.blockSignals(False)

    def clear_row(self, row):
        self.cart_table.blockSignals(True)
        for col in range(5):
            if self.cart_table.item(row, col):
                self.cart_table.item(row, col).setText("")
        self.cart_table.blockSignals(False)

    def open_search_dialog(self, row):
        dialog = MedicineSearchDialog(self.controller, self)
        if dialog.exec() == QDialog.DialogCode.Accepted and dialog.selected_medicine:
            med = dialog.selected_medicine
            
            # Check for duplicates
            for r in range(self.cart_table.rowCount()):
                if r != row:
                    id_item = self.cart_table.item(r, 0)
                    if id_item and id_item.text() == str(med['id']):
                        qty_item = self.cart_table.item(r, 3)
                        current_qty = int(qty_item.text()) if qty_item.text() else 0
                        qty_item.setText(str(current_qty + 1))
                        
                        self.clear_row(row)
                        self.recalculate_row(r)
                        self.cart_table.setCurrentCell(r, 3) # Focus qty of merged row
                        return
            
            self.cart_table.blockSignals(True)
            self.cart_table.setItem(row, 0, QTableWidgetItem(str(med['id'])))
            self.cart_table.setItem(row, 1, QTableWidgetItem(med['name']))
            self.cart_table.setItem(row, 2, QTableWidgetItem(str(med['sale_price'])))
            self.cart_table.setItem(row, 3, QTableWidgetItem("1"))
            self.cart_table.setItem(row, 4, QTableWidgetItem(str(med['sale_price'])))
            
            # Store is_discountable flag
            self.cart_table.item(row, 0).setData(Qt.ItemDataRole.UserRole, med.get('is_discountable', 1))
            self.cart_table.blockSignals(False)
            
            self.recalculate_row(row)
            self.ensure_empty_row()
            
            # Jump to Price editing
            self.cart_table.setCurrentCell(row, 2)
            self.cart_table.editItem(self.cart_table.item(row, 2))

    def on_item_changed(self, item):
        if item.column() in [2, 3]: # Price or Qty
            self.recalculate_row(item.row())

    def recalculate_row(self, row):
        self.cart_table.blockSignals(True)
        try:
            price_text = self.cart_table.item(row, 2).text()
            qty_text = self.cart_table.item(row, 3).text()
            
            if not price_text or not qty_text:
                self.cart_table.blockSignals(False)
                return
                
            price = float(price_text)
            qty = int(qty_text)
            
            id_item = self.cart_table.item(row, 0)
            if id_item and id_item.text():
                med_id = int(id_item.text())
                stock = self.controller.get_stock_for_medicine(med_id)
                if qty > stock:
                    QMessageBox.warning(self, "Out of Stock", f"Only {stock} items available.")
                    qty = stock
                    self.cart_table.item(row, 3).setText(str(qty))
                    
            total = price * qty
            self.cart_table.item(row, 4).setText(f"{total:.2f}")
            self.ensure_empty_row()
        except ValueError:
            pass
        finally:
            self.cart_table.blockSignals(False)
            self.update_totals()

    def update_totals(self):
        subtotal = 0.0
        discountable_subtotal = 0.0
        for r in range(self.cart_table.rowCount()):
            id_item = self.cart_table.item(r, 0)
            if id_item and id_item.text():
                try:
                    price = float(self.cart_table.item(r, 2).text())
                    qty = int(self.cart_table.item(r, 3).text())
                    is_discountable = id_item.data(Qt.ItemDataRole.UserRole)
                    
                    row_tot = price * qty
                    subtotal += row_tot
                    if is_discountable:
                        discountable_subtotal += row_tot
                except (ValueError, AttributeError):
                    pass
                    
        try:
            discount_str = self.discount_input.text().strip()
            discount_val = 0.0
            
            if discount_str:
                if discount_str.endswith('%'):
                    perc = float(discount_str.rstrip('%'))
                    discount_val = discountable_subtotal * (perc / 100.0)
                else:
                    discount_val = float(discount_str)
                    
            if discount_val > discountable_subtotal:
                discount_val = discountable_subtotal
                
            total = subtotal - discount_val
            
            self.subtotal_lbl.setText(f"{subtotal:.2f}")
            self.total_lbl.setText(f"{total:.2f}")
            if not self.amount_paid_input.isReadOnly():
                self.amount_paid_input.setText(f"{total:.2f}")
        except ValueError:
            pass

    def focus_discount(self):
        self.discount_input.setFocus()
        self.discount_input.selectAll()

    def focus_amount(self):
        self.amount_paid_input.setFocus()
        self.amount_paid_input.selectAll()

    def on_payment_method_changed(self, method):
        if method == "Credit (Khata)":
            self.amount_paid_input.setText("0.00")
            self.amount_paid_input.setReadOnly(True)
        else:
            self.amount_paid_input.setReadOnly(False)
            self.update_totals()

    def process_sale(self):
        cart_items = []
        for r in range(self.cart_table.rowCount()):
            id_item = self.cart_table.item(r, 0)
            if id_item and id_item.text():
                try:
                    med_id = int(id_item.text())
                    name = self.cart_table.item(r, 1).text()
                    qty = int(self.cart_table.item(r, 3).text())
                    price = float(self.cart_table.item(r, 2).text())
                    if qty > 0:
                        cart_items.append({
                            'medicine_id': med_id,
                            'name': name,
                            'quantity': qty,
                            'price': price
                        })
                except ValueError:
                    pass
                    
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
            self.cart_table.blockSignals(True)
            self.cart_table.setRowCount(0)
            self.ensure_empty_row()
            self.cart_table.blockSignals(False)
            
            self.customer_dropdown.setCurrentIndex(0)
            self.discount_input.setText("0")
            self.amount_paid_input.setText("0.00")
            self.update_totals()
        else:
            QMessageBox.warning(self, "Error", msg)
