# Copyright (c) 2026, Harshit Jain and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from license_management.license_management.doctype.license_information.license_information import (
	EXCLUDED_USERS,
	get_provider_contact_line,
	get_user_counts,
)


def _is_newly_activated(doc):
	"""True if this save is turning on a User that wasn't already active.

	Covers both a brand new User being created enabled, and an existing
	disabled User being manually switched to enabled. A save that leaves an
	already-active User active (e.g. editing their name) is not "newly
	activated" and should not be re-checked against the limit.
	"""
	if doc.is_new():
		return True

	before_save = doc.get_doc_before_save()
	was_enabled = bool(before_save.enabled) if before_save else True
	return not was_enabled


def validate_active_user_limit(doc, method=None):
	"""Hooked on User's `validate` event (runs on every `doc.save()`).

	The User is always allowed to save. If activating it — by creating a new
	enabled User, or by manually re-enabling a previously disabled one —
	would push the active-user count (excluding Administrator/Guest) past
	the Maximum Active User limit on the License Information doctype, the
	User is kept disabled instead, with a warning alert shown.
	"""
	if doc.name in EXCLUDED_USERS:
		return

	if not doc.enabled:
		# Disabling (or creating disabled) never violates the limit.
		return

	if not _is_newly_activated(doc):
		# Already active before this save — nothing new to enforce.
		return

	max_active_users = frappe.db.get_single_value("License Information", "max_active_users")

	if not max_active_users:
		# No limit configured on the license yet, nothing to enforce.
		return

	_total_users, current_active_users = get_user_counts()

	if current_active_users >= max_active_users:
		doc.enabled = 0
		if doc.is_new():
			message = _(
				"Maximum Active User limit ({0}) reached. This User has been created as disabled. "
				"To enable more users, {1}."
			)
		else:
			message = _(
				"Maximum Active User limit ({0}) reached. This User could not be enabled and "
				"remains disabled. To enable more users, {1}."
			)
		frappe.msgprint(
			message.format(max_active_users, get_provider_contact_line()),
			title=_("License Limit Reached"),
			indicator="orange",
			alert=True,
		)
