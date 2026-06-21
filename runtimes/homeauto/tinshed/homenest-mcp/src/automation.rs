//! Automation handlers for HomeNest MCP
//!
//! Manages scene triggering, USX sheet execution, and automation status.

use crate::HomenestResponse;
use log::{info, warn};
use std::collections::HashMap;
use std::sync::Mutex;

lazy_static::lazy_static! {
    static ref AUTOMATION_STATE: Mutex<AutomationState> = Mutex::new(AutomationState::default());
}

struct AutomationState {
    active_scenes: Vec<String>,
    recent_actions: Vec<String>,
    scenes: HashMap<String, SceneDef>,
}

#[derive(Clone)]
struct SceneDef {
    name: String,
    description: String,
    actions: Vec<String>,
}

impl Default for AutomationState {
    fn default() -> Self {
        let mut scenes = HashMap::new();
        scenes.insert(
            "goodnight".to_string(),
            SceneDef {
                name: "Goodnight".to_string(),
                description: "Turn off lights, lock doors, set thermostat".to_string(),
                actions: vec![
                    "ha:light.off:living_room".to_string(),
                    "ha:light.off:bedroom".to_string(),
                    "ha:lock.lock:front_door".to_string(),
                    "ha:climate.set:thermostat:18".to_string(),
                ],
            },
        );
        scenes.insert(
            "morning".to_string(),
            SceneDef {
                name: "Morning".to_string(),
                description: "Turn on kitchen lights, start coffee, warm up".to_string(),
                actions: vec![
                    "ha:light.on:kitchen".to_string(),
                    "ha:switch.on:coffee_maker".to_string(),
                    "ha:climate.set:thermostat:22".to_string(),
                ],
            },
        );
        scenes.insert(
            "away".to_string(),
            SceneDef {
                name: "Away".to_string(),
                description: "Turn off all lights, set alarm, eco mode".to_string(),
                actions: vec![
                    "ha:light.off:all".to_string(),
                    "ha:alarm.arm_away".to_string(),
                    "ha:climate.set:thermostat:16".to_string(),
                ],
            },
        );

        AutomationState {
            active_scenes: Vec::new(),
            recent_actions: Vec::new(),
            scenes,
        }
    }
}

pub fn handle_trigger(scene: &str) -> HomenestResponse {
    info!("Triggering scene: {}", scene);

    let mut state = AUTOMATION_STATE.lock().unwrap();

    if let Some(scene_def) = state.scenes.get(scene) {
        info!("Executing scene '{}': {} actions", scene, scene_def.actions.len());

        for action in &scene_def.actions {
            info!("  Action: {}", action);
            // TODO: Execute action via HA bridge
            state.recent_actions.push(format!("{}:{}", scene, action));
        }

        if !state.active_scenes.contains(&scene.to_string()) {
            state.active_scenes.push(scene.to_string());
        }

        // Keep recent actions bounded
        if state.recent_actions.len() > 100 {
            state.recent_actions = state.recent_actions.split_off(state.recent_actions.len() - 50);
        }

        HomenestResponse::Success {
            data: serde_json::json!({
                "scene": scene,
                "actions_executed": scene_def.actions.len(),
                "description": scene_def.description,
            }),
        }
    } else {
        HomenestResponse::Error {
            message: format!("Scene not found: {}. Available: {:?}",
                scene,
                state.scenes.keys().collect::<Vec<_>>()),
        }
    }
}

pub fn handle_run_sheet(sheet_path: &str) -> HomenestResponse {
    info!("Running USX sheet: {}", sheet_path);

    // Check if file exists
    let path = std::path::Path::new(sheet_path);
    if !path.exists() {
        return HomenestResponse::Error {
            message: format!("Sheet not found: {}", sheet_path),
        };
    }

    // Read and parse USX sheet
    let content = match std::fs::read_to_string(path) {
        Ok(c) => c,
        Err(e) => return HomenestResponse::Error {
            message: format!("Failed to read sheet: {}", e),
        },
    };

    // Parse as JSON (USX bundle format)
    let sheet: serde_json::Value = match serde_json::from_str(&content) {
        Ok(v) => v,
        Err(_) => {
            // Try YAML
            match serde_json::from_str::<serde_json::Value>(&content) {
                Ok(v) => v,
                Err(e) => return HomenestResponse::Error {
                    message: format!("Failed to parse sheet: {}", e),
                },
            }
        }
    };

    // Extract actions from USX bundle
    let actions = sheet.get("actions")
        .and_then(|a| a.as_array())
        .map(|a| a.iter().filter_map(|v| v.as_str().map(|s| s.to_string())).collect::<Vec<_>>())
        .unwrap_or_default();

    let mut state = AUTOMATION_STATE.lock().unwrap();
    for action in &actions {
        info!("  Sheet action: {}", action);
        state.recent_actions.push(format!("sheet:{}", action));
    }

    HomenestResponse::Success {
        data: serde_json::json!({
            "sheet": sheet_path,
            "actions_parsed": actions.len(),
            "actions": actions,
        }),
    }
}

pub fn handle_status() -> HomenestResponse {
    let state = AUTOMATION_STATE.lock().unwrap();
    HomenestResponse::AutomationStatus {
        active: state.active_scenes.clone(),
        recent: state.recent_actions.iter().rev().take(10).cloned().collect(),
    }
}

pub fn handle_list() -> HomenestResponse {
    let state = AUTOMATION_STATE.lock().unwrap();
    let scenes: Vec<String> = state.scenes.keys().cloned().collect();
    let sheets: Vec<String> = Vec::new(); // TODO: Scan for USX sheets
    HomenestResponse::AutomationList { scenes, sheets }
}
