# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate, nowdate


class SeedLot(Document):
	def validate(self):
		self.set_current_quantity()
		self.check_expiry()

	def set_current_quantity(self):
		"""Set current quantity to initial if not set"""
		if not self.current_quantity:
			self.current_quantity = self.initial_quantity

	def check_expiry(self):
		"""Check if seed lot is expired"""
		if self.expiry_date and getdate(self.expiry_date) < getdate(nowdate()):
			if self.status not in ["Expired", "Discarded", "Exhausted"]:
				self.status = "Expired"
				frappe.msgprint(_("This seed lot has expired"), indicator="red", alert=True)

	def consume(self, quantity, crop_cycle=None):
		"""Consume seeds from this lot"""
		if quantity > self.current_quantity:
			frappe.throw(_("Cannot consume {0}. Only {1} available").format(
				quantity, self.current_quantity
			))
		
		self.current_quantity -= quantity
		
		if self.current_quantity <= 0:
			self.status = "Exhausted"
		
		self.save()
		
		# Log consumption
		frappe.get_doc({
			"doctype": "Comment",
			"comment_type": "Info",
			"reference_doctype": "Seed Lot",
			"reference_name": self.name,
			"content": f"Consumed {quantity} {self.quantity_uom}" + 
				(f" for Crop Cycle: {crop_cycle}" if crop_cycle else "")
		}).insert(ignore_permissions=True)
		
		return self.current_quantity

	def get_quality_status(self):
		"""Return quality status based on germination rate"""
		if not self.germination_rate:
			return "Unknown"
		
		if self.germination_rate >= 85:
			return "Excellent"
		elif self.germination_rate >= 70:
			return "Good"
		elif self.germination_rate >= 50:
			return "Fair"
		else:
			return "Poor"
