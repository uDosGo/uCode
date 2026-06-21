# Jellyfin Integration

Status: stable
Updated: 2026-03-10

## Overview

`uHOME Server` integrates with Jellyfin for media library management and
playback session tracking. The integration is optional but recommended for full
media functionality.

## Configuration

Jellyfin integration requires two environment variables or config values:

- `JELLYFIN_URL`: Base URL of the Jellyfin server (e.g., `http://localhost:8096`)
- `JELLYFIN_API_KEY`: API key for server-to-server communication

### Setting Up Configuration

Option 1: Environment variables

```bash
export JELLYFIN_URL=http://localhost:8096
export JELLYFIN_API_KEY=your_api_key_here
```

Option 2: Config file (`memory/config/uhome.json`)

```json
{
  "JELLYFIN_URL": "http://localhost:8096",
  "JELLYFIN_API_KEY": "your_api_key_here"
}
```

### Obtaining A Jellyfin API Key

1. Log into your Jellyfin instance as an admin
2. Navigate to Dashboard → API Keys
3. Create a new API key for `uHOME Server`
4. Copy the generated key to your configuration

## Integration Points

### Playback Status

The server queries Jellyfin's `/Sessions` endpoint to report active playback
sessions:

- tracks which users are watching content
- reports currently playing media titles and types
- exposes active client information

Accessed via:

- `uhome.playback.status` command (Home Assistant bridge)
- Runtime readiness probe (reports Jellyfin reachability)

### Health Checks

The runtime readiness probe includes a Jellyfin health check:

- `jellyfin_configured`: whether URL and API key are set
- `jellyfin_reachable`: whether the server responded successfully

This check is non-blocking — the server remains healthy even if Jellyfin is
unreachable.

### Media Library

Future integration points (planned):

- library sync and indexing
- media metadata resolution
- playback handoff to living-room clients

## API Endpoints

### Runtime Readiness

`GET /api/runtime/ready`

Includes Jellyfin status in the health probe:

```json
{
  "ok": true,
  "checks": {
    "jellyfin": {
      "ok": true,
      "jellyfin_configured": true,
      "jellyfin_reachable": true
    }
  }
}
```

### Playback Status (Home Assistant Bridge)

`POST /api/ha/command`

```json
{
  "command": "uhome.playback.status",
  "params": {}
}
```

Response includes active Jellyfin sessions:

```json
{
  "command": "uhome.playback.status",
  "jellyfin_configured": true,
  "jellyfin_reachable": true,
  "active_sessions": [
    {
      "user": "alice",
      "title": "Movie Title",
      "media_type": "Movie",
      "client": "Jellyfin Web"
    }
  ]
}
```

## Troubleshooting

### Jellyfin Not Reachable

If `jellyfin_reachable` is `false`:

1. Verify `JELLYFIN_URL` is correct and accessible from the server
2. Check that Jellyfin is running
3. Verify network connectivity and firewall rules
4. Check Jellyfin logs for authentication or API errors

### API Key Issues

If playback status returns empty sessions despite active playback:

1. Verify `JELLYFIN_API_KEY` is correct
2. Ensure the API key has appropriate permissions
3. Regenerate the API key if suspect

### HTTPS And Certificates

For HTTPS Jellyfin URLs:

- ensure the certificate is valid and trusted by the server
- use `http://` for local development if certificate issues arise

## Testing

Run Jellyfin integration tests:

```bash
pytest tests/ -k jellyfin
```

Manual verification:

```bash
# Check runtime status
curl http://localhost:8000/api/runtime/ready | jq '.checks.jellyfin'

# Check playback status
curl -X POST http://localhost:8000/api/ha/command \
  -H 'Content-Type: application/json' \
  -d '{"command":"uhome.playback.status","params":{}}' | jq
```

## Future Work

- extract playback endpoints to first-class REST routes (Phase 5)
- add library sync and indexing integration
- support media metadata resolution and artwork
- implement playback handoff coordination with Jellyfin
