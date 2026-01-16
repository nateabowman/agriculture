# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import date_diff, getdate, nowdate, add_days


class Livestock(Document):
	def validate(self):
		self.calculate_age()
		self.validate_parentage()
		self.validate_batch()
		self.validate_pregnancy()

	def calculate_age(self):
		"""Calculate age in months from birth date"""
		if self.birth_date:
			days = date_diff(nowdate(), self.birth_date)
			self.age_months = int(days / 30)

	def validate_parentage(self):
		"""Validate dam and sire relationships"""
		if self.dam:
			dam = frappe.get_doc("Livestock", self.dam)
			if dam.gender != "Female":
				frappe.throw(_("Dam must be female"))
			if dam.livestock_type != self.livestock_type:
				frappe.throw(_("Dam must be of the same livestock type"))

		if self.sire:
			sire = frappe.get_doc("Livestock", self.sire)
			if sire.gender != "Male":
				frappe.throw(_("Sire must be male"))
			if sire.livestock_type != self.livestock_type:
				frappe.throw(_("Sire must be of the same livestock type"))

	def validate_batch(self):
		"""Validate batch-specific fields"""
		if self.is_batch and not self.batch_quantity:
			frappe.throw(_("Batch quantity is required for batch tracking"))
		
		if not self.is_batch:
			self.batch_quantity = None
			self.batch_weight = None

	def validate_pregnancy(self):
		"""Validate pregnancy information"""
		if self.is_pregnant and self.gender != "Female":
			frappe.throw(_("Only female animals can be marked as pregnant"))

	def get_offspring(self):
		"""Get list of offspring for this animal"""
		offspring = []
		if self.gender == "Female":
			offspring = frappe.get_all(
				"Livestock",
				filters={"dam": self.name},
				fields=["name", "animal_name", "birth_date", "gender", "status"]
			)
		elif self.gender == "Male":
			offspring = frappe.get_all(
				"Livestock",
				filters={"sire": self.name},
				fields=["name", "animal_name", "birth_date", "gender", "status"]
			)
		return offspring

	def get_events(self, limit=20):
		"""Get recent events for this animal"""
		return frappe.get_all(
			"Livestock Event",
			filters={"livestock": self.name},
			fields=["name", "event_type", "event_date", "description"],
			order_by="event_date desc",
			limit=limit
		)

	def record_weight(self, weight, date=None):
		"""Record a new weight measurement"""
		self.current_weight = weight
		self.last_weighed_date = date or nowdate()
		self.save()

		# Create weight event
		frappe.get_doc({
			"doctype": "Livestock Event",
			"livestock": self.name,
			"event_type": "Weight Record",
			"event_date": self.last_weighed_date,
			"description": f"Weight recorded: {weight} {self.weight_uom}"
		}).insert()
