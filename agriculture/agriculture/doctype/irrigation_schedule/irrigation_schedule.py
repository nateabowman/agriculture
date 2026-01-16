# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import add_to_date, get_time, nowdate, nowtime, time_diff_in_seconds


class IrrigationSchedule(Document):
	def validate(self):
		self.calculate_end_time()
		self.calculate_next_run()
		self.set_farm_from_plot()

	def calculate_end_time(self):
		"""Calculate end time based on start time and duration"""
		if self.start_time and self.duration_minutes:
			start_seconds = time_diff_in_seconds(self.start_time, "00:00:00")
			end_seconds = start_seconds + (self.duration_minutes * 60)
			hours = int(end_seconds // 3600)
			minutes = int((end_seconds % 3600) // 60)
			self.end_time = f"{hours:02d}:{minutes:02d}:00"

	def calculate_next_run(self):
		"""Calculate next scheduled run based on frequency"""
		if self.status != "Active":
			self.next_scheduled_run = None
			return
		
		from frappe.utils import combine_datetime
		
		# Simple calculation - in real implementation would be more complex
		if self.start_date and self.start_time:
			self.next_scheduled_run = combine_datetime(self.start_date, self.start_time)

	def set_farm_from_plot(self):
		"""Set farm from plot if not provided"""
		if self.plot and not self.farm:
			self.farm = frappe.db.get_value("Plot", self.plot, "farm")

	def record_run(self, water_used=None):
		"""Record an irrigation run"""
		self.last_run_date = nowdate()
		self.last_run_time = nowtime()
		self.total_runs = (self.total_runs or 0) + 1
		
		if water_used:
			self.total_water_used = (self.total_water_used or 0) + water_used
		elif self.water_amount_liters:
			self.total_water_used = (self.total_water_used or 0) + self.water_amount_liters
		
		self.calculate_next_run()
		self.save()

	def should_irrigate(self):
		"""Check if irrigation should be triggered based on sensor data"""
		if not self.is_automated or not self.sensor_device:
			return False
		
		sensor = frappe.get_doc("Sensor Device", self.sensor_device)
		latest_reading = sensor.get_latest_reading()
		
		if latest_reading and self.trigger_moisture_below:
			if latest_reading[0].reading_value < self.trigger_moisture_below:
				return True
		
		return False
