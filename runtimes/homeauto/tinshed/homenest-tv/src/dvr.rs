//! DVR Scheduler — One-time + series recording management

use crate::{Program, Recording, RecordingConflict, RecordingStatus, RecordingType};
use chrono::{DateTime, Utc};
use std::collections::HashMap;
use uuid::Uuid;

/// DVR scheduler for managing recording schedules
pub struct DvrScheduler {
    recordings: Vec<Recording>,
    /// Series recording rules (series_id -> program title pattern)
    series_rules: HashMap<String, String>,
}

impl DvrScheduler {
    pub fn new() -> Self {
        Self {
            recordings: Vec::new(),
            series_rules: HashMap::new(),
        }
    }

    /// Schedule a one-time recording from a program
    pub fn schedule_one_time(&mut self, program: &Program) -> Result<Recording, String> {
        // Check for conflicts
        let conflicts = self.find_conflicts(&program.start_time, &program.end_time);
        if !conflicts.is_empty() {
            return Err(format!(
                "Scheduling conflict: {} overlaps with {} existing recording(s)",
                program.title,
                conflicts.len()
            ));
        }

        let recording = Recording {
            id: Uuid::new_v4().to_string(),
            channel_id: program.channel_id.clone(),
            program_id: Some(program.id.clone()),
            title: program.title.clone(),
            start_time: program.start_time.clone(),
            end_time: program.end_time.clone(),
            duration_minutes: program.duration_minutes,
            status: RecordingStatus::Scheduled,
            recording_type: RecordingType::OneTime,
            file_path: None,
            file_size: None,
            created_at: Utc::now().to_rfc3339(),
        };

        self.recordings.push(recording.clone());
        Ok(recording)
    }

    /// Schedule a series recording (records all matching programs)
    pub fn schedule_series(&mut self, title_pattern: &str) -> String {
        let series_id = Uuid::new_v4().to_string();
        self.series_rules.insert(series_id.clone(), title_pattern.to_string());
        series_id
    }

    /// Schedule recordings for all programs matching a series rule
    pub fn apply_series_rule(&mut self, programs: &[Program], series_id: &str) -> Vec<Recording> {
        let pattern = match self.series_rules.get(series_id) {
            Some(p) => p,
            None => return Vec::new(),
        };

        let mut scheduled = Vec::new();
        for program in programs {
            if program.title.contains(pattern) {
                // Check if already scheduled
                if self.recordings.iter().any(|r| r.program_id == Some(program.id.clone())) {
                    continue;
                }

                if let Ok(recording) = self.schedule_one_time(program) {
                    scheduled.push(recording);
                }
            }
        }
        scheduled
    }

    /// Schedule a manual recording (time-based, no program)
    pub fn schedule_manual(
        &mut self,
        channel_id: &str,
        title: &str,
        start_time: &str,
        duration_minutes: u32,
    ) -> Recording {
        let start = start_time.to_string();
        // Calculate end time
        let end = if let Some(dt) = parse_iso_time(start_time) {
            let end_dt = dt + chrono::Duration::minutes(duration_minutes as i64);
            end_dt.to_rfc3339()
        } else {
            start_time.to_string()
        };

        let recording = Recording {
            id: Uuid::new_v4().to_string(),
            channel_id: channel_id.to_string(),
            program_id: None,
            title: title.to_string(),
            start_time: start,
            end_time: end,
            duration_minutes,
            status: RecordingStatus::Scheduled,
            recording_type: RecordingType::Manual,
            file_path: None,
            file_size: None,
            created_at: Utc::now().to_rfc3339(),
        };

        self.recordings.push(recording.clone());
        recording
    }

    /// Cancel a scheduled recording
    pub fn cancel(&mut self, recording_id: &str) -> Result<(), String> {
        let recording = self.recordings.iter_mut()
            .find(|r| r.id == recording_id)
            .ok_or_else(|| format!("Recording not found: {}", recording_id))?;

        if recording.status == RecordingStatus::Completed || recording.status == RecordingStatus::Recording {
            return Err(format!("Cannot cancel recording in status: {:?}", recording.status));
        }

        recording.status = RecordingStatus::Cancelled;
        Ok(())
    }

