//! Media playback handlers for HomeNest MCP
//!
//! Manages media playback via mpv, media scanning, and queue management.

use crate::{HomenestResponse, MediaItem};
use log::{info, warn};
use std::path::Path;
use std::process::Command;
use std::sync::Mutex;
use std::collections::VecDeque;

lazy_static::lazy_static! {
    static ref PLAYBACK_STATE: Mutex<PlaybackState> = Mutex::new(PlaybackState::default());
}

struct PlaybackState {
    current_media: Option<String>,
    position: f64,
    duration: f64,
    is_playing: bool,
    queue: VecDeque<String>,
    mpv_pid: Option<u32>,
}

impl Default for PlaybackState {
    fn default() -> Self {
        PlaybackState {
            current_media: None,
            position: 0.0,
            duration: 0.0,
            is_playing: false,
            queue: VecDeque::new(),
            mpv_pid: None,
        }
    }
}

pub fn handle_play(media_id: &str, target: Option<&str>, media_dir: &Path) -> HomenestResponse {
    info!("Media play: {} (target: {:?})", media_id, target);

    // Resolve media path
    let media_path = resolve_media_path(media_id, media_dir);
    if !media_path.exists() {
        return HomenestResponse::Error {
            message: format!("Media not found: {}", media_id),
        };
    }

    // Launch mpv
    match Command::new("mpv")
        .arg(&media_path)
        .arg("--no-terminal")
        .arg("--keep-open=yes")
        .spawn()
    {
        Ok(child) => {
            let mut state = PLAYBACK_STATE.lock().unwrap();
            state.current_media = Some(media_id.to_string());
            state.is_playing = true;
            state.mpv_pid = Some(child.id());

            HomenestResponse::Success {
                data: serde_json::json!({
                    "message": format!("Playing: {}", media_id),
                    "pid": child.id(),
                    "path": media_path.to_string_lossy(),
                }),
            }
        }
        Err(e) => HomenestResponse::Error {
            message: format!("Failed to launch mpv: {}", e),
        },
    }
}

pub fn handle_pause() -> HomenestResponse {
    let mut state = PLAYBACK_STATE.lock().unwrap();
    if let Some(pid) = state.mpv_pid {
        // Send pause command to mpv via IPC
        let _ = Command::new("kill")
            .arg("-STOP")
            .arg(pid.to_string())
            .output();
        state.is_playing = false;
        HomenestResponse::Success {
            data: serde_json::json!({"message": "Paused"}),
        }
    } else {
        HomenestResponse::Error {
            message: "No media playing".to_string(),
        }
    }
}

pub fn handle_resume() -> HomenestResponse {
    let mut state = PLAYBACK_STATE.lock().unwrap();
    if let Some(pid) = state.mpv_pid {
        let _ = Command::new("kill")
            .arg("-CONT")
            .arg(pid.to_string())
            .output();
        state.is_playing = true;
        HomenestResponse::Success {
            data: serde_json::json!({"message": "Resumed"}),
        }
    } else {
        HomenestResponse::Error {
            message: "No media playing".to_string(),
        }
    }
}

pub fn handle_stop() -> HomenestResponse {
    let mut state = PLAYBACK_STATE.lock().unwrap();
    if let Some(pid) = state.mpv_pid.take() {
        let _ = Command::new("kill")
            .arg(pid.to_string())
            .output();
        state.current_media = None;
        state.is_playing = false;
        state.position = 0.0;
        HomenestResponse::Success {
            data: serde_json::json!({"message": "Stopped"}),
        }
    } else {
        HomenestResponse::Error {
            message: "No media playing".to_string(),
        }
    }
}

pub fn handle_seek(position: f64) -> HomenestResponse {
    let state = PLAYBACK_STATE.lock().unwrap();
    if state.mpv_pid.is_some() {
        // TODO: Implement mpv IPC seek
        HomenestResponse::Success {
            data: serde_json::json!({"message": format!("Seek to {}", position)}),
        }
    } else {
        HomenestResponse::Error {
            message: "No media playing".to_string(),
        }
    }
}

pub fn handle_queue(media_id: &str) -> HomenestResponse {
    let mut state = PLAYBACK_STATE.lock().unwrap();
    state.queue.push_back(media_id.to_string());
    HomenestResponse::Success {
        data: serde_json::json!({
            "message": format!("Queued: {}", media_id),
            "queue_length": state.queue.len(),
        }),
    }
}

pub fn handle_now_playing() -> HomenestResponse {
    let state = PLAYBACK_STATE.lock().unwrap();
    HomenestResponse::MediaStatus {
        state: if state.is_playing { "playing" } else { "paused" }.to_string(),
        media_id: state.current_media.clone(),
        position: state.position,
        duration: state.duration,
    }
}

pub fn handle_list(path: Option<&str>, media_dir: &Path) -> HomenestResponse {
    let scan_path = match path {
        Some(p) => media_dir.join(p),
        None => media_dir.to_path_buf(),
    };

    if !scan_path.is_dir() {
        return HomenestResponse::Error {
            message: format!("Directory not found: {}", scan_path.display()),
        };
    }

    let mut items = Vec::new();
    if let Ok(entries) = std::fs::read_dir(&scan_path) {
        for entry in entries.flatten() {
            let path = entry.path();
            let metadata = match entry.metadata() {
                Ok(m) => m,
                Err(_) => continue,
            };

            if metadata.is_file() {
                let ext = path.extension()
                    .and_then(|e| e.to_str())
                    .unwrap_or("")
                    .to_lowercase();

                let media_type = match ext.as_str() {
                    "mp4" | "mkv" | "avi" | "mov" => "video",
                    "mp3" | "flac" | "wav" | "aac" => "audio",
                    "jpg" | "jpeg" | "png" | "gif" => "image",
                    _ => "unknown",
                };

                items.push(MediaItem {
                    id: entry.file_name().to_string_lossy().into_owned(),
                    title: path.file_stem()
                        .and_then(|s| s.to_str())
                        .unwrap_or("")
                        .to_string(),
                    media_type: media_type.to_string(),
                    duration: 0.0, // TODO: Probe media duration
                    path: path.to_string_lossy().into_owned(),
                });
            }
        }
    }

    HomenestResponse::MediaList { items }
}

fn resolve_media_path(media_id: &str, media_dir: &Path) -> std::path::PathBuf {
    let path = Path::new(media_id);
    if path.is_absolute() {
        path.to_path_buf()
    } else {
        media_dir.join(media_id)
    }
}
