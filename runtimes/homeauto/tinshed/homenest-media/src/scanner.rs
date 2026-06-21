//! Media scanner — walks media directories, detects new files, emits feed events

use crate::{MediaItem, MediaType, ScanResult};
use chrono::Utc;
use sha2::{Digest, Sha256};
use std::collections::HashMap;
use std::fs;
use std::path::{Path, PathBuf};
use uuid::Uuid;
use walkdir::WalkDir;

/// Configuration for the media scanner
#[derive(Debug, Clone)]
pub struct ScannerConfig {
    /// Directories to scan for media files
    pub media_dirs: Vec<PathBuf>,
    /// File extensions to include
    pub extensions: Vec<String>,
    /// Whether to scan recursively
    pub recursive: bool,
    /// Whether to compute SHA256 hashes (slow for large files)
    pub compute_hashes: bool,
    /// Whether to emit feed events for new files
    pub emit_feed_events: bool,
}

impl Default for ScannerConfig {
    fn default() -> Self {
        Self {
            media_dirs: vec![
                PathBuf::from("/media/movies"),
                PathBuf::from("/media/tv"),
                PathBuf::from("/media/music"),
                PathBuf::from("/media/recordings"),
            ],
            extensions: vec![
                "mp4".into(), "mkv".into(), "avi".into(), "mov".into(), "m4v".into(),
                "mp3".into(), "flac".into(), "wav".into(), "aac".into(), "ogg".into(), "m4a".into(),
                "ts".into(), "dvr".into(),
            ],
            recursive: true,
            compute_hashes: false,
            emit_feed_events: true,
        }
    }
}

/// Media scanner — walks directories and discovers media files
pub struct MediaScanner {
    config: ScannerConfig,
    /// Known files (path -> sha256) for change detection
    known_files: HashMap<PathBuf, String>,
}

impl MediaScanner {
    /// Create a new media scanner with the given configuration
    pub fn new(config: ScannerConfig) -> Self {
        Self {
            config,
            known_files: HashMap::new(),
        }
    }

    /// Load known files from a previous scan state
    pub fn load_state(&mut self, state: HashMap<PathBuf, String>) {
        self.known_files = state;
    }

    /// Get the current known files state (for persistence)
    pub fn get_state(&self) -> &HashMap<PathBuf, String> {
        &self.known_files
    }

    /// Run a full scan of all configured media directories
    pub fn scan(&mut self) -> ScanResult {
        let mut items = Vec::new();
        let mut errors = Vec::new();
        let mut new_count = 0;
        let mut updated_count = 0;

        for dir in &self.config.media_dirs {
            if !dir.exists() {
                log::warn!("Media directory does not exist: {:?}", dir);
                errors.push(format!("Directory not found: {:?}", dir));
                continue;
            }

            let walker = if self.config.recursive {
                WalkDir::new(dir).follow_links(true)
            } else {
                WalkDir::new(dir).max_depth(1)
            };

            for entry in walker.into_iter().filter_map(|e| e.ok()) {
                let path = entry.path();
                if !path.is_file() {
                    continue;
                }

                let ext = path.extension()
                    .and_then(|e| e.to_str())
                    .map(|e| e.to_lowercase())
                    .unwrap_or_default();

                if !self.config.extensions.contains(&ext) {
                    continue;
                }

                match self.process_file(path) {
                    Ok(item) => {
                        let is_new = !self.known_files.contains_key(path);
                        let is_updated = self.known_files.get(path)
                            .map(|old_hash| item.sha256.as_ref().map(|h| h != old_hash).unwrap_or(false))
                            .unwrap_or(false);

                        if is_new {
                            new_count += 1;
                        }
                        if is_updated {
                            updated_count += 1;
                        }

                        items.push(item);
                    }
                    Err(e) => {
                        log::error!("Error processing {:?}: {}", path, e);
                        errors.push(format!("{:?}: {}", path, e));
                    }
                }
            }
        }

        let total = items.len();
        ScanResult {
            total_files: total,
            new_files: new_count,
            updated_files: updated_count,
            errors,
            items,
        }
    }

