//! Wyoming Protocol — Local Whisper STT integration
//!
//! Wyoming is an open protocol for speech-to-text and text-to-speech services.
//! This module provides a client for connecting to Wyoming-compatible servers
//! (e.g., wyoming-faster-whisper, wyoming-piper).

use crate::{VoiceCommand, VoiceResult, WyomingConfig};
use serde::{Deserialize, Serialize};
use std::time::Duration;

/// Wyoming protocol message types
#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(tag = "type")]
pub enum WyomingMessage {
    #[serde(rename = "audio-start")]
    AudioStart {
        rate: u32,
        width: u32,
        channels: u32,
    },
    #[serde(rename = "audio-chunk")]
    AudioChunk {
        data: Vec<u8>,
    },
    #[serde(rename = "audio-stop")]
    AudioStop,
    #[serde(rename = "transcript")]
    Transcript {
        text: String,
        #[serde(default)]
        confidence: f32,
    },
    #[serde(rename = "error")]
    Error {
        code: String,
        message: String,
    },
}

/// Wyoming protocol client for speech-to-text
pub struct WyomingClient {
    config: WyomingConfig,
    client: reqwest::Client,
}

impl WyomingClient {
    pub fn new(config: WyomingConfig) -> Self {
        let client = reqwest::Client::builder()
            .timeout(Duration::from_secs(config.timeout_secs))
            .build()
            .unwrap_or_default();

        Self { config, client }
    }

    /// Transcribe audio data to text using the Wyoming server
    pub async fn transcribe(&self, audio_data: &[u8]) -> Result<VoiceResult, String> {
        let start = std::time::Instant::now();

        // In production, this would:
        // 1. Connect to the Wyoming server via WebSocket or HTTP
        // 2. Send audio-start, audio-chunk, audio-stop messages
        // 3. Receive transcript response
        // 4. Parse the transcript into a VoiceCommand

        // For now, simulate a Wyoming protocol exchange
        let url = format!("{}/transcribe", self.config.server_url);

        let response = self.client
            .post(&url)
            .header("Content-Type", "audio/wav")
            .body(audio_data.to_vec())
            .send()
            .await
            .map_err(|e| format!("Wyoming request failed: {}", e))?;

        let result: serde_json::Value = response
            .json()
            .await
            .map_err(|e| format!("Failed to parse Wyoming response: {}", e))?;

        let transcript = result["text"].as_str()
            .unwrap_or("")
            .to_string();

        let confidence = result["confidence"].as_f64().unwrap_or(0.0) as f32;
        let duration = start.elapsed().as_millis() as u64;

        Ok(VoiceResult {
            success: !transcript.is_empty(),
            transcript: Some(transcript.clone()),
            command: self.parse_command(&transcript),
            confidence,
            duration_ms: duration,
            error: None,
        })
    }

    /// Check if the Wyoming server is available
    pub async fn health_check(&self) -> Result<bool, String> {
        let url = format!("{}/health", self.config.server_url);

        match self.client.get(&url).send().await {
            Ok(response) => Ok(response.status().is_success()),
            Err(_) => Ok(false),
        }
    }

    /// Parse a transcript into a structured voice command
    fn parse_command(&self, transcript: &str) -> Option<VoiceCommand> {
        let lower = transcript.to_lowercase();

        // Simple keyword-based intent parsing
        if lower.contains("play") || lower.contains("start") {
            Some(VoiceCommand {
                intent: crate::IntentType::PlayMedia,
                target: extract_target(transcript, &["play", "start"]),
                value: None,
                raw_text: transcript.to_string(),
            })
        } else if lower.contains("pause") || lower.contains("stop") {
            Some(VoiceCommand {
                intent: if lower.contains("pause") {
                    crate::IntentType::PauseMedia
                } else {
                    crate::IntentType::StopMedia
                },
                target: None,
                value: None,
                raw_text: transcript.to_string(),
            })
        } else if lower.contains("volume") {
            let intent = if lower.contains("up") {
                crate::IntentType::VolumeUp
            } else if lower.contains("down") {
                crate::IntentType::VolumeDown
            } else {
                crate::IntentType::SetVolume
            };
            Some(VoiceCommand {
                intent,
                target: None,
                value: extract_number(transcript).map(|n| serde_json::json!(n)),
                raw_text: transcript.to_string(),
            })
        } else if lower.contains("turn on") || lower.contains("switch on") {
            Some(VoiceCommand {
                intent: crate::IntentType::TurnOn,
                target: extract_target(transcript, &["turn on", "switch on"]),
                value: None,
                raw_text: transcript.to_string(),
            })
        } else if lower.contains("turn off") || lower.contains("switch off") {
            Some(VoiceCommand {
                intent: crate::IntentType::TurnOff,
                target: extract_target(transcript, &["turn off", "switch off"]),
                value: None,
                raw_text: transcript.to_string(),
            })
        } else if lower.contains("scene") || lower.contains("activate") {
            Some(VoiceCommand {
                intent: crate::IntentType::ActivateScene,
                target: extract_target(transcript, &["scene", "activate"]),
                value: None,
                raw_text: transcript.to_string(),
            })
        } else if lower.contains("search") || lower.contains("find") {
            Some(VoiceCommand {
                intent: crate::IntentType::SearchMedia,
                target: extract_target(transcript, &["search", "find"]),
                value: None,
                raw_text: transcript.to_string(),
            })
        } else if lower.contains("status") || lower.contains("what") {
            Some(VoiceCommand {
                intent: crate::IntentType::QueryStatus,
                target: None,
                value: None,
                raw_text: transcript.to_string(),
            })
        } else {
            None
        }
    }

