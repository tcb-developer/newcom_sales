# Copyright (c) 2025, TCB and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from collections import OrderedDict
import copy


def execute(filters={}):
    columns = get_columns()
    si_list = get_si_list(filters=filters)
    data = group_items_by_invoice(si_list)
    return columns, data


def get_columns():
    columns = [
        {
            "label": _("Customer"),
            "fieldname": "customer",
            "fieldtype": "Link",
            "options": "NCS Sales Plan",
            "width": 150,
        },
        {
            "label": _("Customer Name"),
            "fieldname": "customer_name",
            "fieldtype": "Data",
            "width": 200,
        },
        {
            "label": _("Customer Group"),
            "fieldname": "customer_group",
            "fieldtype": "Link",
            "options": "Customer Group",
            "width": 100,
        },
        {
            "label": _("Customer Sub Group"),
            "fieldname": "customer_sub_group",
            "fieldtype": "Link",
            "options": "Customer Sub Group",
            "width": 200,
        },
        {
            "label": _("Sales Person"),
            "fieldname": "sales_person",
            "fieldtype": "Link",
            "options": "Sales Person",
            "width": 100,
        },
        {
            "label": _("Sales Invoice / Item"),
            "fieldname": "sales_invoice",
            "fieldtype": "Data",
            "width": 150,
        },
        {
            "label": _("Brand"),
            "fieldname": "brand",
            "fieldtype": "Link",
            "options": "Brand",
            "width": 100,
        },
        {
            "label": _("Qty"),
            "fieldname": "qty",
            "fieldtype": "Float",
            "width": 150,
        },
        {
            "label": _("Selling Total"),
            "fieldname": "selling_total",
            "fieldtype": "Currency",
            "width": 150,
        },
        {
            "label": _("Buying Total"),
            "fieldname": "buying_total",
            "fieldtype": "Currency",
            "width": 150,
        },
        {
            "label": _("Date"),
            "fieldname": "date",
            "fieldtype": "Date",
            "width": 100,
        },
        {
            "label": _("Year"),
            "fieldname": "year",
            "fieldtype": "Data",
            "width": 100,
        },
        {
            "label": _("Month & Year"),
            "fieldname": "month_and_year",
            "fieldtype": "Data",
            "width": 150,
        },
        {
            "label": _("Q & FY"),
            "fieldname": "q_and_fy",
            "fieldtype": "Data",
            "width": 100,
        },
    ]

    return columns


def get_si_list(filters={}):
    doctype = "NCS Sales Data"
    si = frappe.qb.DocType(doctype)
    sii = frappe.qb.DocType("NCS Sales Data Item")
    customer = frappe.qb.DocType("NCS Sales Plan")

    # Query
    query = (
        frappe.qb.from_(sii)
        .left_join(si)
        .on(si.name == sii.parent)
        .select(
            si.sales_invoice,
            sii.name.as_("child"),
            sii.sales_invoice.as_("parent"),
            sii.brand,
            sii.item.as_("item_code"),
            sii.description,
            si.customer_code.as_("customer"),
            si.customer_name,
            si.customer_group,
            si.customer_sub_group,
            si.date,
            si.sales_person,
            si.year,
            si.month_and_year,
            si.q_and_fy,
            sii.qty,
            sii.total_selling_amount,
            sii.total_buying_amount,
            sii.gross_profit,
            si.buying_total,
            si.selling_total,
            si.total_gross_profit,
            si.total_qty,
            si.name,
        )
        .groupby(sii.name)
        .orderby(sii.sales_invoice)
    )

    base_condition = si.docstatus == 1

    if filters.get("from_date"):
        base_condition &= si.date >= filters.get("from_date")

    if filters.get("to_date"):
        base_condition &= si.date <= filters.get("to_date")

    if filters.get("customer"):
        customer = filters.get("customer")
        base_condition &= si.customer_code == customer

    if filters.get("customer"):
        customer = filters.get("customer")
        base_condition &= si.customer_code == customer

    if filters.get("customer_group"):
        customer_group = filters.get("customer_group")
        base_condition &= si.customer_group == customer_group

    if filters.get("customer_sub_group"):
        customer_sub_group = filters.get("customer_sub_group")
        base_condition &= si.customer_sub_group == customer_sub_group

    if filters.get("sales_person"):
        sales_person = filters.get("sales_person")
        base_condition &= si.sales_person == sales_person

    if filters.get("sales_invoice"):
        sales_invoice = filters.get("sales_invoice")
        base_condition &= sii.sales_invoice == sales_invoice

    if filters.get("brand"):
        brand = filters.get("brand")
        base_condition &= sii.brand == brand

    frappe.log_error("Get si list filters", filters)

    query = query.where(base_condition)

    results = query.run(as_dict=True)

    return results


def group_items_by_invoice(si_list):
    frappe.log_error("Si list", si_list)
    grouped = OrderedDict()

    for row in si_list:
        grouped.setdefault(row.parent, [get_invoice_row(row)])

        data = grouped.get(row.parent)

        new_row = copy.deepcopy(row)

        data.append(
                {
                    "indent": 1.0,
                    "brand": row.brand,
                    "sales_person": row.sales_person,
                    "parent_invoice": row.parent,
                    "sales_invoice": row.item_code,
                    "qty": row.qty,
                    "selling_total": row.total_selling_amount,
                    "buying_total": row.total_buying_amount,
                }
        )
        grouped.update({row.parent: data})

    si_list.clear()

    for items in grouped.values():
        si_list.extend(items)

    frappe.log_error("Group items by invoice", si_list)

    return si_list


def get_invoice_row(row):
    # header row format
    return frappe._dict(
        {
            "item": "",
            "indent": 0.0,
            "sales_invoice": row.sales_invoice,
            "parent": None,
            "date": row.date,
            "customer": row.customer,
            "customer_name": row.customer_name,
            "customer_group": row.customer_group,
            "customer_sub_group": row.customer_sub_group,
            "sales_person": row.sales_person,
            "month_and_year": row.month_and_year,
            "q_and_fy": row.q_and_fy,
            "year": row.year,
            "item_code": None,
            "description": None,
            "brand": None,
            "qty": None,
            "item_row": None,
            "qty": frappe.db.get_value(
                "NCS Sales Data", row.name, "total_qty"
            ),
            "selling_total": frappe.db.get_value(
                "NCS Sales Data", row.name, "selling_total"
            ),
            "buying_total": frappe.db.get_value(
                "NCS Sales Data", row.name, "buying_total"
            ),
        }
    )
