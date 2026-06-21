---
title: "Home Assistant Deep Integration — uHomeNest Console Embed"
status: draft
last_updated: 2026-05-20T22:32:12+10:00
category: readme
tags: [ai, assist, home-assistant, iot, ucode3]
description: "**Document ID:** UDN-HA-EMBED-001"
---
# Home Assistant Deep Integration — uHomeNest Console Embed

**Document ID:** UDN-HA-EMBED-001  
**Status:** Active  
**Version:** 1.0.0  
**Date:** 2026-04-21  
**Priority:** HIGH  
**Related:** [Matter+HA Integration Plan](./UDN-INTEGRATION-001.md), [Alexa/Google/HomeKit Guide](./UDN-VOICE-INTEGRATION-001.md), [uHomeNest v1.0.0 Dev Brief](./UHOMENEST-V1-DEV-BRIEF.md)

***

## Executive Summary

Home Assistant already provides a **world-class, production-ready UI** for home automation. Rather than rebuilding dashboard surfaces, uHomeNest will **embed HA's UI directly** into the controller-first console experience.

**Core Principle:** uHomeNest owns the **launcher and navigation**; HA owns the **automation UI**. The user should never feel like they left the console.

***

## Architecture: Embedded HA Console

### Topology

````
┌─────────────────────────────────────────────────────────────────────┐
│                    uHomeNest Kiosk Browser                          │
│                    (Controller-first UI)                            │
├─────────────────────────────────────────────────────────────────────┤
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │                    USXD Launcher Surface                       │  │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐             │  │
│  │  │ Media   │ │  HA     │ │ Matter  │ │ Settings│             │  │
│  │  │ Library │ │Dashboard│ │ Devices │ │         │             │  │
│  │  └─────────┘ └────┬────┘ └─────────┘ └─────────┘             │  │
│  └───────────────────┼───────────────────────────────────────────┘  │
│                      │                                              │
│  ┌───────────────────▼───────────────────────────────────────────┐  │
│  │                    HA Embed Frame                              │  │
│  │  ┌─────────────────────────────────────────────────────────┐  │  │
│  │  │                                                         │  │  │
│  │  │           Home Assistant Lovelace UI                    │  │  │
│  │  │           (iframe or webview embed)                     │  │  │
│  │  │                                                         │  │  │
│  │  │  ┌─────────┐ ┌─────────┐ ┌─────────┐                   │  │  │
│  │  │  │ Living  │ │ Kitchen │ │ Bedroom │                   │  │  │
│  │  │  │ Room    │ │ Lights  │ │ Temp    │                   │  │  │
│  │  │  │ 72°     │ │ ●●●○○   │ │ 68°     │                   │  │  │
│  │  │  └─────────┘ └─────────┘ └─────────┘                   │  │  │
│  │  │                                                         │  │  │
│  │  └─────────────────────────────────────────────────────────┘  │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                                                                     │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │                    Console Footer                              │  │
│  │  [B: Back] [A: Select] [X: HA Menu] [Y: Voice]                │  │
│  └───────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              │ HA API (WebSocket/REST)
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    Home Assistant Core                              │
│                    (cloned & running)                               │
│                                                                     │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                 │
│  │ Lovelace    │  │ Entities    │  │ Automations │                 │
│  │ Dashboards  │  │ Registry    │  │ Engine      │                 │
│  └─────────────┘  └─────────────┘  └─────────────┘                 │
└─────────────────────────────────────────────────────────────────────┘
````

### Embed Strategies

| Strategy              | Method                                | Pros                             | Cons                                                | Recommendation         |
| --------------------- | ------------------------------------- | -------------------------------- | --------------------------------------------------- | ---------------------- |
| **Iframe Embed**      | `<iframe src="http://ha.local:8123">` | Simplest, full HA UI             | Controller navigation may not work, URL bar visible | ⭐⭐                   |
| **WebView Embed**     | Electron-style webview                | Better isolation, IPC possible   | Complex, requires native                            | ⭐⭐⭐                 |
| **HA Guest Mode**     | HA's built-in kiosk mode              | Designed for this, hides sidebar | Requires HA configuration                           | ⭐⭐⭐⭐               |
| **API-Driven Custom** | REST/WebSocket + custom components    | Full controller integration      | Most work to build                                  | ⭐⭐⭐⭐⭐ (long-term) |

**Recommended Path (Phased):**

