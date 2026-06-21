# Launcher API Contract

**Status:** Stable (Phase 5)  
**Base Path:** `/api/launcher`  
**Version:** 1.0  
**Last Updated:** 2026-03-17

## Overview

The Launcher API provides stable REST endpoints for managing uHOME presentation
sessions on TV nodes and console devices. It supports starting, stopping, and
querying launcher sessions for different presentation modes (thin-gui,
steam-console), along with a console-friendly action menu.

## Authentication

All endpoints require server authentication. Authentication mechanism TBD
(placeholder for future authentication implementation).

## Endpoints

### GET /api/launcher/status

Get current launcher session status including active presentation, node role,
and configuration.

**Request:**
```http
GET /api/launcher/status HTTP/1.1
Host: uhome-server.local:8090
```

**Response:**
```json
{
  "supported_presentations": ["thin-gui", "steam-console"],
  "supported_node_roles": ["server", "tv-node"],
  "active_presentation": "thin-gui",
  "running": true,
  "preferred_presentation": "thin-gui",
  "preferred_presentation_source": "template_workspace",
  "node_role": "tv-node",
  "node_role_source": "template_workspace",
  "state_path": "/path/to/memory/kiosk/uhome/presentation.json",
  "updated_at": "2026-03-10T15:30:00Z",
  "session_id": "abc123def456"
}
```

**Response Fields:**
- `supported_presentations`: List of valid presentation mode names
- `supported_node_roles`: List of valid node role names
- `active_presentation`: Currently running presentation (null if stopped)
- `running`: Boolean indicating if a session is active
- `preferred_presentation`: Default presentation mode from config
- `preferred_presentation_source`: Source of preferred value (template_workspace, default)
- `node_role`: Current node role (server or tv-node)
- `node_role_source`: Source of node role value
- `state_path`: File path where session state is persisted
- `updated_at`: ISO 8601 timestamp of last state change
- `session_id`: Unique session identifier (if available)

**Status Codes:**
- `200 OK` - Status retrieved successfully

### GET /api/launcher/menu

Get a console-friendly menu that describes launcher and stream-control actions.

**Request:**
```http
GET /api/launcher/menu HTTP/1.1
Host: uhome-server.local:8090
```

**Response:**
```json
{
  "menu_id": "uhome-console-main",
  "title": "uHOME Console",
  "running": true,
  "active_presentation": "thin-gui",
  "preferred_presentation": "thin-gui",
  "node_role": "tv-node",
  "items": [
    {
      "id": "start-steam-console",
      "label": "Start Steam Console",
      "enabled": true,
      "action": {
        "method": "POST",
        "path": "/api/launcher/start",
        "body": {"presentation": "steam-console"}
      }
    }
  ]
}
```

**Status Codes:**
- `200 OK` - Menu payload retrieved successfully

### POST /api/launcher/start

Start a new launcher presentation session.

**Request:**
```http
POST /api/launcher/start HTTP/1.1
Host: uhome-server.local:8090
Content-Type: application/json

{
  "presentation": "thin-gui"
}
```

**Request Body Schema:**
```typescript
{
  presentation?: string;  // Optional: Presentation mode (thin-gui, steam-console)
                          // Uses default from config if not specified
}
```

**Response:**
```json
{
  "status": "started",
  "active_presentation": "thin-gui",
  "node_role": "tv-node",
  "updated_at": "2026-03-10T15:30:00Z",
  "session_id": "abc123def456"
}
```

**Response Fields:**
- `status`: Always "started" on success
- `active_presentation`: The presentation mode that was started
- `node_role`: Node role for this session
- `updated_at`: ISO 8601 timestamp when session was started
- `session_id`: Unique session identifier (if available)

**Validation Errors:**
```json
{
  "detail": "Unsupported uHOME presentation: invalid-mode"
}
```

**Status Codes:**
- `200 OK` - Session started successfully
- `400 Bad Request` - Invalid presentation mode
- `422 Unprocessable Entity` - Validation error

### POST /api/launcher/stop

Stop the currently running launcher session.

**Request:**
```http
POST /api/launcher/stop HTTP/1.1
Host: uhome-server.local:8090
```

