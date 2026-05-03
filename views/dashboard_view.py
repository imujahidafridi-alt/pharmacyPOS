from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame
)
from PyQt6.QtCore import Qt
from controllers.reports_controller import ReportsController
import matplotlib
matplotlib.use('QtAgg')
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class DashboardView(QWidget):
    def __init__(self):
        super().__init__()
        self.controller = ReportsController()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        title = QLabel("Dashboard")
        title.setObjectName("pageTitle")
        layout.addWidget(title)
        
        # Cards Layout
        cards_layout = QHBoxLayout()
        
        self.sales_val_lbl = QLabel("Rs. 0.00")
        sales_card = self.create_card("Today's Sales", self.sales_val_lbl, "#3498db")
        cards_layout.addWidget(sales_card)
        
        self.stock_val_lbl = QLabel("0")
        stock_card = self.create_card("Low Stock Items", self.stock_val_lbl, "#e74c3c")
        cards_layout.addWidget(stock_card)
        
        self.meds_val_lbl = QLabel("0")
        meds_card = self.create_card("Total Medicines", self.meds_val_lbl, "#2ecc71")
        cards_layout.addWidget(meds_card)
        
        self.expiry_val_lbl = QLabel("0")
        expiry_card = self.create_card("Expiring Soon (<30d)", self.expiry_val_lbl, "#f39c12")
        cards_layout.addWidget(expiry_card)
        
        layout.addLayout(cards_layout)
        
        # Charts Layout
        self.charts_layout = QHBoxLayout()
        self.charts_layout.setSpacing(20)
        
        # We will populate these inside load_data
        self.trend_canvas = None
        self.top_meds_canvas = None
        
        layout.addLayout(self.charts_layout)
        layout.addStretch()
        
        self.load_data()

    def create_card(self, title_text, value_label, color):
        frame = QFrame()
        frame.setObjectName("card")
        frame.setStyleSheet(f"""
            QFrame {{
                background-color: {color};
                border-radius: 10px;
                padding: 20px;
                color: white;
            }}
        """)
        
        vbox = QVBoxLayout(frame)
        
        title = QLabel(title_text)
        title.setStyleSheet("font-size: 16px; background-color: transparent;")
        vbox.addWidget(title)
        
        value_label.setStyleSheet("font-size: 28px; font-weight: bold; background-color: transparent;")
        vbox.addWidget(value_label)
        
        return frame

    def load_data(self):
        metrics = self.controller.get_dashboard_metrics()
        self.sales_val_lbl.setText(f"Rs. {metrics['total_sales_today']:.2f}")
        self.stock_val_lbl.setText(str(metrics['low_stock_count']))
        self.meds_val_lbl.setText(str(metrics['total_medicines']))
        self.expiry_val_lbl.setText(str(metrics.get('near_expiry_count', 0)))
        
        self.render_charts()

    def render_charts(self):
        # Clear existing charts if any
        if self.trend_canvas:
            self.charts_layout.removeWidget(self.trend_canvas)
            self.trend_canvas.deleteLater()
        if self.top_meds_canvas:
            self.charts_layout.removeWidget(self.top_meds_canvas)
            self.top_meds_canvas.deleteLater()
            
        # 1. Sales Trend Chart
        trend_data = self.controller.get_sales_trend(7)
        dates = [d['date'][-5:] for d in trend_data] # Just MM-DD
        totals = [d['total'] for d in trend_data]
        
        fig1 = Figure(figsize=(6, 4), dpi=100)
        ax1 = fig1.add_subplot(111)
        ax1.plot(dates, totals, marker='o', linestyle='-', color='#0369A1', linewidth=2)
        ax1.fill_between(dates, totals, alpha=0.1, color='#0369A1')
        ax1.set_title("7-Day Sales Trend", fontsize=12, fontweight='bold', color='#334155')
        ax1.set_ylabel("Sales (Rs)", fontsize=10, color='#64748B')
        ax1.tick_params(axis='x', colors='#64748B', rotation=45)
        ax1.tick_params(axis='y', colors='#64748B')
        ax1.spines['top'].set_visible(False)
        ax1.spines['right'].set_visible(False)
        ax1.spines['left'].set_color('#CBD5E1')
        ax1.spines['bottom'].set_color('#CBD5E1')
        fig1.tight_layout()
        
        self.trend_canvas = FigureCanvas(fig1)
        self.trend_canvas.setStyleSheet("background-color: white; border: 1px solid #E2E8F0; border-radius: 8px;")
        
        # 2. Top Selling Medicines Chart
        top_meds = self.controller.get_top_medicines(5)
        med_names = [m['name'][:12] for m in top_meds] # Truncate long names
        med_qtys = [m['quantity'] for m in top_meds]
        
        fig2 = Figure(figsize=(6, 4), dpi=100)
        ax2 = fig2.add_subplot(111)
        bars = ax2.barh(med_names, med_qtys, color='#10B981')
        ax2.set_title("Top 5 Selling Medicines", fontsize=12, fontweight='bold', color='#334155')
        ax2.set_xlabel("Quantity Sold", fontsize=10, color='#64748B')
        ax2.tick_params(axis='x', colors='#64748B')
        ax2.tick_params(axis='y', colors='#64748B')
        ax2.spines['top'].set_visible(False)
        ax2.spines['right'].set_visible(False)
        ax2.spines['left'].set_color('#CBD5E1')
        ax2.spines['bottom'].set_color('#CBD5E1')
        
        # Add labels to the end of bars
        for bar in bars:
            width = bar.get_width()
            ax2.text(width, bar.get_y() + bar.get_height()/2, f' {int(width)}', 
                    va='center', ha='left', fontsize=9, color='#334155')
                    
        fig2.tight_layout()
        
        self.top_meds_canvas = FigureCanvas(fig2)
        self.top_meds_canvas.setStyleSheet("background-color: white; border: 1px solid #E2E8F0; border-radius: 8px;")
        
        # Add to layout
        self.charts_layout.addWidget(self.trend_canvas)
        self.charts_layout.addWidget(self.top_meds_canvas)
