//! HomeNest MCP Server Library
//!
//! Provides MCP tools for HomeNest operations:
//! - Media playback (play, pause, stop, seek, queue)
//! - Automation (trigger scenes, run OBF sheets)
//! - TV/DVR (EPG, recordings, live TV)
//! - System status (services, health)

use serde::{Deserialize, Serialize};
use std::path::PathBuf;
use std::sync::Arc;
use tokio::sync::Mutex;
use log::{info, error, debug};

pub mod media;
pub mod automation;
pub mod tv;
pub mod system;

/// HomeNest MCP request types
#[derive(Debug, Serialize, Deserialize)]
pub enum HomenestRequest {
    // Media
    MediaPlay { media_id: String, target: Option<String> },
    MediaPause,
    MediaResume,
    MediaStop,
    MediaSeek { position: f64 },
    MediaQueue { media_id: String },
    MediaNowPlaying,
    MediaList { path: Option<String> },

    // Automation
    AutomationTrigger { scene: String },
    AutomationRunSheet { sheet_path: String },
    AutomationStatus,
    AutomationList,

    // TV/DVR
    TvEpg { channel: Option<String> },
    TvRecord { channel: String, duration: u64 },
    TvRecordings,
    TvLive { channel: String },

    // System
    SystemStatus,
    SystemHealth,
    SystemServices,
    Ping,
    Shutdown,
}

