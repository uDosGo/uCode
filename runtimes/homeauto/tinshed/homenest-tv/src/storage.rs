//! Storage Manager — Retention policy engine for DVR recordings

use crate::{Recording, RecordingStatus, StorageInfo};
use chrono::{DateTime, Utc};
use std::path::PathBuf;

/// Retention policy for recordings
#[derive(Debug, Clone)]
pub struct RetentionPolicy {
    /// Default retention in days
    pub default_days: u32,
    /// Retention for movies (overrides default)
    pub movie_days: Option<u32>,
    /// Retention for series (overrides default)
    pub series_days: Option<u32>,
    /// Maximum storage in bytes (0 = unlimited)
    pub max_storage_bytes: u64,
    /// Whether to auto-delete watched recordings
    pub auto_delete_watched: bool,
}

impl Default for RetentionPolicy {
    fn default() -> Self {
        Self {
            default_days: 30,
            movie_days: Some(90),
            series_days: Some(14),
            max_storage_bytes: 500_000_000_000, // 500 GB
            auto_delete_watched: true,
        }
    }
}

/// Storage manager for DVR recordings
pub struct StorageManager {
    /// Recording storage directory
    storage_dir: PathBuf,
    /// Retention policy
    policy: RetentionPolicy,
    /// Current storage usage
    usage: StorageInfo,
}

impl StorageManager {
    /// Create a new storage manager
    pub fn new(storage_dir: PathBuf, policy: RetentionPolicy) -> Self {
        Self {
            storage_dir,
            policy,
            usage: StorageInfo {
                total_bytes: policy.max_storage_bytes,
                used_bytes: 0,
                free_bytes: policy.max_storage_bytes,
                recording_count: 0,
                retention_days: policy.default_days,
            },
        }
    }

    /// Calculate storage usage from a list of recordings
    pub fn calculate_usage(&mut self, recordings: &[Recording]) -> StorageInfo {
        let mut total_size: u64 = 0;
        let mut count: u32 = 0;

        for recording in recordings {
            if recording.status == RecordingStatus::Completed {
                if let Some(size) = recording.file_size {
                    total_size += size;
                }
                count += 1;
            }
        }

        let free = self.policy.max_storage_bytes.saturating_sub(total_size);

        self.usage = StorageInfo {
            total_bytes: self.policy.max_storage_bytes,
            used_bytes: total_size,
            free_bytes: free,
            recording_count: count,
            retention_days: self.policy.default_days,
        };

        self.usage.clone()
    }

    /// Get recordings that should be deleted based on retention policy
    pub fn get_expired(&self, recordings: &[Recording]) -> Vec<&Recording> {
        let now = Utc::now();

        recordings.iter()
            .filter(|r| {
                if r.status != RecordingStatus::Completed {
                    return false;
                }

                let created = match parse_iso_time(&r.created_at) {
                    Some(t) => t,
                    None => return false,
                };

                let retention = self.get_retention_days(r);
                let expiry = created + chrono::Duration::days(retention as i64);
                now > expiry
            })
            .collect()
    }

    /// Get retention days for a specific recording
    fn get_retention_days(&self, recording: &Recording) -> u32 {
        // Check if it's a movie (longer retention)
        if recording.title.to_lowercase().contains("movie") {
            self.policy.movie_days.unwrap_or(self.policy.default_days)
        } else if recording.recording_type == crate::RecordingType::Series {
            self.policy.series_days.unwrap_or(self.policy.default_days)
        } else {
            self.policy.default_days
        }
    }

    /// Check if there's enough space for a new recording
    pub fn has_space_for(&self, size_bytes: u64) -> bool {
        self.usage.free_bytes >= size_bytes
    }

    /// Get recommended recordings to delete to free up space
    pub fn get_cleanup_candidates(&self, recordings: &[Recording], needed_bytes: u64) -> Vec<&Recording> {
        let mut candidates: Vec<&Recording> = recordings.iter()
            .filter(|r| r.status == RecordingStatus::Completed)
            .collect();

        // Sort by age (oldest first)
        candidates.sort_by(|a, b| {
            let a_time = parse_iso_time(&a.created_at).unwrap_or(Utc::now());
            let b_time = parse_iso_time(&b.created_at).unwrap_or(Utc::now());
            a_time.cmp(&b_time)
        });

        // Return oldest recordings until we have enough space
        let mut freed: u64 = 0;
        let mut result = Vec::new();
        for recording in candidates {
            if freed >= needed_bytes {
                break;
            }
            if let Some(size) = recording.file_size {
                freed += size;
                result.push(recording);
            }
        }

        result
    }

