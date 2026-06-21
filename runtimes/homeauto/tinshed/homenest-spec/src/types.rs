//! USX bundle type definitions for HomeNest

use serde::{Deserialize, Serialize};
use std::collections::HashMap;

/// A complete USX bundle
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct UsxBundle {
    /// Bundle metadata
    pub meta: BundleMeta,
    /// Surface definition (UI layout)
    pub surface: Option<SurfaceDef>,
    /// Automation actions
    pub actions: Vec<Action>,
    /// Bindings (input mappings)
    pub bindings: Option<HashMap<String, String>>,
    /// Theme configuration
    pub theme: Option<ThemeConfig>,
}

/// Bundle metadata
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct BundleMeta {
    /// USX version
    pub version: String,
    /// Bundle name
    pub name: String,
    /// Human-readable label
    pub label: Option<String>,
    /// Bundle description
    pub description: Option<String>,
    /// Author
    pub author: Option<String>,
    /// Creation timestamp
    pub created: Option<String>,
    /// Tags for categorization
    pub tags: Option<Vec<String>>,
}

/// Surface definition (UI layout)
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SurfaceDef {
    /// Surface identifier
    pub id: String,
    /// Layout type
    pub layout: LayoutType,
    /// Grid columns (for grid layout)
    pub columns: Option<u32>,
    /// Grid rows (for grid layout)
    pub rows: Option<u32>,
    /// Gap between elements
    pub gap: Option<u32>,
    /// Tiles/widgets on this surface
    pub tiles: Option<Vec<TileDef>>,
    /// Widget references
    pub widgets: Option<Vec<String>>,
}

/// Layout type
#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "lowercase")]
pub enum LayoutType {
    Grid,
    List,
    Overlay,
    Flex,
    Canvas,
}

/// A tile/widget on a surface
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct TileDef {
    /// Tile identifier
    pub id: String,
    /// Display label
    pub label: Option<String>,
    /// Icon reference
    pub icon: Option<String>,
    /// Action to execute on activation
    pub action: Option<String>,
    /// Tile position (for grid)
    pub position: Option<TilePosition>,
}

/// Tile position in a grid
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct TilePosition {
    pub x: u32,
    pub y: u32,
    pub width: Option<u32>,
    pub height: Option<u32>,
}

/// An automation action
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Action {
    /// Action identifier
    pub id: String,
    /// Action type
    #[serde(rename = "type")]
    pub action_type: ActionType,
    /// Target entity or device
    pub target: Option<String>,
    /// Action parameters
    pub params: Option<HashMap<String, serde_json::Value>>,
    /// Delay before execution (seconds)
    pub delay: Option<f64>,
    /// Condition for execution
    pub condition: Option<Condition>,
}

/// Action type
#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum ActionType {
    /// Home Assistant operations
    HaLight,
    HaSwitch,
    HaLock,
    HaClimate,
    HaAlarm,
    HaMedia,
    HaScene,
    /// Media playback
    MediaPlay,
    MediaPause,
    MediaStop,
    MediaSeek,
    /// TV/DVR
    TvChannel,
    TvRecord,
    TvEpg,
    /// System
    SystemCommand,
    SystemNotification,
    SystemScript,
    /// Custom
    Custom,
}

/// Condition for action execution
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Condition {
    /// Condition type
    #[serde(rename = "type")]
    pub condition_type: ConditionType,
    /// Entity to check
    pub entity: Option<String>,
    /// Expected value
    pub value: Option<serde_json::Value>,
    /// Time condition
    pub time: Option<String>,
}

/// Condition type
#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum ConditionType {
    EntityState,
    TimeRange,
    TimeOfDay,
    DayOfWeek,
    Always,
}

/// Theme configuration
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ThemeConfig {
    /// Theme name
    pub name: Option<String>,
    /// Color scheme
    pub colors: Option<ColorScheme>,
    /// Font configuration
    pub font: Option<FontConfig>,
}

/// Color scheme
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ColorScheme {
    pub primary: Option<String>,
    pub secondary: Option<String>,
    pub background: Option<String>,
    pub surface: Option<String>,
    pub text: Option<String>,
    pub accent: Option<String>,
}

/// Font configuration
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct FontConfig {
    pub family: Option<String>,
    pub size: Option<u32>,
    pub weight: Option<String>,
}

/// Compilation result
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CompilationResult {
    /// Number of actions compiled
    pub action_count: usize,
    /// Number of surfaces defined
    pub surface_count: usize,
    /// Number of tiles/widgets
    pub tile_count: usize,
    /// Any warnings during compilation
    pub warnings: Vec<String>,
    /// Errors during compilation
    pub errors: Vec<String>,
    /// Whether compilation was successful
    pub success: bool,
}
