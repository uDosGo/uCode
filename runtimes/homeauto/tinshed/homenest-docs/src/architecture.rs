//! Architecture Docs — Grid, temporal, feed/spool, system architecture

use crate::DocSection;

/// Generate the architecture documentation
pub fn generate() -> DocSection {
    DocSection {
        title: "Architecture".into(),
        content: "HomeNest is built on a modular architecture with clear separation of concerns.".into(),
        subsections: vec![
            DocSection {
                title: "System Overview".into(),
                content: "HomeNest follows a hub-and-spoke architecture centered around the MCP server.".into(),
                subsections: vec![
                    DocSection {
                        title: "Component Diagram".into(),
                        content: "```\n┌─────────────────────────────────────────────────┐\n│                  homenest-console                │\n│           (Vue 3 + Tailwind + Gamepad)           │\n└──────────────────────┬──────────────────────────┘\n                       │\n                       ▼\n┌─────────────────────────────────────────────────┐\n│                  homenest-mcp                    │\n│           (Unix Socket JSON-RPC Server)          │\n└──┬──────────┬──────────┬──────────┬─────────────┘\n   │          │          │          │\n   ▼          ▼          ▼          ▼\n┌──────┐ ┌────────┐ ┌──────┐ ┌──────────┐\n│media │ │  tv    │ │ feed │ │automation│\n└──────┘ └────────┘ └──────┘ └──────────┘\n   │          │          │          │\n   ▼          ▼          ▼          ▼\n┌──────┐ ┌────────┐ ┌──────┐ ┌──────────┐\n│ mpv  │ │HDHomeRun│ │ RSS  │ │  HA      │\n│yt-dlp│ │  EPG    │ │Spool │ │  Bridge  │\n└──────┘ └────────┘ └──────┘ └──────────┘\n```".into(),
                        subsections: vec![],
                    },
                    DocSection {
                        title: "Data Flow".into(),
                        content: "1. **User Input** → Console (gamepad/keyboard/voice)\n2. **Console** → MCP (JSON-RPC over Unix socket)\n3. **MCP** → Service crate (media, tv, feed, automation)\n4. **Service** → External system (mpv, HDHomeRun, HA, RSS)\n5. **Events** → Feed spool (NDJSON log)\n6. **Feed** → Console (real-time updates via polling)".into(),
                        subsections: vec![],
                    },
                ],
            },
            DocSection {
                title: "Grid System".into(),
                content: "The grid provides a 2D spatial coordinate system for organizing media and automation items.".into(),
                subsections: vec![
                    DocSection {
                        title: "Coordinate Space".into(),
                        content: "- **Size:** 24x24 units per quadrant\n- **Storage:** ~45KB per cell\n- **Format:** `L1000-AA10-0317-2`\n  - `L1000` = Layer ID\n  - `AA10` = Quadrant\n  - `0317` = X/Y position\n  - `2` = Z-index (temporal)".into(),
                        subsections: vec![],
                    },
                    DocSection {
                        title: "Layers".into(),
                        content: "| Layer | Purpose |\n|-------|---------|\n| Movies | Feature films mapped by genre/decade |\n| Music | Albums mapped by artist/genre |\n| TV | Episodes mapped by series/season |\n| Recordings | DVR recordings by date |\n| Bookmarks | User-saved positions |\n| Automation | Scene tiles |\n\nEach layer is independent and can be navigated separately.".into(),
                        subsections: vec![],
                    },
                    DocSection {
                        title: "Temporal Layer".into(),
                        content: "The temporal layer tracks viewing history and recording schedules as a time-based overlay on the grid. This enables:\n- \"What was I watching last night?\" queries\n- Recording conflict visualization\n- Viewing pattern heatmaps".into(),
                        subsections: vec![],
                    },
                ],
            },
            DocSection {
                title: "Feed/Spool System".into(),
                content: "The feed spool is a unified event log that all system components write to.".into(),
                subsections: vec![
                    DocSection {
                        title: "Storage Format".into(),
                        content: "Events are stored as NDJSON (Newline-Delimited JSON) in `~/.local/share/udos/feed.spool`:\n\n```json\n{\"id\":\"uuid\",\"type\":\"media_scan\",\"source\":\"scanner\",\"title\":\"New file detected\",\"body\":\"movie.mp4\",\"metadata\":{\"path\":\"/media/movie.mp4\"},\"timestamp\":\"2026-05-17T12:00:00Z\",\"read\":false}\n```".into(),
                        subsections: vec![],
                    },
                    DocSection {
                        title: "Event Sources".into(),
                        content: "| Source | Trigger | Frequency |\n|--------|---------|-----------|\n| RSS Poller | Timer | Configurable (default: 30min) |\n| HA Events | WebSocket | Real-time |\n| Media Scanner | File system | On-demand / inotify |\n| EPG Parser | Timer | Daily |\n| MCP Bridge | MCP calls | On-demand |\n| udev Listener | USB events | Real-time |\n| DBus Listener | Service status | Real-time |".into(),
                        subsections: vec![],
                    },
                    DocSection {
                        title: "Retention".into(),
                        content: "The spool automatically prunes entries older than the configured retention period (default: 30 days). Pruning runs on each write operation to keep the file size manageable.".into(),
                        subsections: vec![],
                    },
                ],
            },
            DocSection {
                title: "Voice Architecture".into(),
                content: "Voice processing follows a pipeline architecture.".into(),
                subsections: vec![
                    DocSection {
                        title: "Pipeline".into(),
                        content: "```\nAudio Input → Wake Word Detection → STT (Wyoming) → Intent Parsing → Command Dispatch → Action\n```\n\n1. **Wake Word:** \"Hey HomeNest\" triggers recording\n2. **STT:** Wyoming protocol sends audio to local Whisper server\n3. **Intent Parsing:** Keyword-based intent classification\n4. **Command Dispatch:** Routes to appropriate handler\n5. **Action:** Media, HA, or system command execution".into(),
                        subsections: vec![],
                    },
                    DocSection {
                        title: "HomeKit Integration".into(),
                        content: "The HomeKit bridge exposes HomeNest accessories to Apple Home:\n- Accessories are registered with the bridge\n- Bridge advertises via Bonjour/mDNS\n- Home app discovers and pairs with the bridge\n- Characteristic updates sync in real-time".into(),
                        subsections: vec![],
                    },
                ],
            },
            DocSection {
                title: "Storage Layout".into(),
                content: "XDG-compliant storage paths.".into(),
                subsections: vec![
                    DocSection {
                        title: "XDG Paths".into(),
                        content: "| Path | Purpose |\n|------|---------|\n| `~/.local/share/udos/` | Runtime data (socket, spool) |\n| `~/.config/udos/` | Configuration files |\n| `~/.cache/udos/` | Cache data (EPG, thumbnails) |\n| `~/media/` | Media vault |\n| `~/.local/bin/` | CLI scripts |".into(),
                        subsections: vec![],
                    },
                ],
            },
        ],
    }
}
