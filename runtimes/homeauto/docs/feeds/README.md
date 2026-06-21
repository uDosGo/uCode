---
title: "uHomeNest Feed/Spool Specification"
status: draft
last_updated: 2026-05-20T22:32:12+10:00
category: readme
tags: [feed, streaming, ucode3]
description: "**Document ID:** UDN-FEEDSPOOL-001"
---
# uHomeNest Feed/Spool Specification

**Document ID:** UDN-FEEDSPOOL-001  
**Status:** Active  
**Version:** 1.0.0  
**Date:** 2026-04-21  
**Priority:** HIGH  
**Related:** [uHome Media Player](./UDN-MEDIA-001.md), [HA Deep Integration](./UDN-HA-EMBED-001.md), [Matter+HA Integration](./UDN-INTEGRATION-001.md)

***

## Executive Summary

The **Feed/Spool Specification** defines a **unified data format** for all streaming, scheduled, and reactive content in uHomeNest. One format handles:

- **Feeds** — Incoming data streams (RSS, JSON, MCP resources, EPG, media catalogs)
- **Spools** — Outgoing/scheduled bundles (playlists, automation sequences, OBF sheets)
- **Protocols** — Transport definitions for feed/spool exchange
- **Settings** — Configuration embedded in the same structure

**Core Principle:** Everything is a feed. Every feed can be spooled. Every spool can be a feed.

***

## Core Concepts

### Feed

A **Feed** is any source of timestamped items that can be consumed sequentially or randomly.

```yaml
feed:
  id: string                    # Unique identifier
  type: string                  # rss | json | mcp | media | epg | automation | settings
  protocol: string              # http | file | mcp | websocket | udev | dbus
  url: string                   # Source location
  ttl: integer                  # Time to live (seconds)
  last_poll: timestamp          
  items: []Item                 # Array of feed items
```

### Spool

A **Spool** is a collection of items scheduled for execution/playback, with state tracking.

```yaml
spool:
  id: string                    # Unique identifier
  name: string                  # Human-readable name
  type: string                  # playlist | automation | backup | sync | install
  schedule: string              # Cron expression or "immediate"
  items: []QueuedItem           # Items with execution state
  current_position: integer     # For resume capability
  status: string                # pending | active | paused | completed | failed
```

### Item

An **Item** is a single unit within a feed or spool.

```yaml
item:
  id: string                    # Unique within feed/spool
  type: string                  # media | command | automation | setting | mcp_tool | mcp_resource
  timestamp: timestamp          # Original/created time
  ttl: integer                  # Optional expiry
  payload: any                  # Type-specific data
  metadata:                     
    title: string
    description: string
    tags: []string
    weight: integer             # Priority (0-100)
```

***

## Unified Format Specification

### Top-Level Structure

```yaml
# feedspool.yaml
version: "1.0.0"
namespace: string               # e.g., "uhome.media", "uhome.automation"

# Optional: Protocol definitions
protocols:
  - name: string
    type: string                # http | mcp | websocket | file | udev | dbus
    endpoint: string
    auth: 
      type: string              # none | bearer | basic | oauth
      credentials: string       # Reference to secret store
    headers: {}
    timeout: integer

# Feeds (sources)
feeds:
  - id: string
    type: string
    protocol: string            # Reference protocol name or inline
    url: string
    ttl: integer
    transform: string           # Optional jq/xpath expression
    filters:
      - field: string
        operator: string        # eq | ne | contains | regex | gt | lt
        value: any
    items: []Item               # Current items (cached)

# Spools (destinations/queues)
spools:
  - id: string
    name: string
    type: string
    schedule: string
    source_feed: string         # Optional: feed this spool consumes
    transform: string           # Optional transform before enqueue
    items: []QueuedItem
    retention: integer          # Days to keep completed items
    status: string

# Settings (embedded configuration)
settings:
  - key: string
    value: any
    source: string              # feed id or "default"
    last_updated: timestamp
```

