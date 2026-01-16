# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class Plot(Document):
	def validate(self):
		self.validate_area()
		self.update_farm_area()

	def validate_area(self):
		"""Ensure plot area doesn't exceed farm's total area"""
		if self.farm and self.area:
			farm = frappe.get_doc("Farm", self.farm)
			total_plot_area = frappe.db.sql("""
				SELECT SUM(area) FROM `tabPlot` 
				WHERE farm = %s AND name != %s AND area_uom = %s
			""", (self.farm, self.name or "", self.area_uom))[0][0] or 0
			
			if total_plot_area + self.area > farm.total_area:
				frappe.msgprint(
					_("Total plot area ({0}) may exceed farm's total area ({1})").format(
						total_plot_area + self.area, farm.total_area
					),
					indicator="orange",
					alert=True
				)

	def update_farm_area(self):
		"""Update farm's cultivable area based on plots"""
		pass  # Can be implemented to auto-update farm areas

	def set_current_crop(self, crop, crop_cycle):
		"""Set the current crop and cycle for this plot"""
		self.current_crop = crop
		self.current_crop_cycle = crop_cycle
		self.status = "Planted"
		self.save()

	def clear_current_crop(self):
		"""Clear the current crop when harvest is complete"""
		self.current_crop = None
		self.current_crop_cycle = None
		self.status = "Available"
		self.save()

	def get_crop_history(self, limit=10):
		"""Get history of crops grown on this plot"""
		return frappe.get_all(
			"Crop Cycle",
			filters={"plot": self.name},
			fields=["name", "crop", "start_date", "end_date", "title"],
			order_by="start_date desc",
			limit=limit
		)

	def get_soil_analysis_history(self, limit=5):
		"""Get recent soil analysis for this plot"""
		return frappe.get_all(
			"Soil Analysis",
			filters={"location": self.name},
			fields=["name", "collection_datetime"],
			order_by="collection_datetime desc",
			limit=limit
		)
