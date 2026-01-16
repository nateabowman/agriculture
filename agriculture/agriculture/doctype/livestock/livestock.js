// Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("Livestock", {
	refresh(frm) {
		if (!frm.is_new()) {
			// View Events
			frm.add_custom_button(__("Events"), function() {
				frappe.set_route("List", "Livestock Event", {"livestock": frm.doc.name});
			}, __("View"));

			// View Offspring
			frm.add_custom_button(__("Offspring"), function() {
				let filters = {};
				if (frm.doc.gender === "Female") {
					filters.dam = frm.doc.name;
				} else if (frm.doc.gender === "Male") {
					filters.sire = frm.doc.name;
				}
				frappe.set_route("List", "Livestock", filters);
			}, __("View"));

			// Create Events
			frm.add_custom_button(__("Record Event"), function() {
				frappe.new_doc("Livestock Event", {
					"livestock": frm.doc.name,
					"farm": frm.doc.farm
				});
			}, __("Create"));

			frm.add_custom_button(__("Record Weight"), function() {
				show_weight_dialog(frm);
			}, __("Create"));

			// Health actions
			if (frm.doc.gender === "Female" && !frm.doc.is_pregnant) {
				frm.add_custom_button(__("Mark Pregnant"), function() {
					show_pregnancy_dialog(frm);
				}, __("Actions"));
			}
		}

		// Show age indicator
		if (frm.doc.age_months) {
			let years = Math.floor(frm.doc.age_months / 12);
			let months = frm.doc.age_months % 12;
			let age_str = years > 0 ? `${years}y ${months}m` : `${months}m`;
			frm.dashboard.add_indicator(__("Age: {0}", [age_str]), "blue");
		}

		// Show health status
		if (frm.doc.health_status) {
			let color = {
				"Healthy": "green",
				"Sick": "red",
				"Under Treatment": "orange",
				"Recovering": "yellow",
				"Quarantined": "red",
				"Critical": "red"
			}[frm.doc.health_status] || "gray";
			frm.dashboard.add_indicator(frm.doc.health_status, color);
		}
	},

	livestock_type(frm) {
		if (frm.doc.livestock_type) {
			frappe.db.get_doc("Livestock Type", frm.doc.livestock_type).then(lt => {
				if (lt.weight_uom) {
					frm.set_value("weight_uom", lt.weight_uom);
				}
			});
		}
	},

	is_batch(frm) {
		if (frm.doc.is_batch) {
			frm.set_value("gender", "Mixed (Batch)");
		}
	}
});

function show_weight_dialog(frm) {
	let d = new frappe.ui.Dialog({
		title: __("Record Weight"),
		fields: [
			{
				fieldname: "weight",
				fieldtype: "Float",
				label: "Weight",
				reqd: 1
			},
			{
				fieldname: "date",
				fieldtype: "Date",
				label: "Date",
				default: frappe.datetime.nowdate()
			}
		],
		primary_action_label: __("Record"),
		primary_action(values) {
			frappe.call({
				method: "record_weight",
				doc: frm.doc,
				args: {
					weight: values.weight,
					date: values.date
				},
				callback: function(r) {
					frm.reload_doc();
					d.hide();
				}
			});
		}
	});
	d.show();
}

function show_pregnancy_dialog(frm) {
	let d = new frappe.ui.Dialog({
		title: __("Record Pregnancy"),
		fields: [
			{
				fieldname: "expected_date",
				fieldtype: "Date",
				label: "Expected Delivery Date",
				reqd: 1
			},
			{
				fieldname: "sire",
				fieldtype: "Link",
				label: "Sire (Father)",
				options: "Livestock",
				filters: {
					gender: "Male",
					livestock_type: frm.doc.livestock_type
				}
			}
		],
		primary_action_label: __("Confirm"),
		primary_action(values) {
			frm.set_value("is_pregnant", 1);
			frm.set_value("expected_delivery_date", values.expected_date);
			frm.save().then(() => {
				d.hide();
			});
		}
	});
	d.show();
}
