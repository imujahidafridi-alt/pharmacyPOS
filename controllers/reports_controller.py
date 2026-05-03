from core.database import get_db
from core.models import Sale, Inventory, Medicine
from sqlalchemy import func
import datetime

class ReportsController:
    """Handles reporting and dashboard metrics."""

    def get_dashboard_metrics(self):
        """Fetches high-level metrics for the dashboard."""
        db = next(get_db())
        metrics = {
            'total_sales_today': 0,
            'low_stock_count': 0,
            'total_medicines': 0,
            'near_expiry_count': 0
        }
        
        # Today's Sales
        today_str = datetime.datetime.now().strftime("%Y-%m-%d")
        sales = db.query(Sale).filter(Sale.date.like(f"{today_str}%")).all()
        metrics['total_sales_today'] = sum(s.total_amount for s in sales)
            
        # Low Stock
        inventory_summary = db.query(
            Inventory.medicine_id, 
            func.sum(Inventory.quantity).label('total_qty')
        ).group_by(Inventory.medicine_id).having(func.sum(Inventory.quantity) < 10).all()
        metrics['low_stock_count'] = len(inventory_summary)
            
        # Total Medicines
        metrics['total_medicines'] = db.query(Medicine).count()
        
        # Near Expiry (< 30 days)
        future_30_days = (datetime.datetime.now() + datetime.timedelta(days=30)).strftime("%Y-%m-%d")
        near_expiry_batches = db.query(Inventory).filter(
            Inventory.quantity > 0,
            Inventory.expiry_date <= future_30_days
        ).count()
        metrics['near_expiry_count'] = near_expiry_batches
            
        return metrics

    def get_sales_trend(self, days=7):
        """Fetches sales trend for the last N days."""
        db = next(get_db())
        trend = []
        for i in range(days - 1, -1, -1):
            target_date = (datetime.datetime.now() - datetime.timedelta(days=i)).strftime("%Y-%m-%d")
            sales = db.query(func.sum(Sale.total_amount)).filter(Sale.date.like(f"{target_date}%")).scalar()
            trend.append({'date': target_date, 'total': sales or 0})
        return trend

    def get_top_medicines(self, limit=5):
        """Fetches top selling medicines based on quantity."""
        db = next(get_db())
        from core.models import SaleItem
        results = db.query(
            Medicine.name,
            func.sum(SaleItem.quantity).label('total_qty')
        ).join(SaleItem, Medicine.id == SaleItem.medicine_id)\
         .group_by(Medicine.id)\
         .order_by(func.sum(SaleItem.quantity).desc())\
         .limit(limit).all()
        return [{'name': r.name, 'quantity': r.total_qty} for r in results]

    def get_sales_report(self):
        """Fetches all sales for reporting."""
        db = next(get_db())
        sales = db.query(Sale).order_by(Sale.date.desc()).all()
        return [{"id": s.id, "date": s.date, "total_amount": s.total_amount, "discount": s.discount, "payment_method": s.payment_method} for s in sales]

    def get_stock_report(self):
        """Fetches current stock levels."""
        db = next(get_db())
        results = db.query(Medicine.name, Inventory.batch_no, Inventory.expiry_date, Inventory.quantity).join(Inventory, Medicine.id == Inventory.medicine_id).order_by(Medicine.name, Inventory.expiry_date).all()
        return [{"name": r.name, "batch_no": r.batch_no, "expiry_date": r.expiry_date, "quantity": r.quantity} for r in results]
