from core.database import get_db
from core.models import Supplier, Purchase, PurchaseItem, Inventory
import datetime

class PurchaseController:
    """Handles suppliers, purchases, and stock additions."""

    def get_all_suppliers(self):
        db = next(get_db())
        suppliers = db.query(Supplier).all()
        return [{"id": s.id, "name": s.name, "phone": s.phone, "address": s.address} for s in suppliers]

    def add_supplier(self, name, phone, address):
        if not name:
            return False, "Supplier name is required."
            
        db = next(get_db())
        try:
            supplier = Supplier(name=name, phone=phone, address=address)
            db.add(supplier)
            db.commit()
            return True, "Supplier added successfully."
        except Exception as e:
            db.rollback()
            return False, f"Error adding supplier: {e}"

    def add_purchase(self, supplier_id, purchase_items):
        """
        Records a purchase and updates inventory.
        purchase_items is a list of dicts: 
        {'medicine_id': int, 'batch_no': str, 'expiry_date': str, 'quantity': int, 'purchase_price': float}
        """
        if not purchase_items:
            return False, "No items in purchase."
            
        total_amount = sum(item['purchase_price'] * item['quantity'] for item in purchase_items)
        date_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        db = next(get_db())
        try:
            purchase = Purchase(supplier_id=supplier_id, date=date_str, total_amount=total_amount)
            db.add(purchase)
            db.flush()
            
            for item in purchase_items:
                p_item = PurchaseItem(
                    purchase_id=purchase.id, medicine_id=item['medicine_id'], 
                    batch_no=item['batch_no'], expiry_date=item['expiry_date'], 
                    quantity=item['quantity'], purchase_price=item['purchase_price']
                )
                db.add(p_item)
                
                inv_item = Inventory(
                    medicine_id=item['medicine_id'], batch_no=item['batch_no'], 
                    expiry_date=item['expiry_date'], quantity=item['quantity'], 
                    purchase_price=item['purchase_price'], supplier_id=supplier_id,
                    sale_price=item.get('sale_price', 0.0)
                )
                db.add(inv_item)
                
                # Update Master Medicine Retail Price
                if 'sale_price' in item and item['sale_price'] > 0:
                    from core.models import Medicine
                    med = db.query(Medicine).filter_by(id=item['medicine_id']).first()
                    if med:
                        med.sale_price = item['sale_price']

            db.commit()
            return True, "Purchase recorded successfully."
        except Exception as e:
            db.rollback()
            return False, f"Error recording purchase: {e}"
