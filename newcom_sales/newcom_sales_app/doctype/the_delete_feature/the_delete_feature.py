# Copyright (c) 2025, TCB and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
import traceback


class TheDeleteFeature(Document):
    @frappe.whitelist()
    def delete_all_records(self, doctype_name):
        try:
            meta = frappe.get_meta(doctype_name)
            parent_table = f"tab{doctype_name}"
            child_tables = [f"tab{df.options}" for df in meta.fields if df.fieldtype == "Table"]


            # Delete from child tables first
            for table in child_tables:
                frappe.db.sql(f"DELETE FROM `{table}`")

            # Delete from parent table
            frappe.db.sql(f"DELETE FROM `{parent_table}`")

            frappe.db.commit()

            frappe.msgprint("All records are deleted!")
            self.log_error("Delete all records success", f"Deleted all records from {doctype_name} and its child tables.")
        except Exception:
            self.log_error("Error delete_all_records", traceback.print_exc())
