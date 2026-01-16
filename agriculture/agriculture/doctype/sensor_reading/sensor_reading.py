# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class SensorReading(Document):
	def after_insert(self):
		self.update_sensor_last_communication()
		self.check_and_create_alert()

	def update_sensor_last_communication(self):
		"""Update sensor's last communication time"""
		if self.sensor_device:
			sensor = frappe.get_doc("Sensor Device", self.sensor_device)
			sensor.update_last_communication()

	def check_and_create_alert(self):
		"""Check thresholds and create alert if needed"""
		if not self.sensor_device:
			return
		
		sensor = frappe.get_doc("Sensor Device", self.sensor_device)
		alert_type = sensor.check_threshold_alert(self.reading_value)
		
		if alert_type:
			self.create_alert(sensor, alert_type)

	def create_alert(self, sensor, alert_type):
		"""Create an alert notification"""
		message = ""
		if alert_type == "low":
			message = f"{sensor.device_name}: {sensor.measurement_parameter} is below minimum threshold. Value: {self.reading_value}"
		else:
			message = f"{sensor.device_name}: {sensor.measurement_parameter} exceeds maximum threshold. Value: {self.reading_value}"
		
		# Create notification
		frappe.get_doc({
			"doctype": "Notification Log",
			"subject": f"Sensor Alert: {sensor.device_name}",
			"email_content": message,
			"document_type": "Sensor Reading",
			"document_name": self.name,
			"for_user": frappe.session.user
		}).insert(ignore_permissions=True)
