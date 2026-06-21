//! TV/DVR handlers for HomeNest MCP
//!
//! Manages EPG data, recordings, and live TV channels.

use crate::{HomenestResponse, EpgChannel, EpgProgram, Recording};
use log::{info, warn};
use std::collections::HashMap;
use std::sync::Mutex;

lazy_static::lazy_static! {
    static ref TV_STATE: Mutex<TvState> = Mutex::new(TvState::default());
}

struct TvState {
    channels: HashMap<String, ChannelDef>,
    recordings: Vec<Recording>,
    live_channel: Option<String>,
}

struct ChannelDef {
    id: String,
    name: String,
    icon: Option<String>,
    programs: Vec<EpgProgram>,
}

impl Default for TvState {
    fn default() -> Self {
        let mut channels = HashMap::new();

        // Simulated EPG data
        channels.insert("abc".to_string(), ChannelDef {
            id: "abc".to_string(),
            name: "ABC".to_string(),
            icon: Some("abc.png".to_string()),
            programs: vec![
                EpgProgram {
                    title: "ABC News".to_string(),
                    start: "2026-05-17T18:00:00".to_string(),
                    end: "2026-05-17T19:00:00".to_string(),
                    description: Some("National news coverage".to_string()),
                },
                EpgProgram {
                    title: "The Weekly".to_string(),
                    start: "2026-05-17T19:00:00".to_string(),
                    end: "2026-05-17T20:00:00".to_string(),
                    description: Some("Current affairs program".to_string()),
                },
            ],
        });

        channels.insert("sbs".to_string(), ChannelDef {
            id: "sbs".to_string(),
            name: "SBS".to_string(),
            icon: Some("sbs.png".to_string()),
            programs: vec![
                EpgProgram {
                    title: "SBS World News".to_string(),
                    start: "2026-05-17T18:30:00".to_string(),
                    end: "2026-05-17T19:30:00".to_string(),
                    description: Some("International news".to_string()),
                },
                EpgProgram {
                    title: "Documentary".to_string(),
                    start: "2026-05-17T19:30:00".to_string(),
                    end: "2026-05-17T20:30:00".to_string(),
                    description: Some("Featured documentary".to_string()),
                },
            ],
        });

        channels.insert("seven".to_string(), ChannelDef {
            id: "seven".to_string(),
            name: "Channel 7".to_string(),
            icon: Some("seven.png".to_string()),
            programs: vec![
                EpgProgram {
                    title: "Seven News".to_string(),
                    start: "2026-05-17T18:00:00".to_string(),
                    end: "2026-05-17T19:00:00".to_string(),
                    description: Some("Local and national news".to_string()),
                },
                EpgProgram {
                    title: "Better Homes and Gardens".to_string(),
                    start: "2026-05-17T19:00:00".to_string(),
                    end: "2026-05-17T20:00:00".to_string(),
                    description: Some("Lifestyle and home improvement".to_string()),
                },
            ],
        });

        TvState {
            channels,
            recordings: vec![
                Recording {
                    id: "rec-001".to_string(),
                    title: "ABC News - Evening".to_string(),
                    channel: "abc".to_string(),
                    start: "2026-05-16T18:00:00".to_string(),
                    duration: 3600,
                    status: "completed".to_string(),
                },
                Recording {
                    id: "rec-002".to_string(),
                    title: "SBS Documentary - Planet Earth".to_string(),
                    channel: "sbs".to_string(),
                    start: "2026-05-16T20:00:00".to_string(),
                    duration: 5400,
                    status: "completed".to_string(),
                },
            ],
            live_channel: None,
        }
    }
}

pub fn handle_epg(channel: Option<&str>) -> HomenestResponse {
    let state = TV_STATE.lock().unwrap();

    let channels: Vec<EpgChannel> = match channel {
        Some(ch) => {
            // Return single channel
            match state.channels.get(ch) {
                Some(def) => {
                    let now = def.programs.first().cloned();
                    let next = def.programs.get(1).cloned();
                    vec![EpgChannel {
                        id: def.id.clone(),
                        name: def.name.clone(),
                        icon: def.icon.clone(),
                        now,
                        next,
                    }]
                }
                None => return HomenestResponse::Error {
                    message: format!("Channel not found: {}", ch),
                },
            }
        }
        None => {
            // Return all channels
            state.channels.values().map(|def| {
                let now = def.programs.first().cloned();
                let next = def.programs.get(1).cloned();
                EpgChannel {
                    id: def.id.clone(),
                    name: def.name.clone(),
                    icon: def.icon.clone(),
                    now,
                    next,
                }
            }).collect()
        }
    };

    HomenestResponse::EpgData { channels }
}

pub fn handle_record(channel: &str, duration: u64) -> HomenestResponse {
    info!("Recording channel: {} for {}s", channel, duration);

    let mut state = TV_STATE.lock().unwrap();

    if !state.channels.contains_key(channel) {
        return HomenestResponse::Error {
            message: format!("Channel not found: {}", channel),
        };
    }

    let recording = Recording {
        id: format!("rec-{:04}", state.recordings.len() + 1),
        title: format!("Recording - {}", channel),
        channel: channel.to_string(),
        start: chrono::Utc::now().to_rfc3339(),
        duration,
        status: "scheduled".to_string(),
    };

    state.recordings.push(recording.clone());

    HomenestResponse::Success {
        data: serde_json::json!({
            "recording_id": recording.id,
            "channel": channel,
            "duration": duration,
            "status": "scheduled",
        }),
    }
}

pub fn handle_recordings() -> HomenestResponse {
    let state = TV_STATE.lock().unwrap();
    HomenestResponse::Recordings {
        items: state.recordings.clone(),
    }
}

pub fn handle_live(channel: &str) -> HomenestResponse {
    info!("Tuning to live channel: {}", channel);

    let mut state = TV_STATE.lock().unwrap();

    if !state.channels.contains_key(channel) {
        return HomenestResponse::Error {
            message: format!("Channel not found: {}", channel),
        };
    }

    state.live_channel = Some(channel.to_string());

    // TODO: Launch mpv with TV stream URL
    HomenestResponse::Success {
        data: serde_json::json!({
            "channel": channel,
            "status": "tuned",
            "stream": format!("tv://{}", channel),
        }),
    }
}
