# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class AgriculturalInput(Document):
	def validate(self):
		self.validate_item_link()

	def validate_item_link(self):
		"""Create or link to ERPNext Item if not exists"""
		if not self.item and self.input_name:
			# Check if an item with this name exists
			existing_item = frappe.db.exists("Item", {"item_name": self.input_name})
			if existing_item:
				self.item = existing_item

	def create_linked_item(self):
		"""Create a linked Item in ERPNext inventory"""
		if self.item:
			return self.item

		item_group = self._get_item_group()
		
		item = frappe.get_doc({
			"doctype": "Item",
			"item_code": self.name,
			"item_name": self.input_name,
			"item_group": item_group,
			"stock_uom": "Nos",
			"is_stock_item": 1,
			"description": self.description
		})
		item.insert(ignore_permissions=True)
		
		self.item = item.name
		self.save()
		
		return item.name

	def _get_item_group(self):
		"""Determine item group based on input type"""
		group_mapping = {
			"Seed": "Seeds",
			"Fertilizer": "Fertilizers",
			"Pesticide": "Pesticides",
			"Herbicide": "Pesticides",
			"Fungicide": "Pesticides",
			"Insecticide": "Pesticides",
			"Animal Feed": "Animal Feed",
			"Veterinary Medicine": "Veterinary Supplies"
		}
		
		return group_mapping.get(self.input_type, "Agricultural Inputs")
