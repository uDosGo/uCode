# Playback API Contract

**Status:** Stable (Phase 5)  
**Base Path:** `/api/playback`  
**Version:** 1.0  
**Last Updated:** 2026-03-10

## Overview

The Playback API provides stable REST endpoints for client applications (Android,
Google TV, Apple TV) to coordinate media playback across household devices. It
supports status queries, playback handoff, and queue management.

## Authentication

All endpoints require server authentication. Authentication mechanism TBD
(placeholder for future authentication implementation).

## Endpoints

### GET /api/playback/status

Get current playback status including Jellyfin integration state and active sessions.

**Request:**
```http
GET /api/playback/status HTTP/1.1
Host: uhome-server.local:8090
```

**Response (Jellyfin Configured & Reachable):**
```json
{
  "jellyfin_configured": true,
  "jellyfin_reachable": true,
  "active_sessions": [
    {
      "user": "alice",
      "client": "Jellyfin Web",
      "title": "Example Movie",
      "type": "Movie",
      "id": "abc123"
    }
  ]
}
```

**Response (Jellyfin Not Configured):**
```json
{
  "jellyfin_configured": false,
  "note": "Jellyfin integration not configured. Set JELLYFIN_URL and JELLYFIN_API_KEY."
}
```

**Response (Jellyfin Unreachable):**
```json
{
  "jellyfin_configured": true,
  "jellyfin_reachable": false,
  "issue": "Connection refused to http://localhost:8096"
}
```

**Status Codes:**
- `200 OK` - Status retrieved successfully

### POST /api/playback/handoff

Request playback handoff to transfer media from one device to another.

**Request:**
```http
POST /api/playback/handoff HTTP/1.1
Host: uhome-server.local:8090
Content-Type: application/json

{
  "item_id": "abc123",
  "target": "living-room-tv"
}
```

**Request Body Schema:**
```typescript
{
  item_id: string;      // Required: Jellyfin item ID to play
  target?: string;      // Optional: Target device name (defaults to "living-room")
}
```

**Response:**
```json
{
  "status": "queued",
  "item_id": "abc123",
  "target": "living-room-tv",
  "note": "Playback handoff queued for living-room-tv"
}
```

**Validation Errors:**
```json
{
  "detail": [
    {
      "type": "missing",
      "loc": ["body", "item_id"],
      "msg": "Field required"
    }
  ]
}
```

**Status Codes:**
- `200 OK` - Handoff queued successfully
- `422 Unprocessable Entity` - Validation error (missing or invalid fields)

### GET /api/playback/queue

Get the current playback queue for a target device.

**Request:**
```http
GET /api/playback/queue?target=living-room-tv HTTP/1.1
Host: uhome-server.local:8090
```

**Query Parameters:**
- `target` (string, optional): Target device name (defaults to "living-room")

**Response:**
```json
{
  "target": "living-room-tv",
  "queue": [
    {
      "item_id": "abc123",
      "target": "living-room-tv"
    },
    {
      "item_id": "def456",
      "target": "living-room-tv"
    }
  ]
}
```

**Status Codes:**
- `200 OK` - Queue retrieved successfully

### DELETE /api/playback/queue

Clear the playback queue for a target device.

**Request:**
```http
DELETE /api/playback/queue?target=living-room-tv HTTP/1.1
Host: uhome-server.local:8090
```

**Query Parameters:**
- `target` (string, optional): Target device name (defaults to "living-room")

**Response:**
```json
{
  "status": "cleared",
  "target": "living-room-tv"
}
```

**Status Codes:**
- `200 OK` - Queue cleared successfully

## Integration Examples

### Android Client

```kotlin
import retrofit2.http.*
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory

data class PlaybackStatus(
    val jellyfin_configured: Boolean,
    val jellyfin_reachable: Boolean?,
    val active_sessions: List<ActiveSession>?
)

data class ActiveSession(
    val user: String,
    val client: String,
    val title: String,
    val type: String,
    val id: String
)

data class HandoffRequest(
    val item_id: String,
    val target: String? = null
)

data class HandoffResponse(
    val status: String,
    val item_id: String,
    val target: String
)

interface UHomePlaybackApi {
    @GET("/api/playback/status")
    suspend fun getStatus(): PlaybackStatus

    @POST("/api/playback/handoff")
    suspend fun handoff(@Body request: HandoffRequest): HandoffResponse
}

// Usage
val retrofit = Retrofit.Builder()
    .baseUrl("http://uhome-server.local:8090")
    .addConverterFactory(GsonConverterFactory.create())
    .build()

val api = retrofit.create(UHomePlaybackApi::class.java)
val status = api.getStatus()
```

