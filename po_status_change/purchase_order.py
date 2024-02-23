import frappe
from frappe.utils import now_datetime
from erpnext.buying.doctype.purchase_order.purchase_order import PurchaseOrder
from frappe import _

frappe.utils.logger.set_log_level("DEBUG")
logger = frappe.logger("api", allow_site=True, file_count=50)

class PurchaseOrderCustom(PurchaseOrder):
    def validate(self):
        super(PurchaseOrderCustom, self).validate()
        self.update_status_change_log()


    def update_status_change_log(self):
        doc_before_save = self.get_doc_before_save()
        if self.get("__islocal"):
            self.append("custom_purchase_order_status", {
                "user": frappe.session.user,
                "status": self.workflow_state,
                "start_time": now_datetime()
            })
        else:
            if doc_before_save.workflow_state != self.workflow_state:
                if self.workflow_state != "Expect Delivery":
                    self.custom_purchase_order_status[-1].update({
                        "end_time": now_datetime(),
                        "time_duration": (now_datetime() - self.custom_purchase_order_status[-1].start_time).total_seconds()
                    })
                    self.append("custom_purchase_order_status", {
                        "user": frappe.session.user,
                        "status": self.workflow_state,
                        "start_time": now_datetime()
                    })
                else:
                    self.custom_purchase_order_status[-1].update({
                        "end_time": now_datetime(),
                        "time_duration": (now_datetime() - self.custom_purchase_order_status[-1].start_time).total_seconds()
                    })
                    self.append("custom_purchase_order_status", {
                        "user": frappe.session.user,
                        "status": self.status,
                        "start_time": now_datetime()
                    })