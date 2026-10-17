# Release Notes

For the full technical list of changes, see [CHANGELOG.md](CHANGELOG.md).

## v1.0.0 — 2026-09-04

Initial release of **License Management**.

This release connects the site to an external license server and enforces what the license allows, directly inside Frappe:

- **License Information** shows your current license at a glance — ID, status, expiry, and both limits (max active users, max attachment size) — with a one-click refresh, either from the doctype itself or a "Refresh License" button on the User list.
- **Automatic daily sync**, at 12:00 PM, keeps this current without anyone needing to remember to check it manually.
- **The active-user limit is enforced where it actually matters, without locking anyone out by surprise**: creating a new user, or re-enabling a disabled one, is blocked — the user is saved but kept disabled — once you're at the license's user cap, with a message naming who to contact to raise it. Users who are already active are never touched automatically, even if a license downgrade puts you over the limit; instead, System Managers get an alert and a live over-limit banner, so a person decides who (if anyone) to disable.
- **Attachment-size and simultaneous-session limits from the license are applied automatically** to the site, so there's no manual config editing after the initial setup.

### Upgrade / setup notes

- Set your license server once: `bench --site $SITE_NAME set-config license_server "https://your-license-server"`.

