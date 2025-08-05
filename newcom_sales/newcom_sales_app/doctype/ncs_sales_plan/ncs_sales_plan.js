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

		if (!frm.doc.__islocal) {
			frappe.dynamic_link = { doc: frm.doc, fieldname: "name", doctype: frm.doctype };
			frm.trigger("render_ncs_contact");
		}
	},
	validate: function (frm) {
		// clear linked customer / supplier / sales partner on saving...
		if (frm.doc.links) {
			frm.doc.links.forEach(function (d) {
				frappe.model.remove_from_locals(d.link_doctype, d.link_name);
			});
		}
	},
	after_save: function (frm) {
		frappe.run_serially([
			() => frappe.timeout(1),
			() => {
				const last_doc = frappe.contacts.get_last_doc(frm);
				if (
					frappe.dynamic_link &&
					frappe.dynamic_link.doc &&
					frappe.dynamic_link.doc.name == last_doc.docname
				) {
					for (let i in frm.doc.links) {
						let link = frm.doc.links[i];
						if (
							last_doc.doctype == link.link_doctype &&
							last_doc.docname == link.link_name
						) {
							frappe.set_route("Form", last_doc.doctype, last_doc.docname);
						}
					}
				}
			},
		]);
	},

	render_ncs_contact: function (frm) {
		// render ncs contact
		if (frm.fields_dict["ncs_contact_html"] && "ncs_contact_list" in frm.doc.__onload) {
			$(frm.fields_dict["ncs_contact_html"].wrapper)
				.html(frappe.render_template("ncs_contact", frm.doc.__onload))
				.find(".btn-address")
				.on("click", function () {
					frappe.new_doc("NCS Customer Contact");
				});
		}
	},
});