### Item Payload Types

#### Media Item

```yaml
item:
  type: media
  payload:
    title: string
    url: string                 # Stream URL or local path
    duration: integer           # Seconds
    thumbnail: string
    metadata:
      - tmdb_id: integer
      - imdb_id: string
      - year: integer
      - genre: []string
    engine: string              # jellyfin | kodi | mpv | yt-dlp
    subtitles: []string
    audio_tracks: []string
```

#### Command Item

```yaml
item:
  type: command
  payload:
    executable: string          # /usr/bin/uhome
    args: []string
    env: {}
    working_directory: string
    timeout: integer
    on_success: string          # Item ID to enqueue next
    on_failure: string
```

#### Automation Item

```yaml
item:
  type: automation
  payload:
    domain: string              # light | climate | media_player | automation
    service: string             # turn_on | set_temperature | play_media
    target:
      entity_id: string
      device_id: string
      area_id: string
    data: {}
    wait_for_result: boolean
    timeout: integer
```

#### MCP Tool Item

```yaml
item:
  type: mcp_tool
  payload:
    server: string              # MCP server name
    tool: string                # Tool name
    arguments: {}
    context: {}                 # Optional context for tool execution
```

#### MCP Resource Item

```yaml
item:
  type: mcp_resource
  payload:
    server: string
    uri: string                 # resource://server/path
    content_type: string
    data: any                   # Cached resource data
    ttl: integer
```

#### Setting Item

```yaml
item:
  type: setting
  payload:
    key: string
    value: any
    scope: string               # user | system | feed | spool
    validation: string          # JSON schema reference
    sensitive: boolean          # Mask in logs
```

***

## Protocol Definitions

### HTTP Protocol

```yaml
protocol:
  name: http-default
  type: http
  endpoint: https://api.example.com
  headers:
    User-Agent: "uHomeNest/1.0"
  timeout: 30
  retry:
    max_attempts: 3
    backoff: exponential
```

**Feed example (RSS):**

```yaml
feed:
  id: news-rss
  type: rss
  protocol: http-default
  url: /feeds/news.xml
  ttl: 3600
  transform: '.rss.channel.item[] | {title: .title, link: .link, timestamp: .pubDate}'
```

### MCP Protocol

```yaml
protocol:
  name: mcp-local
  type: mcp
  endpoint: http://localhost:7891/mcp
  auth:
    type: bearer
    credentials: secret://mcp-token
  capabilities:
    - tools
    - resources
    - prompts
```

**Feed example (MCP resources):**

```yaml
feed:
  id: ha-entities
  type: mcp
  protocol: mcp-local
  url: resource://homeassistant/entities
  ttl: 60
  items: []
```

**Spool example (MCP tools):**

```yaml
spool:
  id: ha-automation-queue
  name: "Home Assistant Automation Queue"
  type: automation
  source_feed: ha-events
  items: []
  schedule: "* * * * *"  # Every minute
```

### WebSocket Protocol

```yaml
protocol:
  name: ws-live
  type: websocket
  endpoint: ws://localhost:8123/api/websocket
  auth:
    type: bearer
    credentials: secret://ha-token
  heartbeat: 30
  reconnect: true
```

**Feed example (real-time HA events):**

```yaml
feed:
  id: ha-events-live
  type: json
  protocol: ws-live
  url: /
  ttl: 0  # Real-time, no polling
  filters:
    - field: event_type
      operator: eq
      value: state_changed
```

### File Protocol

```yaml
protocol:
  name: media-vault
  type: file
  endpoint: /home/uhome/media
  watch: true
  debounce: 1000  # milliseconds
```

**Feed example (media vault):**

```yaml
feed:
  id: media-vault-scanner
  type: media
  protocol: media-vault
  url: /
  ttl: 86400  # Rescan daily
  items: []
```

### udev Protocol

