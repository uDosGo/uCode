//! Metadata workflow — privacy-first confirmation flow for metadata enrichment
//!
//! The workflow:
//! 1. Scanner finds file → Feed spool entry → Console notification
//! 2. User confirms → TMDB search → "Do you own this?"
//! 3. Yes: Download metadata, mark playable → Grid cell
//! 4. No: Add as browsable-only → Visual-only slot

use crate::{MediaItem, MediaMetadata, MetadataSource};
use serde::{Deserialize, Serialize};
use std::collections::HashMap;

/// Status of a metadata enrichment request
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub enum MetadataStatus {
    Pending,
    AwaitingConfirmation,
    Confirmed,
    Rejected,
    Enriched,
    Failed(String),
}

/// A metadata enrichment request awaiting user action
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct MetadataRequest {
    pub item_id: String,
    pub file_name: String,
    pub file_size: u64,
    pub status: MetadataStatus,
    pub candidates: Vec<MetadataCandidate>,
    pub selected_candidate: Option<usize>,
    pub created_at: String,
    pub updated_at: String,
}

/// A candidate match from TMDB or other metadata source
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct MetadataCandidate {
    pub title: String,
    pub year: Option<u16>,
    pub media_type: String, // "movie" or "tv"
    pub overview: Option<String>,
    pub poster_url: Option<String>,
    pub backdrop_url: Option<String>,
    pub rating: Option<f32>,
    pub genre: Vec<String>,
    pub source: String, // "tmdb", "local", etc.
    pub confidence: f32, // 0.0 - 1.0
}

/// Metadata workflow manager
pub struct MetadataWorkflow {
    /// Pending requests (item_id -> request)
    pending_requests: HashMap<String, MetadataRequest>,
    /// Enriched metadata cache (item_id -> metadata)
    metadata_cache: HashMap<String, MediaMetadata>,
}

impl MetadataWorkflow {
    pub fn new() -> Self {
        Self {
            pending_requests: HashMap::new(),
            metadata_cache: HashMap::new(),
        }
    }

    /// Submit a new media item for metadata enrichment
    pub fn submit(&mut self, item: &MediaItem) -> MetadataRequest {
        let request = MetadataRequest {
            item_id: item.id.clone(),
            file_name: item.file_name.clone(),
            file_size: item.file_size,
            status: MetadataStatus::Pending,
            candidates: Vec::new(),
            selected_candidate: None,
            created_at: item.discovered_at.clone(),
            updated_at: item.discovered_at.clone(),
        };

        self.pending_requests.insert(item.id.clone(), request.clone());
        request
    }

    /// Add metadata candidates for a pending request
    pub fn add_candidates(
        &mut self,
        item_id: &str,
        candidates: Vec<MetadataCandidate>,
    ) -> Result<(), String> {
        let request = self.pending_requests.get_mut(item_id)
            .ok_or_else(|| format!("No pending request for item: {}", item_id))?;

        request.candidates = candidates;
        request.status = MetadataStatus::AwaitingConfirmation;
        request.updated_at = chrono::Utc::now().to_rfc3339();
        Ok(())
    }

    /// User confirms a candidate — mark as playable
    pub fn confirm(&mut self, item_id: &str, candidate_idx: usize) -> Result<MediaMetadata, String> {
        let request = self.pending_requests.get(item_id)
            .ok_or_else(|| format!("No pending request for item: {}", item_id))?;

        let candidate = request.candidates.get(candidate_idx)
            .ok_or_else(|| format!("Invalid candidate index: {}", candidate_idx))?;

        let metadata = MediaMetadata {
            title: Some(candidate.title.clone()),
            year: candidate.year,
            genre: Some(candidate.genre.clone()),
            duration_secs: None,
            resolution: None,
            audio_codec: None,
            video_codec: None,
            subtitles: Vec::new(),
            poster_url: candidate.poster_url.clone(),
            backdrop_url: candidate.backdrop_url.clone(),
            overview: candidate.overview.clone(),
            rating: candidate.rating,
            source: MetadataSource::Tmdb,
        };

        self.metadata_cache.insert(item_id.to_string(), metadata.clone());

        let request = self.pending_requests.get_mut(item_id).unwrap();
        request.status = MetadataStatus::Confirmed;
        request.selected_candidate = Some(candidate_idx);
        request.updated_at = chrono::Utc::now().to_rfc3339();

        Ok(metadata)
    }

