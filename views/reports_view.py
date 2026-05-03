from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, 
    QTableWidgetItem, QHeaderView, QLabel, QTabWidget
)
from controllers.reports_controller import ReportsController

class ReportsView(QWidget):
    def __init__(self):
        super().__init__()
        self.controller = ReportsController()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        
        title = QLabel("Reports")
        title.setStyleSheet("font-size: 20px; font-weight: bold;")
        layout.addWidget(title)
        
        self.tabs = QTabWidget()
        
        # Sales Tab
        self.sales_tab = QWidget()
        sales_layout = QVBoxLayout(self.sales_tab)
        self.sales_table = QTableWidget()
        self.sales_table.setColumnCount(5)
        self.sales_table.setHorizontalHeaderLabels(["ID", "Date", "Total Amount", "Discount", "Payment Method"])
        self.sales_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        sales_layout.addWidget(self.sales_table)
        self.tabs.addTab(self.sales_tab, "Sales Report")
        
        # Stock Tab
        self.stock_tab = QWidget()
        stock_layout = QVBoxLayout(self.stock_tab)
        self.stock_table = QTableWidget()
        self.stock_table.setColumnCount(4)
        self.stock_table.setHorizontalHeaderLabels(["Medicine Name", "Batch No", "Expiry Date", "Quantity"])
        self.stock_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        stock_layout.addWidget(self.stock_table)
        self.tabs.addTab(self.stock_tab, "Stock Report")
        
        layout.addWidget(self.tabs)
        
        # Load Data
        self.load_data()

    def load_data(self):
        # Load Sales
        sales = self.controller.get_sales_report()
        self.sales_table.setRowCount(len(sales))
        for i, s in enumerate(sales):
            self.sales_table.setItem(i, 0, QTableWidgetItem(str(s['id'])))
            self.sales_table.setItem(i, 1, QTableWidgetItem(s['date']))
            self.sales_table.setItem(i, 2, QTableWidgetItem(str(s['total_amount'])))
            self.sales_table.setItem(i, 3, QTableWidgetItem(str(s['discount'])))
            self.sales_table.setItem(i, 4, QTableWidgetItem(s['payment_method']))
            
        # Load Stock
        stock = self.controller.get_stock_report()
        self.stock_table.setRowCount(len(stock))
        for i, s in enumerate(stock):
            self.stock_table.setItem(i, 0, QTableWidgetItem(s['name']))
            self.stock_table.setItem(i, 1, QTableWidgetItem(s['batch_no']))
            self.stock_table.setItem(i, 2, QTableWidgetItem(s['expiry_date']))
            self.stock_table.setItem(i, 3, QTableWidgetItem(str(s['quantity'])))