```yaml
protocol:
  name: udev-monitor
  type: udev
  subsystem: block
  properties:
    - ID_FS_LABEL
    - DEVTYPE
```

**Feed example (USB device events):**

```yaml
feed:
  id: usb-devices
  type: udev
  protocol: udev-monitor
  url: /
  ttl: 0  # Event-driven
  filters:
    - field: DEVTYPE
      operator: eq
      value: partition
```

### DBus Protocol

```yaml
protocol:
  name: systemd-dbus
  type: dbus
  bus: system
  service: org.freedesktop.systemd1
  path: /org/freedesktop/systemd1
  interface: org.freedesktop.systemd1.Manager
```

**Feed example (service status):**

```yaml
feed:
  id: systemd-services
  type: dbus
  protocol: systemd-dbus
  url: /org/freedesktop/systemd1/unit/uhome_2dapi_2eservice
  ttl: 30
```

***

## QueuedItem with State

```yaml
queued_item:
  id: string
  feed_id: string               # Original feed source (optional)
  spool_id: string              # Containing spool
  item: Item                    # The actual item
  state:
    status: string              # pending | processing | completed | failed | skipped
    attempts: integer
    last_attempt: timestamp
    next_retry: timestamp
    error: string
    started_at: timestamp
    completed_at: timestamp
    result: any                 # Execution result
  position: integer
  depends_on: []string          # Item IDs that must complete first
  timeout: integer
  priority: integer             # 0-100 (higher = more urgent)
```

***

## MCP Integration as Feed/Spool

### MCP as Feed Source

MCP servers expose **resources** that become feeds:

```yaml
feed:
  id: mcp-ha-states
  type: mcp
  protocol: mcp-local
  url: resource://homeassistant/states
  ttl: 10
  transform: |
    .[] | {
      id: .entity_id,
      type: "automation",
      payload: {
        domain: split(".")[0],
        entity_id: .entity_id,
        state: .state,
        attributes: .attributes
      }
    }
```

### MCP as Spool Destination

MCP **tools** are spool items that can be scheduled:

```yaml
spool:
  id: mcp-call-queue
  name: "MCP Tool Queue"
  type: automation
  items:
    - item:
        type: mcp_tool
        payload:
          server: homeassistant
          tool: light_turn_on
          arguments:
            entity_id: light.living_room
            brightness: 255
      state:
        status: pending
      priority: 50
```

### MCP Settings Feed

Settings stored as MCP resources:

```yaml
feed:
  id: mcp-settings
  type: mcp
  protocol: mcp-local
  url: resource://uhome/settings
  ttl: 300
  transform: |
    .settings[] | {
      type: "setting",
      payload: {
        key: .key,
        value: .value,
        scope: "system"
      }
    }
```

***

## Example: Complete Feed/Spool Configuration

### `~/config/feedspool.yaml`

