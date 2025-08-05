import frappe
from frappe.model.document import Document

import functools
import random, string


class NCSSalesPlan(Document):

    def get_contact_template(self):
        template = """
{% if contact_name %}Contact Name: {{contact_name}}<br>{% endif -%}
{% if designation %}Designation: {{designation}}<br>{% endif -%}
{%if contact_number %}Contact No.: {{contact_number}}<br>{% endif -%}
{% if email_id %}Email: {{email_id}}<br>{% endif -%}
{% if dob %}DOB: {{frappe.format(dob, {'fieldtype': 'Date'})}}{% endif -%}
"""
        return template

    def get_contact_display(self, contact):
        template = self.get_contact_template()
        result = frappe.render_template(template, contact)
        return result


#         display = f"""
# {% if contact.contact_name %}Contact Name: {contact.contact_name}<br>{% endif -%}
# {% if contact.designation %}Designation: {contact.designation}<br>{% endif -%}
# {%if contact.contact_number %}Contact No.: {contact.contact_number}<br>{% endif -%}
# {% if contact.email_id %}Email: {contact.email_id}<br>{% endif -%}
# {% if contact.dob %}DOB: {contact.dob}{% endif -%}
# """


    def onload(self):
        filters = [
            ["Dynamic Link", "link_doctype", "=", self.doctype],
            ["Dynamic Link", "link_name", "=", self.name],
            ["Dynamic Link", "parenttype", "=", "NCS Customer Contact"],
        ]
        contact_list = frappe.get_list("NCS Customer Contact",
                                       filters=filters,
                                       fields=["*"],
                                       order_by="creation asc")
        contact_list = [
            c.update({"display": self.get_contact_display(c)})
            for c in contact_list
        ]
        contact_list = sorted(
            contact_list,
            key=functools.cmp_to_key(lambda a, b:
                                     (1 if a.modified - b.modified else 0)),
            reverse=True,
        )
        self.set_onload("ncs_contact_list", contact_list)


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
