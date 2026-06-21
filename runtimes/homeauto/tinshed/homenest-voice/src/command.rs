//! Voice Command — Siri shortcut support and command dispatch

use crate::{IntentType, VoiceCommand, VoiceResult};
use serde::{Deserialize, Serialize};

/// A Siri shortcut definition
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SiriShortcut {
    pub id: String,
    pub name: String,
    pub phrase: String,
    pub intent: IntentType,
    pub target: Option<String>,
    pub value: Option<serde_json::Value>,
    pub enabled: bool,
}

/// Voice command dispatcher
pub struct CommandDispatcher {
    shortcuts: Vec<SiriShortcut>,
}

impl CommandDispatcher {
    pub fn new() -> Self {
        Self {
            shortcuts: Vec::new(),
        }
    }

    /// Register a Siri shortcut
    pub fn register_shortcut(&mut self, shortcut: SiriShortcut) {
        self.shortcuts.push(shortcut);
    }

    /// Dispatch a voice command to the appropriate handler
    pub fn dispatch(&self, command: &VoiceCommand) -> VoiceResult {
        match command.intent {
            IntentType::PlayMedia => {
                log::info!("Playing media: {:?}", command.target);
                VoiceResult {
                    success: true,
                    transcript: None,
                    command: Some(command.clone()),
                    confidence: 1.0,
                    duration_ms: 0,
                    error: None,
                }
            }
            IntentType::PauseMedia => {
                log::info!("Pausing media");
                VoiceResult {
                    success: true,
                    transcript: None,
                    command: Some(command.clone()),
                    confidence: 1.0,
                    duration_ms: 0,
                    error: None,
                }
            }
            IntentType::StopMedia => {
                log::info!("Stopping media");
                VoiceResult {
                    success: true,
                    transcript: None,
                    command: Some(command.clone()),
                    confidence: 1.0,
                    duration_ms: 0,
                    error: None,
                }
            }
            IntentType::TurnOn => {
                log::info!("Turning on: {:?}", command.target);
                VoiceResult {
                    success: true,
                    transcript: None,
                    command: Some(command.clone()),
                    confidence: 1.0,
                    duration_ms: 0,
                    error: None,
                }
            }
            IntentType::TurnOff => {
                log::info!("Turning off: {:?}", command.target);
                VoiceResult {
                    success: true,
                    transcript: None,
                    command: Some(command.clone()),
                    confidence: 1.0,
                    duration_ms: 0,
                    error: None,
                }
            }
            IntentType::ActivateScene => {
                log::info!("Activating scene: {:?}", command.target);
                VoiceResult {
                    success: true,
                    transcript: None,
                    command: Some(command.clone()),
                    confidence: 1.0,
                    duration_ms: 0,
                    error: None,
                }
            }
            IntentType::QueryStatus => {
                log::info!("Querying system status");
                VoiceResult {
                    success: true,
                    transcript: None,
                    command: Some(command.clone()),
                    confidence: 1.0,
                    duration_ms: 0,
                    error: None,
                }
            }
            IntentType::SearchMedia => {
                log::info!("Searching media: {:?}", command.target);
                VoiceResult {
                    success: true,
                    transcript: None,
                    command: Some(command.clone()),
                    confidence: 1.0,
                    duration_ms: 0,
                    error: None,
                }
            }
            _ => {
                VoiceResult {
                    success: false,
                    transcript: None,
                    command: Some(command.clone()),
                    confidence: 0.0,
                    duration_ms: 0,
                    error: Some(format!("Unhandled intent: {:?}", command.intent)),
                }
            }
        }
    }

    /// Find a shortcut by phrase
    pub fn find_shortcut(&self, phrase: &str) -> Option<&SiriShortcut> {
        let lower = phrase.to_lowercase();
        self.shortcuts.iter().find(|s| {
            s.enabled && lower.contains(&s.phrase.to_lowercase())
        })
    }

    /// Get all shortcuts
    pub fn get_shortcuts(&self) -> &[SiriShortcut] {
        &self.shortcuts
    }

    /// Enable or disable a shortcut
    pub fn set_shortcut_enabled(&mut self, shortcut_id: &str, enabled: bool) -> Result<(), String> {
        let shortcut = self.shortcuts.iter_mut()
            .find(|s| s.id == shortcut_id)
            .ok_or_else(|| format!("Shortcut not found: {}", shortcut_id))?;
        shortcut.enabled = enabled;
        Ok(())
    }

    /// Remove a shortcut
    pub fn remove_shortcut(&mut self, shortcut_id: &str) -> Result<(), String> {
        let idx = self.shortcuts.iter().position(|s| s.id == shortcut_id)
            .ok_or_else(|| format!("Shortcut not found: {}", shortcut_id))?;
        self.shortcuts.remove(idx);
        Ok(())
    }

    /// Get shortcut count
    pub fn shortcut_count(&self) -> usize {
        self.shortcuts.len()
    }
}

impl Default for CommandDispatcher {
    fn default() -> Self {
        Self::new()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_dispatch_play() {
        let dispatcher = CommandDispatcher::new();
        let cmd = VoiceCommand {
            intent: IntentType::PlayMedia,
            target: Some("some music".into()),
            value: None,
            raw_text: "play some music".into(),
        };

        let result = dispatcher.dispatch(&cmd);
        assert!(result.success);
    }

    #[test]
    fn test_register_shortcut() {
        let mut dispatcher = CommandDispatcher::new();
        dispatcher.register_shortcut(SiriShortcut {
            id: "sc1".into(),
            name: "Goodnight".into(),
            phrase: "goodnight".into(),
            intent: IntentType::ActivateScene,
            target: Some("goodnight_scene".into()),
            value: None,
            enabled: true,
        });

        assert_eq!(dispatcher.shortcut_count(), 1);
    }

    #[test]
    fn test_find_shortcut() {
        let mut dispatcher = CommandDispatcher::new();
        dispatcher.register_shortcut(SiriShortcut {
            id: "sc1".into(),
            name: "Movie Time".into(),
            phrase: "movie time".into(),
            intent: IntentType::ActivateScene,
            target: Some("movie_scene".into()),
            value: None,
            enabled: true,
        });

        let found = dispatcher.find_shortcut("it's movie time").unwrap();
        assert_eq!(found.name, "Movie Time");
    }

    #[test]
    fn test_disable_shortcut() {
        let mut dispatcher = CommandDispatcher::new();
        dispatcher.register_shortcut(SiriShortcut {
            id: "sc1".into(),
            name: "Test".into(),
            phrase: "test".into(),
            intent: IntentType::QueryStatus,
            target: None,
            value: None,
            enabled: true,
        });

        dispatcher.set_shortcut_enabled("sc1", false).unwrap();
        assert!(dispatcher.find_shortcut("test").is_none());
    }

    #[test]
    fn test_remove_shortcut() {
        let mut dispatcher = CommandDispatcher::new();
        dispatcher.register_shortcut(SiriShortcut {
            id: "sc1".into(),
            name: "Test".into(),
            phrase: "test".into(),
            intent: IntentType::QueryStatus,
            target: None,
            value: None,
            enabled: true,
        });

        dispatcher.remove_shortcut("sc1").unwrap();
        assert_eq!(dispatcher.shortcut_count(), 0);
    }
}