/// HomeNest MCP response types
#[derive(Debug, Serialize, Deserialize)]
pub enum HomenestResponse {
    Success { data: serde_json::Value },
    Error { message: String },
    MediaStatus {
        state: String,
        media_id: Option<String>,
        position: f64,
        duration: f64,
    },
    MediaList {
        items: Vec<MediaItem>,
    },
    AutomationList {
        scenes: Vec<String>,
        sheets: Vec<String>,
    },
    AutomationStatus {
        active: Vec<String>,
        recent: Vec<String>,
    },
    EpgData {
        channels: Vec<EpgChannel>,
    },
    Recordings {
        items: Vec<Recording>,
    },
    SystemInfo {
        version: String,
        services: Vec<ServiceStatus>,
        uptime: String,
    },
    Pong,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct MediaItem {
    pub id: String,
    pub title: String,
    pub media_type: String,
    pub duration: f64,
    pub path: String,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct EpgChannel {
    pub id: String,
    pub name: String,
    pub icon: Option<String>,
    pub now: Option<EpgProgram>,
    pub next: Option<EpgProgram>,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct EpgProgram {
    pub title: String,
    pub start: String,
    pub end: String,
    pub description: Option<String>,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct Recording {
    pub id: String,
    pub title: String,
    pub channel: String,
    pub start: String,
    pub duration: u64,
    pub status: String,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct ServiceStatus {
    pub name: String,
    pub status: String,
    pub uptime: Option<String>,
}

/// HomeNest MCP Server
pub struct HomenestMcpServer {
    socket_path: PathBuf,
    media_dir: PathBuf,
    running: Arc<Mutex<bool>>,
}

impl HomenestMcpServer {
    pub fn new(media_dir: &str) -> Self {
        let data_home = std::env::var("XDG_DATA_HOME").unwrap_or_else(|_| {
            let home = std::env::var("HOME").unwrap_or_else(|_| ".".to_string());
            format!("{home}/.local/share")
        });
        let socket_path = PathBuf::from(&data_home).join("udos/mcp/homenest.sock");

        HomenestMcpServer {
            socket_path,
            media_dir: PathBuf::from(media_dir),
            running: Arc::new(Mutex::new(false)),
        }
    }

    pub async fn start(&mut self) -> anyhow::Result<()> {
        use std::fs;
        use std::os::unix::net::UnixListener;
        use std::thread;

        // Clean up existing socket
        if self.socket_path.exists() {
            fs::remove_file(&self.socket_path)?;
        }

        // Create parent directory
        if let Some(parent) = self.socket_path.parent() {
            fs::create_dir_all(parent)?;
        }

        let listener = UnixListener::bind(&self.socket_path)?;

        // Set restrictive permissions
        #[cfg(unix)]
        {
            use std::os::unix::fs::PermissionsExt;
            if let Ok(metadata) = fs::metadata(&self.socket_path) {
                let mut permissions = metadata.permissions();
                permissions.set_mode(0o600);
                fs::set_permissions(&self.socket_path, permissions)?;
            }
        }

        *self.running.lock().await = true;
        info!("HomeNest MCP server started on {}", self.socket_path.display());

        let running = self.running.clone();
        let media_dir = self.media_dir.clone();

        thread::spawn(move || {
            for stream in listener.incoming() {
                if !*running.blocking_lock() {
                    break;
                }

                match stream {
                    Ok(stream) => {
                        let running = running.clone();
                        let media_dir = media_dir.clone();

                        thread::spawn(move || {
                            if let Err(e) = Self::handle_connection(stream, media_dir, running) {
                                error!("Connection error: {}", e);
                            }
                        });
                    }
                    Err(e) => {
                        error!("Accept error: {}", e);
                        break;
                    }
                }
            }
        });

        Ok(())
    }

    pub async fn stop(&mut self) {
        *self.running.lock().await = false;
        std::fs::remove_file(&self.socket_path).ok();
        info!("HomeNest MCP server stopped");
    }

    fn handle_connection(
        stream: std::os::unix::net::UnixStream,
        media_dir: PathBuf,
        running: Arc<Mutex<bool>>,
    ) -> anyhow::Result<()> {
        use std::io::{BufRead, BufReader, BufWriter, Write};

        let mut reader = BufReader::new(stream.try_clone()?);
        let mut writer = BufWriter::new(stream);

        let mut buffer = String::new();
        reader.read_line(&mut buffer)?;

        if buffer.trim().is_empty() {
            return Ok(());
        }

        debug!("Received HomeNest request: {}", buffer.trim());

        let request: HomenestRequest = match serde_json::from_str(&buffer.trim()) {
            Ok(req) => req,
            Err(e) => {
                error!("Failed to parse request: {}", e);
                let response = HomenestResponse::Error {
                    message: format!("Invalid request: {}", e),
                };
                let response_str = serde_json::to_string(&response).unwrap() + "\n";
                writer.write_all(response_str.as_bytes())?;
                writer.flush()?;
                return Ok(());
            }
        };

        let response = match request {
            HomenestRequest::MediaPlay { media_id, target } => {
                media::handle_play(&media_id, target.as_deref(), &media_dir)
            }
            HomenestRequest::MediaPause => media::handle_pause(),
            HomenestRequest::MediaResume => media::handle_resume(),
            HomenestRequest::MediaStop => media::handle_stop(),
            HomenestRequest::MediaSeek { position } => media::handle_seek(position),
            HomenestRequest::MediaQueue { media_id } => media::handle_queue(&media_id),
            HomenestRequest::MediaNowPlaying => media::handle_now_playing(),
            HomenestRequest::MediaList { path } => media::handle_list(path.as_deref(), &media_dir),
            HomenestRequest::AutomationTrigger { scene } => {
                automation::handle_trigger(&scene)
            }
            HomenestRequest::AutomationRunSheet { sheet_path } => {
                automation::handle_run_sheet(&sheet_path)
            }
            HomenestRequest::AutomationStatus => automation::handle_status(),
            HomenestRequest::AutomationList => automation::handle_list(),
            HomenestRequest::TvEpg { channel } => tv::handle_epg(channel.as_deref()),
            HomenestRequest::TvRecord { channel, duration } => {
                tv::handle_record(&channel, duration)
            }
            HomenestRequest::TvRecordings => tv::handle_recordings(),
            HomenestRequest::TvLive { channel } => tv::handle_live(&channel),
            HomenestRequest::SystemStatus => system::handle_status(),
            HomenestRequest::SystemHealth => system::handle_health(),
            HomenestRequest::SystemServices => system::handle_services(),
            HomenestRequest::Ping => HomenestResponse::Pong,
            HomenestRequest::Shutdown => {
                *running.blocking_lock() = false;
                HomenestResponse::Success {
                    data: serde_json::json!({"message": "shutting down"}),
                }
            }
        };

        let response_str = serde_json::to_string(&response).unwrap() + "\n";
        writer.write_all(response_str.as_bytes())?;
        writer.flush()?;

        Ok(())
    }
}
