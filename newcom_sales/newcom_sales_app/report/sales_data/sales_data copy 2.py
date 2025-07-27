# Copyright (c) 2025, TCB and contributors
# For license information, please see license.txt

import frappe
from frappe import _, scrub
from collections import OrderedDict
import copy
from frappe.utils import cstr, flt


def execute(filters={}):
    columns = get_columns(filters=filters)
    si_list = get_si_list(filters=filters)
    data = group_items_by_invoice(si_list)
    return columns, data


def get_columns(filters={}):
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
        # {
        #     "label": _("Customer Group"),
        #     "fieldname": "customer_group",
        #     "fieldtype": "Link",
        #     "options": "Customer Group",
        #     "width": 100,
        # },
        # {
        #     "label": _("Customer Sub Group"),
        #     "fieldname": "customer_sub_group",
        #     "fieldtype": "Link",
        #     "options": "Customer Sub Group",
        #     "width": 200,
        # },
        {
            "label": _("Sales Person"),
            "fieldname": "sales_person",
            "fieldtype": "Link",
            "options": "Sales Person",
            "width": 140,
        },
        # {
        #     "label": _("Sales Invoice / Item"),
        #     "fieldname": "sales_invoice",
        #     "fieldtype": "Data",
        #     "width": 150,
        # },
        {
            "label": _("Brand"),
            "fieldname": "brand",
            "fieldtype": "Link",
            "options": "Brand",
            "width": 120,
        },
        # {
        #     "label": _("Qty"),
        #     "fieldname": "qty",
        #     "fieldtype": "Float",
        #     "width": 150,
        # },
        # {
        #     "label": _("Selling Total"),
        #     "fieldname": "selling_total",
        #     "fieldtype": "Currency",
        #     "width": 150,
        # },
        # {
        #     "label": _("Buying Total"),
        #     "fieldname": "buying_total",
        #     "fieldtype": "Currency",
        #     "width": 150,
        # },
        # {
        #     "label": _("Date"),
        #     "fieldname": "date",
        #     "fieldtype": "Date",
        #     "width": 100,
        # },
        # {
        #     "label": _("Year"),
        #     "fieldname": "year",
        #     "fieldtype": "Data",
        #     "width": 100,
        # },
        # {
        #     "label": _("Month & Year"),
        #     "fieldname": "month_and_year",
        #     "fieldtype": "Data",
        #     "width": 150,
        # },
        # {
        #     "label": _("Q & FY"),
        #     "fieldname": "q_and_fy",
        #     "fieldtype": "Data",
        #     "width": 100,
        # },
    ]

    year_columns = get_year_columns(filters=filters)
    if year_columns:
        columns.extend(year_columns)

    return columns


def get_year_columns(filters={}):
    doctype = "NCS Sales Data"
    si = frappe.qb.DocType(doctype)

    # Query
    query = (
        frappe.qb.from_(si)
        .select(
            si.year,
        )
        .groupby(si.year)
        .orderby(si.year)
    )

    base_condition = si.docstatus == 1

    if filters.get("from_date"):
        base_condition &= si.date >= filters.get("from_date")

    if filters.get("to_date"):
        base_condition &= si.date <= filters.get("to_date")

    query = query.where(base_condition)
    results = query.run(as_dict=True)

    columns = []
    if results:
        frappe.log_error("Year column results", results)
        for result in results:
            label = result.get("year")
            column = {
                "label": _(f"{label} Sale"),
                "fieldname": scrub(label),
                "fieldtype": "Currency",
                "width": 180,
            }

            columns.append(column)

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

    # base_condition = si.docstatus == 1
    base_condition = si.docstatus.isin([0, 1])

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

    customer_total = OrderedDict()
    brand_total = frappe._dict({})

    for row in si_list:
        grouped.setdefault(row.customer, [get_invoice_row(row)])
        customer_total.setdefault(row.customer, 0)
        brand_total.setdefault(row.brand, frappe._dict({})).setdefault(row.customer, 0)

        data = grouped.get(row.customer)

        new_row = copy.deepcopy(row)

        year_field = "year"
        if row.year:
            year_field = scrub(row.year)

        data.append(
                {
                    "indent": 1.0,
                    "brand": row.brand,
                    year_field: row.total_selling_amount,
                    "parent": row.customer,
                    "customer": "-",
                    "customer_name": "-",
                    # "qty": row.qty,
                    # "selling_total": row.total_selling_amount,
                    # "buying_total": row.total_buying_amount,
                    "total_selling_amount": row.total_selling_amount,
                    "year": row.year,
                    "customer_org": row.customer,
                }
        )
        grouped.update({row.customer: data})

    si_list.clear()

    for customer, items in grouped.items():
        c_total = customer_total.get(customer)

        for item in items:
            c_total += flt(item.get("total_selling_amount"))

            brand = item.get("brand")
            b_total_data = brand_total.get(brand)
            if b_total_data:
                b_c_total = flt(b_total_data.get(customer))
                b_c_total += flt(item.get("total_selling_amount"))

                b_total_data.update({customer: b_c_total})
                brand_total.update({brand: b_total_data})

        # c_total = sum([flt(item.get("total_selling_amount")) for item in items])
        si_list.extend(items)
        customer_total.update({customer: c_total})

    new_si_list = []
    for row in si_list:
        year_field = "year"
        if row.get("year"):
            year_field = scrub(row.get("year"))

        indent = row.get("indent")
        brand = row.get("brand")

        if indent == 0.0:
            row[year_field] = customer_total.get(row.get("customer"))
            new_si_list.append(row)

        b_c_total = 0
        if indent == 1.0:
            b_total_data = brand_total.get(brand)
            if b_total_data:
                b_c_total = b_total_data.get(row.get("customer_org"))
                if b_c_total:
                    row[year_field] = flt(b_c_total)

                    del b_total_data[row.get("customer_org")]
                    new_si_list.append(row)



    frappe.log_error("Brand total data", brand_total)
    frappe.log_error("Customer total data", customer_total)

    frappe.log_error("Group items by invoice", si_list)

    # return si_list
    return new_si_list


def get_invoice_row(row):
    # header row format
    year_field = "year"
    if row.year:
        year_field = scrub(row.year)
    return frappe._dict(
        {
            "indent": 0.0,
            "customer": row.customer,
            "customer_name": row.customer_name,
            year_field: frappe.db.get_value(
                "NCS Sales Data", row.name, "selling_total"
            ),
            "brand": "All",
            "parent": None,
            "sales_person": row.sales_person,
            "total_selling_amount": row.total_selling_amount,
            "year": row.year,
            # "qty": frappe.db.get_value(
            #     "NCS Sales Data", row.name, "total_qty"
            # ),
            # "selling_total": frappe.db.get_value(
            #     "NCS Sales Data", row.name, "selling_total"
            # ),
            # "buying_total": frappe.db.get_value(
            #     "NCS Sales Data", row.name, "buying_total"
            # ),
        }
    )
