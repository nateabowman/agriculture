// Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("Farm", {
	refresh(frm) {
		if (!frm.is_new()) {
			frm.add_custom_button(__("View Plots"), function() {
				frappe.set_route("List", "Plot", {"farm": frm.doc.name});
			}, __("View"));

			frm.add_custom_button(__("View Crop Cycles"), function() {
				frappe.set_route("List", "Crop Cycle", {"farm": frm.doc.name});
			}, __("View"));

			frm.add_custom_button(__("View Livestock"), function() {
				frappe.set_route("List", "Livestock", {"farm": frm.doc.name});
			}, __("View"));

			frm.add_custom_button(__("New Plot"), function() {
				frappe.new_doc("Plot", {"farm": frm.doc.name});
			}, __("Create"));
		}
	},

	total_area(frm) {
		if (frm.doc.total_area && !frm.doc.cultivable_area) {
			frm.set_value("cultivable_area", frm.doc.total_area);
		}
	},

	cultivable_area(frm) {
		calculate_rainfed_area(frm);
	},

	irrigated_area(frm) {
		calculate_rainfed_area(frm);
	}
});

function calculate_rainfed_area(frm) {
	if (frm.doc.cultivable_area && frm.doc.irrigated_area) {
		let rainfed = frm.doc.cultivable_area - frm.doc.irrigated_area;
		if (rainfed >= 0) {
			frm.set_value("rainfed_area", rainfed);
		}
	}
}
