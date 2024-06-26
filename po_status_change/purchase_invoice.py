import frappe
from frappe.utils import now_datetime
from erpnext.accounts.doctype.purchase_invoice.purchase_invoice import PurchaseInvoice

class PurchaseInvoiceCustom(PurchaseInvoice):
    def on_submit(self):
        super(PurchaseInvoiceCustom, self).on_submit()

        po_list = []
        for item in self.items:
            if item.purchase_order not in po_list:
                if item.purchase_order:
                        po_list.append(item.purchase_order)
        
        for po in po_list:
            po_doc = frappe.get_doc("Purchase Order", po)

            if po_doc.per_received < 100 and po_doc.per_billed >= 100:
                if len(po_doc.custom_purchase_order_status) > 0:
                    po_doc.custom_purchase_order_status[-1].update(
                        {
                            "user": frappe.session.user,
                            "end_time": now_datetime(),
                            "time_duration": (now_datetime() - po_doc.custom_purchase_order_status[-1].start_time).total_seconds()
                        }
                    )
                    po_doc.save()

                po_doc.append("custom_purchase_order_status", {
                    "status": "To Receive",
                    "start_time": now_datetime()
                })
                po_doc.save()

            elif po_doc.per_received >= 100 and po_doc.per_billed >= 100:
                if len(po_doc.custom_purchase_order_status) > 0:
                    po_doc.custom_purchase_order_status[-1].update(
                        {
                            "user": frappe.session.user,
                            "end_time": now_datetime(),
                            "time_duration": (now_datetime() - po_doc.custom_purchase_order_status[-1].start_time).total_seconds()
                        }
                    )
                    po_doc.save()
                
                po_doc.append("custom_purchase_order_status", {
                    "status": "Completed",
                    "start_time": now_datetime()
                })
                po_doc.save()

    def on_cancel(self):
        super(PurchaseInvoiceCustom, self).on_cancel()

        po_list = []
        for item in self.items:
            if item.purchase_order not in po_list:
                po_list.append(item.purchase_order)
        
        for po in po_list:
            po_doc = frappe.get_doc("Purchase Order", po)

            if po_doc.per_received >= 100 and po_doc.per_billed < 100:
                if len(po_doc.custom_purchase_order_status) > 0:
                    po_doc.custom_purchase_order_status[-1].update(
                        {
                            "user": frappe.session.user,
                            "end_time": now_datetime(),
                            "time_duration": (now_datetime() - po_doc.custom_purchase_order_status[-1].start_time).total_seconds()
                        }
                    )
                    po_doc.save()

                po_doc.append("custom_purchase_order_status", {
                    "status": "To Bill",
                    "start_time": now_datetime()
                })
                po_doc.save()
            
            if po_doc.per_received < 100 and po_doc.per_billed < 100:
                if len(po_doc.custom_purchase_order_status) > 0:
                    po_doc.custom_purchase_order_status[-1].update(
                        {
                            "user": frappe.session.user,
                            "end_time": now_datetime(),
                            "time_duration": (now_datetime() - po_doc.custom_purchase_order_status[-1].start_time).total_seconds()
                        }
                    )
                    po_doc.save()

                po_doc.append("custom_purchase_order_status", {
                    "status": "To Receive and Bill",
                    "start_time": now_datetime()
                })
                po_doc.save()