**Response:**
```json
{
  "status": "stopped",
  "active_presentation": null,
  "node_role": "tv-node",
  "updated_at": "2026-03-10T15:35:00Z"
}
```

**Response Fields:**
- `status`: Always "stopped" on success
- `active_presentation`: Always null after stopping
- `node_role`: Node role (preserved from previous session)
- `updated_at`: ISO 8601 timestamp when session was stopped

**Status Codes:**
- `200 OK` - Session stopped successfully

## Presentation Modes

### thin-gui
Lightweight GUI presentation for standard TV nodes. Suitable for browser-based
clients and Android TV devices.

### steam-console
Steam Big Picture mode presentation for gaming console nodes. Provides
controller-friendly interface with gamepad navigation.

## Node Roles

### server
Server node role for headless operation. Typically runs background services
without local presentation.

### tv-node
TV node role for living-room devices. Runs local presentation layer with
household-safe UI.

## Integration Examples

### Android TV Client

```kotlin
import retrofit2.http.*
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory

data class LauncherStatus(
    val supported_presentations: List<String>,
    val supported_node_roles: List<String>,
    val active_presentation: String?,
    val running: Boolean,
    val preferred_presentation: String,
    val node_role: String,
    val updated_at: String?,
    val session_id: String?
)

data class LauncherStartRequest(
    val presentation: String? = null
)

data class LauncherStartResponse(
    val status: String,
    val active_presentation: String,
    val node_role: String,
    val updated_at: String,
    val session_id: String?
)

data class LauncherStopResponse(
    val status: String,
    val active_presentation: String?,
    val node_role: String,
    val updated_at: String
)

interface UHomeLauncherApi {
    @GET("/api/launcher/status")
    suspend fun getStatus(): LauncherStatus

    @POST("/api/launcher/start")
    suspend fun startSession(@Body request: LauncherStartRequest): LauncherStartResponse

    @POST("/api/launcher/stop")
    suspend fun stopSession(): LauncherStopResponse
}

// Usage
val retrofit = Retrofit.Builder()
    .baseUrl("http://uhome-server.local:8090")
    .addConverterFactory(GsonConverterFactory.create())
    .build()

val api = retrofit.create(UHomeLauncherApi::class.java)

// Start thin-gui presentation
val startResponse = api.startSession(LauncherStartRequest(presentation = "thin-gui"))
println("Started session: ${startResponse.session_id}")

// Check status
val status = api.getStatus()
if (status.running) {
    println("Active: ${status.active_presentation}")
}

// Stop session
val stopResponse = api.stopSession()
println("Session stopped at ${stopResponse.updated_at}")
```

### Swift Client (Apple TV)

```swift
import Foundation

struct LauncherStatus: Codable {
    let supported_presentations: [String]
    let supported_node_roles: [String]
    let active_presentation: String?
    let running: Bool
    let preferred_presentation: String
    let node_role: String
    let updated_at: String?
    let session_id: String?
}

struct LauncherStartRequest: Codable {
    let presentation: String?
}

struct LauncherStartResponse: Codable {
    let status: String
    let active_presentation: String
    let node_role: String
    let updated_at: String
    let session_id: String?
}

struct LauncherStopResponse: Codable {
    let status: String
    let active_presentation: String?
    let node_role: String
    let updated_at: String
}

class UHomeLauncherClient {
    let baseURL = URL(string: "http://uhome-server.local:8090")!
    
    func getStatus() async throws -> LauncherStatus {
        let url = baseURL.appendingPathComponent("/api/launcher/status")
        let (data, _) = try await URLSession.shared.data(from: url)
        return try JSONDecoder().decode(LauncherStatus.self, from: data)
    }
    
    func startSession(presentation: String? = nil) async throws -> LauncherStartResponse {
        let url = baseURL.appendingPathComponent("/api/launcher/start")
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        
        let body = LauncherStartRequest(presentation: presentation)
        request.httpBody = try JSONEncoder().encode(body)
        
        let (data, _) = try await URLSession.shared.data(for: request)
        return try JSONDecoder().decode(LauncherStartResponse.self, from: data)
    }
    
    func stopSession() async throws -> LauncherStopResponse {
        let url = baseURL.appendingPathComponent("/api/launcher/stop")
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        
        let (data, _) = try await URLSession.shared.data(for: request)
        return try JSONDecoder().decode(LauncherStopResponse.self, from: data)
    }
}

// Usage
let client = UHomeLauncherClient()

// Start default presentation
let startResponse = try await client.startSession()
print("Started: \(startResponse.active_presentation)")

// Check if running
let status = try await client.getStatus()
if status.running {
    print("Active presentation: \(status.active_presentation ?? "none")")
}
```

