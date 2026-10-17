# Changelog

All notable changes to License Management are documented in this file.

Versioning follows [Semantic Versioning](https://semver.org/): MAJOR for breaking changes, MINOR for backward-compatible features, and PATCH for backward-compatible fixes.

## [2.0.0] - 2026-10-16

### Added

- `Max User Session Allowed` field on `License Information` (read-only, defaults to 1), populated from the license server's `simultaneous_sessions` on every refresh.
- User `validate` hook: every User create/edit now sets "Simultaneous Sessions" to Max User Session Allowed (1 if unset), so a hand-edited value can't outlive the next save.
- Session-limit exemptions: Exempt users (matched by user name or email, case-insensitively) are skipped by both the refresh sync and the User `validate` hook, so any "Simultaneous Sessions" value saved on their User record (2, 5, 10, ...) is kept; everyone else follows Max User Session Allowed.

## [1.0.0] - 2026-09-04

### Added

- `License Information` Single doctype with read-only License ID, License Status, License Expiry, Maximum Active User, and Maximum Attachment Size (MB) fields, plus a "Refresh License Information" button.
- "Refresh License" button on the User list view, calling the same sync.
- Daily scheduled job (`0 12 * * *`) that fetches license data from the license server configured via the `license_server` site config key.
- Active-user-limit enforcement on the User doctype: creating a new User, or manually re-enabling an existing disabled one, is kept disabled (with a `frappe.msgprint` warning naming the license provider) once active users (excluding Administrator/Guest) reach the license's Maximum Active User limit. Users already active are never auto-disabled.
- Alerting for an already-over-limit license (e.g. after the limit is lowered below the current active-user count): a Notification Log for every System Manager, plus a live over-limit banner and Active/Current/Max stats indicators on the License Information form.
- Sync of the license server's response into site behaviour: Maximum Attachment Size (MB) → site's `max_file_size` config (bytes); Simultaneous Sessions → every User's "Simultaneous Sessions" field; provider name/email → site config, used to build "please contact your license provider {name} at {email}" in warning and notification messages.
- Usage reporting: the site's current total/active user counts are sent as query params on every license API call.

### Changed

- License endpoint moved from `POST /api/license/validate` to `GET /api/license/{host}`, with `{host}` being the site's own name (`frappe.local.site`).
- Site config key renamed from `laravel_server` to `license_server`.
- Active-user-limit check no longer blocks the save outright — the User is always saved; if it would exceed the limit, it's saved disabled instead, with an explanatory message, rather than raising an error.
- Active-user count used for the limit check excludes the user executing the save only when they are the very User being (re)activated, so a self-referential edge case can't cause an incorrect result — without undercounting (and so incorrectly allowing an over-limit save) when acting on a different user.

### Removed

- None.