```yaml
version: "1.0.0"
namespace: "uhome.living_room"

# Protocols
protocols:
  - name: ha-api
    type: http
    endpoint: http://localhost:8123
    auth:
      type: bearer
      credentials: secret://ha-token
    timeout: 10

  - name: ha-ws
    type: websocket
    endpoint: ws://localhost:8123/api/websocket
    auth:
      type: bearer
      credentials: secret://ha-token
    reconnect: true

  - name: mcp-uhome
    type: mcp
    endpoint: http://localhost:7891/mcp
    capabilities: [tools, resources, prompts]

  - name: media-vault
    type: file
    endpoint: /home/uhome/media
    watch: true
    debounce: 2000

  - name: rss-default
    type: http
    endpoint: https://feeds.example.com
    timeout: 30

# Feeds
feeds:
  # Media vault scanner
  - id: media-vault
    type: media
    protocol: media-vault
    url: /
    ttl: 3600
    items: []

  # Home Assistant states
  - id: ha-states
    type: json
    protocol: ha-api
    url: /api/states
    ttl: 30
    items: []

  # HA real-time events
  - id: ha-events
    type: json
    protocol: ha-ws
    url: /
    ttl: 0
    filters:
      - field: type
        operator: eq
        value: event
    items: []

  # RSS news feed
  - id: news-rss
    type: rss
    protocol: rss-default
    url: /news.xml
    ttl: 3600
    transform: '.item[] | {title: .title, link: .link, timestamp: .pubDate}'
    items: []

  # MCP resources
  - id: mcp-resources
    type: mcp
    protocol: mcp-uhome
    url: resource://list
    ttl: 300
    items: []

# Spools
spools:
  # Daily news briefing
  - id: news-briefing
    name: "Morning News Briefing"
    type: playlist
    schedule: "0 7 * * *"  # 7 AM daily
    source_feed: news-rss
    transform: 'limit(5) | {type: "media", payload: {title: .title, url: .link}}'
    items: []
    retention: 7
    status: active

  # HA automation queue
  - id: ha-automations
    name: "Home Assistant Automation Queue"
    type: automation
    source_feed: ha-events
    transform: |
      if .event.event_type == "state_changed" then
        {type: "automation", payload: {domain: "homeassistant", service: "update_entity", target: {entity_id: .event.data.entity_id}}}
      else empty end
    items: []
    status: active

  # Backup spool (weekly)
  - id: weekly-backup
    name: "Weekly System Backup"
    type: backup
    schedule: "0 2 * * 0"  # Sunday 2 AM
    items:
      - item:
          type: command
          payload:
            executable: /usr/local/bin/uhome
            args: ["backup", "create", "--full"]
          metadata:
            title: "Full System Backup"
            weight: 100
        state:
          status: pending
    retention: 30
    status: active

# Settings
settings:
  - key: media.vault.path
    value: /home/uhome/media
    source: default
    last_updated: "2026-04-21T00:00:00Z"

  - key: media.scan.interval
    value: 3600
    source: media-vault
    last_updated: "2026-04-21T00:00:00Z"

  - key: automation.morning.enabled
    value: true
    source: default
    last_updated: "2026-04-21T00:00:00Z"

  - key: mcp.auto_discover
    value: true
    source: mcp-resources
    last_updated: "2026-04-21T00:00:00Z"
```

***

## uhome CLI — Feed/Spool Commands

### Command Structure

```bash
uhome feed <subcommand> [options]
uhome spool <subcommand> [options]
```

### Feed Commands

| Command                | Description               | Example                                            |
| ---------------------- | ------------------------- | -------------------------------------------------- |
| `uhome feed list`      | List all feeds            | `uhome feed list --active`                         |
| `uhome feed show`      | Show feed details         | `uhome feed show media-vault`                      |
| `uhome feed poll`      | Manually poll a feed      | `uhome feed poll news-rss`                         |
| `uhome feed items`     | List items in feed        | `uhome feed items media-vault --limit 10`          |
| `uhome feed transform` | Test transform expression | `uhome feed transform '.item[] \| {title: .title}'` |
| `uhome feed add`       | Add new feed              | `uhome feed add --type rss --url https://...`      |
| `uhome feed remove`    | Remove feed               | `uhome feed remove old-feed`                       |

### Spool Commands

| Command               | Description            | Example                                                          |
| --------------------- | ---------------------- | ---------------------------------------------------------------- |
| `uhome spool list`    | List all spools        | `uhome spool list --status active`                               |
| `uhome spool show`    | Show spool details     | `uhome spool show news-briefing`                                 |
| `uhome spool enqueue` | Add item to spool      | `uhome spool enqueue news-briefing --item '{"type":"media"...}'` |
| `uhome spool dequeue` | Remove item            | `uhome spool dequeue news-briefing --id abc123`                  |
| `uhome spool process` | Manually process spool | `uhome spool process ha-automations`                             |
| `uhome spool pause`   | Pause spool            | `uhome spool pause weekly-backup`                                |
| `uhome spool resume`  | Resume spool           | `uhome spool resume weekly-backup`                               |
| `uhome spool clear`   | Clear completed items  | `uhome spool clear --completed`                                  |

