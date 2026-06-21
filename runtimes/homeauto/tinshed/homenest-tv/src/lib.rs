//! homenest-tv — TV Guide (EPG), DVR scheduling, live TV
//!
//! Provides:
//! - `EpgParser` — XMLTV format parser
//! - `HdHomeRunModule` — Tuner discovery + channel scanning
//! - `DvrScheduler` — One-time + series recording
//! - `StorageManager` — Retention policy engine

pub mod epg;
pub mod hdhomerun;
pub mod dvr;
pub mod storage;

use serde::{Deserialize, Serialize};

/// A TV channel
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Channel {
    pub id: String,
    pub number: String,
    pub name: String,
    pub icon_url: Option<String>,
    pub source: ChannelSource,
}

/// Source of a TV channel
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub enum ChannelSource {
    HdHomeRun,
    PlutoTv,
    Tubi,
    Custom,
}

/// A TV program/listing
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Program {
    pub id: String,
    pub channel_id: String,
    pub title: String,
    pub subtitle: Option<String>,
    pub description: Option<String>,
    pub start_time: String,  // ISO 8601
    pub end_time: String,    // ISO 8601
    pub duration_minutes: u32,
    pub category: Option<String>,
    pub episode_title: Option<String>,
    pub episode_number: Option<String>,
    pub season_number: Option<u32>,
    pub year: Option<u16>,
    pub rating: Option<String>,
    pub icon_url: Option<String>,
    pub is_live: bool,
    pub is_new: bool,
    pub is_movie: bool,
    pub is_sports: bool,
}

/// A recording schedule
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Recording {
    pub id: String,
    pub channel_id: String,
    pub program_id: Option<String>,
    pub title: String,
    pub start_time: String,
    pub end_time: String,
    pub duration_minutes: u32,
    pub status: RecordingStatus,
    pub recording_type: RecordingType,
    pub file_path: Option<String>,
    pub file_size: Option<u64>,
    pub created_at: String,
}

/// Status of a recording
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub enum RecordingStatus {
    Scheduled,
    Recording,
    Completed,
    Failed(String),
    Cancelled,
}

/// Type of recording
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub enum RecordingType {
    OneTime,
    Series,
    Manual,
}

/// EPG data for a channel
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct EpgData {
    pub channel: Channel,
    pub programs: Vec<Program>,
}

/// Complete EPG snapshot
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct EpgSnapshot {
    pub channels: Vec<Channel>,
    pub programs: Vec<Program>,
    pub generated_at: String,
    pub source: String,
}

/// DVR schedule
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct DvrSchedule {
    pub recordings: Vec<Recording>,
    pub conflicts: Vec<RecordingConflict>,
}

/// A scheduling conflict between two recordings
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct RecordingConflict {
    pub recording_a: String,
    pub recording_b: String,
    pub overlap_seconds: u64,
    pub description: String,
}

/// Storage usage information
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct StorageInfo {
    pub total_bytes: u64,
    pub used_bytes: u64,
    pub free_bytes: u64,
    pub recording_count: u32,
    pub retention_days: u32,
}