1. **Phase 1:** HA Guest Mode + iframe (quick win)
2. **Phase 2:** HA Guest Mode + postMessage API for controller events
3. **Phase 3:** Native HA Lovelace card type for uHomeNest

***

## HA Guest Mode Configuration

### Lovelace Kiosk Mode

Home Assistant has built-in **kiosk mode** features via HACS or custom configuration:

**Option A:** **`kiosk-mode`** **kiosk-mode** **HACS integration**

```yaml
# configuration.yaml
kiosk_mode:
  hide_header: true
  hide_sidebar: true
  hide_menu_button: true
  hide_overflow: true
  allowed_users:
    - uhome_kiosk
```

**Option B: Custom Lovelace view for console**

```yaml
# lovelace configuration for uhome_console view
views:
  - title: uHome Console
    theme: backend-selected
    panel: true
    cards:
      - type: custom:vertical-stack-in-card
        cards:
          - type: entities
            title: Living Room
            entities:
              - light.living_room_main
              - climate.living_room_thermostat
              - media_player.living_room_tv
          - type: glance
            title: Quick Actions
            entities:
              - scene.movie_time
              - scene.good_night
              - automation.welcome_home
    kiosk:
      hide_header: true
      hide_sidebar: true
```

### HA User for Kiosk

```bash
# Create dedicated kiosk user via HA CLI
ha auth create --username uhome_kiosk --password <generated>
ha auth groups add uhome_kiosk --group system-users

# Grant necessary permissions
# - Read entities
# - Execute services (turn on/off, set temperature)
# - No admin access
```

***

## uHomeNest → HA Integration Manager

### Clone & Run Configuration

**`/opt/uhome-integrations/manifest.json`** **/opt/uhome-integrations/manifest.json** (updated for HA):

```json
{
  "components": [
    {
      "name": "home-assistant",
      "enabled": true,
      "repo": "https://github.com/home-assistant/core.git",
      "branch": "2026.4",
      "path": "clones/home-assistant",
      "run_mode": "container",
      "container_config": {
        "image": "ghcr.io/home-assistant/home-assistant:stable",
        "ports": {
          "8123": "8123"
        },
        "volumes": {
          "/opt/uhome-integrations/config/home-assistant": "/config",
          "/opt/uhome-integrations/share": "/share"
        },
        "environment": {
          "TZ": "America/New_York"
        }
      },
      "health_check": "http://localhost:8123/api/health",
      "kiosk_config": {
        "enabled": true,
        "user": "uhome_kiosk",
        "dashboard": "uhome-console",
        "hide_sidebar": true,
        "hide_header": true
      }
    }
  ]
}
```

### Integration Manager HA Controls

The integration manager exposes HA-specific endpoints:

```go
// POST /api/integrations/home-assistant/lovelace/reload
// Reload Lovelace dashboards after config change

// POST /api/integrations/home-assistant/kiosk/enable
// Enable kiosk mode for console

// GET /api/integrations/home-assistant/entities
// List entities for console status bar

// POST /api/integrations/home-assistant/service/call
// Call HA service from uHomeNest
// {"domain": "light", "service": "turn_on", "target": "light.living_room"}
```

***

## uhome CLI — HA Commands

### Command Structure

```bash
uhome ha <subcommand> [options]
```

### Core Subcommands

| Command              | Description                   | Example                                                          |
| -------------------- | ----------------------------- | ---------------------------------------------------------------- |
| `uhome ha status`    | Show HA integration status    | `uhome ha status`                                                |
| `uhome ha start`     | Start HA container/service    | `uhome ha start`                                                 |
| `uhome ha stop`      | Stop HA container/service     | `uhome ha stop`                                                  |
| `uhome ha restart`   | Restart HA                    | `uhome ha restart`                                               |
| `uhome ha logs`      | Tail HA logs                  | `uhome ha logs --tail 50`                                        |
| `uhome ha config`    | Manage HA configuration       | `uhome ha config --edit`                                         |
| `uhome ha entities`  | List entities                 | `uhome ha entities --domain light`                               |
| `uhome ha service`   | Call HA service               | `uhome ha service call light.turn_on --target light.living_room` |
| `uhome ha dashboard` | Manage Lovelace dashboards    | `uhome ha dashboard list`                                        |
| `uhome ha kiosk`     | Configure kiosk mode          | `uhome ha kiosk enable --hide-sidebar`                           |
| `uhome ha sync`      | Sync uHomeNest entities to HA | `uhome ha sync --all`                                            |

