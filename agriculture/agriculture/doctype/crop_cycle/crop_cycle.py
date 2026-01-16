# Copyright (c) 2017, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt


import ast

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import add_days, flt


class CropCycle(Document):
	def validate(self):
		self.set_missing_values()
		self.calculate_totals()
		self.calculate_yield_percentage()

	def after_insert(self):
		self.create_crop_cycle_project()
		self.create_tasks_for_diseases()
		self.update_plot_status()

	def on_update(self):
		self.create_tasks_for_diseases()

	def on_trash(self):
		self.clear_plot_status()

	def set_missing_values(self):
		crop = frappe.get_doc('Crop', self.crop)

		if not self.crop_spacing_uom:
			self.crop_spacing_uom = crop.crop_spacing_uom

		if not self.row_spacing_uom:
			self.row_spacing_uom = crop.row_spacing_uom

		# Set farm from plot if not provided
		if self.plot and not self.farm:
			self.farm = frappe.db.get_value("Plot", self.plot, "farm")

		# Set yield UOM from crop
		if not self.yield_uom and crop.yield_uom:
			self.yield_uom = crop.yield_uom

		# Calculate expected end date from crop period
		if self.start_date and crop.period and not self.expected_end_date:
			self.expected_end_date = add_days(self.start_date, crop.period - 1)

	def calculate_totals(self):
		"""Calculate total costs and profit/loss"""
		self.total_input_cost = flt(self.seed_cost) + flt(self.fertilizer_cost) + \
			flt(self.pesticide_cost) + flt(self.labor_cost) + \
			flt(self.equipment_cost) + flt(self.other_costs)

		if self.area_planted and self.area_planted > 0:
			self.cost_per_unit_area = self.total_input_cost / self.area_planted
		else:
			self.cost_per_unit_area = 0

		self.profit_loss = flt(self.revenue) - flt(self.total_input_cost)

	def calculate_yield_percentage(self):
		"""Calculate actual yield as percentage of expected"""
		if self.expected_yield and self.expected_yield > 0 and self.actual_yield:
			self.yield_percentage = (self.actual_yield / self.expected_yield) * 100
		else:
			self.yield_percentage = 0

	def update_plot_status(self):
		"""Update linked plot status when cycle is created"""
		if self.plot:
			plot = frappe.get_doc("Plot", self.plot)
			plot.current_crop = self.crop
			plot.current_crop_cycle = self.name
			plot.status = "Planted"
			plot.save()

	def clear_plot_status(self):
		"""Clear plot status when cycle is deleted"""
		if self.plot:
			plot = frappe.get_doc("Plot", self.plot)
			if plot.current_crop_cycle == self.name:
				plot.current_crop = None
				plot.current_crop_cycle = None
				plot.status = "Available"
				plot.save()

	def complete_cycle(self):
		"""Mark cycle as completed and update plot"""
		self.status = "Completed"
		self.actual_end_date = frappe.utils.nowdate()
		self.save()
		self.clear_plot_status()

	def create_crop_cycle_project(self):
		crop = frappe.get_doc('Crop', self.crop)

		self.project = self.create_project(crop.period, crop.agriculture_task)
		self.create_task(crop.agriculture_task, self.project, self.start_date)

	def create_tasks_for_diseases(self):
		for disease in self.detected_disease:
			if not disease.tasks_created:
				self.import_disease_tasks(disease.disease, disease.start_date)
				disease.tasks_created = True

				frappe.msgprint(_("Tasks have been created for managing the {0} disease (on row {1})").format(disease.disease, disease.idx))

	def import_disease_tasks(self, disease, start_date):
		disease_doc = frappe.get_doc('Disease', disease)
		self.create_task(disease_doc.treatment_task, self.project, start_date)

	def create_project(self, period, crop_tasks):
		project = frappe.get_doc({
			"doctype": "Project",
			"project_name": self.title,
			"expected_start_date": self.start_date,
			"expected_end_date": add_days(self.start_date, period - 1)
		}).insert()

		return project.name

	def create_task(self, crop_tasks, project_name, start_date):
		for crop_task in crop_tasks:
			frappe.get_doc({
				"doctype": "Task",
				"subject": crop_task.get("task_name"),
				"priority": crop_task.get("priority"),
				"project": project_name,
				"exp_start_date": add_days(start_date, crop_task.get("start_day") - 1),
				"exp_end_date": add_days(start_date, crop_task.get("end_day") - 1)
			}).insert()

	@frappe.whitelist()
	def reload_linked_analysis(self):
		linked_doctypes = ['Soil Texture', 'Soil Analysis', 'Plant Analysis']
		required_fields = ['location', 'name', 'collection_datetime']
		output = {}

		for doctype in linked_doctypes:
			output[doctype] = frappe.get_all(doctype, fields=required_fields)

		output['Location'] = []

		for location in self.linked_location:
			output['Location'].append(frappe.get_doc('Location', location.location))

		frappe.publish_realtime("List of Linked Docs",
								output, user=frappe.session.user)

	@frappe.whitelist()
	def append_to_child(self, obj_to_append):
		for doctype in obj_to_append:
			for doc_name in set(obj_to_append[doctype]):
				self.append(doctype, {doctype: doc_name})

		self.save()


def get_coordinates(doc):
	return ast.literal_eval(doc.location).get('features')[0].get('geometry').get('coordinates')


def get_geometry_type(doc):
	return ast.literal_eval(doc.location).get('features')[0].get('geometry').get('type')


def is_in_location(point, vs):
	x, y = point
	inside = False

	j = len(vs) - 1
	i = 0

	while i < len(vs):
		xi, yi = vs[i]
		xj, yj = vs[j]

		intersect = ((yi > y) != (yj > y)) and (
			x < (xj - xi) * (y - yi) / (yj - yi) + xi)

		if intersect:
			inside = not inside

		i = j
		j += 1

	return inside
