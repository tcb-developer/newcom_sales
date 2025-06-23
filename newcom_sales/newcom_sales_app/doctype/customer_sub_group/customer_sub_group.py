import frappe
from frappe.model.document import Document


class CustomerSubGroup(Document):
    def before_save(self):
        for user in self.get("users"):
            for permission in self.get("permissions"):

                if user.get("disable"):

                    if permission.get("user_permission"):

                        user_permission = frappe.get_doc(
                            "User Permission", permission.get("user_permission")
                        )

                        permission.db_set("user_permission", "")

                        user_permission.delete()

                    continue

                if permission.get("user_permission"):
                    continue

                user_permission = frappe.get_doc(
                    {
                        "doctype": "User Permission",
                        "user": user.user,
                        "allow": permission.doc,
                        "for_value": permission.document,
                        "is_default": permission.is_default,
                        "apply_to_all_doctypes": permission.apply_for_all_docs,
                        "applicable_for": permission.applicable_document,
                    }
                ).insert()

                user_permission.save()

                permission.db_set("user_permission", user_permission.name)
