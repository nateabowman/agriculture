# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe

no_cache = 1


def get_context(context):
	context.no_cache = 1
	context.show_sidebar = False
	
	if frappe.session.user != "Guest":
		context.farms = frappe.get_all(
			"Farm",
			fields=["name", "farm_name", "total_area", "status"],
			limit=10
		)
