//! USX bundle parser
//!
//! Parses USX bundle files in JSON or YAML format.

use crate::types::*;
use log::{debug, info, warn};
use std::path::Path;

/// USX bundle parser
pub struct UsxParser;

impl UsxParser {
    pub fn new() -> Self {
        UsxParser
    }

    /// Parse a USX bundle from a string
    pub fn parse(&self, content: &str, source: &Path) -> anyhow::Result<UsxBundle> {
        debug!("Parsing USX bundle from: {}", source.display());

        // Try JSON first, then YAML
        let bundle: UsxBundle = match serde_json::from_str(content) {
            Ok(b) => b,
            Err(json_err) => {
                debug!("JSON parse failed: {}, trying YAML", json_err);
                match serde_yaml::from_str(content) {
                    Ok(b) => b,
                    Err(yaml_err) => anyhow::bail!(
                        "Failed to parse USX bundle (JSON: {}, YAML: {})",
                        json_err,
                        yaml_err
                    ),
                }
            }
        };

        info!("Parsed USX bundle: {} v{}", bundle.meta.name, bundle.meta.version);
        debug!("  Actions: {}, Surface: {:?}",
            bundle.actions.len(),
            bundle.surface.as_ref().map(|s| &s.id));

        Ok(bundle)
    }

    /// Parse a USX bundle from a file
    pub fn parse_file(&self, path: &Path) -> anyhow::Result<UsxBundle> {
        let content = std::fs::read_to_string(path)?;
        self.parse(&content, path)
    }

    /// Convert a USX bundle to JSON string
    pub fn to_json(&self, bundle: &UsxBundle) -> anyhow::Result<String> {
        Ok(serde_json::to_string_pretty(bundle)?)
    }

    /// Convert a USX bundle to YAML string
    pub fn to_yaml(&self, bundle: &UsxBundle) -> anyhow::Result<String> {
        Ok(serde_yaml::to_string(bundle)?)
    }
}