### Detailed Examples

```bash
# List all feeds with items
uhome feed list --verbose
# Output:
# ID            TYPE    ITEMS   LAST POLL
# media-vault   media   47      2m ago
# ha-states     json    142     5s ago
# news-rss      rss     25      1h ago

# Poll feed and show new items
uhome feed poll news-rss --new-only

# Add item to spool
uhome spool enqueue ha-automations \
  --item '{"type":"automation","payload":{"domain":"light","service":"turn_on","target":{"entity_id":"light.kitchen"}}}'

# Process spool immediately
uhome spool process ha-automations --wait

# Show spool queue
uhome spool show news-briefing --queue
# Position  Status    Item
# 1         pending   Morning News (NPR)
# 2         pending   Weather Update
# 3         pending   Local Traffic
```

***

## OBF to Feed/Spool Mapping

OBF sheets are a **human-readable frontend** for feeds and spools:

```markdown
# OBF: Morning Briefing
# @feed: news-rss
# @spool: news-briefing
# @transform: |
#   limit(5) | {
#     type: "media",
#     payload: {title: .title, url: .link}
#   }

## Section: News
- https://feeds.npr.org/1001/rss.xml
- https://feeds.bbc.co.uk/news/rss.xml

## Section: Weather
- @ha:weather.get_forecast?entity_id=weather.home
```

**Conversion command:**

```bash
uhome obf to-feedspool morning.obf --output feedspool.yaml
uhome feedspool apply feedspool.yaml
```

***

## Feed/Spool Storage

### Directory Structure

````
~/.uhome/feedspool/
├── feeds/
│   ├── media-vault.feed.yaml
│   ├── ha-states.feed.yaml
│   └── news-rss.feed.yaml
├── spools/
│   ├── news-briefing.spool.yaml
│   ├── ha-automations.spool.yaml
│   └── weekly-backup.spool.yaml
├── state/
│   ├── media-vault.state.db    # SQLite for item cache
│   ├── ha-states.state.db
│   └── spool-state.db
├── transforms/
│   ├── rss-to-media.jq
│   └── ha-to-automation.jq
└── feedspool.yaml              # Main config
````

### SQLite State Schema

```sql
-- Feed items cache
CREATE TABLE feed_items (
    id TEXT PRIMARY KEY,
    feed_id TEXT,
    item_json TEXT,
    timestamp DATETIME,
    processed BOOLEAN DEFAULT 0,
    FOREIGN KEY(feed_id) REFERENCES feeds(id)
);

-- Spool queue
CREATE TABLE spool_queue (
    id TEXT PRIMARY KEY,
    spool_id TEXT,
    position INTEGER,
    item_json TEXT,
    status TEXT,
    attempts INTEGER DEFAULT 0,
    last_attempt DATETIME,
    next_retry DATETIME,
    error TEXT,
    result_json TEXT,
    created_at DATETIME,
    completed_at DATETIME,
    FOREIGN KEY(spool_id) REFERENCES spools(id)
);

-- Processing log
CREATE TABLE processing_log (
    id INTEGER PRIMARY KEY,
    spool_id TEXT,
    item_id TEXT,
    action TEXT,
    timestamp DATETIME,
    details TEXT
);
```

***

## API Endpoints

### REST API

