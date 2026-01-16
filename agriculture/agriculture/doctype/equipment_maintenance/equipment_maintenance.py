# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class EquipmentMaintenance(Document):
	def validate(self):
		self.calculate_costs()

	def on_update(self):
		self.update_equipment()

	def calculate_costs(self):
		"""Calculate total costs"""
		parts_cost = 0
		if self.parts_replaced:
			for part in self.parts_replaced:
				parts_cost += part.amount or 0
		
		self.parts_cost = parts_cost
		self.total_cost = (self.labor_cost or 0) + parts_cost + (self.other_cost or 0)

	def update_equipment(self):
		"""Update equipment record after maintenance"""
		if self.status == "Completed" and self.equipment:
			equipment = frappe.get_doc("Equipment", self.equipment)
			equipment.last_maintenance_date = self.completed_date or self.maintenance_date
			
			if self.hours_at_service:
				equipment.hours_meter_reading = self.hours_at_service
				equipment.last_reading_date = self.maintenance_date
			
			if self.next_service_date:
				equipment.next_maintenance_date = self.next_service_date
			
			equipment.status = "Active"
			equipment.save()
