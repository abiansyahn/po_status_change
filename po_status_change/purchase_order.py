import frappe
from frappe.utils import now_datetime, get_datetime
from frappe import _

def check_if_new_doc(self, method):
    if self.is_new():
        self.custom_purchase_order_status = []

def update_status_change_log(self, method):
    if self.flags.get("via_po_status_change"):
        return
    if self.get("workflow_state") and not self.is_new():
        if len(self.custom_purchase_order_status) > 0:
            if self.custom_purchase_order_status[-1].status != self.workflow_state:
                if self.workflow_state != "Expect Delivery":
                    frappe.db.set_value("Workflow Status Update", self.custom_purchase_order_status[-1].name, {
                        "user": frappe.session.user,
                        "end_time": now_datetime(),
                        "time_duration": (now_datetime() - get_datetime(self.custom_purchase_order_status[-1].start_time)).total_seconds() if self.custom_purchase_order_status[-1].start_time else None
                    })
                    new_status = frappe.get_doc({
                        "doctype": "Workflow Status Update",
                        "parent": self.name,
                        "parenttype": "Purchase Order",
                        "parentfield": "custom_purchase_order_status",
                        "status": self.workflow_state,
                        "start_time": now_datetime(),
                        "idx": self.custom_purchase_order_status[-1].idx + 1
                    })
                    new_status.insert()
                else:
                    frappe.db.set_value("Workflow Status Update", self.custom_purchase_order_status[-1].name, {
                        "user": frappe.session.user,
                        "end_time": now_datetime(),
                        "time_duration": (now_datetime() - get_datetime(self.custom_purchase_order_status[-1].start_time)).total_seconds() if self.custom_purchase_order_status[-1].start_time else None
                    })
                    new_status = frappe.get_doc({
                        "doctype": "Workflow Status Update",
                        "parent": self.name,
                        "parenttype": "Purchase Order",
                        "parentfield": "custom_purchase_order_status",
                        "status": self.status,
                        "start_time": now_datetime(),
                        "idx": self.custom_purchase_order_status[-1].idx + 1
                    })
                    new_status.insert()
        else:
            if self.workflow_state != "Expect Delivery":
                new_status = frappe.get_doc({
                    "doctype": "Workflow Status Update",
                    "parent": self.name,
                    "parenttype": "Purchase Order",
                    "parentfield": "custom_purchase_order_status",
                    "status": self.workflow_state,
                    "start_time": now_datetime()
                })
                new_status.insert()
            else:
                new_status = frappe.get_doc({
                    "doctype": "Workflow Status Update",
                    "parent": self.name,
                    "parenttype": "Purchase Order",
                    "parentfield": "custom_purchase_order_status",
                    "status": self.status,
                    "start_time": now_datetime()
                })
                new_status.insert()