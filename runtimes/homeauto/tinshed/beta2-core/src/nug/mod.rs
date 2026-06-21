//! Nug system implementation
//!
//! A "nug" (nugget) is a binary executable unit in the uDos ecosystem.
//! Previously called "relic" — renamed to avoid confusion with development relics.

pub mod binary;
pub mod registry;
pub mod validator;
pub mod schema;

use serde::{Deserialize, Serialize};
use std::path::PathBuf;

/// Represents a Nug - a binary executable unit
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Nug {
    /// Unique identifier for the nug
    pub id: String,
    /// Human-readable name
    pub name: String,
    /// Version in semver format
    pub version: String,
    /// Optional emoji representation
    pub emoji: Option<String>,
    /// Optional single character glyph
    pub glyph: Option<String>,
    /// ASCII representation
    pub ascii: Option<String>,
    /// Type of nug (binary, archive, container)
    pub kind: String,
    /// Platform target
    pub platform: String,
    /// Architecture target
    pub arch: String,
    /// The binary data (base64 encoded)
    pub data: String,
    /// Dependencies (other nug IDs)
    pub requires: Vec<String>,
    /// Input schema
    pub inputs: Vec<NugInput>,
    /// Output schema
    pub outputs: Vec<NugOutput>,
    /// Tags for discovery
    pub tags: Vec<String>,
    /// Lexicon translations
    pub lexicon: Option<NugLexicon>,
    /// Visual representation
    pub visuals: Option<NugVisuals>,
    /// Resources (cells, files, etc.)
    pub resources: Option<Vec<NugResource>>,
}

/// Input parameter for a Nug
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct NugInput {
    pub name: String,
    pub r#type: String,
    pub default: Option<serde_json::Value>,
    pub required: bool,
}

/// Output parameter for a Nug
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct NugOutput {
    pub name: String,
    pub r#type: String,
}

/// Lexicon translations for a Nug
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct NugLexicon {
    pub terms: Vec<String>,
    pub emoji: Option<String>,
    pub short: String,
    pub long: String,
}

/// Visual representation for a Nug
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct NugVisuals {
    pub ascii: Option<String>,
    pub teletext: Option<String>,
    pub color: Option<String>,
}

/// Resource requirement for a Nug
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct NugResource {
    pub r#type: String, // "cell", "file", "database", etc.
    pub identifier: String, // e.g., "L100-BB45-1010-2" for cells
    pub mode: String, // "read", "write", "read_write"
    pub description: Option<String>,
}

impl Nug {
    /// Create a new Nug instance
    pub fn new(id: &str, name: &str, version: &str, data: &str) -> Self {
        Nug {
            id: id.to_string(),
            name: name.to_string(),
            version: version.to_string(),
            emoji: None,
            glyph: None,
            ascii: None,
            kind: "binary".to_string(),
            platform: "unknown".to_string(),
            arch: "unknown".to_string(),
            data: data.to_string(),
            requires: Vec::new(),
            inputs: Vec::new(),
            outputs: Vec::new(),
            tags: Vec::new(),
            lexicon: None,
            visuals: None,
            resources: None,
        }
    }

    /// Load a Nug from a YAML file
    pub fn load_from_file(path: &PathBuf) -> Result<Self, Box<dyn std::error::Error>> {
        let content = std::fs::read_to_string(path)?;
        let nug = serde_yaml::from_str(&content)?;
        Ok(nug)
    }

    /// Save a Nug to a YAML file
    pub fn save_to_file(&self, path: &PathBuf) -> Result<(), Box<dyn std::error::Error>> {
        let content = serde_yaml::to_string(self)?;
        std::fs::write(path, content)?;
        Ok(())
    }

    /// Extract binary data to a file
    pub fn extract_binary(&self, output_path: &PathBuf) -> Result<(), Box<dyn std::error::Error>> {
        use base64::{engine::general_purpose, Engine as _};
        let decoded = general_purpose::STANDARD.decode(&self.data)?;
        std::fs::write(output_path, decoded)?;
        Ok(())
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::path::PathBuf;

    #[test]
    fn test_nug_creation() {
        let nug = Nug::new("R100-U899", "Runner", "1.0.0", "base64encoded");
        assert_eq!(nug.id, "R100-U899");
        assert_eq!(nug.name, "Runner");
        assert_eq!(nug.version, "1.0.0");
        assert_eq!(nug.data, "base64encoded");
    }

    #[test]
    fn test_nug_serialization() {
        let mut nug = Nug::new("R100-U899", "Runner", "1.0.0", "base64encoded");
        nug.emoji = Some("🏃".to_string());
        nug.tags = vec!["runner".to_string(), "execute".to_string()];

        let yaml = serde_yaml::to_string(&nug).unwrap();
        let deserialized: Nug = serde_yaml::from_str(&yaml).unwrap();

        assert_eq!(deserialized.id, "R100-U899");
        assert_eq!(deserialized.emoji, Some("🏃".to_string()));
        assert_eq!(deserialized.tags, vec!["runner", "execute"]);
    }

    #[test]
    fn test_nug_file_operations() {
        let nug = Nug::new("R100-U899", "Runner", "1.0.0", "base64encoded");
        let path = PathBuf::from("/tmp/test_nug.yaml");

        // Save to file
        nug.save_to_file(&path).unwrap();

        // Load from file
        let loaded = Nug::load_from_file(&path).unwrap();
        assert_eq!(loaded.id, "R100-U899");

        // Clean up
        std::fs::remove_file(path).unwrap();
    }
}
