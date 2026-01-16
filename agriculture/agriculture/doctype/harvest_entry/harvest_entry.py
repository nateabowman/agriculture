# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, nowdate, nowtime


class HarvestEntry(Document):
	def validate(self):
		self.calculate_totals()
		self.set_posting_datetime()

	def on_submit(self):
		if self.create_stock_entry:
			self.create_stock_entry_doc()
		self.update_crop_cycle_yield()

	def on_cancel(self):
		if self.stock_entry:
			se = frappe.get_doc("Stock Entry", self.stock_entry)
			if se.docstatus == 1:
				se.cancel()

	def calculate_totals(self):
		"""Calculate total quantity and value from items"""
		total_qty = 0
		total_value = 0
		
		for item in self.items:
			total_qty += flt(item.quantity)
			total_value += flt(item.amount)
		
		self.total_quantity = total_qty
		self.total_value = total_value

	def set_posting_datetime(self):
		"""Set posting date and time if not provided"""
		if not self.posting_date:
			self.posting_date = self.harvest_date or nowdate()
		if not self.posting_time:
			self.posting_time = self.harvest_time or nowtime()

	def create_stock_entry_doc(self):
		"""Create Stock Entry for harvested produce"""
		if not self.target_warehouse:
			frappe.throw(_("Target Warehouse is required to create Stock Entry"))

		se = frappe.new_doc("Stock Entry")
		se.stock_entry_type = "Material Receipt"
		se.posting_date = self.posting_date
		se.posting_time = self.posting_time
		se.set_posting_time = 1

		for item in self.items:
			if item.item_code:
				se.append("items", {
					"item_code": item.item_code,
					"qty": item.quantity,
					"uom": item.uom,
					"t_warehouse": self.target_warehouse,
					"basic_rate": item.rate or 0
				})

		if se.items:
			se.insert()
			se.submit()
			self.stock_entry = se.name
			self.db_set("stock_entry", se.name)
			frappe.msgprint(_("Stock Entry {0} created").format(se.name))

	def update_crop_cycle_yield(self):
		"""Update the crop cycle's actual yield"""
		if self.crop_cycle:
			cycle = frappe.get_doc("Crop Cycle", self.crop_cycle)
			
			# Get total harvested for this cycle
			total_harvested = frappe.db.sql("""
				SELECT SUM(total_quantity) 
				FROM `tabHarvest Entry` 
				WHERE crop_cycle = %s AND docstatus = 1
			""", self.crop_cycle)[0][0] or 0
			
			cycle.actual_yield = total_harvested
			cycle.save()
