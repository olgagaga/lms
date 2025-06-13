import frappe


def execute():
    frappe.reload_doc("lms", "doctype", "lms_quiz_question")
    
    # Update the type field options to include Fill In
    frappe.db.set_value(
        "DocField",
        {"parent": "LMS Quiz Question", "fieldname": "type"},
        "options",
        "Choices\nUser Input\nOpen Ended\nFill In"
    ) 