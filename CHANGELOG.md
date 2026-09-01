# Changelog

All notable changes to License Management are documented in this file.

Versioning follows [Semantic Versioning](https://semver.org/): MAJOR for breaking changes, MINOR for backward-compatible features, and PATCH for backward-compatible fixes.

## [1.0.0] - 2026-08-31

### Added

- `License Information` Single doctype with read-only License ID, License Status, License Expiry, Maximum Active User, and Maximum Attachment Size (MB) fields, plus a "Refresh License Information" button.
- "Refresh License" button on the User list view, calling the same sync.
- Daily scheduled job (`0 12 * * *`) that fetches license data from the Laravel server configured via the `laravel_server` site config key, calling `GET <laravel_server>/api/license/<host>`.
- Sync of the license's Maximum Attachment Size (MB) into the site's `max_file_size` config (bytes), so Frappe's upload limit reflects the license.
- Enforcement on the User doctype: creating a new active user is blocked once active users (excluding Administrator/Guest) reach the license's Maximum Active User limit.