# uHOME Client Integration Guide

**Version:** 1.1  
**Status:** Phase 5 Stable  
**Last Updated:** 2026-03-10

## Overview

This guide helps developers integrate with the uHOME server platform when
building Android, Google TV, Apple TV, and web-based clients. The uHOME server
provides stable REST APIs for playback control, launcher session management,
and household-safe media browsing.

## Prerequisites

- uHOME server running and accessible on local network
- Server accessible at `http://uhome-server.local:8090` (or custom address)
- Basic understanding of REST APIs and JSON
- Development environment set up for target platform (Android, iOS/tvOS, web)

## Quick Start

### 1. Discover the Server

uHOME server announces itself via mDNS/Bonjour with service type
`_uhome._tcp.local.`. Use platform-specific APIs to discover:

#### Android (NSD)
```kotlin
import android.content.Context
import android.net.nsd.NsdManager
import android.net.nsd.NsdServiceInfo

class UHomeDiscovery(private val context: Context) {
    private val nsdManager = context.getSystemService(Context.NSD_SERVICE) as NsdManager
    
    fun discover(onFound: (String, Int) -> Unit) {
        val listener = object : NsdManager.DiscoveryListener {
            override fun onServiceFound(service: NsdServiceInfo) {
                if (service.serviceType == "_uhome._tcp.") {
                    nsdManager.resolveService(service, object : NsdManager.ResolveListener {
                        override fun onServiceResolved(serviceInfo: NsdServiceInfo) {
                            val host = serviceInfo.host.hostAddress
                            val port = serviceInfo.port
                            onFound(host ?: "localhost", port)
                        }
                        override fun onResolveFailed(serviceInfo: NsdServiceInfo, errorCode: Int) {}
                    })
                }
            }
            override fun onDiscoveryStopped(serviceType: String) {}
            override fun onDiscoveryStarted(serviceType: String) {}
            override fun onServiceLost(service: NsdServiceInfo) {}
            override fun onStartDiscoveryFailed(serviceType: String, errorCode: Int) {}
            override fun onStopDiscoveryFailed(serviceType: String, errorCode: Int) {}
        }
        
        nsdManager.discoverServices("_uhome._tcp.", NsdManager.PROTOCOL_DNS_SD, listener)
    }
}

// Usage
val discovery = UHomeDiscovery(context)
discovery.discover { host, port ->
    val serverUrl = "http://$host:$port"
    // Initialize API client with serverUrl
}
```

#### iOS/tvOS (Bonjour)
```swift
import Foundation

class UHomeDiscovery: NSObject, NetServiceBrowserDelegate, NetServiceDelegate {
    private let browser = NetServiceBrowser()
    private var onFound: ((String, Int) -> Void)?
    
    func discover(onFound: @escaping (String, Int) -> Void) {
        self.onFound = onFound
        browser.delegate = self
        browser.searchForServices(ofType: "_uhome._tcp.", inDomain: "local.")
    }
    
    func netServiceBrowser(_ browser: NetServiceBrowser, didFind service: NetService, moreComing: Bool) {
        service.delegate = self
        service.resolve(withTimeout: 5.0)
    }
    
    func netServiceDidResolveAddress(_ sender: NetService) {
        guard let addresses = sender.addresses, !addresses.isEmpty else { return }
        if let host = sender.hostName {
            onFound?(host, sender.port)
        }
    }
    
    func netServiceBrowser(_ browser: NetServiceBrowser, didNotSearch errorDict: [String : NSNumber]) {}
    func netService(_ sender: NetService, didNotResolve errorDict: [String : NSNumber]) {}
}

// Usage
let discovery = UHomeDiscovery()
discovery.discover { host, port in
    let serverURL = "http://\(host):\(port)"
    // Initialize API client with serverURL
}
```

#### JavaScript/Web
```javascript
// Web browsers don't support mDNS discovery directly.
// Use a configuration UI to let users enter the server address,
// or implement server-side mDNS proxy for web clients.

const DEFAULT_SERVER_URL = 'http://uhome-server.local:8090';

// Alternatively, provide discovery hints via local storage
function getServerURL() {
  return localStorage.getItem('uhome_server_url') || DEFAULT_SERVER_URL;
}
```

### 2. Verify Server Connection

Test connectivity with the runtime readiness endpoint:

```http
GET /api/runtime/ready HTTP/1.1
Host: uhome-server.local:8090
```

**Expected Response:**
```json
{
  "ready": true,
  "checks": {
    "workspace": {"ok": true},
    "jellyfin": {"ok": true, "jellyfin_configured": true}
  }
}
```

### 3. Advertise Client Capabilities

Inform the server about your client's capabilities (see [CLIENT-CAPABILITIES.md](CLIENT-CAPABILITIES.md)):

```http
POST /api/client/register HTTP/1.1
Host: uhome-server.local:8090
Content-Type: application/json

{
  "client_id": "android-phone-abc123",
  "device_name": "Pixel 7 Pro",
  "platform": "android",
  "capability_profile": "touch",
  "capabilities": {
    "input_methods": ["touchscreen", "gesture"],
    "display_type": "mobile",
    "touch_capable": true,
    "voice_capable": true
  }
}
```

**Example Response:**
```json
{
    "client_id": "android-phone-abc123",
    "registered_at": "2026-03-17T14:20:00Z",
    "session_token": "session_abc123def456",
    "server_recommendations": {
        "ui_mode": "mobile",
        "enable_gestures": true,
        "enable_voice_search": true,
        "recommended_handoff_target": "living-room-tv"
    }
}
```

Clients can be listed with `GET /api/client` and updated dynamically with
`POST /api/client/{client_id}/capabilities`.

### 4. Integrate Core APIs

Use the stable REST APIs:

- **Playback API** - Media status and handoff ([PLAYBACK-API.md](PLAYBACK-API.md))
- **Launcher API** - Session management and console menu ([LAUNCHER-API.md](LAUNCHER-API.md))
- **Household API** - Living-room-safe status and browsing ([HOUSEHOLD-API.md](HOUSEHOLD-API.md))
- **Network Capability Summary** - Topology + streaming + client profile summary (`GET /api/network/capabilities`)

## Core API Integration

### Playback Control

Monitor playback status and queue handoff requests:

```kotlin
// Android Kotlin example
class UHomePlaybackService(private val api: UHomePlaybackApi) {
    suspend fun getCurrentStatus(): PlaybackStatus {
        return api.getStatus()
    }
    
    suspend fun handoffToTV(itemId: String, target: String = "living-room"): HandoffResponse {
        return api.handoff(HandoffRequest(item_id = itemId, target = target))
    }
}

// Usage in Activity/Fragment
lifecycleScope.launch {
    val status = playbackService.getCurrentStatus()
    if (status.jellyfin_reachable == true) {
        status.active_sessions?.forEach { session ->
            println("${session.user} is watching ${session.title}")
        }
    }
    
    // Queue handoff
    val handoff = playbackService.handoffToTV("movie123", "living-room-tv")
    showToast("Queued to ${handoff.target}")
}
```

### Session Management

Start/stop launcher sessions:

```swift
// iOS/tvOS Swift example
class UHomeLauncherService {
    private let client: UHomeLauncherClient
    
    init(client: UHomeLauncherClient) {
        self.client = client
    }
    
    func startSession(presentation: String = "thin-gui") async throws {
        let response = try await client.startSession(presentation: presentation)
        print("Started: \(response.active_presentation)")
    }
    
    func checkStatus() async throws -> LauncherStatus {
        return try await client.getStatus()
    }
}

// Usage in ViewController
Task {
    do {
        let service = UHomeLauncherService(client: launcherClient)
        try await service.startSession()
        
        let status = try await service.checkStatus()
        if status.running {
            updateUI(activePresentation: status.active_presentation)
        }
    } catch {
        showError(error)
    }
}
```

## Platform-Specific Guidelines

### Android Mobile & Tablet

**Capability Profile:** `touch`

**Key Features:**
- Browse media library with rich filtering and search
- Cast to TV devices via playback handoff
- Voice search integration
- Manage household preferences and settings

**UI Patterns:**
- Material Design 3 components
- Bottom navigation or navigation drawer
- RecyclerView with GridLayoutManager for media grids
- SearchView for text and voice search
- FloatingActionButton for quick actions

**Example Architecture:**
```
MainActivity
├── HomeFragment (browse recent/recommended)
├── LibraryFragment (full catalog browsing)
├── SearchFragment (search and filter)
└── SettingsFragment (preferences)
```

### Android TV & Google TV