### Detailed Command Specs

#### `uhome ha status`

```bash
uhome ha status [--format json|table]

# Output (table)
HA Status: ● RUNNING
Version: 2026.4.0
URL: http://localhost:8123
Kiosk Mode: enabled
Entities: 147
Automations: 12
Uptime: 3d 14h 22m

# Output (JSON)
{
  "status": "running",
  "version": "2026.4.0",
  "url": "http://localhost:8123",
  "kiosk_enabled": true,
  "entity_count": 147,
  "automation_count": 12,
  "uptime_seconds": 308520
}
```

#### `uhome ha service call`

```bash
uhome ha service call <domain.service> [options]

# Turn on a light
uhome ha service call light.turn_on \
    --target light.living_room_main \
    --data '{"brightness": 255, "color_temp": 400}'

# Set thermostat
uhome ha service call climate.set_temperature \
    --target climate.living_room \
    --data '{"temperature": 72, "hvac_mode": "heat"}'

# Trigger automation
uhome ha service call automation.trigger \
    --target automation.movie_time

# Options:
#   --target, -t    Entity ID or area
#   --data, -d      JSON service data
#   --wait          Wait for result (default: async)
```

#### `uhome ha entities`

```bash
uhome ha entities [--domain <domain>] [--state <state>] [--format json|table]

# List all lights
uhome ha entities --domain light

# List all entities that are on
uhome ha entities --state on

# Output
ENTITY ID              STATE    DOMAIN    FRIENDLY NAME
────────────────────────────────────────────────────────
light.living_room_main on       light     Living Room Main
light.living_room_lamp off      light     Living Room Lamp
climate.living_room    72       climate   Living Room Thermostat
```

#### `uhome ha kiosk`

```bash
# Enable kiosk mode for console embedding
uhome ha kiosk enable \
    --hide-sidebar \
    --hide-header \
    --user uhome_kiosk

# Disable kiosk mode
uhome ha kiosk disable

# Configure custom dashboard for kiosk
uhome ha kiosk set-dashboard --dashboard uhome-console

# Status
uhome ha kiosk status
# Kiosk Mode: enabled
# Dashboard: uhome-console
# User: uhome_kiosk
# Header: hidden
# Sidebar: hidden
```

#### `uhome ha sync`

```bash
# Sync uHomeNest media server as HA entity
uhome ha sync media-server

# Sync Matter devices
uhome ha sync matter --all

# Sync all uHomeNest components
uhome ha sync --all

# Generated HA configuration
# /opt/uhome-integrations/config/home-assistant/configuration.yaml
# Includes:
#   - media_player.uhome_server
#   - sensor.uhome_health
#   - switch.uhome_matter_bridge
```

***

## Console Integration: USXD + HA Embed

### USXD Surface for HA

**`ui/usxd/ha-dashboard.json`** **ui/usxd/ha-dashboard.json**:

```json
{
  "surface": "uhome-ha-dashboard",
  "version": "1.0.0",
  "layout": {
    "type": "embed",
    "source": "http://localhost:8123/uhome-console",
    "fullscreen": true,
    "controller_overlay": true
  },
  "navigation": {
    "back": "return-to-launcher",
    "menu": "toggle-ha-sidebar",
    "voice": "trigger-ha-assist"
  },
  "status_bar": {
    "enabled": true,
    "position": "bottom",
    "indicators": [
      {
        "type": "ha-connection",
        "endpoint": "/api/integrations/home-assistant/status"
      },
      {
        "type": "ha-notifications",
        "endpoint": "/api/integrations/home-assistant/notifications"
      }
    ]
  }
}
```

### React Embed Component

