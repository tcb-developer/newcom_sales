// Copyright (c) 2025, TCB and contributors
// For license information, please see license.txt

frappe.ui.form.on('The Delete Feature', {
	refresh: function (frm) {

	},
	delete_all_data_button: function (frm) {
		frappe.call({
			method: "delete_all_records",
			doc: frm.doc,
			args: {
				doctype_name: frm.doc.doctype_name,
			},
			callback: (resp) => {

			},
		});
	}
});
