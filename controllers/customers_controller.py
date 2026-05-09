from core.database import get_db_session
from core.models import Customer, CustomerLedger
from sqlalchemy import func
import datetime

class CustomersController:
    """Handles customers and Khata (credit) logic."""

    def get_all_customers(self):
        with get_db_session() as db:
            # We need customer info along with their total balance
            customers = db.query(Customer).all()
            result = []
            for c in customers:
                # Calculate balance: sum of ledger amounts
                balance = db.query(func.sum(CustomerLedger.amount)).filter(CustomerLedger.customer_id == c.id).scalar()
                balance = balance if balance else 0.0
                
                result.append({
                    "id": c.id,
                    "name": c.name,
                    "phone": c.phone,
                    "address": c.address,
                    "balance": balance
                })
            return result

    def add_customer(self, name, phone, address):
        if not name:
            return False, "Customer name is required."
            
        with get_db_session() as db:
            try:
                customer = Customer(name=name, phone=phone, address=address)
                db.add(customer)
                db.commit()
                return True, "Customer added successfully."
            except Exception as e:
                db.rollback()
                return False, f"Error adding customer: {e}"

    def get_ledger(self, customer_id):
        with get_db_session() as db:
            ledgers = db.query(CustomerLedger).filter(CustomerLedger.customer_id == customer_id).order_by(CustomerLedger.date.asc()).all()
            return [{
                "id": l.id,
                "date": l.date,
                "transaction_type": l.transaction_type,
                "amount": l.amount,
                "description": l.description
            } for l in ledgers]

    def receive_payment(self, customer_id, amount):
        if not amount or float(amount) <= 0:
            return False, "Invalid payment amount."
            
        amount = float(amount)
        date_str = datetime.datetime.now()
        
        with get_db_session() as db:
            try:
                # Validate against current balance
                current_balance = db.query(func.sum(CustomerLedger.amount)).filter(CustomerLedger.customer_id == customer_id).scalar()
                current_balance = current_balance if current_balance else 0.0
                
                if current_balance <= 0:
                    return False, "Customer has no outstanding balance to pay."
                    
                if amount > current_balance:
                    return False, f"Payment amount (Rs. {amount:.2f}) cannot exceed the total outstanding balance (Rs. {current_balance:.2f})."

                payment_entry = CustomerLedger(
                    customer_id=customer_id,
                    date=date_str,
                    transaction_type="PAYMENT",
                    amount=-amount, # Negative amount reduces the debt balance
                    description="Payment Received"
                )
                db.add(payment_entry)
                db.commit()
                return True, f"Payment of Rs. {amount} recorded successfully."
            except Exception as e:
                db.rollback()
                return False, f"Error recording payment: {e}"
