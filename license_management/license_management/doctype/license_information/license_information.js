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

			const { active_users, max_active_users } = r.message;
			if (!max_active_users) return;

			if (active_users > max_active_users) {
				frm.dashboard.set_headline_alert(
					__(
						"Active users ({0}) exceed the Maximum Active User limit ({1}). No users were disabled automatically — please review and disable users as needed, or contact your license provider.",
						[active_users, max_active_users]
					),
					"red",
					true
				);
			}

			frm.dashboard.add_indicator(
				__("Active Users: {0} / {1}", [active_users, max_active_users]),
				active_users > max_active_users ? "red" : "green"
			);
		},
	});
}
