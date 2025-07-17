// Copyright (c) 2025, TCB and contributors
// For license information, please see license.txt

frappe.ui.form.on('NCS Sales Plan', {
	refresh: function (frm) {
		if (frm.is_new()) {
			frm.add_custom_button("Generate Customer Code", (frm) => {
				frappe.call({
					method: "newcom_sales.newcom_sales_app.doctype.ncs_sales_plan.ncs_sales_plan.get_customer_code",
					callback: (resp) => {
						cur_frm.set_value("customer_code", resp.message)
						frappe.show_alert(
							{
								message: "Customer code updated",
								indicator: "green",
							},
							3
						);
					}
				})
			})
		}
	}
});
