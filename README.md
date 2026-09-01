### License Management

Manages the license of the site by syncing with a Laravel-based license server.

### Features

- **License Information** — a read-only Single doctype showing License ID, License Status, License Expiry, Maximum Active User, and Maximum Attachment Size (MB), with a "Refresh License Information" button to pull the latest data on demand.
- **Refresh License** — a matching button on the User list view for quick access to the same refresh action.
- **Daily sync** — a scheduled job calls the license server every day at 12:00 PM and updates License Information automatically.
- **Active user limit** — creating a new active User is blocked once the number of active users (excluding Administrator/Guest) reaches the license's Maximum Active User value.
- **Attachment size enforcement** — the license's Maximum Attachment Size (MB) is written to the site's `max_file_size` config (in bytes), so Frappe's own upload limit reflects the license.

### Configuration

Set the Laravel license server on the site:

```bash
bench --site $SITE_NAME set-config laravel_server "https://your-laravel-host"
```

The app calls `GET <laravel_server>/api/license/<host>`, where `<host>` is the current site's name (`frappe.local.site`), and expects a JSON response shaped like:

```json
{
	"license_id": "LIC-TEST-001",
	"license_status": "active",
	"license_expiry": "2026-09-09T00:00:00.000000Z",
	"max_active_user": 10,
	"max_attachment_size_mb": 20
}
```

### Installation

You can install this app using the [bench](https://github.com/frappe/bench) CLI:

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
