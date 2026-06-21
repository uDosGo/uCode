//! OBF Launcher — Open Bridge Format scene launcher
//!
//! OBF (Open Bridge Format) is a standard for defining home automation scenes
//! that can be shared across different smart home platforms.

use crate::{ObfDevice, ObfGroup, ObfScene, ObfSchedule, SceneResult};
use chrono::Utc;
use std::collections::HashMap;
use uuid::Uuid;

/// OBF scene launcher
pub struct ObfLauncher {
    scenes: HashMap<String, ObfScene>,
}

impl ObfLauncher {
    pub fn new() -> Self {
        Self {
            scenes: HashMap::new(),
        }
    }

    /// Import an OBF scene from JSON
    pub fn import_scene(&mut self, json: &str) -> Result<ObfScene, String> {
        let scene: ObfScene = serde_json::from_str(json)
            .map_err(|e| format!("Failed to parse OBF scene: {}", e))?;

        let id = scene.id.clone();
        self.scenes.insert(id, scene.clone());
        Ok(scene)
    }

    /// Create a new OBF scene
    pub fn create_scene(&mut self, name: &str) -> ObfScene {
        let scene = ObfScene {
            id: Uuid::new_v4().to_string(),
            name: name.to_string(),
            devices: Vec::new(),
            groups: Vec::new(),
            schedule: None,
        };

        let id = scene.id.clone();
        self.scenes.insert(id, scene.clone());
        scene
    }

    /// Add a device to an OBF scene
    pub fn add_device(&mut self, scene_id: &str, device: ObfDevice) -> Result<(), String> {
        let scene = self.scenes.get_mut(scene_id)
            .ok_or_else(|| format!("Scene not found: {}", scene_id))?;
        scene.devices.push(device);
        Ok(())
    }

    /// Add a group to an OBF scene
    pub fn add_group(&mut self, scene_id: &str, group: ObfGroup) -> Result<(), String> {
        let scene = self.scenes.get_mut(scene_id)
            .ok_or_else(|| format!("Scene not found: {}", scene_id))?;
        scene.groups.push(group);
        Ok(())
    }

    /// Set the schedule for an OBF scene
    pub fn set_schedule(&mut self, scene_id: &str, schedule: ObfSchedule) -> Result<(), String> {
        let scene = self.scenes.get_mut(scene_id)
            .ok_or_else(|| format!("Scene not found: {}", scene_id))?;
        scene.schedule = Some(schedule);
        Ok(())
    }

    /// Execute an OBF scene
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
                    errors: vec!["OBF scene not found".into()],
                    duration_ms: 0,
                };
            }
        };

        let mut executed = 0;
        let mut failed = 0;
        let mut errors = Vec::new();

        // Execute device states
        for device in &scene.devices {
            log::info!("Setting device {} ({}) to {:?}", device.id, device.device_type, device.state);
            executed += 1;
        }

        // Execute group states
        for group in &scene.groups {
            log::info!("Setting group {} ({}) to {:?}", group.id, group.name, group.state);
            executed += 1;
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

    /// Export an OBF scene to JSON
    pub fn export_scene(&self, scene_id: &str) -> Result<String, String> {
        let scene = self.scenes.get(scene_id)
            .ok_or_else(|| format!("Scene not found: {}", scene_id))?;

        serde_json::to_string_pretty(scene)
            .map_err(|e| format!("Failed to serialize scene: {}", e))
    }

    /// Get all OBF scenes
    pub fn get_all_scenes(&self) -> Vec<&ObfScene> {
        self.scenes.values().collect()
    }

    /// Get a scene by ID
    pub fn get_scene(&self, scene_id: &str) -> Option<&ObfScene> {
        self.scenes.get(scene_id)
    }

    /// Delete a scene
    pub fn delete_scene(&mut self, scene_id: &str) -> Result<(), String> {
        self.scenes.remove(scene_id)
            .ok_or_else(|| format!("Scene not found: {}", scene_id))?;
        Ok(())
    }

    /// Get scene count
    pub fn scene_count(&self) -> usize {
        self.scenes.len()
    }
}

impl Default for ObfLauncher {
    fn default() -> Self {
        Self::new()
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use serde_json::json;

    #[test]
    fn test_create_obf_scene() {
        let mut launcher = ObfLauncher::new();
        let scene = launcher.create_scene("Movie Night");
        assert_eq!(scene.name, "Movie Night");
    }

    #[test]
    fn test_add_device_to_scene() {
        let mut launcher = ObfLauncher::new();
        let scene = launcher.create_scene("Test");

        launcher.add_device(&scene.id, ObfDevice {
            id: "light.living_room".into(),
            device_type: "light".into(),
            state: json!({"brightness": 50, "state": "on"}),
            transition_ms: Some(500),
        }).unwrap();

        let updated = launcher.get_scene(&scene.id).unwrap();
        assert_eq!(updated.devices.len(), 1);
    }

    #[test]
    fn test_execute_obf_scene() {
        let mut launcher = ObfLauncher::new();
        let scene = launcher.create_scene("Test");

        launcher.add_device(&scene.id, ObfDevice {
            id: "light.lamp".into(),
            device_type: "light".into(),
            state: json!({"state": "on"}),
            transition_ms: None,
        }).unwrap();

        let result = launcher.execute_scene(&scene.id);
        assert!(result.success);
        assert_eq!(result.actions_executed, 1);
    }

    #[test]
    fn test_import_export_scene() {
        let mut launcher = ObfLauncher::new();

        let json = r#"{
            "id": "test-123",
            "name": "Goodnight",
            "devices": [
                {"id": "light.bedroom", "device_type": "light", "state": {"state": "off"}, "transition_ms": null}
            ],
            "groups": [],
            "schedule": null
        }"#;

        let scene = launcher.import_scene(json).unwrap();
        assert_eq!(scene.name, "Goodnight");

        let exported = launcher.export_scene("test-123").unwrap();
        assert!(exported.contains("Goodnight"));
    }

    #[test]
    fn test_execute_nonexistent() {
        let launcher = ObfLauncher::new();
        let result = launcher.execute_scene("nonexistent");
        assert!(!result.success);
    }
}
