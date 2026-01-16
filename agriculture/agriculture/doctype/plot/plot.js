// Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("Plot", {
	refresh(frm) {
		if (!frm.is_new()) {
			// View buttons
			frm.add_custom_button(__("Crop History"), function() {
				frappe.set_route("List", "Crop Cycle", {"plot": frm.doc.name});
			}, __("View"));

			frm.add_custom_button(__("Soil Analysis"), function() {
				frappe.set_route("List", "Soil Analysis", {"location": frm.doc.name});
			}, __("View"));

			// Create buttons
			frm.add_custom_button(__("New Crop Cycle"), function() {
				frappe.new_doc("Crop Cycle", {
					"plot": frm.doc.name,
					"farm": frm.doc.farm
				});
			}, __("Create"));

			frm.add_custom_button(__("Soil Analysis"), function() {
				frappe.new_doc("Soil Analysis", {"location": frm.doc.name});
			}, __("Create"));

			// Status indicators
			if (frm.doc.status === "Planted" && frm.doc.current_crop) {
				frm.dashboard.add_indicator(
					__("Currently Growing: {0}", [frm.doc.current_crop]),
					"green"
				);
			}
		}
	},

	farm(frm) {
		// Fetch farm's area UOM as default
		if (frm.doc.farm) {
			frappe.db.get_value("Farm", frm.doc.farm, "area_uom", (r) => {
				if (r && r.area_uom) {
					frm.set_value("area_uom", r.area_uom);
				}
			});
		}
	}
});
