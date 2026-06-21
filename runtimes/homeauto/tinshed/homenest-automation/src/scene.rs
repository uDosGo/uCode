//! Scene Manager — Scene definitions, triggers, and execution

use crate::{ActionType, Scene, SceneAction, SceneResult, SceneTrigger, TriggerType};
use chrono::Utc;
use std::collections::HashMap;
use uuid::Uuid;

/// Scene manager for creating and executing automation scenes
pub struct SceneManager {
    scenes: HashMap<String, Scene>,
}

impl SceneManager {
    pub fn new() -> Self {
        Self {
            scenes: HashMap::new(),
        }
    }

    /// Create a new scene
    pub fn create_scene(&mut self, name: &str, description: Option<&str>, icon: Option<&str>) -> Scene {
        let now = Utc::now().to_rfc3339();
        let scene = Scene {
            id: Uuid::new_v4().to_string(),
            name: name.to_string(),
            description: description.map(|s| s.to_string()),
            icon: icon.map(|s| s.to_string()),
            actions: Vec::new(),
            triggers: Vec::new(),
            is_active: true,
            created_at: now.clone(),
            updated_at: now,
        };

        let id = scene.id.clone();
        self.scenes.insert(id.clone(), scene.clone());
        scene
    }

    /// Add an action to a scene
    pub fn add_action(&mut self, scene_id: &str, action: SceneAction) -> Result<(), String> {
        let scene = self.scenes.get_mut(scene_id)
            .ok_or_else(|| format!("Scene not found: {}", scene_id))?;
        scene.actions.push(action);
        scene.updated_at = Utc::now().to_rfc3339();
        Ok(())
    }

    /// Add a trigger to a scene
    pub fn add_trigger(&mut self, scene_id: &str, trigger: SceneTrigger) -> Result<(), String> {
        let scene = self.scenes.get_mut(scene_id)
            .ok_or_else(|| format!("Scene not found: {}", scene_id))?;
        scene.triggers.push(trigger);
        scene.updated_at = Utc::now().to_rfc3339();
        Ok(())
    }

    /// Execute a scene by ID
    pub fn execute_scene(&self, scene_id: &str) -> SceneResult {
        let start = std::time::Instant::now();

        let scene = match self.scenes.get(scene_id) {
            Some(s) => s,
            None => {
                return SceneResult {
                    scene_id: scene_id.to_string(),
                    success: false,
                    actions_executed: 0,
                    actions_failed: 0,
                    errors: vec!["Scene not found".into()],
                    duration_ms: 0,
                };
            }
        };

        let mut executed = 0;
        let mut failed = 0;
        let mut errors = Vec::new();

        for action in &scene.actions {
            match execute_action(action) {
                Ok(()) => executed += 1,
                Err(e) => {
                    failed += 1;
                    errors.push(format!("Action {:?} on {}: {}", action.action_type, action.target, e));
                }
            }
        }

        let duration = start.elapsed().as_millis() as u64;

        SceneResult {
            scene_id: scene_id.to_string(),
            success: failed == 0,
            actions_executed: executed,
            actions_failed: failed,
            errors,
            duration_ms: duration,
        }
    }

    /// Get a scene by ID
    pub fn get_scene(&self, scene_id: &str) -> Option<&Scene> {
        self.scenes.get(scene_id)
    }

    /// Get all scenes
    pub fn get_all_scenes(&self) -> Vec<&Scene> {
        self.scenes.values().collect()
    }

    /// Get scenes by trigger type
    pub fn get_scenes_by_trigger(&self, trigger_type: TriggerType) -> Vec<&Scene> {
        self.scenes.values()
            .filter(|s| s.triggers.iter().any(|t| t.trigger_type == trigger_type))
            .collect()
    }

    /// Delete a scene
    pub fn delete_scene(&mut self, scene_id: &str) -> Result<(), String> {
        self.scenes.remove(scene_id)
            .ok_or_else(|| format!("Scene not found: {}", scene_id))?;
        Ok(())
    }