| Method | Endpoint                                     | Description       |
| ------ | -------------------------------------------- | ----------------- |
| GET    | `/api/feedspool/feeds`                       | List feeds        |
| GET    | `/api/feedspool/feeds/{id}`                  | Get feed details  |
| POST   | `/api/feedspool/feeds/{id}/poll`             | Poll feed         |
| GET    | `/api/feedspool/feeds/{id}/items`            | Get feed items    |
| GET    | `/api/feedspool/spools`                      | List spools       |
| GET    | `/api/feedspool/spools/{id}`                 | Get spool details |
| POST   | `/api/feedspool/spools/{id}/enqueue`         | Add item to spool |
| POST   | `/api/feedspool/spools/{id}/process`         | Process spool     |
| DELETE | `/api/feedspool/spools/{id}/items/{item_id}` | Remove item       |
| GET    | `/api/feedspool/settings`                    | Get all settings  |
| PUT    | `/api/feedspool/settings/{key}`              | Update setting    |

### MCP Integration

Feeds/spools are exposed as MCP resources:

````
resource://uhome/feeds
resource://uhome/feeds/{feed_id}
resource://uhome/feeds/{feed_id}/items
resource://uhome/spools
resource://uhome/spools/{spool_id}
resource://uhome/spools/{spool_id}/queue
resource://uhome/settings
````

MCP tools for feed/spool operations:

```json
{
  "tools": [
    {
      "name": "feed_poll",
      "description": "Poll a feed for new items",
      "arguments": {
        "feed_id": "string"
      }
    },
    {
      "name": "spool_enqueue",
      "description": "Add an item to a spool",
      "arguments": {
        "spool_id": "string",
        "item": "object"
      }
    },
    {
      "name": "spool_process",
      "description": "Process pending items in a spool",
      "arguments": {
        "spool_id": "string",
        "limit": "integer"
      }
    }
  ]
}
```

***

## Example: Media Feed + Playback Spool

```yaml
# Media discovery feed
feed:
  id: media-vault-scanner
  type: media
  protocol: file
  url: /home/uhome/media
  ttl: 3600
  transform: |
    walk(if type == "object" and has("path") and (.path | test("\\.(mp4|mkv|avi)$")) then
      {
        id: .path | gsub("/"; "_"),
        type: "media",
        timestamp: .mtime,
        payload: {
          title: .path | split("/")[-1] | gsub("\\.[^.]*$"; ""),
          url: .path,
          duration: .duration
        }
      }
    else . end)

# Watchlist spool
spool:
  id: watchlist
  name: "My Watchlist"
  type: playlist
  items:
    - item:
        type: media
        payload:
          title: "The Matrix"
          url: /home/uhome/media/movies/the_matrix.mkv
      state:
        status: pending
      position: 1
    - item:
        type: media
        payload:
          title: "Inception"
          url: /home/uhome/media/movies/inception.mkv
      state:
        status: pending
      position: 2

# Playback automation
automation:
  trigger:
    - platform: state
      entity_id: media_player.living_room
      to: "idle"
  action:
    - service: spool_enqueue
      data:
        spool_id: watchlist
        item: "{{ next_unwatched }}"
```

***

## Success Criteria

- [ ] Feed specification supports all required types (RSS, JSON, MCP, media, EPG, udev, DBus)
- [ ] Spool specification supports scheduled and immediate execution
- [ ] MCP resources/tools integrated as native feed/spool types
- [ ] Settings are feed items with TTL and source tracking
- [ ] `uhome feed poll` retrieves and transforms items correctly
- [ ] `uhome spool process` executes queued items with retry logic
- [ ] OBF sheets convert to feed/spool configuration
- [ ] State persists across restarts (SQLite)
- [ ] API endpoints expose all feed/spool operations
- [ ] MCP clients can discover and interact with feeds/spools

***

## Related Documents

- [uHome Media Player](./UDN-MEDIA-001.md)
- [HA Deep Integration](./UDN-HA-EMBED-001.md)
- [Matter+HA Integration](./UDN-INTEGRATION-001.md)
- [uHomeNest v1.0.0 Dev Brief](./UHOMENEST-V1-DEV-BRIEF.md)

***

## Version History

| Version | Date       | Changes                          |
| ------- | ---------- | -------------------------------- |
| 1.0.0   | 2026-04-21 | Initial Feed/Spool specification |