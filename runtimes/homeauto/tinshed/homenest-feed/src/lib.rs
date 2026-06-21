//! homenest-feed — Feed/Spool viewer, unified timeline
//!
//! Provides:
//! - `FeedSpool` — NDJSON-based feed storage with all feed types
//! - `RssPoller` — Configurable RSS polling
//! - `FeedTypes` — RSS, HA events, media scans, EPG, MCP, udev, DBus

pub mod spool;
pub mod rss;
pub mod types;

use serde::{Deserialize, Serialize};

/// A single feed entry in the unified timeline
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct FeedEntry {
    pub id: String,
    pub timestamp: String,
    pub source: FeedSource,
    pub entry_type: FeedEntryType,
    pub title: String,
    pub body: Option<String>,
    pub url: Option<String>,
    pub metadata: Option<serde_json::Value>,
    pub is_read: bool,
}

/// Source of a feed entry
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub enum FeedSource {
    Rss,
    HaEvent,
    MediaScan,
    Epg,
    McpResource,
    Udev,
    DBus,
    System,
}

/// Type of feed entry
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub enum FeedEntryType {
    Info,
    Warning,
    Error,
    NewMedia,
    Recording,
    Automation,
    Event,
    Poll,
}

/// Configuration for the feed spool
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct FeedConfig {
    pub spool_path: String,
    pub max_entries: usize,
    pub retention_days: u32,
    pub poll_interval_secs: u64,
}

impl Default for FeedConfig {
    fn default() -> Self {
        Self {
            spool_path: "~/.local/share/udos/feed.spool".into(),
            max_entries: 10000,
            retention_days: 30,
            poll_interval_secs: 900, // 15 minutes
        }
    }
}

/// Statistics about the feed spool
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct FeedStats {
    pub total_entries: usize,
    pub unread_count: usize,
    pub by_source: std::collections::HashMap<String, usize>,
    pub oldest_entry: Option<String>,
    pub newest_entry: Option<String>,
}
