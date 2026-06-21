//! Feed Spool — NDJSON-based feed storage with all feed types

use crate::{FeedConfig, FeedEntry, FeedSource, FeedEntryType, FeedStats};
use chrono::Utc;
use std::collections::HashMap;
use std::fs::{self, OpenOptions};
use std::io::{BufRead, BufReader, Write};
use std::path::PathBuf;
use uuid::Uuid;

/// Feed spool — manages the unified timeline of feed entries
pub struct FeedSpool {
    config: FeedConfig,
    entries: Vec<FeedEntry>,
    spool_path: PathBuf,
}

impl FeedSpool {
    /// Create a new feed spool
    pub fn new(config: FeedConfig) -> Self {
        let spool_path = shellexpand::tilde(&config.spool_path).to_string();
        let spool_path = PathBuf::from(spool_path);

        let mut spool = Self {
            config,
            entries: Vec::new(),
            spool_path,
        };

        // Load existing entries from disk
        let _ = spool.load();
        spool
    }

    /// Load entries from the NDJSON spool file
    pub fn load(&mut self) -> Result<(), String> {
        if !self.spool_path.exists() {
            return Ok(());
        }

        let file = fs::File::open(&self.spool_path)
            .map_err(|e| format!("Failed to open spool: {}", e))?;
        let reader = BufReader::new(file);

        self.entries.clear();
        for line in reader.lines() {
            let line = line.map_err(|e| format!("Failed to read line: {}", e))?;
            if line.trim().is_empty() {
                continue;
            }
            if let Ok(entry) = serde_json::from_str::<FeedEntry>(&line) {
                self.entries.push(entry);
            }
        }

        // Trim to max entries
        if self.entries.len() > self.config.max_entries {
            let excess = self.entries.len() - self.config.max_entries;
            self.entries.drain(..excess);
        }

        Ok(())
    }

    /// Save all entries to the NDJSON spool file
    pub fn save(&self) -> Result<(), String> {
        // Ensure parent directory exists
        if let Some(parent) = self.spool_path.parent() {
            fs::create_dir_all(parent)
                .map_err(|e| format!("Failed to create spool directory: {}", e))?;
        }

        let mut file = OpenOptions::new()
            .write(true)
            .create(true)
            .truncate(true)
            .open(&self.spool_path)
            .map_err(|e| format!("Failed to open spool for writing: {}", e))?;

        for entry in &self.entries {
            let line = serde_json::to_string(entry)
                .map_err(|e| format!("Failed to serialize entry: {}", e))?;
            writeln!(file, "{}", line)
                .map_err(|e| format!("Failed to write entry: {}", e))?;
        }

        Ok(())
    }

    /// Append a single entry to the spool
    pub fn append(&mut self, entry: FeedEntry) -> Result<(), String> {
        // Ensure parent directory exists
        if let Some(parent) = self.spool_path.parent() {
            fs::create_dir_all(parent)
                .map_err(|e| format!("Failed to create spool directory: {}", e))?;
        }

        let line = serde_json::to_string(&entry)
            .map_err(|e| format!("Failed to serialize entry: {}", e))?;

        let mut file = OpenOptions::new()
            .write(true)
            .create(true)
            .append(true)
            .open(&self.spool_path)
            .map_err(|e| format!("Failed to open spool for append: {}", e))?;

        writeln!(file, "{}", line)
            .map_err(|e| format!("Failed to append entry: {}", e))?;

        self.entries.push(entry);

        // Trim if over max
        if self.entries.len() > self.config.max_entries {
            let excess = self.entries.len() - self.config.max_entries;
            self.entries.drain(..excess);
            // Rewrite the file
            self.save()?;
        }

        Ok(())
    }

    /// Add a new feed entry
    pub fn add_entry(
        &mut self,
        source: FeedSource,
        entry_type: FeedEntryType,
        title: &str,
        body: Option<&str>,
        url: Option<&str>,
        metadata: Option<serde_json::Value>,
    ) -> Result<FeedEntry, String> {
        let entry = FeedEntry {
            id: Uuid::new_v4().to_string(),
            timestamp: Utc::now().to_rfc3339(),
            source,
            entry_type,
            title: title.to_string(),
            body: body.map(|s| s.to_string()),
            url: url.map(|s| s.to_string()),
            metadata,
            is_read: false,
        };

        self.append(entry.clone())?;
        Ok(entry)
    }

    /// Mark an entry as read
    pub fn mark_read(&mut self, entry_id: &str) -> Result<(), String> {
        let entry = self.entries.iter_mut()
            .find(|e| e.id == entry_id)
            .ok_or_else(|| format!("Entry not found: {}", entry_id))?;
        entry.is_read = true;
        self.save()?;
        Ok(())
    }

    /// Mark all entries as read
    pub fn mark_all_read(&mut self) -> Result<(), String> {
        for entry in &mut self.entries {
            entry.is_read = true;
        }
        self.save()?;
        Ok(())
    }

    /// Get entries filtered by source
    pub fn get_by_source(&self, source: FeedSource) -> Vec<&FeedEntry> {
        self.entries.iter()
            .filter(|e| e.source == source)
            .collect()
    }

    /// Get entries filtered by type
    pub fn get_by_type(&self, entry_type: FeedEntryType) -> Vec<&FeedEntry> {
        self.entries.iter()
            .filter(|e| e.entry_type == entry_type)
            .collect()
    }

    /// Get unread entries
    pub fn get_unread(&self) -> Vec<&FeedEntry> {
        self.entries.iter()
            .filter(|e| !e.is_read)
            .collect()
    }

    /// Get recent entries (last N)
    pub fn get_recent(&self, count: usize) -> Vec<&FeedEntry> {
        self.entries.iter()
            .rev()
            .take(count)
            .collect()
    }