    /// Mark a recording as started
    pub fn mark_started(&mut self, recording_id: &str) -> Result<(), String> {
        let recording = self.recordings.iter_mut()
            .find(|r| r.id == recording_id)
            .ok_or_else(|| format!("Recording not found: {}", recording_id))?;

        recording.status = RecordingStatus::Recording;
        Ok(())
    }

    /// Mark a recording as completed
    pub fn mark_completed(&mut self, recording_id: &str, file_path: &str, file_size: u64) -> Result<(), String> {
        let recording = self.recordings.iter_mut()
            .find(|r| r.id == recording_id)
            .ok_or_else(|| format!("Recording not found: {}", recording_id))?;

        recording.status = RecordingStatus::Completed;
        recording.file_path = Some(file_path.to_string());
        recording.file_size = Some(file_size);
        Ok(())
    }

    /// Mark a recording as failed
    pub fn mark_failed(&mut self, recording_id: &str, error: &str) -> Result<(), String> {
        let recording = self.recordings.iter_mut()
            .find(|r| r.id == recording_id)
            .ok_or_else(|| format!("Recording not found: {}", recording_id))?;

        recording.status = RecordingStatus::Failed(error.to_string());
        Ok(())
    }

    /// Find conflicts for a given time range
    pub fn find_conflicts(&self, start_time: &str, end_time: &str) -> Vec<RecordingConflict> {
        let mut conflicts = Vec::new();

        for recording in &self.recordings {
            if recording.status == RecordingStatus::Cancelled || recording.status == RecordingStatus::Completed {
                continue;
            }

            if times_overlap(start_time, end_time, &recording.start_time, &recording.end_time) {
                let overlap = calculate_overlap(start_time, end_time, &recording.start_time, &recording.end_time);
                conflicts.push(RecordingConflict {
                    recording_a: recording.id.clone(),
                    recording_b: recording.id.clone(), // Will be resolved by caller
                    overlap_seconds: overlap,
                    description: format!("Overlaps with '{}' on channel {}", recording.title, recording.channel_id),
                });
            }
        }

        conflicts
    }

    /// Get all scheduled recordings
    pub fn get_scheduled(&self) -> Vec<&Recording> {
        self.recordings.iter()
            .filter(|r| r.status == RecordingStatus::Scheduled)
            .collect()
    }

    /// Get all recordings
    pub fn get_all(&self) -> &[Recording] {
        &self.recordings
    }

    /// Get upcoming recordings (within the next 24 hours)
    pub fn get_upcoming(&self) -> Vec<&Recording> {
        let now = Utc::now();
        let tomorrow = now + chrono::Duration::hours(24);

        self.recordings.iter()
            .filter(|r| {
                if r.status != RecordingStatus::Scheduled {
                    return false;
                }
                if let Some(start) = parse_iso_time(&r.start_time) {
                    start >= now && start <= tomorrow
                } else {
                    false
                }
            })
            .collect()
    }

    /// Get active (currently recording) recordings
    pub fn get_active(&self) -> Vec<&Recording> {
        self.recordings.iter()
            .filter(|r| r.status == RecordingStatus::Recording)
            .collect()
    }
}

impl Default for DvrScheduler {
    fn default() -> Self {
        Self::new()
    }
}

/// Check if two time ranges overlap
fn times_overlap(start1: &str, end1: &str, start2: &str, end2: &str) -> bool {
    let s1 = parse_iso_time(start1);
    let e1 = parse_iso_time(end1);
    let s2 = parse_iso_time(start2);
    let e2 = parse_iso_time(end2);

    match (s1, e1, s2, e2) {
        (Some(s1), Some(e1), Some(s2), Some(e2)) => s1 < e2 && s2 < e1,
        _ => false,
    }
}

