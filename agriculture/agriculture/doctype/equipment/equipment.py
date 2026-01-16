# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import add_days, getdate, nowdate


class Equipment(Document):
	def validate(self):
		self.calculate_next_maintenance()
		self.update_total_maintenance_cost()

	def calculate_next_maintenance(self):
		"""Calculate next maintenance date based on intervals"""
		if self.last_maintenance_date and self.maintenance_interval_days:
			self.next_maintenance_date = add_days(
				self.last_maintenance_date, 
				self.maintenance_interval_days
			)

	def update_total_maintenance_cost(self):
		"""Calculate total maintenance cost from maintenance records"""
		total = frappe.db.sql("""
			SELECT SUM(total_cost) FROM `tabEquipment Maintenance`
			WHERE equipment = %s AND docstatus != 2
		""", self.name)[0][0] or 0
		
		self.total_maintenance_cost = total

	def get_maintenance_history(self, limit=10):
		"""Get maintenance history for this equipment"""
		return frappe.get_all(
			"Equipment Maintenance",
			filters={"equipment": self.name},
			fields=["name", "maintenance_type", "maintenance_date", "total_cost"],
			order_by="maintenance_date desc",
			limit=limit
		)

	def is_maintenance_due(self):
		"""Check if maintenance is due"""
		if self.next_maintenance_date:
			return getdate(self.next_maintenance_date) <= getdate(nowdate())
		return False

	def record_hours(self, hours, date=None):
		"""Record new hours meter reading"""
		self.hours_meter_reading = hours
		self.last_reading_date = date or nowdate()
		self.save()
