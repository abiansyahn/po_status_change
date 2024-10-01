import frappe
from frappe.utils import now_datetime
from frappe import _

def update_status_change_log(self, method):
    doc_before_save = self.get_doc_before_save()
    if self.get("__islocal"):
        self.append("custom_purchase_order_status", {
            "status": self.workflow_state,
            "start_time": now_datetime()
        })
    else:
        if doc_before_save.workflow_state != self.workflow_state:
            if self.workflow_state != "Expect Delivery":
                if len(self.custom_purchase_order_status) > 0:
                    self.custom_purchase_order_status[-1].update({
                        "user": frappe.session.user,
                        "end_time": now_datetime(),
                        "time_duration": (now_datetime() - self.custom_purchase_order_status[-1].start_time).total_seconds()
                    })
                self.append("custom_purchase_order_status", {
                    "status": self.workflow_state,
                    "start_time": now_datetime()
                })
            else:
                if len(self.custom_purchase_order_status) > 0:
                    self.custom_purchase_order_status[-1].update({
                        "user": frappe.session.user,
                        "end_time": now_datetime(),
                        "time_duration": (now_datetime() - self.custom_purchase_order_status[-1].start_time).total_seconds()
                    })
                self.append("custom_purchase_order_status", {
                    "status": self.status,
                    "start_time": now_datetime()
                })