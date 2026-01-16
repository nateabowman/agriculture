# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class Farm(Document):
	def validate(self):
		self.validate_areas()
		self.calculate_areas()

	def validate_areas(self):
		"""Ensure area values are consistent"""
		if self.cultivable_area and self.total_area:
			if self.cultivable_area > self.total_area:
				frappe.throw(_("Cultivable area cannot exceed total area"))

		if self.irrigated_area and self.cultivable_area:
			if self.irrigated_area > self.cultivable_area:
				frappe.throw(_("Irrigated area cannot exceed cultivable area"))

	def calculate_areas(self):
		"""Auto-calculate rainfed area if not provided"""
		if self.cultivable_area and self.irrigated_area and not self.rainfed_area:
			self.rainfed_area = self.cultivable_area - self.irrigated_area

	def get_active_plots(self):
		"""Return list of active plots in this farm"""
		return frappe.get_all(
			"Plot",
			filters={"farm": self.name, "status": "Active"},
			fields=["name", "plot_name", "area", "current_crop"]
		)

	def get_active_crop_cycles(self):
		"""Return list of active crop cycles in this farm"""
		plots = self.get_active_plots()
		plot_names = [p.name for p in plots]
		
		if not plot_names:
			return []
		
		return frappe.get_all(
			"Crop Cycle",
			filters={"plot": ["in", plot_names], "docstatus": ["!=", 2]},
			fields=["name", "title", "crop", "start_date"]
		)
