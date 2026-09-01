# Copyright (c) 2026, Harshit Jain and contributors
# For license information, please see license.txt

import frappe
from frappe import _

EXCLUDED_USERS = ("Administrator", "Guest")


def validate_active_user_limit(doc, method=None):
	"""Hooked on User's `validate` event (runs on every `doc.save()`).

	Blocks the creation of a new, enabled User once the number of active
	users (excluding Administrator/Guest) has reached the Maximum Active
	User limit configured on the License Information doctype.
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

	current_active_users = frappe.db.count(
		"User",
		filters={
			"enabled": 1,
			"name": ["not in", list(EXCLUDED_USERS)],
		},
	)

	if current_active_users >= max_active_users:
		frappe.throw(
			_(
				"Cannot create User. It exceeds the Maximum Active User limit ({0}) allowed by your License."
			).format(max_active_users)
		)
