// Copyright (c) 2026, Harshit Jain and contributors
// For license information, please see license.txt

frappe.ui.form.on("License Information", {
	refresh_license_information(frm) {
		frappe.call({
			method:
				"license_management.license_management.doctype.license_information.license_information.refresh_license_information",
			freeze: true,
			freeze_message: __("Refreshing License Information..."),
			callback: function () {
				frm.reload_doc();
			},
		});
	},
});