### JavaScript Client (Web/Google TV)

```javascript
class UHomeLauncherClient {
  constructor(baseURL = 'http://uhome-server.local:8090') {
    this.baseURL = baseURL;
  }

  async getStatus() {
    const response = await fetch(`${this.baseURL}/api/launcher/status`);
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
    return response.json();
  }

  async startSession(presentation = null) {
    const response = await fetch(`${this.baseURL}/api/launcher/start`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ presentation })
    });
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || response.statusText);
    }
    return response.json();
  }

  async stopSession() {
    const response = await fetch(`${this.baseURL}/api/launcher/stop`, {
      method: 'POST'
    });
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
    return response.json();
  }
}

// Usage
const client = new UHomeLauncherClient();

// Check current status
const status = await client.getStatus();
console.log('Running:', status.running);
console.log('Active:', status.active_presentation);

// Start thin-gui presentation
const startResponse = await client.startSession('thin-gui');
console.log('Started session:', startResponse.session_id);

// Stop session
const stopResponse = await client.stopSession();
console.log('Stopped at:', stopResponse.updated_at);
```

## State Persistence

Launcher session state is persisted to disk at:
```
{repo_root}/memory/kiosk/uhome/presentation.json
```

Older installs may still have state under `{repo_root}/memory/wizard/uhome/presentation.json`; the server reads that path until data is migrated by a new write.

Example state file:
```json
{
  "active_presentation": "thin-gui",
  "node_role": "tv-node",
  "updated_at": "2026-03-10T15:30:00Z",
  "last_action": "start",
  "session_id": "abc123def456",
  "thin_gui": {
    "intent": {
      "target": "uhome-console",
      "mode": "home",
      "launcher": "thin-gui",
      "workspace": "uhome",
      "profile_id": "tv-node",
      "auth": {
        "kiosk_local_session": true,
        "wizard_mode_active": false,
        "uhome_role": "tv-node"
      }
    },
    "action": "start",
    "status": "ready"
  }
}
```

## Configuration

Launcher preferences can be set in the template workspace configuration:

**File:** `defaults/workspace/settings/uhome.json`

```json
{
  "presentation_mode": "thin-gui",
  "node_role": "tv-node"
}
```

If not configured, defaults to:
- `presentation_mode`: "thin-gui"
- `node_role`: "server"

## Error Handling

All endpoints use standard HTTP status codes and return JSON error responses:

**400 Bad Request** - Invalid presentation mode or request
**422 Unprocessable Entity** - Validation error
**500 Internal Server Error** - Server-side error

Example error response:
```json
{
  "detail": "Unsupported uHOME presentation: invalid-mode"
}
```

## Backwards Compatibility

The legacy platform routes (`/api/platform/uhome/presentation/*`) remain
available for backwards compatibility but clients should migrate to the new
first-class Launcher API (`/api/launcher/*`).

## Discovery

uHOME server announces itself via mDNS/Bonjour:

- **Service Type:** `_uhome._tcp.local.`
- **Port:** 8090 (default)
- **TXT Records:**
  - `version=1.0`
  - `api_version=1.0`
  - `node_role=tv-node` (or `server`)

Clients should discover the server using platform-specific mDNS/Bonjour APIs
(same as Playback API discovery).

## Future Enhancements

_Planned for future phases:_

- Authentication and authorization
- Multi-user session management
- Remote presentation control from mobile devices
- Session health monitoring and automatic restart
- Advanced presentation modes (kiosk, signage, multi-screen)
- Session handoff between devices
