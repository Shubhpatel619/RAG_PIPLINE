# Aperture API Reference (v1)

Base URL: `https://api.aperture.example/v1`

All requests require an `Authorization: Bearer <api_key>` header. API keys are generated per workspace under Workspace Settings > API Keys, and only workspace owners and admins can generate them.

## Authentication

`GET /me`
Returns the workspace and permission level associated with the current API key. Use this to verify a key is valid before making other calls.

## Resetting an API key

There is no endpoint to reset a key remotely. To reset a key, an owner or admin must go to Workspace Settings > API Keys in the dashboard and click "Revoke," then generate a new one. Revoking a key takes effect within 60 seconds; any requests using the old key after that point return `401 Unauthorized`.

## Endpoints

`GET /workspaces/{id}/snapshots?from=&to=`
Returns daily snapshots in the given date range. Range is limited to 90 days per request; paginate for longer ranges.

`GET /workspaces/{id}/cycle-time?since=`
Returns aggregated weekly cycle-time data since the given date. Returns `422` if the workspace's cycle definition has not been configured.

`GET /workspaces/{id}/burndown?cycle=`
Returns burn-down data for the named cycle (sprint). If no cycle name is given, returns the currently active cycle.

## Rate limits

100 requests per minute per API key. Exceeding this returns `429 Too Many Requests` with a `Retry-After` header.
