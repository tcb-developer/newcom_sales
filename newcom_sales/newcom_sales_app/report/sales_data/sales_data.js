// Copyright (c) 2025, TCB and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Sales Data"] = {
	filters: [
		{
			fieldname: "customer",
			label: __("Customer"),
			fieldtype: "Link",
			options: "NCS Sales Plan",
		},
		{
			fieldname: "from_date",
			label: __("From Date"),
			fieldtype: "Date",
			default: erpnext.utils.get_fiscal_year(frappe.datetime.get_today(), true)[1],
			reqd: 1,
		},
		{
			fieldname: "to_date",
			label: __("To Date"),
			fieldtype: "Date",
			default: erpnext.utils.get_fiscal_year(frappe.datetime.get_today(), true)[2],
			reqd: 1,
		},
		{
			fieldname: "sales_invoice",
			label: __("Sales Invoice"),
			fieldtype: "Data",
		},
		{
			fieldname: "customer_group",
			label: __("Customer Group"),
			fieldtype: "Link",
			options: "Customer Group",
		},
		{
			fieldname: "customer_sub_group",
			label: __("Customer Sub Group"),
			fieldtype: "Link",
			options: "Customer Sub Group",
		},
		{
			fieldname: "sales_person",
			label: __("Sales Person"),
			fieldtype: "Link",
			options: "Sales Person",
		},
		{
			fieldname: "brand",
			label: __("Brand"),
			fieldtype: "Link",
			options: "Brand",
		},
	],
	tree: true,
	name_field: "sales_invoice",
	parent_field: "sales_invoice",
	initial_depth: 3,
	formatter: function (value, row, column, data, default_formatter) {
		if (column.fieldname == "sales_invoice" && column.options == "Brand" && data && data.indent == 0) {
			column._options = "Sales Invoice";
		} else {
			column._options = "";
		}
		value = default_formatter(value, row, column, data);

		if (data && (data.indent == 0.0 || (row[1] && row[1].content == "Total"))) {
			value = $(`<span>${value}</span>`);
			var $value = $(value).css("font-weight", "bold");
			value = $value.wrap("<p></p>").parent().html();
		}

		return value;
	},
};