    /// User rejects all candidates — add as browsable-only
    pub fn reject(&mut self, item_id: &str) -> Result<(), String> {
        let request = self.pending_requests.get_mut(item_id)
            .ok_or_else(|| format!("No pending request for item: {}", item_id))?;

        request.status = MetadataStatus::Rejected;
        request.updated_at = chrono::Utc::now().to_rfc3339();

        let metadata = MediaMetadata {
            title: Some(request.file_name.clone()),
            year: None,
            genre: None,
            duration_secs: None,
            resolution: None,
            audio_codec: None,
            video_codec: None,
            subtitles: Vec::new(),
            poster_url: None,
            backdrop_url: None,
            overview: None,
            rating: None,
            source: MetadataSource::UserProvided,
        };

        self.metadata_cache.insert(item_id.to_string(), metadata);
        Ok(())
    }

    /// Get cached metadata for an item
    pub fn get_metadata(&self, item_id: &str) -> Option<&MediaMetadata> {
        self.metadata_cache.get(item_id)
    }

    /// Get all pending requests awaiting user action
    pub fn get_pending(&self) -> Vec<&MetadataRequest> {
        self.pending_requests.values()
            .filter(|r| r.status == MetadataStatus::AwaitingConfirmation)
            .collect()
    }

    /// Get all requests
    pub fn get_all_requests(&self) -> Vec<&MetadataRequest> {
        self.pending_requests.values().collect()
    }

    /// Number of items awaiting user confirmation
    pub fn pending_count(&self) -> usize {
        self.pending_requests.values()
            .filter(|r| r.status == MetadataStatus::AwaitingConfirmation)
            .count()
    }
}

impl Default for MetadataWorkflow {
    fn default() -> Self {
        Self::new()
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::MediaType;
    use std::path::PathBuf;

    fn make_test_item() -> MediaItem {
        MediaItem {
            id: "test-1".into(),
            path: PathBuf::from("/media/movies/test.mp4"),
            file_name: "test.mp4".into(),
            file_size: 1024,
            media_type: MediaType::Movie,
            mime_type: "video/mp4".into(),
            sha256: None,
            discovered_at: "2026-05-17T18:00:00Z".into(),
            metadata: None,
        }
    }

    #[test]
    fn test_submit_and_confirm() {
        let item = make_test_item();
        let mut workflow = MetadataWorkflow::new();

        let request = workflow.submit(&item);
        assert_eq!(request.status, MetadataStatus::Pending);

        let candidates = vec![
            MetadataCandidate {
                title: "Test Movie".into(),
                year: Some(2024),
                media_type: "movie".into(),
                overview: Some("A test movie".into()),
                poster_url: None,
                backdrop_url: None,
                rating: Some(7.5),
                genre: vec!["Action".into()],
                source: "tmdb".into(),
                confidence: 0.95,
            },
        ];

        workflow.add_candidates("test-1", candidates).unwrap();
        assert_eq!(workflow.pending_count(), 1);

        let metadata = workflow.confirm("test-1", 0).unwrap();
        assert_eq!(metadata.title, Some("Test Movie".into()));
        assert_eq!(metadata.source, MetadataSource::Tmdb);
    }

    #[test]
    fn test_reject_adds_browsable() {
        let item = make_test_item();
        let mut workflow = MetadataWorkflow::new();

        workflow.submit(&item);
        workflow.reject("test-1").unwrap();

        let metadata = workflow.get_metadata("test-1").unwrap();
        assert_eq!(metadata.source, MetadataSource::UserProvided);
    }
}
