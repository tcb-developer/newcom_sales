// Copyright (c) 2025, TCB and contributors
// For license information, please see license.txt

frappe.ui.form.on('NCS Sales Data', {
	refresh: function (frm) {

	}
});

frappe.ui.form.on('NCS Sales Data Item', {
	qty: function (frm, cdt, cdn) {
		handleCalculations(frm, cdt, cdn);
	},
	buying_rate: function (frm, cdt, cdn) {
		handleCalculations(frm, cdt, cdn);
	},
	selling_rate: function (frm, cdt, cdn) {
		handleCalculations(frm, cdt, cdn);
	},
	buying_rate: function (frm, cdt, cdn) {
		handleCalculations(frm, cdt, cdn);
	},
});

// Utils Start
function cleanValue(variable, default_value) {
	return variable
		? variable
		: default_value || isNaN(variable)
			? default_value
			: variable;
}

function getAttr(obj, key, default_value = null) {
	key = key.trim();
	try {
		return cleanValue(obj[key], default_value);
	} catch (err) {
		return default_value;
	}
}

function isObjectsEquel(obj1, obj2) {
	return JSON.stringify(obj1) === JSON.stringify(obj2)
}
// Utils End

function handleCalculations(frm, cdt, cdn) {
	// let child = locals[cdt][cdn];
	// let qty = getAttr(child, "qty", 0);
	// let selling_rate = getAttr(child, "selling_rate", 0);
	// let buying_rate = getAttr(child, "buying_rate", 0);
	// let total_selling_amount = selling_rate * qty;
	// let total_buying_amount = buying_rate * qty;
	// let gross_profit = total_selling_amount - total_buying_amount;

	// frappe.model.set_value(cdt, cdn, "total_selling_amount", total_selling_amount)
	// frappe.model.set_value(cdt, cdn, "total_buying_amount", total_buying_amount)
	// frappe.model.set_value(cdt, cdn, "gross_profit", gross_profit)

	let items = frm.doc.items || [];
	if (items) {
		items.forEach(item => {
			let qty = getAttr(item, "qty", 0);
			let selling_rate = getAttr(item, "selling_rate", 0);
			let buying_rate = getAttr(item, "buying_rate", 0);
			let total_selling_amount = selling_rate * qty;
			let total_buying_amount = buying_rate * qty;
			let gross_profit = total_selling_amount - total_buying_amount;
			frappe.model.set_value(item.doctype, item.name, "total_selling_amount", total_selling_amount)
			frappe.model.set_value(item.doctype, item.name, "total_buying_amount", total_buying_amount)
			frappe.model.set_value(item.doctype, item.name, "gross_profit", gross_profit)
		})
	}
}