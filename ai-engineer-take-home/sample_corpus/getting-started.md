# Getting Started with Aperture

## 1. Create a workspace

Sign up at the Aperture dashboard and create a workspace. You'll be asked to name it after your team (e.g., "Payments Team") and choose a time zone. The time zone determines when daily snapshots are taken (default: 02:00 in the workspace time zone).

## 2. Connect a tracker

From Workspace Settings > Integrations, choose Jira Cloud, Linear, or Trello. You will be redirected to that provider to authorize read-only access. Aperture never requests write access during setup.

Only one tracker integration is allowed per workspace. If you need to track two trackers, create two workspaces.

## 3. Choose a cycle definition

Aperture needs to know which status in your tracker counts as "In Progress" and which counts as "Done," since teams name these differently. This is configured under Workspace Settings > Cycle Definition. Until this is set, cycle-time reports will show as "Not configured" rather than an estimate.

## 4. Wait for the first snapshot

The first full snapshot runs within 15 minutes of connecting a tracker. Historical backfill (computing cycle time for issues closed before you connected Aperture) is only available on the Team and Enterprise plans, and only covers the trailing 90 days at signup.

## 5. Invite teammates

Teammates can be invited from Workspace Settings > Members. Any member can view dashboards; only the workspace owner and admins can change the tracker integration or cycle definition.
