# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt


class CropBudget(Document):
	def validate(self):
		self.calculate_totals()
		self.calculate_per_hectare()
		self.calculate_revenue_metrics()

	def calculate_totals(self):
		"""Calculate all budget totals"""
		# Input costs
		self.total_input_budget = flt(self.seed_budget) + flt(self.fertilizer_budget) + \
			flt(self.pesticide_budget) + flt(self.herbicide_budget) + flt(self.other_input_budget)
		
		# Operations costs
		self.total_operations_budget = flt(self.land_prep_budget) + flt(self.planting_budget) + \
			flt(self.irrigation_budget) + flt(self.harvesting_budget) + flt(self.post_harvest_budget)
		
		# Labor & Equipment
		self.total_labor_equipment = flt(self.labor_budget) + flt(self.equipment_budget) + \
			flt(self.transport_budget)
		
		# Subtotal before overhead
		subtotal = self.total_input_budget + self.total_operations_budget + self.total_labor_equipment
		
		# Contingency
		if self.contingency_percent:
			self.contingency_amount = subtotal * self.contingency_percent / 100
		
		# Overhead
		self.total_overhead = flt(self.overhead_budget) + flt(self.contingency_amount) + \
			flt(self.interest_cost) + flt(self.insurance_cost)
		
		# Total cost
		self.total_cost_budget = subtotal + self.total_overhead

	def calculate_per_hectare(self):
		"""Calculate cost and revenue per hectare"""
		if self.planned_area and self.planned_area > 0:
			self.cost_per_hectare = self.total_cost_budget / self.planned_area
			if self.expected_revenue:
				self.revenue_per_hectare = self.expected_revenue / self.planned_area

	def calculate_revenue_metrics(self):
		"""Calculate revenue, profit, ROI"""
		# Expected revenue
		if self.expected_yield and self.expected_price:
			self.expected_revenue = self.expected_yield * self.expected_price
		
		# Expected profit
		self.expected_profit = flt(self.expected_revenue) - flt(self.total_cost_budget)
		
		# ROI
		if self.total_cost_budget and self.total_cost_budget > 0:
			self.roi_percent = (self.expected_profit / self.total_cost_budget) * 100
		
		# Break-even yield
		if self.expected_price and self.expected_price > 0:
			self.break_even_yield = self.total_cost_budget / self.expected_price

	def compare_with_actual(self):
		"""Compare budget with actual crop cycle costs"""
		if not self.crop_cycle:
			return None
		
		cycle = frappe.get_doc("Crop Cycle", self.crop_cycle)
		
		return {
			"budgeted_cost": self.total_cost_budget,
			"actual_cost": cycle.total_input_cost,
			"variance": self.total_cost_budget - cycle.total_input_cost,
			"budgeted_yield": self.expected_yield,
			"actual_yield": cycle.actual_yield,
			"yield_variance": self.expected_yield - (cycle.actual_yield or 0)
		}
