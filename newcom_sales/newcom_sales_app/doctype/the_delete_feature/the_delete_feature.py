# Copyright (c) 2025, TCB and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
import traceback
import json


class TheDeleteFeature(Document):
    @frappe.whitelist()
    def delete_all_records(self, doctype_name):
        try:

            meta = frappe.get_meta(doctype_name)
            parent_table = f"tab{doctype_name}"
            child_tables = [f"tab{df.options}" for df in meta.fields if df.fieldtype == "Table"]

            enable_filters = self.get("enable_filters", False)
            filters = self.get("filters")
            try:
                filters = json.loads(filters)
            except Exception:
                filters = {}

            if enable_filters and not filters:
                frappe.throw("Unable to refine filters, please disable filters")
                return

            if filters and enable_filters:
                names = frappe.get_all(doctype_name, filters=filters, pluck="name")

                if not names:
                    frappe.msgprint("No records found")
                    return

                for table in child_tables:
                    frappe.db.sql(f"DELETE FROM `{table}` WHERE parent IN %s", (tuple(names),))

                # Delete parents
                frappe.db.sql(f"DELETE FROM `{parent_table}` WHERE name IN %s", (tuple(names),))
                frappe.msgprint("All filtered records are deleted!")
            else:
                # Delete from child tables first
                for table in child_tables:
                    frappe.db.sql(f"DELETE FROM `{table}`")

                # Delete from parent table
                frappe.db.sql(f"DELETE FROM `{parent_table}`")
                frappe.msgprint("All records are deleted!")

            frappe.db.commit()

            self.log_error("Delete all records success", f"Deleted all records from {doctype_name} and its child tables.")
        except Exception:
            frappe.db.rollback()
            self.log_error("Error delete_all_records", traceback.print_exc())

    @frappe.whitelist()
    def delete_all_records_old(self, doctype_name):
        try:
            meta = frappe.get_meta(doctype_name)
            parent_table = f"tab{doctype_name}"
            child_tables = [f"tab{df.options}" for df in meta.fields if df.fieldtype == "Table"]

            filters = self.get("filters")
            # try:
            #     filters = json.loads(filters)
            # except Exception:
            #     pass

            query = f"DELETE FROM `{parent_table}`"

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