**Capability Profile:** `remote` (or `controller` with gamepad)

**Key Features:**
- Leanback UI for 10-foot experience
- Launcher session management
- Playback status monitoring
- Simple voice search

**UI Patterns:**
- Leanback library (BrowseSupportFragment, DetailsFragment)
- Large text and artwork
- Clear focus indicators
- Limited text entry (prefer voice)
- Background playback indicators

**Example Architecture:**
```
MainActivity (BrowseSupportFragment)
├── Row: Continue Watching
├── Row: Recommended
└── Row: Categories
    
DetailsActivity (DetailsFragment)
└── Actions: Play, Queue, More Info
```

### Apple TV (tvOS)

**Capability Profile:** `remote` (or `controller` with game controller)

**Key Features:**
- Native tvOS UI (UIKit for tvOS or SwiftUI)
- Focus engine for navigation
- Launcher session control
- Playback handoff from iOS devices

**UI Patterns:**
- Collection views with UICollectionViewCompositionalLayout
- Large, clear button targets
- Parallax effects on focus
- Minimal text entry
- Tab bar for top-level navigation

**Example Architecture:**
```
TabBarController
├── HomeViewController (featured content)
├── LibraryViewController (browse)
└── SettingsViewController (preferences)

MediaDetailsViewController
└── Actions: Play, Add to Queue, More Info
```

### iOS Mobile & iPad

**Capability Profile:** `touch`

**Key Features:**
- Full-featured browsing and search
- Cast to Apple TV via playback handoff
- Settings and household management
- Rich media metadata display

**UI Patterns:**
- SwiftUI or UIKit
- NavigationView/NavigationController
- Collection views or LazyVGrid
- Search with UISearchController
- SF Symbols for icons

**Example Architecture:**
```
TabView (SwiftUI) or UITabBarController
├── HomeView (browse)
├── SearchView (search/filter)
├── LibraryView (collections)
└── SettingsView (preferences)
```

### Web/Progressive Web App

**Capability Profile:** `touch` (mobile) or `remote` (TV browsers)

**Key Features:**
- Cross-platform compatibility
- Responsive design (mobile/tablet/TV)
- Browser-based playback handoff
- No installation required

**UI Patterns:**
- React, Vue, or vanilla JavaScript
- CSS Grid and Flexbox
- Media queries for responsive design
- Touch and keyboard/remote navigation
- Service worker for offline caching

**Example Architecture:**
```
App Component
├── HeaderComponent (navigation)
├── HomeComponent (featured)
├── BrowseComponent (library)
├── SearchComponent (search)
└── DetailsComponent (media details)
```

## Authentication & Security

**Phase 5 Status:** Authentication not yet implemented

Future authentication will likely use:
- Token-based authentication (JWT or similar)
- mDNS-based device trust for local network
- Optional household PIN or biometric auth
- Secure storage for credentials

For now, all endpoints are open within the local network. Clients should:
- Only connect to trusted local networks
- Validate server certificates (if using HTTPS)
- Store server URL securely (keychain/keystore)

## Error Handling

All APIs use standard HTTP status codes:

| Code | Meaning | Action |
|------|---------|--------|
| 200 | OK | Success, parse response |
| 400 | Bad Request | Check request payload, show error message |
| 404 | Not Found | Resource doesn't exist, handle gracefully |
| 422 | Validation Error | Fix validation issues (e.g., missing fields) |
| 500 | Server Error | Retry with exponential backoff, show error to user |

**Example Error Response:**
```json
{
  "detail": "Unsupported uHOME presentation: invalid-mode"
}
```

**Example Validation Error:**
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

## Testing

### Test with Mock Data

Use the example installer artifacts to populate test data:

```bash
# On uHOME server
cd /path/to/uHomeNest
pytest tests/test_example_installer_artifacts.py -v
```

### Test Playback API

```bash
# Get playback status
curl http://uhome-server.local:8090/api/playback/status

# Queue playback handoff
curl -X POST http://uhome-server.local:8090/api/playback/handoff \
  -H "Content-Type: application/json" \
  -d '{"item_id": "abc123", "target": "living-room-tv"}'
```

### Test Launcher API

```bash
# Get launcher status
curl http://uhome-server.local:8090/api/launcher/status

# Start session
curl -X POST http://uhome-server.local:8090/api/launcher/start \
  -H "Content-Type: application/json" \
  -d '{"presentation": "thin-gui"}'

# Stop session
curl -X POST http://uhome-server.local:8090/api/launcher/stop
```