/// Calculate overlap duration in seconds
fn calculate_overlap(start1: &str, end1: &str, start2: &str, end2: &str) -> u64 {
    let s1 = parse_iso_time(start1);
    let e1 = parse_iso_time(end1);
    let s2 = parse_iso_time(start2);
    let e2 = parse_iso_time(end2);

    match (s1, e1, s2, e2) {
        (Some(s1), Some(e1), Some(s2), Some(e2)) => {
            let overlap_start = s1.max(s2);
            let overlap_end = e1.min(e2);
            if overlap_start < overlap_end {
                (overlap_end - overlap_start).num_seconds() as u64
            } else {
                0
            }
        }
        _ => 0,
    }
}

/// Parse an ISO 8601 time string
fn parse_iso_time(time_str: &str) -> Option<DateTime<Utc>> {
    DateTime::parse_from_rfc3339(time_str)
        .map(|dt| dt.with_timezone(&Utc))
        .or_else(|_| {
            // Try parsing without timezone
            chrono::NaiveDateTime::parse_from_str(time_str, "%Y-%m-%dT%H:%M:%S")
                .map(|dt| dt.and_utc())
                .ok()
        })
        .ok()
}

#[cfg(test)]
mod tests {
    use super::*;

    fn make_test_program(title: &str, start: &str, end: &str) -> Program {
        Program {
            id: Uuid::new_v4().to_string(),
            channel_id: "ABC".into(),
            title: title.into(),
            subtitle: None,
            description: None,
            start_time: start.into(),
            end_time: end.into(),
            duration_minutes: 30,
            category: None,
            episode_title: None,
            episode_number: None,
            season_number: None,
            year: None,
            rating: None,
            icon_url: None,
            is_live: false,
            is_new: false,
            is_movie: false,
            is_sports: false,
        }
    }

    #[test]
    fn test_schedule_one_time() {
        let mut scheduler = DvrScheduler::new();
        let program = make_test_program(
            "Evening News",
            "2026-05-17T18:00:00Z",
            "2026-05-17T18:30:00Z",
        );

        let recording = scheduler.schedule_one_time(&program).unwrap();
        assert_eq!(recording.title, "Evening News");
        assert_eq!(recording.status, RecordingStatus::Scheduled);
    }

    #[test]
    fn test_conflict_detection() {
        let mut scheduler = DvrScheduler::new();
        let prog1 = make_test_program("News", "2026-05-17T18:00:00Z", "2026-05-17T18:30:00Z");
        let prog2 = make_test_program("Movie", "2026-05-17T18:15:00Z", "2026-05-17T19:00:00Z");

        scheduler.schedule_one_time(&prog1).unwrap();
        let result = scheduler.schedule_one_time(&prog2);
        assert!(result.is_err());
        assert!(result.unwrap_err().contains("conflict"));
    }

    #[test]
    fn test_cancel_recording() {
        let mut scheduler = DvrScheduler::new();
        let program = make_test_program("Test", "2026-05-17T20:00:00Z", "2026-05-17T20:30:00Z");
        let recording = scheduler.schedule_one_time(&program).unwrap();

        scheduler.cancel(&recording.id).unwrap();
        let rec = scheduler.get_all().iter().find(|r| r.id == recording.id).unwrap();
        assert_eq!(rec.status, RecordingStatus::Cancelled);
    }

    #[test]
    fn test_times_overlap() {
        assert!(times_overlap(
            "2026-05-17T18:00:00Z", "2026-05-17T18:30:00Z",
            "2026-05-17T18:15:00Z", "2026-05-17T18:45:00Z",
        ));
        assert!(!times_overlap(
            "2026-05-17T18:00:00Z", "2026-05-17T18:30:00Z",
            "2026-05-17T18:30:00Z", "2026-05-17T19:00:00Z",
        ));
    }
}
