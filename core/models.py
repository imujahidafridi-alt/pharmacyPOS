from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship, declarative_base
import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, nullable=False)

class AuditLog(Base):
    __tablename__ = 'audit_logs'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    action = Column(String, nullable=False)
    details = Column(String)
    timestamp = Column(String, default=lambda: datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    # Relationships
    user = relationship("User")

class Medicine(Base):
    __tablename__ = 'medicines'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    generic_name = Column(String)
    category = Column(String)
    sale_price = Column(Float, nullable=False)
    units_per_box = Column(Integer, default=1)
    is_discountable = Column(Integer, default=1) # 1 for True, 0 for False (SQLite compatibility)

    # Relationships
    inventory = relationship("Inventory", back_populates="medicine")
    sale_items = relationship("SaleItem", back_populates="medicine")
    purchase_items = relationship("PurchaseItem", back_populates="medicine")

class Supplier(Base):
    __tablename__ = 'suppliers'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    phone = Column(String)
    address = Column(String)

    # Relationships
    inventory = relationship("Inventory", back_populates="supplier")
    purchases = relationship("Purchase", back_populates="supplier")

class Customer(Base):
    __tablename__ = 'customers'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    phone = Column(String)
    address = Column(String)
    created_at = Column(String, default=lambda: datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    # Relationships
    ledgers = relationship("CustomerLedger", back_populates="customer")
    sales = relationship("Sale", back_populates="customer")

class CustomerLedger(Base):
    __tablename__ = 'customer_ledgers'

    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(Integer, ForeignKey('customers.id'), nullable=False)
    date = Column(String, nullable=False)
    transaction_type = Column(String, nullable=False) # 'SALE' or 'PAYMENT'
    amount = Column(Float, nullable=False) # Positive for SALE (increases debt), Negative for PAYMENT
    sale_id = Column(Integer, ForeignKey('sales.id'), nullable=True)
    description = Column(String)

    # Relationships
    customer = relationship("Customer", back_populates="ledgers")
    sale = relationship("Sale", back_populates="ledger_entries")

class Inventory(Base):
    __tablename__ = 'inventory'

    id = Column(Integer, primary_key=True, autoincrement=True)
    medicine_id = Column(Integer, ForeignKey('medicines.id'), nullable=False)
    batch_no = Column(String, nullable=False)
    expiry_date = Column(String, nullable=False)
    quantity = Column(Integer, nullable=False, default=0)
    purchase_price = Column(Float, nullable=False)
    supplier_id = Column(Integer, ForeignKey('suppliers.id'))

    # Relationships
    medicine = relationship("Medicine", back_populates="inventory")
    supplier = relationship("Supplier", back_populates="inventory")

class Sale(Base):
    __tablename__ = 'sales'

    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(String, nullable=False)
    total_amount = Column(Float, nullable=False)
    discount = Column(Float, default=0)
    payment_method = Column(String, nullable=False)
    
    # Khata fields
    customer_id = Column(Integer, ForeignKey('customers.id'), nullable=True)
    amount_paid = Column(Float, default=0)

    # Relationships
    items = relationship("SaleItem", back_populates="sale")
    customer = relationship("Customer", back_populates="sales")
    ledger_entries = relationship("CustomerLedger", back_populates="sale")

class SaleItem(Base):
    __tablename__ = 'sale_items'

    id = Column(Integer, primary_key=True, autoincrement=True)
    sale_id = Column(Integer, ForeignKey('sales.id'), nullable=False)
    medicine_id = Column(Integer, ForeignKey('medicines.id'), nullable=False)
    quantity = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)

    # Relationships
    sale = relationship("Sale", back_populates="items")
    medicine = relationship("Medicine", back_populates="sale_items")

class Purchase(Base):
    __tablename__ = 'purchases'

    id = Column(Integer, primary_key=True, autoincrement=True)
    supplier_id = Column(Integer, ForeignKey('suppliers.id'), nullable=False)
    date = Column(String, nullable=False)
    total_amount = Column(Float, nullable=False)

    # Relationships
    supplier = relationship("Supplier", back_populates="purchases")
    items = relationship("PurchaseItem", back_populates="purchase")

class PurchaseItem(Base):
    __tablename__ = 'purchase_items'

    id = Column(Integer, primary_key=True, autoincrement=True)
    purchase_id = Column(Integer, ForeignKey('purchases.id'), nullable=False)
    medicine_id = Column(Integer, ForeignKey('medicines.id'), nullable=False)
    batch_no = Column(String, nullable=False)
    expiry_date = Column(String, nullable=False)
    quantity = Column(Integer, nullable=False)
    purchase_price = Column(Float, nullable=False)

    # Relationships
    purchase = relationship("Purchase", back_populates="items")
    medicine = relationship("Medicine", back_populates="purchase_items")
