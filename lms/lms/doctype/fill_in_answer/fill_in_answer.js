// Copyright (c) 2024, Frappe and contributors
// For license information, please see license.txt

frappe.ui.form.on('Fill In Answer', {
	refresh: function(frm) {
		// Add any custom form refresh logic here
	},
	
	blank_number: function(frm) {
		// Validate that blank number is positive
		if (frm.doc.blank_number < 1) {
			frappe.validated = false;
			frappe.msgprint(__('Blank number must be greater than 0'));
		}
	},
	
	correct_answer: function(frm) {
		// Validate that correct answer is not empty
		if (!frm.doc.correct_answer) {
			frappe.validated = false;
			frappe.msgprint(__('Correct answer cannot be empty'));
		}
	}
}); 