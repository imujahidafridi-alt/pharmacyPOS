import os
import logging
from escpos.printer import Dummy, Usb, Network
import datetime

logger = logging.getLogger("pharmacy_pos.printer")

class ReceiptPrinter:
    def __init__(self):
        self.printer_type = os.environ.get("PRINTER_TYPE", "Dummy")
        try:
            if self.printer_type == "USB":
                usb_vendor = int(os.environ.get("PRINTER_USB_VENDOR", "0x04b8"), 16)
                usb_product = int(os.environ.get("PRINTER_USB_PRODUCT", "0x0202"), 16)
                self.printer = Usb(usb_vendor, usb_product, 0, 0x81, 0x01)
            elif self.printer_type == "Network":
                printer_ip = os.environ.get("PRINTER_IP", "192.168.1.100")
                self.printer = Network(printer_ip)
            else:
                self.printer = Dummy()
        except Exception as e:
            logger.warning(f"Printer connection failed: {e}. Falling back to Dummy.")
            self.printer = Dummy()

    def print_receipt(self, cart_items, total_amount, discount, payment_method, sale_id):
        try:
            p = self.printer
            
            p.set(align='center', font='a', width=2, height=2)
            p.text("PHARMACY POS\n")
            p.set(align='center', font='a')
            p.text(os.environ.get("RECEIPT_HEADER_LINE1", "123 Health St, Lahore, PK") + "\n")
            p.text(os.environ.get("RECEIPT_HEADER_LINE2", "Phone: +92 300 1234567") + "\n")
            p.text("-" * 32 + "\n")
            
            date_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
            p.set(align='left')
            p.text(f"Receipt #: {sale_id}\n")
            p.text(f"Date: {date_str}\n")
            p.text(f"Pay Mode: {payment_method}\n")
            p.text("-" * 32 + "\n")
            
            p.text("Item            Qty  Price  Total\n")
            p.text("-" * 32 + "\n")
            
            for item in cart_items:
                name = item['name'][:15].ljust(15)
                qty = str(item['quantity']).rjust(3)
                price = f"{item['price']:.0f}".rjust(6)
                total = f"{(item['price'] * item['quantity']):.0f}".rjust(6)
                p.text(f"{name} {qty} {price} {total}\n")
            
            p.text("-" * 32 + "\n")
            p.set(align='right')
            p.text(f"Subtotal: Rs. {total_amount + discount:.2f}\n")
            p.text(f"Discount: Rs. {discount:.2f}\n")
            p.text(f"Total: Rs. {total_amount:.2f}\n")
            
            p.set(align='center')
            p.text("-" * 32 + "\n")
            p.text("Thank you for your visit!\n")
            p.text("Wishing you good health.\n\n\n\n\n")
            p.cut()
            
            if isinstance(self.printer, Dummy):
                logger.info(self.printer.output.decode('utf-8', errors='ignore'))
            return True
        except Exception as e:
            logger.error(f"Failed to print receipt: {e}")
            return False
