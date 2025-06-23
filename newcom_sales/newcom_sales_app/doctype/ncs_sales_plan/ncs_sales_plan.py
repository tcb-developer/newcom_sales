import frappe
from frappe.model.document import Document
import random, string


class NCSSalesPlan(Document):
    pass


def generate_customer_code(length=10):
    chars = string.digits
    code = "".join(random.choices(chars, k=length))
    if frappe.db.exists("NCS Sales Plan", code):
        return generate_customer_code(length=length)
    else:
        return code


@frappe.whitelist()
def get_customer_code():
    length = 10
    customer_code = generate_customer_code(length=length)
    return customer_code
