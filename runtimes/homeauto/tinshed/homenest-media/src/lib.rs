//! homenest-media — Media scanner, metadata workflow, mpv integration
//!
//! Provides:
//! - `MediaScanner` — Walks media directories, detects new files, emits feed events
//! - `MetadataWorkflow` — Privacy-first confirmation flow for metadata enrichment
//! - `MpvController` — MCP tool for mpv playback control
//! - `SubtitleParser` — SRT/ASS parser and overlay

pub mod scanner;
pub mod metadata;
pub mod mpv;
pub mod subtitle;

use serde::{Deserialize, Serialize};
use std::path::PathBuf;

/// Media file types supported by HomeNest
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub enum MediaType {
    Movie,
    TvShow,
    Music,
    Recording,
    Other,
}

impl MediaType {
    pub fn from_extension(path: &str) -> Self {
        let lower = path.to_lowercase();
        if lower.ends_with(".mp4") || lower.ends_with(".mkv") || lower.ends_with(".avi")
            || lower.ends_with(".mov") || lower.ends_with(".m4v")
        {
            // Could be movie or TV show — needs metadata lookup
            MediaType::Movie
        } else if lower.ends_with(".mp3") || lower.ends_with(".flac")
            || lower.ends_with(".wav") || lower.ends_with(".aac")
            || lower.ends_with(".ogg") || lower.ends_with(".m4a")
        {
            MediaType::Music
        } else if lower.ends_with(".ts") || lower.ends_with(".dvr") {
            MediaType::Recording
        } else {
            MediaType::Other
        }
    }
}

/// A discovered media item
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct MediaItem {
    pub id: String,
    pub path: PathBuf,
    pub file_name: String,
    pub file_size: u64,
    pub media_type: MediaType,
    pub mime_type: String,
    pub sha256: Option<String>,
    pub discovered_at: String,
    pub metadata: Option<MediaMetadata>,
}

/// Enriched metadata for a media item
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct MediaMetadata {
    pub title: Option<String>,
    pub year: Option<u16>,
    pub genre: Option<Vec<String>>,
    pub duration_secs: Option<u64>,
    pub resolution: Option<String>,
    pub audio_codec: Option<String>,
    pub video_codec: Option<String>,
    pub subtitles: Vec<String>,
    pub poster_url: Option<String>,
    pub backdrop_url: Option<String>,
    pub overview: Option<String>,
    pub rating: Option<f32>,
    pub source: MetadataSource,
}

/// Where metadata was obtained from
#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum MetadataSource {
    Local,
    Tmdb,
    UserProvided,
    None,
}

/// Result of a media scan operation
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ScanResult {
    pub total_files: usize,
    pub new_files: usize,
    pub updated_files: usize,
    pub errors: Vec<String>,
    pub items: Vec<MediaItem>,
}

/// Playback state
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub enum PlaybackState {
    Stopped,
    Playing,
    Paused,
}

/// Current playback status
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PlaybackStatus {
    pub state: PlaybackState,
    pub current_item: Option<MediaItem>,
    pub position_secs: f64,
    pub duration_secs: f64,
    pub volume: u8,
}

impl Default for PlaybackStatus {
    fn default() -> Self {
        Self {
            state: PlaybackState::Stopped,
            current_item: None,
            position_secs: 0.0,
            duration_secs: 0.0,
            volume: 65,
        }
    }
}
