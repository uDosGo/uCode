//! homenest-automation — Automation panel, scene management, OBF launcher
//!
//! Provides:
//! - `SceneManager` — Scene definitions, triggers, and execution
//! - `RuleEngine` — Condition-based automation rules
//! - `ObfLauncher` — OBF (Open Bridge Format) scene launcher

pub mod scene;
pub mod rule;
pub mod obf;

use serde::{Deserialize, Serialize};

/// An automation scene
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Scene {
    pub id: String,
    pub name: String,
    pub description: Option<String>,
    pub icon: Option<String>,
    pub actions: Vec<SceneAction>,
    pub triggers: Vec<SceneTrigger>,
    pub is_active: bool,
    pub created_at: String,
    pub updated_at: String,
}

/// An action within a scene
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SceneAction {
    pub action_type: ActionType,
    pub target: String,
    pub value: Option<serde_json::Value>,
    pub delay_ms: Option<u64>,
}

/// Type of scene action
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub enum ActionType {
    Light,
    Media,
    Tv,
    Climate,
    Lock,
    Script,
    Http,
    Mqtt,
    Custom(String),
}

/// A trigger for a scene
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SceneTrigger {
    pub trigger_type: TriggerType,
    pub config: serde_json::Value,
}

/// Type of scene trigger
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub enum TriggerType {
    Time,
    Sensor,
    Device,
    Voice,
    Schedule,
    Manual,
}

/// An automation rule (condition → action)
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AutomationRule {
    pub id: String,
    pub name: String,
    pub description: Option<String>,
    pub conditions: Vec<RuleCondition>,
    pub actions: Vec<SceneAction>,
    pub enabled: bool,
    pub priority: u32,
}

/// A condition in an automation rule
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct RuleCondition {
    pub field: String,
    pub operator: ConditionOperator,
    pub value: serde_json::Value,
}

/// Comparison operator for conditions
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub enum ConditionOperator {
    Equals,
    NotEquals,
    GreaterThan,
    LessThan,
    Contains,
    Between,
    TimeRange,
}

/// OBF (Open Bridge Format) scene definition
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ObfScene {
    pub id: String,
    pub name: String,
    pub devices: Vec<ObfDevice>,
    pub groups: Vec<ObfGroup>,
    pub schedule: Option<ObfSchedule>,
}

/// A device in an OBF scene
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ObfDevice {
    pub id: String,
    pub device_type: String,
    pub state: serde_json::Value,
    pub transition_ms: Option<u64>,
}

/// A group in an OBF scene
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ObfGroup {
    pub id: String,
    pub name: String,
    pub devices: Vec<String>,
    pub state: serde_json::Value,
}

/// Schedule for an OBF scene
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ObfSchedule {
    pub enabled: bool,
    pub time: Option<String>,
    pub days: Vec<String>,
    pub sunset_offset: Option<i32>,
    pub sunrise_offset: Option<i32>,
}

/// Result of executing a scene
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SceneResult {
    pub scene_id: String,
    pub success: bool,
    pub actions_executed: usize,
    pub actions_failed: usize,
    pub errors: Vec<String>,
    pub duration_ms: u64,
}
