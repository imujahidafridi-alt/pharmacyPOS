from core.database import get_db
from core.models import Medicine, Inventory
import csv
import os

class InventoryController:
    """Handles inventory management logic."""
    
    def get_all_medicines(self):
        db = next(get_db())
        medicines = db.query(Medicine).all()
        return [{"id": m.id, "name": m.name, "generic_name": m.generic_name, "category": m.category, "sale_price": m.sale_price, "units_per_box": m.units_per_box, "is_discountable": m.is_discountable} for m in medicines]
        
    def add_medicine(self, name, generic_name, category, sale_price, units_per_box=1, is_discountable=1):
        if not name or not sale_price:
            return False, "Name and Sale Price are required."
        
        try:
            sale_price = float(sale_price)
            units_per_box = int(units_per_box)
        except ValueError:
            return False, "Sale Price must be a number and Units per Box must be an integer."

        db = next(get_db())
        try:
            medicine = Medicine(name=name, generic_name=generic_name, category=category, sale_price=sale_price, units_per_box=units_per_box, is_discountable=is_discountable)
            db.add(medicine)
            db.commit()
            
            from controllers.audit_controller import AuditController
            AuditController.log_action(1, "MEDICINE_ADDED", f"Medicine {name} added manually.")
            
            return True, "Medicine added successfully."
        except Exception as e:
            db.rollback()
            return False, f"Error adding medicine: {e}"

    def import_medicines_csv(self, file_path):
        if not os.path.exists(file_path):
            return False, "File does not exist."
            
        db = next(get_db())
        try:
            with open(file_path, mode='r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                count = 0
                for row in reader:
                    # Expected: Name, Generic Name, Category, Sale Price, Units per Box
                    name = row.get('Name', '').strip()
                    if not name:
                        continue
                    
                    try:
                        sale_price = float(row.get('Sale Price', 0))
                        units_per_box = int(row.get('Units per Box', 1))
                    except ValueError:
                        continue
                        
                    medicine = Medicine(
                        name=name,
                        generic_name=row.get('Generic Name', '').strip(),
                        category=row.get('Category', '').strip(),
                        sale_price=sale_price,
                        units_per_box=units_per_box
                    )
                    db.add(medicine)
                    count += 1
            
            db.commit()
            from controllers.audit_controller import AuditController
            AuditController.log_action(1, "MEDICINE_IMPORTED", f"Imported {count} medicines from CSV.")
            return True, f"Successfully imported {count} medicines."
        except Exception as e:
            db.rollback()
            return False, f"Error importing CSV: {e}"

    def get_inventory_stock(self):
        db = next(get_db())
        results = db.query(Medicine, Inventory).outerjoin(Inventory, Medicine.id == Inventory.medicine_id).all()
        stock = []
        for med, inv in results:
            stock.append({
                "id": med.id,
                "name": med.name,
                "batch_no": inv.batch_no if inv else "N/A",
                "expiry_date": inv.expiry_date if inv else "N/A",
                "quantity": inv.quantity if inv else 0,
                "purchase_price": inv.purchase_price if inv else 0.0
            })
        return stock