    /// Toggle scene active state
    pub fn toggle_scene(&mut self, scene_id: &str) -> Result<bool, String> {
        let scene = self.scenes.get_mut(scene_id)
            .ok_or_else(|| format!("Scene not found: {}", scene_id))?;
        scene.is_active = !scene.is_active;
        scene.updated_at = Utc::now().to_rfc3339();
        Ok(scene.is_active)
    }

    /// Get scene count
    pub fn scene_count(&self) -> usize {
        self.scenes.len()
    }
}

impl Default for SceneManager {
    fn default() -> Self {
        Self::new()
    }
}

/// Execute a single scene action
fn execute_action(action: &SceneAction) -> Result<(), String> {
    // In production, this would dispatch to the appropriate handler
    // For now, validate the action structure
    match &action.action_type {
        ActionType::Light => {
            log::info!("Setting light {} to {:?}", action.target, action.value);
            Ok(())
        }
        ActionType::Media => {
            log::info!("Media action on {}: {:?}", action.target, action.value);
            Ok(())
        }
        ActionType::Tv => {
            log::info!("TV action on {}: {:?}", action.target, action.value);
            Ok(())
        }
        ActionType::Climate => {
            log::info!("Climate action on {}: {:?}", action.target, action.value);
            Ok(())
        }
        ActionType::Lock => {
            log::info!("Lock action on {}: {:?}", action.target, action.value);
            Ok(())
        }
        ActionType::Script => {
            log::info!("Running script: {}", action.target);
            Ok(())
        }
        ActionType::Http => {
            log::info!("HTTP request to {}: {:?}", action.target, action.value);
            Ok(())
        }
        ActionType::Mqtt => {
            log::info!("MQTT publish to {}: {:?}", action.target, action.value);
            Ok(())
        }
        ActionType::Custom(ref name) => {
            log::info!("Custom action '{}' on {}: {:?}", name, action.target, action.value);
            Ok(())
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use serde_json::json;

    #[test]
    fn test_create_scene() {
        let mut manager = SceneManager::new();
        let scene = manager.create_scene("Goodnight", Some("Turn off everything"), Some("moon"));
        assert_eq!(scene.name, "Goodnight");
        assert!(scene.is_active);
    }

    #[test]
    fn test_add_action() {
        let mut manager = SceneManager::new();
        let scene = manager.create_scene("Test", None, None);

        let action = SceneAction {
            action_type: ActionType::Light,
            target: "living_room_lights".into(),
            value: Some(json!({"brightness": 0, "state": "off"})),
            delay_ms: None,
        };

        manager.add_action(&scene.id, action).unwrap();
        let updated = manager.get_scene(&scene.id).unwrap();
        assert_eq!(updated.actions.len(), 1);
    }

    #[test]
    fn test_execute_scene() {
        let mut manager = SceneManager::new();
        let scene = manager.create_scene("Test", None, None);

        manager.add_action(&scene.id, SceneAction {
            action_type: ActionType::Light,
            target: "lamp".into(),
            value: Some(json!({"state": "on"})),
            delay_ms: None,
        }).unwrap();

        let result = manager.execute_scene(&scene.id);
        assert!(result.success);
        assert_eq!(result.actions_executed, 1);
    }

    #[test]
    fn test_execute_nonexistent_scene() {
        let manager = SceneManager::new();
        let result = manager.execute_scene("nonexistent");
        assert!(!result.success);
        assert_eq!(result.errors.len(), 1);
    }

    #[test]
    fn test_toggle_scene() {
        let mut manager = SceneManager::new();
        let scene = manager.create_scene("Test", None, None);

        let active = manager.toggle_scene(&scene.id).unwrap();
        assert!(!active); // Was toggled off

        let active = manager.toggle_scene(&scene.id).unwrap();
        assert!(active); // Back on
    }

    #[test]
    fn test_delete_scene() {
        let mut manager = SceneManager::new();
        let scene = manager.create_scene("Test", None, None);

        assert_eq!(manager.scene_count(), 1);
        manager.delete_scene(&scene.id).unwrap();
        assert_eq!(manager.scene_count(), 0);
    }
}
