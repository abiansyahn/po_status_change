import frappe
from frappe.utils import now_datetime
from erpnext.stock.doctype.purchase_receipt.purchase_receipt import PurchaseReceipt

class PurchaseReceiptCustom(PurchaseReceipt):
    def on_submit(self):
        super(PurchaseReceiptCustom, self).on_submit()

        po_list = []
        for item in self.items:
            if item.purchase_order not in po_list:
                po_list.append(item.purchase_order)
        
        for po in po_list:
            po_doc = frappe.get_doc("Purchase Order", po)

            if po_doc.per_received >= 100 and po_doc.per_billed < 100:
                po_doc.custom_purchase_order_status[-1].update(
                    {
                        "end_time": now_datetime(),
                        "time_duration": (now_datetime() - po_doc.custom_purchase_order_status[-1].start_time).total_seconds()
                    }
                )
                po_doc.save()

                po_doc.append("custom_purchase_order_status", {
                    "user": frappe.session.user,
                    "status": "To Bill",
                    "start_time": now_datetime()
                })
                po_doc.save()

            if po_doc.per_received >= 100 and po_doc.per_billed >= 100:
                po_doc.custom_purchase_order_status[-1].update(
                    {
                        "end_time": now_datetime(),
                        "time_duration": (now_datetime() - po_doc.custom_purchase_order_status[-1].start_time).total_seconds()
                    }
                )
                po_doc.save()
                
                po_doc.append("custom_purchase_order_status", {
                    "user": frappe.session.user,
                    "status": "Completed",
                    "start_time": now_datetime()
                })
                po_doc.save()

    def on_cancel(self):
        super(PurchaseReceiptCustom, self).on_cancel()

        po_list = []
        for item in self.items:
            if item.purchase_order not in po_list:
                po_list.append(item.purchase_order)
        
        for po in po_list:
            po_doc = frappe.get_doc("Purchase Order", po)

            if po_doc.per_received < 100 and po_doc.per_billed >= 100:
                po_doc.custom_purchase_order_status[-1].update(
                    {
                        "end_time": now_datetime(),
                        "time_duration": (now_datetime() - po_doc.custom_purchase_order_status[-1].start_time).total_seconds()
                    }
                )
                po_doc.save()

                po_doc.append("custom_purchase_order_status", {
                    "user": frappe.session.user,
                    "status": "To Receive",
                    "start_time": now_datetime()
                })
                po_doc.save()
            
            if po_doc.per_received < 100 and po_doc.per_billed < 100:
                po_doc.custom_purchase_order_status[-1].update(
                    {
                        "end_time": now_datetime(),
                        "time_duration": (now_datetime() - po_doc.custom_purchase_order_status[-1].start_time).total_seconds()
                    }
                )
                po_doc.save()

                po_doc.append("custom_purchase_order_status", {
                    "user": frappe.session.user,
                    "status": "To Receive and Bill",
                    "start_time": now_datetime()
                })
                po_doc.save()