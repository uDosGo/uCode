//! homenest-voice — Voice assistant integration
//!
//! Provides:
//! - `HomeKitBridge` — Apple HomeKit bridge configuration
//! - `WyomingClient` — Wyoming protocol for local Whisper STT
//! - `VoiceCommand` — Parsed voice command types
//! - `SiriShortcut` — Optional iOS shortcut support

pub mod homekit;
pub mod wyoming;
pub mod command;

use serde::{Deserialize, Serialize};

/// Voice assistant configuration
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct VoiceConfig {
    pub enabled: bool,
    pub homekit: Option<HomeKitConfig>,
    pub wyoming: Option<WyomingConfig>,
    pub siri_shortcuts: bool,
    pub wake_word: String,
    pub language: String,
}

impl Default for VoiceConfig {
    fn default() -> Self {
        Self {
            enabled: false,
            homekit: None,
            wyoming: None,
            siri_shortcuts: false,
            wake_word: "hey homenest".into(),
            language: "en-US".into(),
        }
    }
}

/// HomeKit bridge configuration
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct HomeKitConfig {
    pub enabled: bool,
    pub bridge_name: String,
    pub pin_code: String,
    pub setup_id: String,
    pub advertise_port: u16,
}

impl Default for HomeKitConfig {
    fn default() -> Self {
        Self {
            enabled: false,
            bridge_name: "HomeNest Bridge".into(),
            pin_code: "11122333".into(),
            setup_id: "HNST".into(),
            advertise_port: 8080,
        }
    }
}

/// Wyoming protocol configuration
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct WyomingConfig {
    pub enabled: bool,
    pub server_url: String,
    pub model: String,
    pub timeout_secs: u64,
}

impl Default for WyomingConfig {
    fn default() -> Self {
        Self {
            enabled: false,
            server_url: "http://localhost:10400".into(),
            model: "base".into(),
            timeout_secs: 30,
        }
    }
}

/// Result of voice processing
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct VoiceResult {
    pub success: bool,
    pub transcript: Option<String>,
    pub command: Option<VoiceCommand>,
    pub confidence: f32,
    pub duration_ms: u64,
    pub error: Option<String>,
}

/// Parsed voice command
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct VoiceCommand {
    pub intent: IntentType,
    pub target: Option<String>,
    pub value: Option<serde_json::Value>,
    pub raw_text: String,
}

/// Supported voice intents
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub enum IntentType {
    PlayMedia,
    PauseMedia,
    StopMedia,
    NextTrack,
    PreviousTrack,
    VolumeUp,
    VolumeDown,
    SetVolume,
    TurnOn,
    TurnOff,
    SetBrightness,
    SetTemperature,
    RecordChannel,
    SwitchChannel,
    ActivateScene,
    DeactivateScene,
    QueryStatus,
    SearchMedia,
    Custom(String),
}

impl std::fmt::Display for IntentType {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            IntentType::PlayMedia => write!(f, "play_media"),
            IntentType::PauseMedia => write!(f, "pause_media"),
            IntentType::StopMedia => write!(f, "stop_media"),
            IntentType::NextTrack => write!(f, "next_track"),
            IntentType::PreviousTrack => write!(f, "previous_track"),
            IntentType::VolumeUp => write!(f, "volume_up"),
            IntentType::VolumeDown => write!(f, "volume_down"),
            IntentType::SetVolume => write!(f, "set_volume"),
            IntentType::TurnOn => write!(f, "turn_on"),
            IntentType::TurnOff => write!(f, "turn_off"),
            IntentType::SetBrightness => write!(f, "set_brightness"),
            IntentType::SetTemperature => write!(f, "set_temperature"),
            IntentType::RecordChannel => write!(f, "record_channel"),
            IntentType::SwitchChannel => write!(f, "switch_channel"),
            IntentType::ActivateScene => write!(f, "activate_scene"),
            IntentType::DeactivateScene => write!(f, "deactivate_scene"),
            IntentType::QueryStatus => write!(f, "query_status"),
            IntentType::SearchMedia => write!(f, "search_media"),
            IntentType::Custom(ref name) => write!(f, "custom_{}", name),
        }
    }
}