### Test Household API

```bash
# Get household-safe status
curl http://uhome-server.local:8090/api/household/status

# Browse household-safe entries
curl "http://uhome-server.local:8090/api/household/browse?q=home&limit=10"
```

## Best Practices

### Performance

1. **Cache Server Discovery:** Store discovered server URL locally, retry discovery on connection failure
2. **Debounce API Calls:** Avoid rapid-fire requests (e.g., debounce search input)
3. **Use Efficient Polling:** Poll status endpoints at reasonable intervals (5-30 seconds)
4. **Handle Offline:** Cache data locally for offline browsing when possible

### UX Guidelines

1. **Show Connection State:** Clearly indicate when connected/disconnected from server
2. **Provide Feedback:** Show loading states, success/error messages for all actions
3. **Household-Safe UI:** Filter content appropriately for living-room displays
4. **Accessibility:** Support screen readers, large text, high contrast modes
5. **Error Recovery:** Provide clear error messages with retry actions

### Code Organization

1. **Separate API Layer:** Create dedicated API client classes/modules
2. **Use Dependency Injection:** Make API clients injectable for testing
3. **Handle Network Errors:** Wrap API calls in try/catch with proper error handling
4. **Type Safety:** Use strongly-typed models (Kotlin data classes, Swift structs)
5. **Test Coverage:** Write unit tests for API integration logic

## Migration from Legacy APIs

If you were using the legacy Home Assistant bridge endpoints:

**Old:** `/api/ha/command` with `uhome.playback.status` command  
**New:** `/api/playback/status`

**Old:** `/api/platform/uhome/presentation/start`  
**New:** `/api/launcher/start`

The legacy endpoints remain available for backwards compatibility but all new
development should use the first-class REST APIs under `/api/playback/*` and
`/api/launcher/*`.

For living-room-safe UX, new clients should also consume `/api/household/*`
instead of reusing raw subsystem payloads.

## Troubleshooting

### Server Not Discovered via mDNS

- Verify server is running: `curl http://localhost:8090/api/runtime/ready`
- Check firewall settings allow mDNS (port 5353 UDP)
- Try manual server URL entry as fallback
- Ensure client and server are on same local network

### API Requests Failing

- Verify server accessibility: `curl http://uhome-server.local:8090/api/runtime/ready`
- Check request format matches API documentation
- Enable debug logging to see raw requests/responses
- Verify Content-Type header is set correctly (`application/json`)

### Playback Handoff Not Working

- Verify Jellyfin is configured: `GET /api/playback/status` shows `jellyfin_configured: true`
- Check Jellyfin server is reachable from uHOME server
- Verify target device name matches configuration
- Check playback queue: `GET /api/playback/queue?target=living-room`

### Launcher Session Won't Start

- Verify presentation mode is valid: `thin-gui` or `steam-console`
- Check launcher status: `GET /api/launcher/status`
- Review server logs for errors
- Ensure workspace is properly initialized

## Resources

- [Playback API Documentation](PLAYBACK-API.md) - Complete API reference for media playback
- [Launcher API Documentation](LAUNCHER-API.md) - Complete API reference for sessions
- [Household API Documentation](HOUSEHOLD-API.md) - Living-room-safe status and browsing
- [Client Capability Model](CLIENT-CAPABILITIES.md) - Capability profiles and detection
- [uHOME development entry (v4)](../architecture/UHOME-SERVER-DEV-PLAN.md) — roadmaps and thin UI handoff
- [uHOME v4 roadmap](../../../docs/ROADMAP-V4.md) — product line (monorepo `docs/`)

## Support & Contributing

For questions, issues, or contributions:
- Review existing documentation in `/docs`
- Check test suites in `/tests` for usage examples
- Refer to example installer artifacts for test data

## Version History

- **1.1** (2026-03-10): Added household-safe API integration guidance
    - Added household endpoint testing examples
    - Added household API to integration resources
    - Added recommendation to use `/api/household/*` for living-room UX

- **1.0** (2026-03-10): Initial stable client integration guide for Phase 5
  - Playback API documented and stable
  - Launcher API extracted and documented
  - Client capability model defined
  - Platform-specific guidelines added
