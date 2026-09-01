# Copyright (c) 2026, Harshit Jain and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document

# Path template on the Laravel license server. The server itself (LARAVEL_SERVER)
# is expected to be configured per site, e.g.:
#   bench --site <site> set-config laravel_server "https://license.example.com"
LICENSE_ENDPOINT = "/api/license/{host}"


class LicenseInformation(Document):
	pass


def get_current_host():
	"""Return the current site's host, e.g. 'license.test'."""
	return frappe.local.site


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


def _call_license_api(host=None):
	"""GET the raw license payload for `host` from the Laravel server."""
	import requests

	host = host or get_current_host()
	url = get_license_api_url(host)

	try:
		response = requests.get(url, timeout=30)
		response.raise_for_status()
		return response.json()
	except Exception:
		frappe.log_error(title=_("License Information Sync Failed"))
		frappe.throw(_("Failed to fetch License Information from the license server."))


def fetch_license_information():
	"""Call the Laravel license API and update the License Information single.

	Called daily by the scheduler (see hooks.py) and on-demand via the
	"Refresh License Information" button on the License Information doctype
	and the "Refresh License" button on the User list.
	"""
	data = _call_license_api()

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
		from frappe.utils import cint

		update_site_config("max_file_size", cint(license_doc.max_attachment_size) * 1024 * 1024)

	return license_doc


@frappe.whitelist()
def refresh_license_information():
	"""Whitelisted handler for the "Refresh License Information" button."""
	frappe.only_for("System Manager")
	fetch_license_information()
	frappe.msgprint(_("License Information refreshed successfully."))
