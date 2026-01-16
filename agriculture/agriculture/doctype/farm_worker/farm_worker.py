# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class FarmWorker(Document):
	def validate(self):
		self.sync_from_employee()

	def sync_from_employee(self):
		"""Sync data from linked HRMS Employee"""
		if self.employee and not self.worker_name:
			emp = frappe.get_doc("Employee", self.employee)
			self.worker_name = emp.employee_name
			self.phone = emp.cell_number
			self.email = emp.personal_email or emp.company_email
			self.user = emp.user_id

	def get_assigned_tasks(self, status=None):
		"""Get tasks assigned to this worker"""
		filters = {"assigned_to": self.name}
		if status:
			filters["status"] = status
		
		return frappe.get_all(
			"Field Task",
			filters=filters,
			fields=["name", "task_type", "farm", "plot", "scheduled_date", "status"]
		)

	def calculate_earnings(self, from_date, to_date):
		"""Calculate earnings for a period"""
		# This would integrate with attendance and piece-rate records
		pass