    /// Process a single file — compute hash, determine type, create MediaItem
    fn process_file(&mut self, path: &Path) -> Result<MediaItem, anyhow::Error> {
        let metadata = fs::metadata(path)?;
        let file_name = path.file_name()
            .and_then(|n| n.to_str())
            .unwrap_or("unknown")
            .to_string();

        let file_size = metadata.len();
        let media_type = MediaType::from_extension(&file_name);
        let mime_type = mime_guess::from_path(path)
            .first_or_octet_stream()
            .to_string();

        let sha256 = if self.config.compute_hashes {
            let mut file = fs::File::open(path)?;
            let mut hasher = Sha256::new();
            std::io::copy(&mut file, &mut hasher)?;
            let hash = format!("{:x}", hasher.finalize());
            self.known_files.insert(path.to_path_buf(), hash.clone());
            Some(hash)
        } else {
            None
        };

        Ok(MediaItem {
            id: Uuid::new_v4().to_string(),
            path: path.to_path_buf(),
            file_name,
            file_size,
            media_type,
            mime_type,
            sha256,
            discovered_at: Utc::now().to_rfc3339(),
            metadata: None,
        })
    }

    /// Scan a single directory (non-recursive)
    pub fn scan_directory(&mut self, dir: &Path) -> ScanResult {
        let mut items = Vec::new();
        let mut errors = Vec::new();

        if !dir.exists() {
            return ScanResult {
                total_files: 0,
                new_files: 0,
                updated_files: 0,
                errors: vec![format!("Directory not found: {:?}", dir)],
                items: vec![],
            };
        }

        for entry in fs::read_dir(dir)? {
            let entry = entry?;
            let path = entry.path();
            if !path.is_file() {
                continue;
            }

            match self.process_file(&path) {
                Ok(item) => items.push(item),
                Err(e) => errors.push(format!("{:?}: {}", path, e)),
            }
        }

        ScanResult {
            total_files: items.len(),
            new_files: items.len(),
            updated_files: 0,
            errors,
            items,
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::fs;
    use tempfile::TempDir;

    #[test]
    fn test_scanner_detects_media_files() {
        let dir = TempDir::new().unwrap();
        let movie_path = dir.path().join("test_movie.mp4");
        let music_path = dir.path().join("test_song.mp3");
        let text_path = dir.path().join("notes.txt");

        fs::write(&movie_path, "fake movie data").unwrap();
        fs::write(&music_path, "fake music data").unwrap();
        fs::write(&text_path, "just text").unwrap();

        let config = ScannerConfig {
            media_dirs: vec![dir.path().to_path_buf()],
            extensions: vec!["mp4".into(), "mp3".into()],
            recursive: false,
            compute_hashes: false,
            emit_feed_events: false,
        };

        let mut scanner = MediaScanner::new(config);
        let result = scanner.scan();

        assert_eq!(result.total_files, 2);
        assert_eq!(result.new_files, 2);
        assert!(result.items.iter().any(|i| i.file_name == "test_movie.mp4"));
        assert!(result.items.iter().any(|i| i.file_name == "test_song.mp3"));
    }

    #[test]
    fn test_scanner_detects_new_files() {
        let dir = TempDir::new().unwrap();
        let path = dir.path().join("movie.mp4");
        fs::write(&path, "data").unwrap();

        let config = ScannerConfig {
            media_dirs: vec![dir.path().to_path_buf()],
            extensions: vec!["mp4".into()],
            recursive: false,
            compute_hashes: true,
            emit_feed_events: false,
        };

        let mut scanner = MediaScanner::new(config);
        let result1 = scanner.scan();
        assert_eq!(result1.new_files, 1);

        // Second scan should have no new files
        let result2 = scanner.scan();
        assert_eq!(result2.new_files, 0);
    }

    #[test]
    fn test_media_type_from_extension() {
        assert_eq!(MediaType::from_extension("movie.mp4"), MediaType::Movie);
        assert_eq!(MediaType::from_extension("song.mp3"), MediaType::Music);
        assert_eq!(MediaType::from_extension("show.ts"), MediaType::Recording);
        assert_eq!(MediaType::from_extension("notes.txt"), MediaType::Other);
    }
}