    /// Get entries within a time range
    pub fn get_in_range(&self, start: &str, end: &str) -> Vec<&FeedEntry> {
        self.entries.iter()
            .filter(|e| e.timestamp >= start.to_string() && e.timestamp <= end.to_string())
            .collect()
    }

    /// Remove old entries based on retention policy
    pub fn prune(&mut self) -> Result<usize, String> {
        let cutoff = Utc::now() - chrono::Duration::days(self.config.retention_days as i64);
        let cutoff_str = cutoff.to_rfc3339();

        let before = self.entries.len();
        self.entries.retain(|e| e.timestamp >= cutoff_str);
        let removed = before - self.entries.len();

        if removed > 0 {
            self.save()?;
        }

        Ok(removed)
    }

    /// Get feed statistics
    pub fn get_stats(&self) -> FeedStats {
        let mut by_source = HashMap::new();
        for entry in &self.entries {
            let key = format!("{:?}", entry.source);
            *by_source.entry(key).or_insert(0) += 1;
        }

        FeedStats {
            total_entries: self.entries.len(),
            unread_count: self.entries.iter().filter(|e| !e.is_read).count(),
            by_source,
            oldest_entry: self.entries.first().map(|e| e.timestamp.clone()),
            newest_entry: self.entries.last().map(|e| e.timestamp.clone()),
        }
    }

    /// Clear all entries
    pub fn clear(&mut self) -> Result<(), String> {
        self.entries.clear();
        if self.spool_path.exists() {
            fs::remove_file(&self.spool_path)
                .map_err(|e| format!("Failed to remove spool file: {}", e))?;
        }
        Ok(())
    }

    /// Get total entry count
    pub fn len(&self) -> usize {
        self.entries.len()
    }

    /// Check if spool is empty
    pub fn is_empty(&self) -> bool {
        self.entries.is_empty()
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use tempfile::TempDir;

    fn make_spool() -> (FeedSpool, TempDir) {
        let dir = TempDir::new().unwrap();
        let config = FeedConfig {
            spool_path: dir.path().join("feed.spool").to_string_lossy().to_string(),
            max_entries: 100,
            retention_days: 30,
            poll_interval_secs: 900,
        };
        (FeedSpool::new(config), dir)
    }

    #[test]
    fn test_add_and_retrieve() {
        let (mut spool, _dir) = make_spool();

        spool.add_entry(
            FeedSource::System,
            FeedEntryType::Info,
            "Test entry",
            Some("This is a test"),
            None,
            None,
        ).unwrap();

        assert_eq!(spool.len(), 1);
        let recent = spool.get_recent(10);
        assert_eq!(recent.len(), 1);
        assert_eq!(recent[0].title, "Test entry");
    }

    #[test]
    fn test_mark_read() {
        let (mut spool, _dir) = make_spool();

        let entry = spool.add_entry(
            FeedSource::Rss,
            FeedEntryType::Poll,
            "RSS Update",
            None,
            Some("http://example.com"),
            None,
        ).unwrap();

        assert_eq!(spool.get_unread().len(), 1);
        spool.mark_read(&entry.id).unwrap();
        assert_eq!(spool.get_unread().len(), 0);
    }

    #[test]
    fn test_filter_by_source() {
        let (mut spool, _dir) = make_spool();

        spool.add_entry(FeedSource::Rss, FeedEntryType::Poll, "RSS", None, None, None).unwrap();
        spool.add_entry(FeedSource::System, FeedEntryType::Info, "System", None, None, None).unwrap();
        spool.add_entry(FeedSource::MediaScan, FeedEntryType::NewMedia, "Media", None, None, None).unwrap();

        assert_eq!(spool.get_by_source(FeedSource::Rss).len(), 1);
        assert_eq!(spool.get_by_source(FeedSource::System).len(), 1);
        assert_eq!(spool.get_by_source(FeedSource::MediaScan).len(), 1);
    }

    #[test]
    fn test_prune_old_entries() {
        let (mut spool, _dir) = make_spool();

        // Add entries with old timestamps by manipulating the entries directly
        let old_time = (Utc::now() - chrono::Duration::days(60)).to_rfc3339();
        let old_entry = FeedEntry {
            id: Uuid::new_v4().to_string(),
            timestamp: old_time,
            source: FeedSource::System,
            entry_type: FeedEntryType::Info,
            title: "Old entry".into(),
            body: None,
            url: None,
            metadata: None,
            is_read: false,
        };
        spool.entries.push(old_entry);

        let new_entry = FeedEntry {
            id: Uuid::new_v4().to_string(),
            timestamp: Utc::now().to_rfc3339(),
            source: FeedSource::System,
            entry_type: FeedEntryType::Info,
            title: "New entry".into(),
            body: None,
            url: None,
            metadata: None,
            is_read: false,
        };
        spool.entries.push(new_entry);

        let removed = spool.prune().unwrap();
        assert_eq!(removed, 1);
        assert_eq!(spool.len(), 1);
        assert_eq!(spool.entries[0].title, "New entry");
    }

    #[test]
    fn test_stats() {
        let (mut spool, _dir) = make_spool();

        spool.add_entry(FeedSource::Rss, FeedEntryType::Poll, "RSS 1", None, None, None).unwrap();
        spool.add_entry(FeedSource::Rss, FeedEntryType::Poll, "RSS 2", None, None, None).unwrap();
        spool.add_entry(FeedSource::System, FeedEntryType::Info, "System", None, None, None).unwrap();

        let stats = spool.get_stats();
        assert_eq!(stats.total_entries, 3);
        assert_eq!(stats.unread_count, 3);
        assert_eq!(*stats.by_source.get("Rss").unwrap(), 2);
        assert_eq!(*stats.by_source.get("System").unwrap(), 1);
    }
}
