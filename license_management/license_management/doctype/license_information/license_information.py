# Copyright (c) 2026, Harshit Jain and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import cint

# Path template on the Laravel license server. The server itself (LARAVEL_SERVER)
# is expected to be configured per site, e.g.:
#   bench --site <site> set-config laravel_server "https://license.example.com"
LICENSE_ENDPOINT = "/api/license/{host}"

# Users that don't count towards the license's active-user limit or usage reporting.
EXCLUDED_USERS = ("Administrator", "Guest")


class LicenseInformation(Document):
	pass


def get_current_host():
	"""Return the current site's host, e.g. 'license.test'."""
	return frappe.local.site


def get_user_counts():
	"""Return (total_users, active_users), excluding Administrator/Guest."""
	filters = {"name": ["not in", list(EXCLUDED_USERS)]}
	total_users = frappe.db.count("User", filters=filters)
	active_users = frappe.db.count("User", filters={**filters, "enabled": 1})
	return total_users, active_users


def apply_simultaneous_sessions(simultaneous_sessions):
	"""Bulk-set the "Simultaneous Sessions" limit on every User to the license's value."""
	if simultaneous_sessions is None:
		return
	frappe.db.set_value("User", {}, "simultaneous_sessions", cint(simultaneous_sessions))


def save_license_provider(provider):
	"""Save the license provider's name/email (from the API's "provider" object)
	into the site config, so error/warning messages can point users to them.
	"""
	if not provider:
		return

	from frappe.installer import update_site_config

	name = provider.get("name")
	email = provider.get("email")
	if name:
		update_site_config("license_provider_name", name)
	if email:
		update_site_config("license_provider_email", email)


def get_provider_contact_line():
	"""A "contact your license provider" phrase, using site config details when set."""
	name = frappe.conf.get("license_provider_name")
	email = frappe.conf.get("license_provider_email")

	if name and email:
		return _("please contact your license provider {0} at {1}").format(name, email)
	if email:
		return _("please contact your license provider at {0}").format(email)
	return _("please contact your license provider")


def notify_active_user_overage(active_users, max_active_users):
	"""Alert System Managers when active users already exceed the license's limit.

	Deliberately does not touch any existing User — disabling someone's account
	automatically on a license downgrade is disruptive and not done here. This
	only raises visibility (a Notification Log for every System Manager) so a
	human can decide who, if anyone, to disable. New-user creation is still
	auto-disabled-with-warning by license_management.overrides.user.
	"""
	if not max_active_users or active_users <= max_active_users:
		return

	from frappe.desk.doctype.notification_log.notification_log import enqueue_create_notification
	from frappe.utils.user import get_system_managers

	system_managers = get_system_managers(only_name=True)
	if not system_managers:
		return

	subject = _(
		"Active users ({0}) exceed the Maximum Active User limit ({1}) allowed by your License. "
		"No users were disabled automatically — please review and disable users as needed, "
		"or {2} to raise the limit."
	).format(active_users, max_active_users, get_provider_contact_line())

	enqueue_create_notification(
		system_managers,
		{
			"subject": subject,
			"type": "Alert",
			"document_type": "License Information",
			"document_name": "License Information",
			"link": "/app/license-information",
		},
		# Skip re-notifying for the same active/max combination; a fresh mismatch
		# (either number changes) still raises a new notification.
		dedupe_on=["document_type", "document_name", "subject"],
	)


@frappe.whitelist()
def get_active_user_status():
	"""Current user counts alongside the license's Maximum Active User limit.

	Used by the License Information form to show a live over-limit banner.
	"""
	frappe.only_for("System Manager")
	total_users, active_users = get_user_counts()
	max_active_users = frappe.db.get_single_value("License Information", "max_active_users")
	return {
		"total_users": total_users,
		"active_users": active_users,
		"max_active_users": max_active_users,
		"provider_name": frappe.conf.get("license_provider_name"),
		"provider_email": frappe.conf.get("license_provider_email"),
	}


def get_license_api_url(host=None):
	"""Build the full URL of the Laravel license validation endpoint for `host`."""
	laravel_server = frappe.conf.get("laravel_server")
	if not laravel_server:
		frappe.throw(
			_(
				"Laravel Server is not configured. Please set 'laravel_server' in the site config."
			)
		)

	host = host or get_current_host()
	return laravel_server.rstrip("/") + LICENSE_ENDPOINT.format(host=host)


def _call_license_api(host=None, total_users=None, active_users=None):
	"""GET the raw license payload for `host` from the Laravel server.

	Also reports the site's current total/active user counts as query params,
	so the license server can track usage alongside validating the license.
	"""
	import requests

	host = host or get_current_host()
	url = get_license_api_url(host)
	params = {}
	if total_users is not None:
		params["total_users"] = total_users
	if active_users is not None:
		params["active_users"] = active_users

	try:
		response = requests.get(url, params=params, timeout=30)
		response.raise_for_status()
		return response.json()
	except Exception:
		frappe.log_error(title=_("License Information Sync Failed"))
		frappe.throw(_("Failed to fetch License Information from the license server."))


def fetch_license_information():
	"""Call the Laravel license API and update the License Information single.

	Called daily by the scheduler (see hooks.py) and on-demand via the
	"Refresh License Information" button on the License Information doctype
	and the "Refresh License" button on the User list. Also reports the
	current total/active user counts to the license server.
	"""
	total_users, active_users = get_user_counts()
	data = _call_license_api(total_users=total_users, active_users=active_users)

	license_doc = frappe.get_single("License Information")
	license_doc.license_id = data.get("license_id")
	license_doc.license_status = data.get("license_status")
	license_doc.license_expiry = (
		frappe.utils.getdate(data.get("license_expiry")) if data.get("license_expiry") else None
	)
	# Laravel returns "max_active_user" (singular) and "max_attachment_size_mb".
	license_doc.max_active_users = data.get("max_active_user")
	license_doc.max_attachment_size = data.get("max_attachment_size_mb")
	license_doc.save(ignore_permissions=True)
	frappe.db.commit()

	if license_doc.max_attachment_size:
		# Frappe's file-size limit (frappe.utils.file_manager.get_max_file_size) reads
		# "max_file_size" from the site config in bytes, so convert from MB here.
		from frappe.installer import update_site_config

		update_site_config("max_file_size", cint(license_doc.max_attachment_size) * 1024 * 1024)

	# Sync the license's session limit onto every User (core "Simultaneous Sessions" field).
	apply_simultaneous_sessions(data.get("simultaneous_sessions"))

	# Save the license provider's contact details for use in messages/errors.
	save_license_provider(data.get("provider"))
	frappe.db.commit()

	# The limit may have just been lowered below the current active-user count.
	# Never auto-disable existing users for this — just alert System Managers.
	notify_active_user_overage(active_users, license_doc.max_active_users)

	return license_doc


@frappe.whitelist()
def refresh_license_information():
	"""Whitelisted handler for the "Refresh License Information" button."""
	frappe.only_for("System Manager")
	fetch_license_information()
	frappe.msgprint(_("License Information refreshed successfully."))
