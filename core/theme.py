GLOBAL_STYLE = """
/* Global Styles for Pharmacy POS - Enterprise Theme */

QWidget {
    background-color: #F8FAFC; /* Light gray/blue app background */
    color: #1E293B; /* Dark slate text */
    font-family: 'Segoe UI', Arial, sans-serif;
    font-size: 14px;
}

/* Base Cards and Containers */
QWidget#card, QFrame#card {
    background-color: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 8px;
}

/* Global Input Fields */
QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox {
    background-color: #FFFFFF;
    border: 1px solid #CBD5E1;
    border-radius: 6px;
    padding: 6px 10px;
    color: #334155;
    min-height: 20px;
}

/* Fix inline editor overflowing in tables */
QTableView QLineEdit, QTableView QSpinBox, QTableView QDoubleSpinBox {
    border: none;
    border-radius: 0px;
    padding: 0px 4px;
    min-height: 0px;
    background-color: transparent;
}

QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus {
    border: 2px solid #0369A1; /* Brand Blue Focus Ring */
    background-color: #FFFFFF;
}

/* Dropdown specific */
QComboBox QAbstractItemView {
    border: 1px solid #CBD5E1;
    background-color: #FFFFFF;
    selection-background-color: #F1F5F9;
    selection-color: #0369A1;
}

/* Global Buttons */
QPushButton {
    background-color: #0369A1; /* Brand Blue */
    color: #FFFFFF;
    border: none;
    border-radius: 8px;
    padding: 10px 16px;
    font-weight: bold;
}
QPushButton:hover {
    background-color: #0284C7;
}
QPushButton:pressed {
    background-color: #075985;
}

/* Secondary/Cancel Buttons (Can be overridden inline if needed) */
QPushButton#secondaryBtn {
    background-color: #E2E8F0;
    color: #475569;
}
QPushButton#secondaryBtn:hover {
    background-color: #CBD5E1;
}

/* Success Buttons */
QPushButton#successBtn {
    background-color: #10B981;
}
QPushButton#successBtn:hover {
    background-color: #059669;
}
QPushButton#successBtn:pressed {
    background-color: #047857;
}

/* Typography */
QLabel#pageTitle {
    font-size: 22px;
    font-weight: bold;
    color: #1E293B;
}
QLabel#sectionTitle {
    font-size: 18px;
    font-weight: bold;
    color: #334155;
}

/* Tables */
QTableWidget, QTableView {
    background-color: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 8px;
    gridline-color: #E2E8F0;
    alternate-background-color: #F8FAFC;
    selection-background-color: #E0F2FE;
    selection-color: #0369A1;
    font-size: 13px; /* Denser text */
    outline: none; /* Removes the default dotted focus border */
}

QTableView::item {
    padding: 2px 5px; /* Tighter padding */
    outline: none;
}

QTableView::item:selected {
    background-color: #E0F2FE;
    color: #0F172A;
}

QTableView::item:focus {
    border: 2px solid #0369A1; /* Excel-style focus border */
    background-color: #F0F9FF;
}

QHeaderView::section {
    background-color: #F1F5F9;
    color: #475569;
    font-weight: bold;
    padding: 6px 8px; /* Tighter header padding */
    border: none;
    border-right: 1px solid #E2E8F0;
    border-bottom: 2px solid #E2E8F0;
}

/* Scrollbars */
QScrollBar:vertical {
    border: none;
    background: #F8FAFC;
    width: 10px;
    border-radius: 5px;
}
QScrollBar::handle:vertical {
    background: #CBD5E1;
    min-height: 20px;
    border-radius: 5px;
}
QScrollBar::handle:vertical:hover {
    background: #94A3B8;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    border: none;
    background: none;
}
"""
