import frappe
from frappe.utils import now_datetime

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
    if self.get("workflow_state"):
        if len(self.custom_workflow_status) > 0:
            if self.custom_workflow_status[-1].status != self.workflow_state:
                if self.workflow_state != "To Pay":
                    frappe.db.set_value("Workflow Status Update", self.custom_workflow_status[-1].name, {
                        "user": frappe.session.user,
                        "end_time": now_datetime(),
                        "time_duration": (now_datetime() - self.custom_workflow_status[-1].start_time).total_seconds()
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
                    frappe.db.commit()
                else:
                    frappe.db.set_value("Workflow Status Update", self.custom_workflow_status[-1].name, {
                        "user": frappe.session.user,
                        "end_time": now_datetime(),
                        "time_duration": (now_datetime() - self.custom_workflow_status[-1].start_time).total_seconds()
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
                    frappe.db.commit()
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
        elif po_doc.per_received < 100 and po_doc.per_billed >= 100:
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
        elif po_doc.per_received < 100 and po_doc.per_billed < 100:
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
            if len(pr_doc.custom_workflow_status) > 0:
                pr_doc.custom_workflow_status[-1].update(
                    {
                        "user": frappe.session.user,
                        "end_time": now_datetime(),
                        "time_duration": (now_datetime() - pr_doc.custom_workflow_status[-1].start_time).total_seconds()
                    }
                )
                pr_doc.save()

            pr_doc.append("custom_workflow_status", {
                "status": "Completed",
                "start_time": now_datetime()
            })
            pr_doc.save()
        elif pr_doc.per_billed < 100 and pr_doc.per_billed > 0:
            if len(pr_doc.custom_workflow_status) > 0:
                pr_doc.custom_workflow_status[-1].update(
                    {
                        "user": frappe.session.user,
                        "end_time": now_datetime(),
                        "time_duration": (now_datetime() - pr_doc.custom_workflow_status[-1].start_time).total_seconds()
                    }
                )
                pr_doc.save()
            
            pr_doc.append("custom_workflow_status", {
                "status": "Partly Billed",
                "start_time": now_datetime()
            })
            pr_doc.save()
        elif pr_doc.per_billed <= 0:
            if len(pr_doc.custom_workflow_status) > 0:
                pr_doc.custom_workflow_status[-1].update(
                    {
                        "user": frappe.session.user,
                        "end_time": now_datetime(),
                        "time_duration": (now_datetime() - pr_doc.custom_workflow_status[-1].start_time).total_seconds()
                    }
                )
                pr_doc.save()

            pr_doc.append("custom_workflow_status", {
                "status": "To Bill",
                "start_time": now_datetime()
            })
            pr_doc.save()