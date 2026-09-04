// Copyright (c) 2026, Harshit Jain and contributors
// For license information, please see license.txt

frappe.ui.form.on("License Information", {
	refresh(frm) {
		show_active_user_status(frm);
	},
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

function show_active_user_status(frm) {
	frappe.call({
		method:
			"license_management.license_management.doctype.license_information.license_information.get_active_user_status",
		callback: function (r) {
			if (!r.message) return;

			const { total_users, active_users, max_active_users, provider_name, provider_email } =
				r.message;
			const over_limit = max_active_users && active_users > max_active_users;

			if (over_limit) {
				let contact = __("please contact your license provider");
				if (provider_name && provider_email) {
					contact = __("please contact your license provider {0} at {1}", [
						provider_name,
						provider_email,
					]);
				} else if (provider_email) {
					contact = __("please contact your license provider at {0}", [provider_email]);
				}

				frm.dashboard.set_headline_alert(
					__(
						"Active users ({0}) exceed the Maximum Active User limit ({1}). No users were disabled automatically — please review and disable users as needed, or {2} to raise the limit.",
						[active_users, max_active_users, contact]
					),
					"red",
					true
				);
			}

			// Stats: Active Users (enabled), Current Users (enabled + disabled), Max Active Allowed.
			frm.dashboard.add_indicator(__("Active Users: {0}", [active_users]), over_limit ? "red" : "green");
			frm.dashboard.add_indicator(__("Current Users: {0}", [total_users]), "blue");
			frm.dashboard.add_indicator(
				__("Max Active Allowed: {0}", [max_active_users == null ? "-" : max_active_users]),
				"grey"
			);
		},
	});
}