    /// Get the Wyoming configuration
    pub fn config(&self) -> &WyomingConfig {
        &self.config
    }
}

/// Extract the target entity from a transcript after removing command words
fn extract_target(transcript: &str, remove_words: &[&str]) -> Option<String> {
    let mut result = transcript.to_string();
    for word in remove_words {
        result = result.replace(word, "");
    }
    let result = result.trim().to_string();
    if result.is_empty() { None } else { Some(result) }
}

/// Extract a number from a transcript
fn extract_number(transcript: &str) -> Option<u32> {
    transcript.split_whitespace()
        .find_map(|word| word.parse::<u32>().ok())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_parse_play_command() {
        let config = WyomingConfig::default();
        let client = WyomingClient::new(config);

        let cmd = client.parse_command("play some music").unwrap();
        assert_eq!(cmd.intent, crate::IntentType::PlayMedia);
        assert_eq!(cmd.target, Some("some music".into()));
    }

    #[test]
    fn test_parse_volume_command() {
        let config = WyomingConfig::default();
        let client = WyomingClient::new(config);

        let cmd = client.parse_command("volume up").unwrap();
        assert_eq!(cmd.intent, crate::IntentType::VolumeUp);

        let cmd = client.parse_command("volume down").unwrap();
        assert_eq!(cmd.intent, crate::IntentType::VolumeDown);

        let cmd = client.parse_command("set volume to 50").unwrap();
        assert_eq!(cmd.intent, crate::IntentType::SetVolume);
        assert_eq!(cmd.value, Some(serde_json::json!(50)));
    }

    #[test]
    fn test_parse_turn_on_off() {
        let config = WyomingConfig::default();
        let client = WyomingClient::new(config);

        let cmd = client.parse_command("turn on the living room light").unwrap();
        assert_eq!(cmd.intent, crate::IntentType::TurnOn);
        assert!(cmd.target.unwrap().contains("living room light"));

        let cmd = client.parse_command("turn off the kitchen light").unwrap();
        assert_eq!(cmd.intent, crate::IntentType::TurnOff);
    }

    #[test]
    fn test_parse_scene_command() {
        let config = WyomingConfig::default();
        let client = WyomingClient::new(config);

        let cmd = client.parse_command("activate movie night scene").unwrap();
        assert_eq!(cmd.intent, crate::IntentType::ActivateScene);
    }

    #[test]
    fn test_parse_search_command() {
        let config = WyomingConfig::default();
        let client = WyomingClient::new(config);

        let cmd = client.parse_command("search for interstellar").unwrap();
        assert_eq!(cmd.intent, crate::IntentType::SearchMedia);
    }

    #[test]
    fn test_parse_status_command() {
        let config = WyomingConfig::default();
        let client = WyomingClient::new(config);

        let cmd = client.parse_command("what is the status").unwrap();
        assert_eq!(cmd.intent, crate::IntentType::QueryStatus);
    }

    #[test]
    fn test_parse_unknown_command() {
        let config = WyomingConfig::default();
        let client = WyomingClient::new(config);

        let cmd = client.parse_command("hello world");
        assert!(cmd.is_none());
    }

    #[test]
    fn test_extract_number() {
        assert_eq!(extract_number("set volume to 50"), Some(50));
        assert_eq!(extract_number("no numbers here"), None);
        assert_eq!(extract_number("brightness 75 percent"), Some(75));
    }
}
