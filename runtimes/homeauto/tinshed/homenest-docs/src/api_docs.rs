//! API Docs — MCP methods, feed schema, grid API

use crate::DocSection;

/// Generate the API documentation
pub fn generate() -> DocSection {
    DocSection {
        title: "API Reference".into(),
        content: "HomeNest exposes a JSON-RPC API over a Unix socket at `~/.local/share/udos/homenest.sock`.".into(),
        subsections: vec![
            DocSection {
                title: "MCP Methods".into(),
                content: "All methods use JSON-RPC 2.0 over Unix socket transport.".into(),
                subsections: vec![
                    DocSection {
                        title: "play".into(),
                        content: "Start media playback.\n\n**Request:**\n```json\n{\"jsonrpc\":\"2.0\",\"method\":\"play\",\"params\":{\"media_id\":\"movie/123\",\"position\":0},\"id\":1}\n```\n\n**Response:**\n```json\n{\"jsonrpc\":\"2.0\",\"result\":{\"status\":\"playing\",\"media_id\":\"movie/123\"},\"id\":1}\n```".into(),
                        subsections: vec![],
                    },
                    DocSection {
                        title: "record".into(),
                        content: "Schedule a recording.\n\n**Request:**\n```json\n{\"jsonrpc\":\"2.0\",\"method\":\"record\",\"params\":{\"channel\":\"ABC\",\"start_time\":\"2026-05-17T20:00:00\",\"end_time\":\"2026-05-17T21:00:00\"},\"id\":1}\n```\n\n**Response:**\n```json\n{\"jsonrpc\":\"2.0\",\"result\":{\"recording_id\":\"rec_abc123\",\"status\":\"scheduled\"},\"id\":1}\n```".into(),
                        subsections: vec![],
                    },
                    DocSection {
                        title: "automate".into(),
                        content: "Execute an OBF automation sheet.\n\n**Request:**\n```json\n{\"jsonrpc\":\"2.0\",\"method\":\"automate\",\"params\":{\"obf_path\":\"/path/to/scene.usx.json\"},\"id\":1}\n```\n\n**Response:**\n```json\n{\"jsonrpc\":\"2.0\",\"result\":{\"status\":\"executing\",\"actions\":5},\"id\":1}\n```".into(),
                        subsections: vec![],
                    },
                    DocSection {
                        title: "status".into(),
                        content: "Return system status.\n\n**Request:**\n```json\n{\"jsonrpc\":\"2.0\",\"method\":\"status\",\"params\":{},\"id\":1}\n```\n\n**Response:**\n```json\n{\"jsonrpc\":\"2.0\",\"result\":{\"playing\":false,\"recording\":false,\"automation\":\"idle\",\"services\":{\"mcp\":\"running\",\"media\":\"running\",\"tv\":\"running\"}},\"id\":1}\n```".into(),
                        subsections: vec![],
                    },
                    DocSection {
                        title: "search".into(),
                        content: "Search media library.\n\n**Request:**\n```json\n{\"jsonrpc\":\"2.0\",\"method\":\"search\",\"params\":{\"query\":\"interstellar\",\"type\":\"movie\"},\"id\":1}\n```\n\n**Response:**\n```json\n{\"jsonrpc\":\"2.0\",\"result\":{\"results\":[{\"id\":\"movie/42\",\"title\":\"Interstellar\",\"year\":2014}]},\"id\":1}\n```".into(),
                        subsections: vec![],
                    },
                    DocSection {
                        title: "feed_list".into(),
                        content: "List feed spool entries.\n\n**Request:**\n```json\n{\"jsonrpc\":\"2.0\",\"method\":\"feed_list\",\"params\":{\"limit\":20,\"offset\":0},\"id\":1}\n```\n\n**Response:**\n```json\n{\"jsonrpc\":\"2.0\",\"result\":{\"entries\":[],\"total\":0},\"id\":1}\n```".into(),
                        subsections: vec![],
                    },
                    DocSection {
                        title: "feed_poll".into(),
                        content: "Poll a feed URL.\n\n**Request:**\n```json\n{\"jsonrpc\":\"2.0\",\"method\":\"feed_poll\",\"params\":{\"feed_url\":\"https://example.com/feed.xml\"},\"id\":1}\n```\n\n**Response:**\n```json\n{\"jsonrpc\":\"2.0\",\"result\":{\"new_entries\":3},\"id\":1}\n```".into(),
                        subsections: vec![],
                    },
                ],
            },
            DocSection {
                title: "Feed Schema".into(),
                content: "The feed spool uses NDJSON format (one JSON object per line).".into(),
                subsections: vec![
                    DocSection {
                        title: "Entry Format".into(),
                        content: "```json\n{\n  \"id\": \"uuid-v4\",\n  \"type\": \"rss|ha_event|media_scan|epg|mcp|udev|dbus|system\",\n  \"source\": \"string\",\n  \"title\": \"string\",\n  \"body\": \"string\",\n  \"metadata\": {},\n  \"timestamp\": \"ISO-8601\",\n  \"read\": false\n}\n```".into(),
                        subsections: vec![],
                    },
                    DocSection {
                        title: "Feed Types".into(),
                        content: "| Type | Source | Description |\n|------|--------|-------------|\n| `rss` | RSS URL | RSS/Atom feed entries |\n| `ha_event` | HA WebSocket | Home Assistant state changes |\n| `media_scan` | Scanner | New media file detected |\n| `epg` | EPG parser | TV program schedule updates |\n| `mcp` | MCP bridge | MCP resource updates |\n| `udev` | udev listener | USB device events |\n| `dbus` | DBus listener | Systemd service status |\n| `system` | System | System notifications |".into(),
                        subsections: vec![],
                    },
                ],
            },
            DocSection {
                title: "Grid API".into(),
                content: "The grid system maps media items to a 24x24 coordinate space.".into(),
                subsections: vec![
                    DocSection {
                        title: "Coordinate Format".into(),
                        content: "Coordinates use the format `L1000-AA10-0317-2`:\n- `L1000` — Layer identifier\n- `AA10` — Row/column quadrant\n- `0317` — X/Y position within quadrant\n- `2` — Z-index (temporal layer)".into(),
                        subsections: vec![],
                    },
                    DocSection {
                        title: "Layer Types".into(),
                        content: "| Layer | Description |\n|-------|-------------|\n| Movies | Feature films |\n| Music | Audio albums and tracks |\n| TV | Television episodes |\n| Recordings | DVR recordings |\n| Bookmarks | User-saved positions |".into(),
                        subsections: vec![],
                    },
                ],
            },
        ],
    }
}