```tsx
// ui/src/components/HAEmbed.tsx
import { useEffect, useRef } from 'react';
import { useGamepad } from '../hooks/useGamepad';

export function HAEmbed({ url, kioskMode = true }) {
  const iframeRef = useRef<HTMLIFrameElement>(null);
  const { buttonPress } = useGamepad();

  // Handle controller navigation within HA iframe
  useEffect(() => {
    const iframe = iframeRef.current;
    if (!iframe) return;

    // Send controller events to HA via postMessage
    const handleButtonPress = (button: string) => {
      iframe.contentWindow?.postMessage({
        type: 'uhome_controller',
        button: button,
        action: mapButtonToHA(button)
      }, 'http://localhost:8123');
    };

    buttonPress && handleButtonPress(buttonPress);
  }, [buttonPress]);

  // Listen for HA events (navigation, state changes)
  useEffect(() => {
    const handleHAMessage = (event: MessageEvent) => {
      if (event.origin !== 'http://localhost:8123') return;
      
      switch (event.data.type) {
        case 'ha_navigate':
          // HA requesting navigation to different view
          break;
        case 'ha_entity_update':
          // Update console status bar
          break;
      }
    };

    window.addEventListener('message', handleHAMessage);
    return () => window.removeEventListener('message', handleHAMessage);
  }, []);

  return (
    <div className="ha-embed-container">
      <iframe
        ref={iframeRef}
        src={`${url}/uhome-console${kioskMode ? '?kiosk' : ''}`}
        className="w-full h-full border-0"
        allow="microphone; camera; autoplay"
        sandbox="allow-same-origin allow-scripts allow-popups allow-forms"
      />
      <ConsoleFooter />
    </div>
  );
}
```

### HA Custom Lovelace Card for uHomeNest

Create a custom Lovelace card that receives controller events:

```javascript
// www/community/uhome-console-card.js
class UhomeConsoleCard extends HTMLElement {
  set hass(hass) {
    this._hass = hass;
    
    // Listen for controller events from parent
    window.addEventListener('message', (event) => {
      if (event.data.type === 'uhome_controller') {
        this.handleController(event.data.button);
      }
    });
  }

  handleController(button) {
    switch(button) {
      case 'a':
        // Select currently focused entity
        this._hass.callService('homeassistant', 'toggle', {
          entity_id: this.focusedEntity
        });
        break;
      case 'x':
        // Show entity context menu
        this.showEntityMenu(this.focusedEntity);
        break;
      case 'y':
        // Trigger voice assistant
        this._hass.callService('assist_pipeline', 'start');
        break;
    }
  }

  render() {
    // Render HA entities in controller-friendly grid
  }
}

customElements.define('uhome-console-card', UhomeConsoleCard);
```

***

## HA Automation Integration with uHomeNest

### Bidirectional State Sync

uHomeNest can both **consume HA state** and **expose its own state** to HA:

```yaml
# configuration.yaml (generated by uhome ha sync)
sensor:
  - platform: rest
    name: uHome Media Status
    resource: http://localhost:7890/api/health
    value_template: "{{ value_json.status }}"
    scan_interval: 60

  - platform: rest
    name: uHome Now Playing
    resource: http://localhost:7890/api/now-playing
    value_template: "{{ value_json.title }}"

switch:
  - platform: rest
    name: uHome Matter Bridge
    resource: http://localhost:7890/api/integrations/matter/status
    body_on: '{"enabled": true}'
    body_off: '{"enabled": false}'
    is_on_template: "{{ value_json.status == 'running' }}"

media_player:
  - platform: rest
    name: uHome Server
    resource: http://localhost:7890/api/playback/status
    commands:
      play: 
        resource: http://localhost:7890/api/playback/start
        method: POST
      pause:
        resource: http://localhost:7890/api/playback/pause
        method: POST
```

### Example Automations

**"Movie Time" scene triggered from uHomeNest console:**

```yaml
automation:
  - alias: "Movie Time from Console"
    trigger:
      - platform: state
        entity_id: scene.movie_time
        to: "on"
    action:
      - service: light.turn_off
        target:
          area_id: living_room
        data:
          except: light.living_room_accent
      - service: media_player.play_media
        target:
          entity_id: media_player.living_room_tv
        data:
          media_content_id: "http://jellyfin.local:8096/movies/latest"
          media_content_type: "video"
      - service: climate.set_temperature
        target:
          entity_id: climate.living_room
        data:
          temperature: 68
```

**"Console Connected" — when kiosk browser connects:**

```yaml
automation:
  - alias: "Console Active"
    trigger:
      - platform: webhook
        webhook_id: uhome_console_connected
    action:
      - service: light.turn_on
        target:
          entity_id: light.kiosk_status
      - service: notify.persistent_notification
        data:
          message: "uHome console is active"
```

***

## CLI Implementation Plan

### Command Structure

