//! Feed types — RSS, HA events, media scans, EPG, MCP, udev, DBus

use serde::{Deserialize, Serialize};

/// RSS feed item
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct RssItem {
    pub title: String,
    pub link: Option<String>,
    pub description: Option<String>,
    pub pub_date: Option<String>,
    pub author: Option<String>,
    pub categories: Vec<String>,
    pub guid: Option<String>,
}

/// RSS feed metadata
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct RssFeed {
    pub title: String,
    pub description: Option<String>,
    pub link: Option<String>,
    pub items: Vec<RssItem>,
}

/// Home Assistant event
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct HaEvent {
    pub event_type: String,
    pub entity_id: Option<String>,
    pub state: Option<String>,
    pub old_state: Option<String>,
    pub attributes: Option<serde_json::Value>,
    pub context_id: Option<String>,
    pub timestamp: String,
}

/// Media scan event
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct MediaScanEvent {
    pub file_path: String,
    pub file_name: String,
    pub file_size: u64,
    pub media_type: String,
    pub action: MediaScanAction,
    pub metadata_status: String,
}

/// Action taken during a media scan
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub enum MediaScanAction {
    New,
    Updated,
    Deleted,
    MetadataPending,
    MetadataComplete,
}

/// EPG update event
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct EpgUpdateEvent {
    pub channel_count: usize,
    pub program_count: usize,
    pub source: String,
    pub updated_at: String,
}

/// MCP resource poll event
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct McpResourceEvent {
    pub resource_uri: String,
    pub resource_type: String,
    pub content_preview: Option<String>,
    pub size_bytes: Option<u64>,
}

/// udev device event
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct UdevEvent {
    pub action: String, // "add", "remove", "change"
    pub device_path: String,
    pub device_name: Option<String>,
    pub subsystem: String,
    pub devtype: Option<String>,
    pub properties: Option<serde_json::Value>,
}

/// DBus signal event
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct DBusEvent {
    pub sender: String,
    pub interface: String,
    pub member: String,
    pub path: String,
    pub body: Option<serde_json::Value>,
}

/// System event (service status changes, etc.)
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SystemEvent {
    pub event: String,
    pub service: Option<String>,
    pub status: Option<String>,
    pub message: Option<String>,
    pub severity: SystemSeverity,
}

/// Severity level for system events
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub enum SystemSeverity {
    Info,
    Warning,
    Error,
    Critical,
}

impl std::fmt::Display for SystemSeverity {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            SystemSeverity::Info => write!(f, "info"),
            SystemSeverity::Warning => write!(f, "warning"),
            SystemSeverity::Error => write!(f, "error"),
            SystemSeverity::Critical => write!(f, "critical"),
        }
    }
}
