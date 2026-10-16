## License Management

Manages the license of the site by syncing with an external license server, enforcing the license's active-user limit, and keeping site behaviour (upload size, session limits) aligned with what the license allows.

📄 [Release Notes](RELEASE.md) · [Changelog](CHANGELOG.md)

### Description

- **License Information** — a read-only Single doctype showing License ID, License Status, License Expiry, Maximum Active User, Maximum Attachment Size (MB), and Max User Session Allowed (defaults to 1), with a "Refresh License Information" button to pull the latest data on demand.
- **Refresh License** — a matching button on the User list view for quick access to the same refresh action.
- **Daily sync** — a scheduled job calls the license server every day at 12:00 AM and updates License Information automatically, reporting the site's current total/active user counts alongside the check.
- **Active user limit, enforced without locking anyone out** — creating a new User, or manually re-enabling a disabled one, is kept disabled once active users (excluding Administrator/Guest) reach the license's Maximum Active User value, with a message naming your license provider. Users who are already active are never auto-disabled — if a license downgrade puts you over the limit, System Managers get a Notification Log alert and a live over-limit banner/stats on the License Information form instead, so a person decides.
- **Site behaviour synced from the license** — Maximum Attachment Size (MB) is written to the site's `max_file_size` config (bytes), and the license's Simultaneous Sessions value (shown as Max User Session Allowed) is applied to every User on each refresh and whenever a User is created or edited. Users on the license's exempt list (emails, managed from the license server UI) are left alone: the license never overwrites their Simultaneous Sessions, so any value saved on their User record is kept.

### Instructions

Set the license server on the site:

```bash
bench --site $SITE_NAME set-config license_server "https://your-license-server"
```

The app calls `GET <license_server>/api/license/<host>`, where `<host>` is the current site's name (`frappe.local.site`), and expects a JSON response shaped like:

```json
{
	"license_id": "LIC-TEST-001",
	"license_status": "active",
	"license_expiry": "2026-09-09T00:00:00.000000Z",
	"max_active_user": 10,
	"max_attachment_size_mb": 20,
	"simultaneous_sessions": 2,
	"provider": {
		"name": "Your License Provider",
		"email": "support@example.com"
	}
}
```

Install this app using the [bench](https://github.com/frappe/bench) CLI:

```bash
cd $PATH_TO_YOUR_BENCH
bench get-app $URL_OF_THIS_REPO --branch main
bench install-app license_management
```

### Contributing

This app uses `pre-commit` for code formatting and linting. Please [install pre-commit](https://pre-commit.com/#installation) and enable it for this repository:

```bash
cd apps/license_management
pre-commit install
```

Pre-commit is configured to use the following tools for checking and formatting your code:

- ruff
- eslint
- prettier
- pyupgrade

### License

mit
