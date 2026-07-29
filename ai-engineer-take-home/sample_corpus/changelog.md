# Changelog

## v3.1 (current)
- Increased API rate limit from 60 to 100 requests per minute per key.
- Fixed a bug where pending member invitations were counted toward seat totals.
- Enterprise plans can now configure SSO session length.

## v3.0
- Replaced the Slack daily digest (introduced in v2.3) with a unified Notification Center supporting both Slack and Microsoft Teams. The old daily-digest format is no longer available; notifications are now configured per-channel under Workspace Settings > Notifications instead of the old Slack-only settings page.
- Cycle Definition changes now apply going forward only; previously (through v2.x) changing the Cycle Definition would silently recompute all historical snapshots, which caused reports to change unexpectedly for past sprints. This recompute behavior was removed in v3.0.
- Historical backfill window increased from 30 to 90 days for Team and Enterprise plans.

## v2.3
- Introduced Slack daily digest: a message posted once a day to a configured Slack channel summarizing snapshot changes. (Superseded by the Notification Center in v3.0; see above.)
- Added Trello as a supported integration, alongside Jira Cloud and Linear.

## v2.0
- API rate limit set to 60 requests per minute per key. (Raised to 100/min in v3.1; see above.)
- Introduced workspace-level API keys, replacing the earlier per-user keys from v1.x.

## v1.0
- Initial release. Jira Cloud integration only. No public API.
