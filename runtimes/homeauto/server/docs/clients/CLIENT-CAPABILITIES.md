# Client Capability Model

**Status:** Specification (Phase 5)  
**Version:** 1.0  
**Last Updated:** 2026-03-10

## Overview

The uHOME Client Capability Model defines standard capability profiles for
downstream clients (Android, Google TV, Apple TV) to advertise their input
methods, display characteristics, and interaction patterns. This enables the
server to adapt responses and recommendations based on client capabilities.

## Capability Profiles

### Controller
**Input:** Gamepad, D-pad navigation, button-based selection  
**Display:** Large-screen TV (10-foot UI)  
**Interaction Pattern:** Lean-back, couch-based navigation

**Typical Devices:**
- Game consoles (Xbox, PlayStation, Nintendo Switch)
- Steam Big Picture mode
- Android TV with game controller
- Apple TV with game controller

**Characteristics:**
```json
{
  "capability_profile": "controller",
  "input_methods": ["gamepad", "dpad"],
  "display_type": "tv",
  "interaction_distance": "10ft",
  "touch_capable": false,
  "voice_capable": false,
  "keyboard_capable": false
}
```

### Remote
**Input:** TV remote, directional pad, numeric keypad  
**Display:** Large-screen TV (10-foot UI)  
**Interaction Pattern:** Lean-back, simple navigation, limited text entry

**Typical Devices:**
- Smart TVs with standard remote
- Android TV with IR remote
- Apple TV with Siri Remote (D-pad mode)
- Fire TV with Alexa Voice Remote
- Google TV with standard remote

**Characteristics:**
```json
{
  "capability_profile": "remote",
  "input_methods": ["dpad", "numeric_keypad"],
  "display_type": "tv",
  "interaction_distance": "10ft",
  "touch_capable": false,
  "voice_capable": true,
  "keyboard_capable": false
}
```

