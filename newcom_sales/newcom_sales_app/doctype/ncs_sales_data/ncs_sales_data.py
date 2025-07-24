
# Copyright (c) 2025, TCB and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt, cstr
import traceback


class NCSSalesData(Document):
    def on_update(self):
        self.update_totals()

    def on_update_after_submit(self):
        self.update_totals()

    def update_totals(self):
        try:
            items = self.get("items", [])

            buying_total = 0
            selling_total = 0
            total_gross_profit = 0
            total_qty = 0

            if items:
                for item in items:
                    tsa = item.get("total_selling_amount")
                    tba = item.get("total_buying_amount")
                    gf = item.get("gross_profit")
                    qty = item.get("qty")

                    buying_total += tba
                    selling_total += tsa
                    total_gross_profit += gf
                    total_qty += qty

                self.db_set("buying_total", buying_total, update_modified=False)
                self.db_set("selling_total", selling_total, update_modified=False)
                self.db_set("total_gross_profit", total_gross_profit, update_modified=False)
                self.db_set("total_qty", total_qty, update_modified=False)
        except Exception:
            pass
