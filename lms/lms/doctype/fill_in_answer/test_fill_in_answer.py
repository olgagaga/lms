# Copyright (c) 2024, Frappe and contributors
# For license information, please see license.txt

import unittest
import frappe

class TestFillInAnswer(unittest.TestCase):
	def setUp(self):
		# Create a test question first
		self.question = frappe.get_doc({
			"doctype": "LMS Question",
			"question": "This is a test question with __1__ and __2__ blanks.",
			"type": "Fill In"
		}).insert()

	def test_fill_in_answer_creation(self):
		# Test creating a fill in answer
		answer = frappe.get_doc({
			"doctype": "Fill In Answer",
			"parent": self.question.name,
			"parenttype": "LMS Question",
			"parentfield": "fill_in_answers",
			"blank_number": 1,
			"correct_answer": "test"
		})
		answer.insert()
		self.assertTrue(answer.name)

	def test_blank_number_validation(self):
		# Test that blank number must be positive
		answer = frappe.get_doc({
			"doctype": "Fill In Answer",
			"parent": self.question.name,
			"parenttype": "LMS Question",
			"parentfield": "fill_in_answers",
			"blank_number": 0,
			"correct_answer": "test"
		})
		self.assertRaises(frappe.ValidationError, answer.insert)

	def test_correct_answer_validation(self):
		# Test that correct answer cannot be empty
		answer = frappe.get_doc({
			"doctype": "Fill In Answer",
			"parent": self.question.name,
			"parenttype": "LMS Question",
			"parentfield": "fill_in_answers",
			"blank_number": 1,
			"correct_answer": ""
		})
		self.assertRaises(frappe.ValidationError, answer.insert)

	def tearDown(self):
		# Clean up test data
		frappe.delete_doc("LMS Question", self.question.name) 