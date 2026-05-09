from core.database import get_db_session
from core.models import Medicine, Inventory
import csv
import os

class InventoryController:
    """Handles inventory management logic."""
    
    def get_all_units(self):
        with get_db_session() as db:
            from core.models import Unit
            units = db.query(Unit).all()
            return [{"id": u.id, "name": u.name} for u in units]

    def get_all_medicines(self):
        with get_db_session() as db:
            medicines = db.query(Medicine).all()
            return [{"id": m.id, "name": m.name, "generic_name": m.generic_name, "category": m.category, "sale_price": m.sale_price, "is_discountable": getattr(m, 'is_discountable', 1)} for m in medicines]
        
    def add_medicine_full(self, data: dict):
        if not data.get('name') or not data.get('sale_price'):
            return False, "Name and Sale Price are required."

        with get_db_session() as db:
            try:
                medicine = Medicine(
                    barcode=data.get('barcode'),
                    name=data.get('name'), 
                    generic_name=data.get('generic_name'), 
                    category=data.get('category'), 
                    manufacturer=data.get('manufacturer'),
                    sale_price=float(data.get('sale_price')), 
                    base_unit_id=data.get('base_unit_id'),
                    min_stock_level=int(data.get('min_stock_level', 10) or 10),
                    location=data.get('location'),
                    status=data.get('status', 'Active'),
                    description=data.get('description'),
                    is_discountable=1
                )
                
                db.add(medicine)
                db.flush() # get medicine id
                
                pack_unit_id = data.get('pack_unit_id')
                pack_conversion = data.get('pack_conversion')
                
                default_sale_unit_choice = data.get('default_sale_unit', 'base')
                if default_sale_unit_choice == 'base':
                    medicine.default_sale_unit_id = data.get('base_unit_id')
                else:
                    medicine.default_sale_unit_id = pack_unit_id

                if pack_unit_id and pack_conversion and int(pack_conversion) > 1:
                    from core.models import UnitConversion
                    conversion = UnitConversion(
                        medicine_id=medicine.id,
                        unit_id=pack_unit_id,
                        conversion_to_base=int(pack_conversion)
                    )
                    db.add(conversion)
                    
                current_stock = int(data.get('current_stock', 0) or 0)
                if current_stock > 0:
                    from core.models import Inventory
                    purchase_price_pack = float(data.get('purchase_price_pack', 0) or 0)
                    pack_conv = int(pack_conversion) if pack_conversion else 1
                    purchase_price_base = purchase_price_pack / pack_conv if pack_conv > 0 else 0

                    inv = Inventory(
                        medicine_id=medicine.id,
                        batch_no=data.get('batch_no', 'Unknown'),
                        expiry_date=data.get('expiry_date', '2099-12-31'),
                        quantity=current_stock,
                        purchase_price=purchase_price_base,
                        sale_price=float(data.get('sale_price'))
                    )
                    db.add(inv)
                    
                db.commit()
                
                from controllers.audit_controller import AuditController
                AuditController.log_action(1, "MEDICINE_ADDED", f"Medicine {medicine.name} added manually.")
                
                return True, "Medicine added successfully."
            except Exception as e:
                db.rollback()
                return False, f"Error adding medicine: {e}"

    def delete_medicine(self, medicine_id):
        with get_db_session() as db:
            try:
                from core.models import SaleItem, PurchaseItem, Inventory, UnitConversion
                
                # Check if used in sales or purchases
                has_sales = db.query(SaleItem).filter_by(medicine_id=medicine_id).first()
                has_purchases = db.query(PurchaseItem).filter_by(medicine_id=medicine_id).first()
                
                if has_sales or has_purchases:
                    return False, "Cannot delete medicine because it is linked to existing sales or purchases history."
                    
                med = db.query(Medicine).filter_by(id=medicine_id).first()
                if med:
                    name = med.name
                    
                    # Delete inventory records for this medicine manually (if no cascade)
                    db.query(Inventory).filter_by(medicine_id=medicine_id).delete()
                    db.query(UnitConversion).filter_by(medicine_id=medicine_id).delete()
                    
                    db.delete(med)
                    db.commit()
                    from controllers.audit_controller import AuditController
                    AuditController.log_action(1, "MEDICINE_DELETED", f"Medicine {name} (ID: {medicine_id}) and its stock were deleted.")
                    return True, "Medicine deleted successfully."
                return False, "Medicine not found."
            except Exception as e:
                db.rollback()
                return False, f"Error deleting medicine: {e}"

    def import_medicines_csv(self, file_path):
        if not os.path.exists(file_path):
            return False, "File does not exist."
            
        with get_db_session() as db:
            try:
                from core.models import Unit
                with open(file_path, mode='r', encoding='utf-8-sig') as f:
                    reader = csv.DictReader(f)
                    
                    # Check for required columns
                    headers = reader.fieldnames
                    if not headers or 'Name' not in headers:
                        return False, "Invalid CSV format. 'Name' column is required."
                        
                    count = 0
                    for row in reader:
                        name = row.get('Name', '').strip()
                        if not name:
                            continue
                            
                        # Find or create base unit
                        base_unit_name = row.get('Base Unit', 'Tablet').strip()
                        if not base_unit_name:
                            base_unit_name = "Tablet"
                            
                        unit = db.query(Unit).filter(Unit.name.ilike(base_unit_name)).first()
                        if not unit:
                            unit = Unit(name=base_unit_name)
                            db.add(unit)
                            db.flush()
                        
                        try:
                            sale_price = float(row.get('Sale Price', 0))
                        except ValueError:
                            sale_price = 0.0
                            
                        medicine = Medicine(
                            barcode=row.get('Barcode', None),
                            name=name,
                            generic_name=row.get('Generic', row.get('Generic Name', '')).strip(),
                            category=row.get('Category', 'Medicine').strip(),
                            manufacturer=row.get('Manufacturer', 'Unknown').strip(),
                            sale_price=sale_price,
                            base_unit_id=unit.id,
                            status='Active',
                            is_discountable=1
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
        with get_db_session() as db:
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
