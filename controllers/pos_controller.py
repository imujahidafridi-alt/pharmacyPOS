from core.database import get_db_session
from core.models import Medicine, Inventory, Sale, SaleItem
from sqlalchemy import or_, func
import datetime

class POSController:
    """Handles Point of Sale logic."""
    
    def search_medicines(self, query):
        with get_db_session() as db:
            search_term = f"%{query}%"

            results = db.query(
                Medicine,
                func.coalesce(func.sum(Inventory.quantity), 0).label('total_stock')
            ).outerjoin(
                Inventory, Medicine.id == Inventory.medicine_id
            ).filter(
                or_(
                    Medicine.name.ilike(search_term),
                    Medicine.generic_name.ilike(search_term),
                    Medicine.barcode.ilike(search_term)
                )
            ).group_by(Medicine.id).all()

            final_results = []
            for m, stock_num in results:
                units = []
                if getattr(m, 'base_unit', None):
                    units.append({'id': m.base_unit.id, 'name': m.base_unit.name, 'conversion': 1})
                else:
                    units.append({'id': None, 'name': 'Unit', 'conversion': 1})

                for c in getattr(m, 'conversions', []):
                    units.append({'id': c.unit_id, 'name': getattr(c.unit, 'name', 'Pack'), 'conversion': c.conversion_to_base})

                # Sort units descending by conversion for human readable formatting
                sorted_units = sorted(units, key=lambda x: x['conversion'], reverse=True)
                
                # Format human readable stock
                stock = int(stock_num or 0)
                stock_str_parts = []
                remaining_stock = stock
                
                for u in sorted_units:
                    conv = u['conversion']
                    if conv > 0 and remaining_stock >= conv:
                        qty = remaining_stock // conv
                        stock_str_parts.append(f"{qty} {u['name']}(s)")
                        remaining_stock %= conv
                
                if not stock_str_parts:
                    stock_str_parts.append(f"0 {sorted_units[-1]['name']}(s)")
                elif remaining_stock > 0:
                    stock_str_parts.append(f"{remaining_stock} {sorted_units[-1]['name']}(s)")
                    
                human_stock = ", ".join(stock_str_parts)

                # Move default_sale_unit_id to the front of units so grid selects it by default
                default_uid = getattr(m, 'default_sale_unit_id', None)
                if default_uid is not None:
                    for i, u in enumerate(units):
                        if u['id'] == default_uid:
                            units.insert(0, units.pop(i))
                            break

                final_results.append({
                    "id": m.id,
                    "name": m.name,
                    "generic_name": m.generic_name,
                    "sale_price": m.sale_price,
                    "is_discountable": getattr(m, 'is_discountable', 1),
                    "stock": stock,
                    "human_stock": human_stock,
                    "units": units
                })

            return final_results
    
    def get_stock_for_medicine(self, medicine_id):
        with get_db_session() as db:
            total_qty = db.query(func.sum(Inventory.quantity)).filter(Inventory.medicine_id == medicine_id).scalar()
            return total_qty if total_qty else 0

    def process_sale(self, cart_items, discount, payment_method, customer_id=None, amount_paid=0.0, user_id=1):
        """
        Processes a sale.
        cart_items is a list of dicts: {'medicine_id': int, 'quantity': int, 'price': float}
        """
        if not cart_items:
            return False, "Cart is empty."
            
        if payment_method == "Credit (Khata)" and not customer_id:
            return False, "A Customer must be selected for Credit (Khata) sales."
            
        total_amount = sum(item['price'] * item['quantity'] for item in cart_items)
        date_str = datetime.datetime.now()

        with get_db_session() as db:
            try:
                sale = Sale(date=date_str, total_amount=total_amount, discount=discount, payment_method=payment_method, customer_id=customer_id, amount_paid=amount_paid)
                db.add(sale)
                db.flush()
                
                for item in cart_items:
                    med_id = item['medicine_id']
                    qty = item['quantity']
                    price = item['price']
                    unit_id = item.get('unit_id', None)
                    conversion_to_base = item.get('conversion_to_base', 1)
                    
                    sale_item = SaleItem(
                        sale_id=sale.id, 
                        medicine_id=med_id, 
                        quantity=qty, 
                        price=price,
                        unit_id=unit_id,
                        conversion_to_base=conversion_to_base
                    )
                    db.add(sale_item)
                    
                    qty_to_deduct = qty * conversion_to_base # CONVERT TO BASE UNITS FOR DEDUCTION
                    
                    # Use with_for_update() to lock these rows during the transaction to prevent concurrent multi-PC race conditions.
                    batches = db.query(Inventory).filter(
                        Inventory.medicine_id == med_id, 
                        Inventory.quantity > 0
                    ).order_by(Inventory.expiry_date.asc()).with_for_update().all()
                    
                    for batch in batches:
                        if qty_to_deduct <= 0:
                            break
                        
                        if batch.quantity >= qty_to_deduct:
                            batch.quantity -= qty_to_deduct
                            qty_to_deduct = 0
                        else:
                            qty_to_deduct -= batch.quantity
                            batch.quantity = 0
                            
                    if qty_to_deduct > 0:
                        db.rollback()
                        return False, f"Not enough stock for medicine ID {med_id}. Short by {qty_to_deduct} base units."

                # Khata logic
                if customer_id:
                    from core.models import CustomerLedger
                    # Add Sale debit
                    sale_entry = CustomerLedger(
                        customer_id=customer_id,
                        date=date_str,
                        transaction_type='SALE',
                        amount=total_amount - discount,
                        sale_id=sale.id,
                        description=f"Sale #{sale.id}"
                    )
                    db.add(sale_entry)
                    
                    # Add Payment credit if amount_paid > 0
                    if amount_paid > 0:
                        payment_entry = CustomerLedger(
                            customer_id=customer_id,
                            date=date_str,
                            transaction_type='PAYMENT',
                            amount=-amount_paid,
                            sale_id=sale.id,
                            description=f"Payment for Sale #{sale.id}"
                        )
                        db.add(payment_entry)

                db.commit()
                
                from controllers.audit_controller import AuditController
                AuditController.log_action(user_id, "SALE", f"Sale #{sale.id} processed for Rs. {total_amount-discount}")
                
                # Print receipt
                try:
                    from core.printer import ReceiptPrinter
                    printer = ReceiptPrinter()
                    printer.print_receipt(cart_items, total_amount, discount, payment_method, sale.id)
                except Exception as e:
                    print(f"Printer error: {e}")
                    
                return True, "Sale completed successfully."
            except Exception as e:
                db.rollback()
                return False, f"Error processing sale: {e}"
