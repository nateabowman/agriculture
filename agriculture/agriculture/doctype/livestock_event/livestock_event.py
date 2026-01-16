# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import add_days


class LivestockEvent(Document):
	def validate(self):
		self.set_farm()

	def after_insert(self):
		self.update_livestock_status()
		self.schedule_followup()

	def set_farm(self):
		"""Set farm from livestock if not provided"""
		if self.livestock and not self.farm:
			self.farm = frappe.db.get_value("Livestock", self.livestock, "farm")

	def update_livestock_status(self):
		"""Update livestock record based on event type"""
		livestock = frappe.get_doc("Livestock", self.livestock)
		
		if self.event_type == "Death":
			livestock.status = "Deceased"
			livestock.save()
		
		elif self.event_type == "Sale":
			livestock.status = "Sold"
			livestock.disposal_type = "Sold"
			livestock.disposal_date = self.event_date
			livestock.save()
		
		elif self.event_type == "Vaccination":
			livestock.vaccination_status = "Up to Date"
			livestock.save()
		
		elif self.event_type == "Health Check":
			livestock.last_checkup_date = self.event_date
			if self.next_followup_date:
				livestock.next_checkup_date = self.next_followup_date
			livestock.save()
		
		elif self.event_type == "Pregnancy Confirmed":
			livestock.is_pregnant = 1
			livestock.save()
		
		elif self.event_type == "Birth Given":
			livestock.is_pregnant = 0
			livestock.expected_delivery_date = None
			livestock.save()
		
		elif self.event_type == "Weight Record":
			# Weight is usually recorded separately with specific value
			pass

	def schedule_followup(self):
		"""Create a todo for follow-up if date is set"""
		if self.next_followup_date and self.performed_by:
			frappe.get_doc({
				"doctype": "ToDo",
				"description": f"Follow-up for {self.livestock}: {self.event_type}",
				"reference_type": "Livestock Event",
				"reference_name": self.name,
				"date": self.next_followup_date,
				"allocated_to": self.performed_by
			}).insert(ignore_permissions=True)
