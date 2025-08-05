import frappe
from frappe.model.document import Document
from frappe.contacts.address_and_contact import set_link_title


class NCSCustomerContact(Document):
    def __setup__(self):
        self.flags.linked = False

    def validate(self):
        set_link_title(self)
