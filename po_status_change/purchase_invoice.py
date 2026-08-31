import frappe
from frappe.utils import now_datetime, get_datetime

def on_submit(self, method):
    update_purchase_order_status(self.items)
    update_purchase_receipt_status(self.items)

def on_cancel(self, method):
    update_purchase_order_status(self.items)
    update_purchase_receipt_status(self.items)

def check_if_new_doc(self, method):
    if self.is_new():
        self.custom_workflow_status = []

def update_status_change_log(self, method):
    if self.get("workflow_state") and not self.is_new():
        if len(self.custom_workflow_status) > 0:
            if self.custom_workflow_status[-1].status != self.workflow_state:
                if self.workflow_state != "To Pay":
                    frappe.db.set_value("Workflow Status Update", self.custom_workflow_status[-1].name, {
                        "user": frappe.session.user,
                        "end_time": now_datetime(),
                        "time_duration": (now_datetime() - get_datetime(self.custom_workflow_status[-1].start_time)).total_seconds() if self.custom_workflow_status[-1].start_time else None
                    })
                    new_status = frappe.get_doc({
                        "doctype": "Workflow Status Update",
                        "parent": self.name,
                        "parenttype": "Purchase Invoice",
                        "parentfield": "custom_workflow_status",
                        "status": self.workflow_state,
                        "start_time": now_datetime(),
                        "idx": self.custom_workflow_status[-1].idx + 1
                    })
                    new_status.insert()
                else:
                    frappe.db.set_value("Workflow Status Update", self.custom_workflow_status[-1].name, {
                        "user": frappe.session.user,
                        "end_time": now_datetime(),
                        "time_duration": (now_datetime() - get_datetime(self.custom_workflow_status[-1].start_time)).total_seconds() if self.custom_workflow_status[-1].start_time else None
                    })
                    new_status = frappe.get_doc({
                        "doctype": "Workflow Status Update",
                        "parent": self.name,
                        "parenttype": "Purchase Invoice",
                        "parentfield": "custom_workflow_status",
                        "status": self.status,
                        "start_time": now_datetime(),
                        "idx": self.custom_workflow_status[-1].idx + 1
                    })
                    new_status.insert()
        else:
            if self.workflow_state != "To Pay":
                new_status = frappe.get_doc({
                    "doctype": "Workflow Status Update",
                    "parent": self.name,
                    "parenttype": "Purchase Invoice",
                    "parentfield": "custom_workflow_status",
                    "status": self.workflow_state,
                    "start_time": now_datetime()
                })
                new_status.insert()
            else:
                new_status = frappe.get_doc({
                    "doctype": "Workflow Status Update",
                    "parent": self.name,
                    "parenttype": "Purchase Invoice",
                    "parentfield": "custom_workflow_status",
                    "status": self.status,
                    "start_time": now_datetime()
                })
                new_status.insert()

def update_purchase_order_status(items):
    po_list = []
    for item in items:
        if item.purchase_order == None or item.purchase_order == "" or item.purchase_order == "None":
            continue
        if item.purchase_order not in po_list:
            po_list.append(item.purchase_order)
    
    for po in po_list:
        po_doc = frappe.get_doc("Purchase Order", po)

        if po_doc.per_received >= 100 and po_doc.per_billed < 100:
            new_status = "To Bill"
        elif po_doc.per_received >= 100 and po_doc.per_billed >= 100:
            new_status = "Completed"
        elif po_doc.per_received < 100 and po_doc.per_billed >= 100:
            new_status = "To Receive"
        elif po_doc.per_received < 100 and po_doc.per_billed < 100:
            new_status = "To Receive and Bill"
        else:
            continue

        # Skip if last status already matches (idempotency guard)
        if len(po_doc.custom_purchase_order_status) > 0:
            if po_doc.custom_purchase_order_status[-1].status == new_status:
                continue
            po_doc.custom_purchase_order_status[-1].update({
                "user": frappe.session.user,
                "end_time": now_datetime(),
                "time_duration": (now_datetime() - get_datetime(po_doc.custom_purchase_order_status[-1].start_time)).total_seconds() if po_doc.custom_purchase_order_status[-1].start_time else None
            })

        po_doc.append("custom_purchase_order_status", {
            "status": new_status,
            "start_time": now_datetime()
        })
        po_doc.flags.via_po_status_change = True
        po_doc.save()

def update_purchase_receipt_status(items):
    pr_list = []
    for item in items:
        if item.purchase_receipt == None or item.purchase_receipt == "" or item.purchase_receipt == "None":
            continue
        if item.purchase_receipt not in pr_list:
            pr_list.append(item.purchase_receipt)
    
    for pr in pr_list:
        pr_doc = frappe.get_doc("Purchase Receipt", pr)

        if pr_doc.per_billed >= 100:
            new_status = "Completed"
        elif pr_doc.per_billed < 100 and pr_doc.per_billed > 0:
            new_status = "Partly Billed"
        elif pr_doc.per_billed <= 0:
            new_status = "To Bill"
        else:
            continue

        # Skip if last status already matches (idempotency guard)
        if len(pr_doc.custom_workflow_status) > 0:
            if pr_doc.custom_workflow_status[-1].status == new_status:
                continue
            pr_doc.custom_workflow_status[-1].update({
                "user": frappe.session.user,
                "end_time": now_datetime(),
                "time_duration": (now_datetime() - get_datetime(pr_doc.custom_workflow_status[-1].start_time)).total_seconds() if pr_doc.custom_workflow_status[-1].start_time else None
            })

        pr_doc.append("custom_workflow_status", {
            "status": new_status,
            "start_time": now_datetime()
        })
        pr_doc.flags.via_po_status_change = True
        pr_doc.save()