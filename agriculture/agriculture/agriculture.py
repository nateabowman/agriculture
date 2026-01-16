# Copyright (c) 2017, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

data = {
	'desktop_icons': [
		'Crop',
		'Crop Cycle',
		'Disease',
		'Fertilizer',
		'Soil Analysis',
		'Plant Analysis',
		'Water Analysis',
		'Soil Texture',
		'Weather',
	],
	'restricted_roles': [
		'Agriculture Manager',
		'Agriculture User'
	],
	'modules': [
		'Agriculture'
	],
	'default_portal_role': 'Agriculture User',
	'custom_fields': {},
	'on_setup': 'agriculture.agriculture.setup.setup_agriculture'
}
