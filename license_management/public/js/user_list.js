// Copyright (c) 2026, Harshit Jain and contributors
// For license information, please see license.txt

// Adds a "Refresh License" button to the User list view, which re-fetches
// License Information from the Laravel license server.
(function () {
	frappe.listview_settings["User"] = frappe.listview_settings["User"] || {};

	const base_onload = frappe.listview_settings["User"].onload;

	frappe.listview_settings["User"].onload = function (listview) {
		if (base_onload) {
			base_onload.call(frappe.listview_settings["User"], listview);
		}

		listview.page.add_inner_button(__("Refresh License"), function () {
			frappe.call({
				method:
					"license_management.license_management.doctype.license_information.license_information.refresh_license_information",
				freeze: true,
				freeze_message: __("Refreshing License Information..."),
				callback: function () {
					frappe.show_alert({
						message: __("License Information refreshed."),
						indicator: "green",
					});
				},
			});
		});
	};
})();
