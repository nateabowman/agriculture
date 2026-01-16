# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import nowdate, nowtime


class FieldTask(Document):
	def validate(self):
		self.update_status_based_on_dates()

	def on_update(self):
		if self.status == "Completed":
			self.mark_completed()

	def update_status_based_on_dates(self):
		"""Auto-update status based on completion"""
		if self.completed_date and self.status not in ["Completed", "Cancelled"]:
			self.status = "Completed"

	def mark_completed(self):
		"""Mark task as completed with timestamp"""
		if not self.completed_date:
			self.completed_date = nowdate()
		if not self.completed_time:
			self.completed_time = nowtime()

	def start_task(self):
		"""Mark task as in progress"""
		self.status = "In Progress"
		self.save()

	def complete_task(self, notes=None, quantity=None):
		"""Complete the task"""
		self.status = "Completed"
		self.completed_date = nowdate()
		self.completed_time = nowtime()
		
		if notes:
			self.completion_notes = notes
		if quantity:
			self.completed_quantity = quantity
		
		self.save()

	def calculate_piece_rate_payment(self):
		"""Calculate payment for piece rate tasks"""
		if self.is_piece_rate and self.completed_quantity and self.rate_per_unit:
			return self.completed_quantity * self.rate_per_unit
		return 0
