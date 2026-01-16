// Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("Equipment", {
	refresh(frm) {
		if (!frm.is_new()) {
			// View buttons
			frm.add_custom_button(__("Maintenance History"), function() {
				frappe.set_route("List", "Equipment Maintenance", {"equipment": frm.doc.name});
			}, __("View"));

			// Create buttons
			frm.add_custom_button(__("Schedule Maintenance"), function() {
				frappe.new_doc("Equipment Maintenance", {
					"equipment": frm.doc.name,
					"farm": frm.doc.farm
				});
			}, __("Create"));

			frm.add_custom_button(__("Record Hours"), function() {
				show_hours_dialog(frm);
			}, __("Create"));

			// Status indicators
			if (frm.doc.status === "Under Maintenance") {
				frm.dashboard.add_indicator(__("Under Maintenance"), "orange");
			}

			// Maintenance due warning
			if (frm.doc.next_maintenance_date) {
				let due_date = frappe.datetime.str_to_obj(frm.doc.next_maintenance_date);
				let today = frappe.datetime.str_to_obj(frappe.datetime.nowdate());
				
				if (due_date <= today) {
					frm.dashboard.add_indicator(__("Maintenance Overdue!"), "red");
				} else {
					let days_until = frappe.datetime.get_diff(due_date, today);
					if (days_until <= 7) {
						frm.dashboard.add_indicator(
							__("Maintenance Due in {0} days", [days_until]), 
							"orange"
						);
					}
				}
			}

			// Insurance expiry warning
			if (frm.doc.insurance_expiry_date) {
				let expiry = frappe.datetime.str_to_obj(frm.doc.insurance_expiry_date);
				let today = frappe.datetime.str_to_obj(frappe.datetime.nowdate());
				
				if (expiry <= today) {
					frm.dashboard.add_indicator(__("Insurance Expired!"), "red");
				} else {
					let days_until = frappe.datetime.get_diff(expiry, today);
					if (days_until <= 30) {
						frm.dashboard.add_indicator(
							__("Insurance expires in {0} days", [days_until]), 
							"orange"
						);
					}
				}
			}
		}
	}
});

function show_hours_dialog(frm) {
	let d = new frappe.ui.Dialog({
		title: __("Record Hours"),
		fields: [
			{
				fieldname: "hours",
				fieldtype: "Float",
				label: "Hours Meter Reading",
				reqd: 1,
				default: frm.doc.hours_meter_reading
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
				method: "record_hours",
				doc: frm.doc,
				args: {
					hours: values.hours,
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
