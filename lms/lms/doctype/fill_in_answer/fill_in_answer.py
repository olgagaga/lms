# Copyright (c) 2024, Frappe and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class FillInAnswer(Document):
	# The 'case_sensitive' field is a boolean (0 or 1) and is handled by Frappe automatically.
	# If any custom validation is needed, add here in the future.
	pass 