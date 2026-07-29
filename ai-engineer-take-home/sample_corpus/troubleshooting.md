# Troubleshooting

## Cycle-time report shows "Not configured"

This means no Cycle Definition has been set for the workspace. Go to Workspace Settings > Cycle Definition and map your tracker's statuses to "In Progress" and "Done." Reports will populate on the next daily snapshot after saving, not retroactively for past snapshots.

## Snapshot hasn't run

Snapshots run once daily at 02:00 in the workspace's configured time zone. If you just connected a tracker, the first snapshot runs within 15 minutes instead of waiting for the next 02:00 window. If more than 24 hours have passed with no snapshot, check Workspace Settings > Integrations for a "Reconnect required" banner. This usually means the tracker revoked Aperture's access, most commonly because someone rotated the Jira/Linear/Trello credentials on the tracker side.

## Historical data is missing after connecting

Historical backfill only covers the trailing 90 days and is only available on Team and Enterprise plans. Free-plan workspaces start with an empty history and accumulate snapshots going forward only.

## Dashboard shows fewer members than expected

Only members who have accepted their invitation appear as active seats. Pending invitations are listed separately under Workspace Settings > Members > Pending, and do not count toward your seat total until accepted.

## API requests return 401 after a key rotation

This is expected: revoking an API key takes effect within 60 seconds, so any in-flight requests using the old key briefly after rotation will fail. Update all callers to use the new key from Workspace Settings > API Keys.
