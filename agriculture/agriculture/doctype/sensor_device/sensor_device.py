# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import now_datetime


class SensorDevice(Document):
	def get_latest_reading(self):
		"""Get the most recent reading from this sensor"""
		return frappe.get_all(
			"Sensor Reading",
			filters={"sensor_device": self.name},
			fields=["name", "reading_value", "reading_datetime"],
			order_by="reading_datetime desc",
			limit=1
		)

	def get_readings(self, from_date=None, to_date=None, limit=100):
		"""Get readings within a date range"""
		filters = {"sensor_device": self.name}
		
		if from_date:
			filters["reading_datetime"] = [">=", from_date]
		if to_date:
			if "reading_datetime" in filters:
				filters["reading_datetime"] = ["between", [from_date, to_date]]
			else:
				filters["reading_datetime"] = ["<=", to_date]
		
		return frappe.get_all(
			"Sensor Reading",
			filters=filters,
			fields=["name", "reading_value", "reading_datetime"],
			order_by="reading_datetime desc",
			limit=limit
		)

	def check_threshold_alert(self, reading_value):
		"""Check if reading exceeds thresholds"""
		if not self.alert_enabled:
			return None
		
		if self.min_threshold and reading_value < self.min_threshold:
			return "low"
		if self.max_threshold and reading_value > self.max_threshold:
			return "high"
		
		return None

	def update_last_communication(self):
		"""Update last communication timestamp"""
		self.last_communication = now_datetime()
		self.db_set("last_communication", self.last_communication)