    /// Get the recording file path for a scheduled recording
    pub fn get_recording_path(&self, recording: &Recording) -> PathBuf {
        let date_str = parse_iso_time(&recording.start_time)
            .map(|dt| dt.format("%Y-%m-%d").to_string())
            .unwrap_or_else(|| "unknown".to_string());

        let safe_title = recording.title.replace(' ', "_")
            .replace('/', "_")
            .replace(':', "_");

        self.storage_dir.join(format!("{}_{}.ts", date_str, safe_title))
    }

    /// Get current storage info
    pub fn get_info(&self) -> &StorageInfo {
        &self.usage
    }

    /// Update the retention policy
    pub fn set_policy(&mut self, policy: RetentionPolicy) {
        self.policy = policy;
    }
}

/// Parse an ISO 8601 time string
fn parse_iso_time(time_str: &str) -> Option<DateTime<Utc>> {
    DateTime::parse_from_rfc3339(time_str)
        .map(|dt| dt.with_timezone(&Utc))
        .or_else(|_| {
            chrono::NaiveDateTime::parse_from_str(time_str, "%Y-%m-%dT%H:%M:%S")
                .map(|dt| dt.and_utc())
                .ok()
        })
        .ok()
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::{RecordingType, RecordingStatus};
    use uuid::Uuid;

    fn make_test_recording(title: &str, days_ago: i64, size: u64) -> Recording {
        let created = Utc::now() - chrono::Duration::days(days_ago);
        Recording {
            id: Uuid::new_v4().to_string(),
            channel_id: "ABC".into(),
            program_id: None,
            title: title.into(),
            start_time: created.to_rfc3339(),
            end_time: (created + chrono::Duration::minutes(30)).to_rfc3339(),
            duration_minutes: 30,
            status: RecordingStatus::Completed,
            recording_type: RecordingType::OneTime,
            file_path: Some(format!("/recordings/{}.ts", title)),
            file_size: Some(size),
            created_at: created.to_rfc3339(),
        }
    }

    #[test]
    fn test_calculate_usage() {
        let mut manager = StorageManager::new(
            PathBuf::from("/recordings"),
            RetentionPolicy::default(),
        );

        let recordings = vec![
            make_test_recording("Movie1", 1, 4_000_000_000),  // 4 GB
            make_test_recording("Movie2", 2, 3_000_000_000),  // 3 GB
        ];

        let info = manager.calculate_usage(&recordings);
        assert_eq!(info.recording_count, 2);
        assert_eq!(info.used_bytes, 7_000_000_000);
    }

    #[test]
    fn test_expired_recordings() {
        let mut manager = StorageManager::new(
            PathBuf::from("/recordings"),
            RetentionPolicy {
                default_days: 30,
                ..Default::default()
            },
        );

        let recordings = vec![
            make_test_recording("Old Movie", 60, 1_000_000_000),   // 60 days old
            make_test_recording("New Movie", 5, 2_000_000_000),    // 5 days old
        ];

        let expired = manager.get_expired(&recordings);
        assert_eq!(expired.len(), 1);
        assert_eq!(expired[0].title, "Old Movie");
    }

    #[test]
    fn test_has_space() {
        let manager = StorageManager::new(
            PathBuf::from("/recordings"),
            RetentionPolicy {
                max_storage_bytes: 100,
                ..Default::default()
            },
        );

        assert!(manager.has_space_for(50));
        assert!(!manager.has_space_for(150));
    }

    #[test]
    fn test_cleanup_candidates() {
        let mut manager = StorageManager::new(
            PathBuf::from("/recordings"),
            RetentionPolicy::default(),
        );

        let recordings = vec![
            make_test_recording("Oldest", 30, 1_000_000_000),
            make_test_recording("Middle", 20, 2_000_000_000),
            make_test_recording("Newest", 10, 3_000_000_000),
        ];

        manager.calculate_usage(&recordings);
        let candidates = manager.get_cleanup_candidates(&recordings, 2_500_000_000);
        assert_eq!(candidates.len(), 2); // Oldest + Middle = 3GB > 2.5GB needed
    }
}
