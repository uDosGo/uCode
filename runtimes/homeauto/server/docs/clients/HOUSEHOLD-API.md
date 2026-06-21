# Household API Contract

**Status:** Stable (Phase 5)  
**Base Path:** `/api/household`  
**Version:** 1.0  
**Last Updated:** 2026-03-10

## Overview

The Household API provides living-room-safe browsing and status endpoints for
shared TV surfaces. Responses are intentionally filtered to avoid explicit
content terms and to reduce user-identifying details.

## Safety Model

The API applies keyword filtering to:

- browse item title and summary
- active session media title in status responses

Default blocked terms:

- `adult`
- `xxx`
- `porn`
- `nsfw`
- `explicit`

Custom blocked terms can be configured with:

- `HOUSEHOLD_BLOCKED_TERMS` (comma-separated string)

Example:

```bash
HOUSEHOLD_BLOCKED_TERMS=adult,xxx,porn,nsfw,explicit,violence
```

## Endpoints

### GET /api/household/status

Returns a household-safe runtime status suitable for living-room clients.

**Request:**

```http
GET /api/household/status HTTP/1.1
Host: uhome-server.local:8090
```

**Response:**

```json
{
  "safe_mode": "household-default",
  "node_role": "tv-node",
  "presentation_mode": "kiosk",
  "preferred_target_client": "living-room",
  "jellyfin_configured": true,
  "jellyfin_reachable": true,
  "active_media": [
    {
      "title": "Family Movie Night",
      "media_type": "Movie",
      "client": "Jellyfin TV"
    }
  ],
  "active_media_count": 1,
  "hidden_media_count": 1,
  "note": null,
  "issue": null,
  "timestamp": "2026-03-10T18:20:00Z"
}
```

**Notes:**

- `active_media` omits user identity fields.
- `hidden_media_count` reports how many sessions were filtered.

### GET /api/household/browse

Returns household-safe browse entries for living-room clients.

**Request:**

```http
GET /api/household/browse?q=home&limit=12 HTTP/1.1
Host: uhome-server.local:8090
```

**Query Parameters:**

- `q` (string, optional): case-insensitive search query
- `limit` (int, optional): max items to return, range `1..100`, default `24`

**Response:**

```json
{
  "safe_mode": "household-default",
  "query": "home",
  "count": 2,
  "total": 2,
  "hidden_count": 1,
  "items": [
    {
      "id": "home-assistant",
      "title": "Home Assistant",
      "summary": "Primary household automation",
      "browser_route": "/ui/home-assistant",
      "category": "container"
    },
    {
      "id": "home-dashboard",
      "title": "Home Dashboard",
      "summary": "Living-room controls",
      "browser_route": "/ui/dashboard",
      "category": "container"
    }
  ],
  "timestamp": "2026-03-10T18:20:00Z"
}
```

**Notes:**

- Items without a `browser_route` are excluded.
- `hidden_count` reports how many candidate items were filtered.

## Integration Example (JavaScript)

```javascript
class UHomeHouseholdClient {
  constructor(baseURL = 'http://uhome-server.local:8090') {
    this.baseURL = baseURL;
  }

  async getStatus() {
    const response = await fetch(`${this.baseURL}/api/household/status`);
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
    return response.json();
  }

  async browse(query = '', limit = 24) {
    const qs = new URLSearchParams({ q: query, limit: String(limit) });
    const response = await fetch(`${this.baseURL}/api/household/browse?${qs.toString()}`);
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
    return response.json();
  }
}
```

## Status Codes

- `200 OK` - successful response
- `422 Unprocessable Entity` - invalid query params (for example `limit=0`)