### Swift Client (Apple TV)

```swift
import Foundation

struct PlaybackStatus: Codable {
    let jellyfin_configured: Bool
    let jellyfin_reachable: Bool?
    let active_sessions: [ActiveSession]?
}

struct ActiveSession: Codable {
    let user: String
    let client: String
    let title: String
    let type: String
    let id: String
}

struct HandoffRequest: Codable {
    let item_id: String
    let target: String?
}

struct HandoffResponse: Codable {
    let status: String
    let item_id: String
    let target: String
}

class UHomePlaybackClient {
    let baseURL = URL(string: "http://uhome-server.local:8090")!
    
    func getStatus() async throws -> PlaybackStatus {
        let url = baseURL.appendingPathComponent("/api/playback/status")
        let (data, _) = try await URLSession.shared.data(from: url)
        return try JSONDecoder().decode(PlaybackStatus.self, from: data)
    }
    
    func handoff(itemId: String, target: String? = nil) async throws -> HandoffResponse {
        let url = baseURL.appendingPathComponent("/api/playback/handoff")
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        
        let body = HandoffRequest(item_id: itemId, target: target)
        request.httpBody = try JSONEncoder().encode(body)
        
        let (data, _) = try await URLSession.shared.data(for: request)
        return try JSONDecoder().decode(HandoffResponse.self, from: data)
    }
}
```

### JavaScript Client (Web/Google TV)

```javascript
class UHomePlaybackClient {
  constructor(baseURL = 'http://uhome-server.local:8090') {
    this.baseURL = baseURL;
  }

  async getStatus() {
    const response = await fetch(`${this.baseURL}/api/playback/status`);
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
    return response.json();
  }

  async handoff(itemId, target = 'living-room') {
    const response = await fetch(`${this.baseURL}/api/playback/handoff`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ item_id: itemId, target })
    });
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
    return response.json();
  }

  async getQueue(target = 'living-room') {
    const response = await fetch(
      `${this.baseURL}/api/playback/queue?target=${encodeURIComponent(target)}`
    );
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
    return response.json();
  }

  async clearQueue(target = 'living-room') {
    const response = await fetch(
      `${this.baseURL}/api/playback/queue?target=${encodeURIComponent(target)}`,
      { method: 'DELETE' }
    );
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
    return response.json();
  }
}

// Usage
const client = new UHomePlaybackClient();
const status = await client.getStatus();
if (status.jellyfin_reachable) {
  console.log('Active sessions:', status.active_sessions);
}
```

## Error Handling

All endpoints use standard HTTP status codes and return JSON error responses:

**400 Bad Request** - Invalid request parameters
**404 Not Found** - Resource not found
**422 Unprocessable Entity** - Validation error (includes structured error details)
**500 Internal Server Error** - Server-side error

Example validation error response:
```json
{
  "detail": [
    {
      "type": "missing",
      "loc": ["body", "item_id"],
      "msg": "Field required",
      "input": {}
    }
  ]
}
```

## Discovery

uHOME server announces itself via mDNS/Bonjour:

- **Service Type:** `_uhome._tcp.local.`
- **Port:** 8090 (default)
- **TXT Records:**
  - `version=1.0`
  - `api_version=1.0`

Clients should discover the server using platform-specific mDNS/Bonjour APIs:

**Android (NSD):**
```kotlin
val serviceInfo = ServiceInfo().apply {
    serviceType = "_uhome._tcp."
    serviceName = "uHOME Server"
}
nsdManager.discoverServices(serviceInfo, NsdManager.PROTOCOL_DNS_SD, listener)
```

**iOS/tvOS (Bonjour):**
```swift
let browser = NetServiceBrowser()
browser.searchForServices(ofType: "_uhome._tcp.", inDomain: "local.")
```

## Backwards Compatibility

The legacy Home Assistant bridge command handlers (`uhome.playback.status` and
`uhome.playback.handoff`) remain available but are now thin wrappers around the
PlaybackService. The legacy handlers return the same data with an added
`"command"` field for backwards compatibility.

Clients should use the new REST API (`/api/playback/*`) for all new integrations.

## Future Enhancements

_Planned for future phases:_

- Authentication and authorization
- User-specific session management
- Multi-user household profiles
- Enhanced queue manipulation (insert, reorder, remove individual items)
- Playback progress tracking and resume support
- Client capability advertisement and negotiation