````
uhome ha
├── status          # Show HA status
├── start/stop/restart
├── logs
├── config
│   ├── show        # Show current config
│   ├── edit        # Edit config
│   └── validate    # Validate config
├── entities
│   ├── list        # List entities
│   ├── get         # Get entity state
│   └── set         # Set entity state
├── service
│   ├── call        # Call service
│   └── list        # List available services
├── dashboard
│   ├── list        # List Lovelace dashboards
│   ├── show        # Show dashboard config
│   ├── reload      # Reload dashboards
│   └── set-kiosk   # Set dashboard as kiosk
├── kiosk
│   ├── enable      # Enable kiosk mode
│   ├── disable     # Disable kiosk mode
│   └── status      # Show kiosk status
├── sync
│   ├── all         # Sync all uHome components
│   ├── media       # Sync media server
│   ├── matter      # Sync Matter devices
│   └── config      # Sync configuration
└── token
    ├── create      # Create long-lived access token
    ├── list        # List tokens
    └── revoke      # Revoke token
````

### Go Implementation Stub

```go
// cmd/uhome/ha.go
package main

import (
    "encoding/json"
    "fmt"
    "net/http"
    "github.com/spf13/cobra"
)

var haCmd = &cobra.Command{
    Use:   "ha",
    Short: "Manage Home Assistant integration",
    Long:  "Control Home Assistant instance embedded in uHomeNest console",
}

var haStatusCmd = &cobra.Command{
    Use:   "status",
    Short: "Show HA integration status",
    RunE: func(cmd *cobra.Command, args []string) error {
        resp, err := http.Get("http://localhost:7891/api/integrations/home-assistant/status")
        if err != nil {
            return fmt.Errorf("HA not running: %w", err)
        }
        defer resp.Body.Close()
        
        var status HAStatus
        json.NewDecoder(resp.Body).Decode(&status)
        
        format := cmd.Flag("format").Value.String()
        return printStatus(status, format)
    },
}

var haServiceCmd = &cobra.Command{
    Use:   "service",
    Short: "Call HA services",
}

var haServiceCallCmd = &cobra.Command{
    Use:   "call <domain.service>",
    Args:  cobra.ExactArgs(1),
    Short: "Call a Home Assistant service",
    RunE: func(cmd *cobra.Command, args []string) error {
        service := args[0]
        target, _ := cmd.Flags().GetString("target")
        data, _ := cmd.Flags().GetString("data")
        
        return callHAService(service, target, data)
    },
}

func init() {
    haCmd.AddCommand(haStatusCmd)
    haCmd.AddCommand(haServiceCmd)
    haServiceCmd.AddCommand(haServiceCallCmd)
    
    haStatusCmd.Flags().String("format", "table", "Output format (table|json)")
    haServiceCallCmd.Flags().StringP("target", "t", "", "Entity ID or area")
    haServiceCallCmd.Flags().StringP("data", "d", "{}", "JSON service data")
}
```

***

## Installation & Configuration Flow

### Fresh Install with HA Embed

```bash
# 1. Install uHomeNest core
./scripts/install.sh

# 2. Install integrations (including HA)
./scripts/install-integrations.sh

# 3. Configure HA for console embedding
uhome ha kiosk enable --hide-sidebar --hide-header

# 4. Create kiosk user
uhome ha token create --user uhome_kiosk --name "Console Kiosk"

# 5. Sync uHomeNest entities to HA
uhome ha sync --all

# 6. Set console dashboard
uhome ha dashboard set-kiosk --dashboard uhome-console

# 7. Verify
uhome ha status
# HA URL: http://localhost:8123/uhome-console?kiosk
```

***

## Success Criteria

- [ ] HA container runs alongside uHomeNest
- [ ] `uhome ha status` shows running instance
- [ ] HA UI embeds in console without browser chrome
- [ ] Controller navigation works within HA views
- [ ] `uhome ha service call` controls HA entities
- [ ] `uhome ha sync` exposes uHomeNest as HA entities
- [ ] Kiosk mode hides HA sidebar/header automatically
- [ ] HA automations can trigger uHomeNest actions
- [ ] Console status bar shows HA connection state

***

## Related Documents

- [Matter + HA Integration Plan](./UDN-INTEGRATION-001.md)
- [Alexa/Google/HomeKit Guide](./UDN-VOICE-INTEGRATION-001.md)
- [Vibe CLI Project Reset](./UDN-RESET-001.md)
- [uHomeNest v1.0.0 Dev Brief](./UHOMENEST-V1-DEV-BRIEF.md)

***

## Version History

| Version | Date       | Changes                           |
| ------- | ---------- | --------------------------------- |
| 1.0.0   | 2026-04-21 | Initial HA deep integration brief |