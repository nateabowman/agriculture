# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt


class FarmingContract(Document):
	def validate(self):
		self.calculate_totals()
		self.calculate_advance()
		self.validate_dates()

	def calculate_totals(self):
		"""Calculate total quantity and value from crops"""
		total_qty = 0
		total_value = 0
		
		for crop in self.crops:
			total_qty += flt(crop.quantity)
			total_value += flt(crop.amount)
		
		self.total_quantity = total_qty
		self.total_value = total_value

	def calculate_advance(self):
		"""Calculate advance amount"""
		if self.advance_percentage and self.total_value:
			self.advance_amount = self.total_value * self.advance_percentage / 100

	def validate_dates(self):
		"""Validate contract dates"""
		if self.start_date and self.end_date:
			if self.start_date > self.end_date:
				frappe.throw(_("Growing season end date must be after start date"))
		
		if self.delivery_start_date and self.delivery_end_date:
			if self.delivery_start_date > self.delivery_end_date:
				frappe.throw(_("Delivery end date must be after start date"))

	def create_sales_order(self):
		"""Create Sales Order from this contract"""
		if not self.customer:
			frappe.throw(_("Customer is required to create Sales Order"))
		
		so = frappe.new_doc("Sales Order")
		so.customer = self.customer
		so.delivery_date = self.delivery_start_date
		so.po_no = self.name
		
		for crop in self.crops:
			if crop.item:
				so.append("items", {
					"item_code": crop.item,
					"qty": crop.quantity,
					"rate": crop.rate
				})
		
		so.insert()
		return so.name

	def link_to_crm_opportunity(self, opportunity):
		"""Link contract to CRM opportunity"""
		self.opportunity = opportunity
		self.save()
		
		# Update opportunity status
		opp = frappe.get_doc("Opportunity", opportunity)
		opp.status = "Converted"
		opp.save()