### Touch
**Input:** Touchscreen, gestures, on-screen keyboard  
**Display:** Mobile screen or tablet (arm's length UI)  
**Interaction Pattern:** Lean-forward, direct manipulation, rich text entry

**Typical Devices:**
- Android phones and tablets
- iOS devices (iPhone, iPad)
- Android tablets
- Mobile web browsers

**Characteristics:**
```json
{
  "capability_profile": "touch",
  "input_methods": ["touchscreen", "gesture"],
  "display_type": "mobile",
  "interaction_distance": "1ft",
  "touch_capable": true,
  "voice_capable": true,
  "keyboard_capable": true
}
```

## Extended Capabilities

Beyond the base profiles, clients can advertise extended capabilities:

### Resolution & Display
```json
{
  "display_resolution": {
    "width": 1920,
    "height": 1080
  },
  "display_density": 320,
  "hdr_capable": true,
  "refresh_rate": 60
}
```

### Media Playback
```json
{
  "codec_support": ["h264", "h265", "vp9", "av1"],
  "audio_channels": 5.1,
  "subtitles_capable": true,
  "local_playback": true
}
```

### Network & Casting
```json
{
  "casting_capable": true,
  "casting_protocols": ["chromecast", "airplay"],
  "network_quality": "wifi-5ghz"
}
```

### Authentication & Security
```json
{
  "biometric_auth": true,
  "secure_storage": true,
  "device_pin_required": false
}
```

## Capability Advertisement

Clients should advertise their capabilities when first connecting to the server
or when capabilities change (e.g., controller connected/disconnected).

**Endpoint:** `POST /api/client/register`

**Request:**
```http
POST /api/client/register HTTP/1.1
Host: uhome-server.local:8090
Content-Type: application/json

{
  "client_id": "android-phone-abc123",
  "device_name": "Pixel 7 Pro",
  "platform": "android",
  "os_version": "14",
  "app_version": "1.0.0",
  "capability_profile": "touch",
  "capabilities": {
    "input_methods": ["touchscreen", "gesture"],
    "display_type": "mobile",
    "interaction_distance": "1ft",
    "touch_capable": true,
    "voice_capable": true,
    "keyboard_capable": true,
    "display_resolution": {
      "width": 1440,
      "height": 3120
    },
    "codec_support": ["h264", "vp9"],
    "casting_capable": true,
    "casting_protocols": ["chromecast"]
  }
}
```

**Response:**
```json
{
  "client_id": "android-phone-abc123",
  "registered_at": "2026-03-10T15:30:00Z",
  "session_token": "session_abc123def456",
  "server_recommendations": {
    "ui_mode": "mobile",
    "enable_gestures": true,
    "enable_voice_search": true
  }
}
```

## Server Adaptations

Based on advertised capabilities, the server should adapt:

### UI Recommendations

**Controller Profile:**
- Large button targets (80x80 px minimum)
- High-contrast focus indicators
- Shallow navigation hierarchies
- Avoid text entry when possible
- Provide numeric shortcuts for common actions

**Remote Profile:**
- Very large button targets (100x100 px minimum)
- Clear directional cues
- Limited options per screen (5-7 items)
- Voice search as primary text entry
- Numeric keypad shortcuts

**Touch Profile:**
- Standard touch targets (44x44 dp minimum)
- Gesture support (swipe, pinch, long-press)
- Rich text entry with on-screen keyboard
- Multi-column layouts
- Pull-to-refresh and infinite scroll

### Content Filtering

**10-foot UI (Controller/Remote):**
- Household-safe content browsing
- Simplified metadata (title, year, rating)
- Large artwork (posters, backdrops)
- Auto-play trailers
- Focus on recently watched and recommendations

**Mobile UI (Touch):**
- Detailed metadata and descriptions
- User-specific watch history
- Advanced search and filtering
- Playlist and queue management
- Settings and configuration

### Playback Handoff

**Source Capabilities:**
- Touch devices can cast to TV devices
- Remote devices can suggest items to other displays
- Controller devices typically receive playback commands

**Target Selection:**
```json
{
  "available_targets": [
    {
      "device_id": "living-room-tv",
      "device_name": "Living Room TV",
      "capability_profile": "remote",
      "currently_playing": null,
      "recommended": true
    },
    {
      "device_id": "bedroom-tv",
      "device_name": "Bedroom TV",
      "capability_profile": "controller",
      "currently_playing": "Example Movie",
      "recommended": false
    }
  ]
}
```

## Capability Detection

### Client-Side Detection Examples

**Android:**
```kotlin
fun detectCapabilities(context: Context): ClientCapabilities {
    val uiMode = context.resources.configuration.uiMode and Configuration.UI_MODE_TYPE_MASK
    
    val profile = when {
        uiMode == Configuration.UI_MODE_TYPE_TELEVISION -> {
            if (hasGameController(context)) "controller" else "remote"
        }
        else -> "touch"
    }
    
    return ClientCapabilities(
        capability_profile = profile,
        input_methods = detectInputMethods(context),
        display_type = if (uiMode == Configuration.UI_MODE_TYPE_TELEVISION) "tv" else "mobile",
        touch_capable = context.packageManager.hasSystemFeature(PackageManager.FEATURE_TOUCHSCREEN),
        voice_capable = SpeechRecognizer.isRecognitionAvailable(context),
        keyboard_capable = context.resources.configuration.keyboard != Configuration.KEYBOARD_NOKEYS
    )
}

fun hasGameController(context: Context): Boolean {
    val inputDeviceIds = InputDevice.getDeviceIds()
    return inputDeviceIds.any { id ->
        val device = InputDevice.getDevice(id)
        device?.sources?.and(InputDevice.SOURCE_GAMEPAD) == InputDevice.SOURCE_GAMEPAD
    }
}
```

**iOS/tvOS:**
```swift
func detectCapabilities() -> ClientCapabilities {
    #if os(tvOS)
    let profile = GCController.controllers().isEmpty ? "remote" : "controller"
    let displayType = "tv"
    let interactionDistance = "10ft"
    #else
    let profile = "touch"
    let displayType = "mobile"
    let interactionDistance = "1ft"
    #endif
    
    return ClientCapabilities(
        capability_profile: profile,
        input_methods: detectInputMethods(),
        display_type: displayType,
        interaction_distance: interactionDistance,
        touch_capable: UIDevice.current.userInterfaceIdiom != .tv,
        voice_capable: SFSpeechRecognizer.authorizationStatus() != .notDetermined,
        keyboard_capable: GCKeyboard.coalesced != nil
    )
}
```

## Capability Evolution

Capabilities can change during a session:

### Dynamic Updates

**Controller Connected:**
```json
{
  "event": "capability_changed",
  "client_id": "android-tv-living-room",
  "previous_profile": "remote",
  "current_profile": "controller",
  "capabilities": {
    "input_methods": ["gamepad", "dpad"],
    "gamepad_connected": true
  }
}
```

**Casting Started:**
```json
{
  "event": "capability_changed",
  "client_id": "android-phone-abc123",
  "capabilities": {
    "casting_active": true,
    "casting_target": "living-room-tv",
    "casting_protocol": "chromecast"
  }
}
```

## Best Practices

### Implementation Guidelines

1. **Detect on Launch:** Determine capability profile during app initialization
2. **Advertise Early:** Register capabilities immediately after server discovery
3. **Update on Change:** Send capability updates when input devices connect/disconnect
4. **Cache Locally:** Store capability profile for offline operation
5. **Respect Overrides:** Allow users to manually select UI mode if desired
6. **Test All Profiles:** Ensure your app works with all three base profiles
7. **Graceful Degradation:** Fall back to simpler capabilities if detection fails

### Server Guidelines

1. **Default to Safe:** Assume `remote` profile if capabilities not advertised
2. **Don't Block:** Allow all clients to function regardless of capabilities
3. **Optimize, Don't Restrict:** Use capabilities to improve UX, not gate features
4. **Version Capabilities:** Support evolving capability schemas across versions
5. **Log Capabilities:** Track client capabilities for analytics and debugging

## Future Extensions

_Planned for future phases:_

- Haptic feedback support
- Spatial audio capabilities
- Multi-screen coordination (companion devices)
- Accessibility profiles (screen reader, voice control, etc.)
- Network bandwidth and quality metrics
- Power state and battery level considerations
