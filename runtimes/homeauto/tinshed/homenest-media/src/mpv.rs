//! mpv integration — MCP tool for mpv playback control
//!
//! Communicates with mpv via its JSON IPC protocol over a Unix socket.
//! mpv must be started with `--input-ipc-server=/tmp/mpv.sock`

use crate::{PlaybackState, PlaybackStatus};
use serde::{Deserialize, Serialize};
use std::io::{BufRead, BufReader, Write};
use std::os::unix::net::UnixStream;
use std::path::Path;
use std::sync::Mutex;
use std::time::Duration;

/// mpv IPC command
#[derive(Debug, Serialize)]
struct MpvCommand {
    command: Vec<serde_json::Value>,
    request_id: u32,
}

/// mpv IPC response
#[derive(Debug, Deserialize)]
struct MpvResponse {
    #[allow(dead_code)]
    request_id: u32,
    error: String,
    #[serde(default)]
    data: Option<serde_json::Value>,
}

/// Controller for mpv media playback via JSON IPC
pub struct MpvController {
    socket_path: String,
    request_id: Mutex<u32>,
    status: Mutex<PlaybackStatus>,
}

impl MpvController {
    /// Create a new mpv controller
    pub fn new(socket_path: Option<&str>) -> Self {
        Self {
            socket_path: socket_path.unwrap_or("/tmp/mpv.sock").to_string(),
            request_id: Mutex::new(0),
            status: Mutex::new(PlaybackStatus::default()),
        }
    }

    /// Send a command to mpv via IPC
    fn send_command(&self, args: Vec<serde_json::Value>) -> Result<Option<serde_json::Value>, String> {
        let mut id = self.request_id.lock().map_err(|e| e.to_string())?;
        *id += 1;
        let req_id = *id;

        let cmd = MpvCommand {
            command: args,
            request_id: req_id,
        };

        let json = serde_json::to_string(&cmd).map_err(|e| e.to_string())?;

        let mut stream = UnixStream::connect(&self.socket_path)
            .map_err(|e| format!("Cannot connect to mpv at {}: {}", self.socket_path, e))?;

        // Set timeout to avoid hanging
        stream.set_read_timeout(Some(Duration::from_secs(5)))
            .map_err(|e| e.to_string())?;
        stream.set_write_timeout(Some(Duration::from_secs(5)))
            .map_err(|e| e.to_string())?;

        stream.write_all(json.as_bytes())
            .map_err(|e| format!("Failed to write to mpv: {}", e))?;
        stream.write_all(b"\n")
            .map_err(|e| format!("Failed to write newline: {}", e))?;

        let mut reader = BufReader::new(&stream);
        let mut response = String::new();
        reader.read_line(&mut response)
            .map_err(|e| format!("Failed to read from mpv: {}", e))?;

        let resp: MpvResponse = serde_json::from_str(&response)
            .map_err(|e| format!("Failed to parse mpv response: {} (raw: {})", e, response))?;

        if resp.error != "success" {
            return Err(format!("mpv error: {}", resp.error));
        }

        Ok(resp.data)
    }

    /// Load and play a media file
    pub fn play(&self, path: &Path) -> Result<(), String> {
        let path_str = path.to_string_lossy().to_string();
        self.send_command(vec![
            serde_json::json!("loadfile"),
            serde_json::json!(path_str),
            serde_json::json!("replace"),
        ])?;

        let mut status = self.status.lock().map_err(|e| e.to_string())?;
        status.state = PlaybackState::Playing;
        Ok(())
    }

    /// Pause playback
    pub fn pause(&self) -> Result<(), String> {
        self.send_command(vec![
            serde_json::json!("set_property"),
            serde_json::json!("pause"),
            serde_json::json!(true),
        ])?;

        let mut status = self.status.lock().map_err(|e| e.to_string())?;
        status.state = PlaybackState::Paused;
        Ok(())
    }

    /// Resume playback
    pub fn resume(&self) -> Result<(), String> {
        self.send_command(vec![
            serde_json::json!("set_property"),
            serde_json::json!("pause"),
            serde_json::json!(false),
        ])?;

        let mut status = self.status.lock().map_err(|e| e.to_string())?;
        status.state = PlaybackState::Playing;
        Ok(())
    }

    /// Stop playback
    pub fn stop(&self) -> Result<(), String> {
        self.send_command(vec![
            serde_json::json!("stop"),
        ])?;

        let mut status = self.status.lock().map_err(|e| e.to_string())?;
        status.state = PlaybackState::Stopped;
        status.position_secs = 0.0;
        status.duration_secs = 0.0;
        Ok(())
    }

    /// Seek to a position (in seconds)
    pub fn seek(&self, seconds: f64) -> Result<(), String> {
        self.send_command(vec![
            serde_json::json!("seek"),
            serde_json::json!(seconds),
            serde_json::json!("absolute"),
        ])?;

        let mut status = self.status.lock().map_err(|e| e.to_string())?;
        status.position_secs = seconds;
        Ok(())
    }

    /// Set volume (0-100)
    pub fn set_volume(&self, volume: u8) -> Result<(), String> {
        let vol = volume.min(100).max(0);
        self.send_command(vec![
            serde_json::json!("set_property"),
            serde_json::json!("volume"),
            serde_json::json!(vol),
        ])?;

        let mut status = self.status.lock().map_err(|e| e.to_string())?;
        status.volume = vol;
        Ok(())
    }

    /// Get current playback status from mpv
    pub fn get_status(&self) -> Result<PlaybackStatus, String> {
        let position = self.send_command(vec![
            serde_json::json!("get_property"),
            serde_json::json!("time-pos"),
        ])?;

        let duration = self.send_command(vec![
            serde_json::json!("get_property"),
            serde_json::json!("duration"),
        ])?;

        let paused = self.send_command(vec![
            serde_json::json!("get_property"),
            serde_json::json!("pause"),
        ])?;

        let volume = self.send_command(vec![
            serde_json::json!("get_property"),
            serde_json::json!("volume"),
        ])?;

        let mut status = self.status.lock().map_err(|e| e.to_string())?;

        status.position_secs = position.and_then(|v| v.as_f64()).unwrap_or(0.0);
        status.duration_secs = duration.and_then(|v| v.as_f64()).unwrap_or(0.0);
        status.state = if paused.and_then(|v| v.as_bool()).unwrap_or(true) {
            PlaybackState::Paused
        } else {
            PlaybackState::Playing
        };
        status.volume = volume.and_then(|v| v.as_u64()).map(|v| v as u8).unwrap_or(65);

        Ok(status.clone())
    }

    /// Check if mpv is running and IPC socket is available
    pub fn is_available(&self) -> bool {
        std::path::Path::new(&self.socket_path).exists()
    }

    /// Get the current cached status (no IPC call)
    pub fn cached_status(&self) -> PlaybackStatus {
        self.status.lock().map(|s| s.clone()).unwrap_or_default()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_mpv_controller_creation() {
        let controller = MpvController::new(Some("/tmp/test-mpv.sock"));
        assert_eq!(controller.socket_path, "/tmp/test-mpv.sock");
        assert!(!controller.is_available());
    }

    #[test]
    fn test_volume_clamping() {
        let controller = MpvController::new(None);
        // Just test that the method doesn't panic with edge values
        let _ = controller.set_volume(150); // Should clamp to 100
        let _ = controller.set_volume(0);
        let _ = controller.set_volume(50);
    }
}
