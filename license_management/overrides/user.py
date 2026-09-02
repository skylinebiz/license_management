# Copyright (c) 2026, Harshit Jain and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from license_management.license_management.doctype.license_information.license_information import (
	EXCLUDED_USERS,
	get_user_counts,
)


def validate_active_user_limit(doc, method=None):
	"""Hooked on User's `validate` event (runs on every `doc.save()`).

	The User is always allowed to save. If creating a new, enabled User
	would push the active-user count (excluding Administrator/Guest) past
	the Maximum Active User limit on the License Information doctype, the
	User is saved as disabled instead, with a warning alert shown.
	"""
	# Only enforce the limit when a brand new active user is being created.
	if not doc.is_new():
		return

	if doc.name in EXCLUDED_USERS:
		return

	if not doc.enabled:
		return

	max_active_users = frappe.db.get_single_value("License Information", "max_active_users")

	if not max_active_users:
		# No limit configured on the license yet, nothing to enforce.
		return

	_total_users, current_active_users = get_user_counts()

	if current_active_users >= max_active_users:
		doc.enabled = 0
		frappe.msgprint(
			_(
				"Maximum Active User limit ({0}) reached. This User has been created as disabled. "
				"To enable more users, please contact your license provider."
			).format(max_active_users),
			title=_("License Limit Reached"),
			indicator="orange",
			alert=True,
		)
