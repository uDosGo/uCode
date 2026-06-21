//! Nug validator implementation

use super::Nug;
use super::schema::{validate_nug_schema, NugSchema, NugInputSchema, NugOutputSchema};
use std::path::PathBuf;

/// Validate a Nug instance
pub fn validate_nug(nug: &Nug) -> Result<(), String> {
    // Convert Nug to NugSchema for validation
    let schema = NugSchema {
        id: nug.id.clone(),
        name: nug.name.clone(),
        version: nug.version.clone(),
        kind: nug.kind.clone(),
        platform: nug.platform.clone(),
        arch: nug.arch.clone(),
        data: nug.data.clone(),
        requires: nug.requires.clone(),
        inputs: nug
            .inputs
            .iter()
            .map(|input| NugInputSchema {
                name: input.name.clone(),
                r#type: input.r#type.clone(),
                default: input.default.clone(),
                required: input.required,
            })
            .collect(),
        outputs: nug
            .outputs
            .iter()
            .map(|output| NugOutputSchema {
                name: output.name.clone(),
                r#type: output.r#type.clone(),
            })
            .collect(),
        tags: nug.tags.clone(),
    };

    validate_nug_schema(&schema)
}

/// Validate a Nug from a YAML file
pub fn validate_nug_file(path: &PathBuf) -> Result<(), String> {
    let nug = Nug::load_from_file(path)
        .map_err(|e| format!("Failed to load nug: {}", e))?;
    validate_nug(&nug)
}

/// Validate resource requirements for a Nug
pub fn validate_nug_resources(nug: &Nug) -> Result<(), String> {
    if let Some(resources) = &nug.resources {
        for resource in resources {
            // Validate resource type
            match resource.r#type.as_str() {
                "cell" => {
                    // Validate cell identifier format
                    if !is_valid_cell_identifier(&resource.identifier) {
                        return Err(format!(
                            "Invalid cell identifier: {}",
                            resource.identifier
                        ));
                    }
                }
                "file" | "database" | "api" => {
                    // Additional validation for other resource types
                    if resource.identifier.is_empty() {
                        return Err(format!(
                            "Resource identifier cannot be empty for type: {}",
                            resource.r#type
                        ));
                    }
                }
                _ => {
                    return Err(format!("Invalid resource type: {}", resource.r#type));
                }
            }

            // Validate resource mode
            match resource.mode.as_str() {
                "read" | "write" | "read_write" => {}
                _ => {
                    return Err(format!("Invalid resource mode: {}", resource.mode));
                }
            }
        }
    }
    
    Ok(())
}

/// Check if a cell identifier is valid
fn is_valid_cell_identifier(identifier: &str) -> bool {
    // Cell identifier format: L<level>-<gridXY>-<cellXY>-<layer>
    // Example: L100-BB45-1010-2
    let parts: Vec<&str> = identifier.split('-').collect();
    if parts.len() != 4 {
        return false;
    }
    
    // Check level prefix
    if !parts[0].starts_with('L') {
        return false;
    }
    
    // Check that all parts are non-empty
    for part in parts {
        if part.is_empty() {
            return false;
        }
    }
    
    true
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::nug::Nug;
    use std::path::PathBuf;

    #[test]
    fn test_validate_valid_nug() {
        let nug = Nug {
            id: "R100-U899".to_string(),
            name: "Runner".to_string(),
            version: "1.0.0".to_string(),
            emoji: Some("🏃".to_string()),
            glyph: None,
            ascii: None,
            kind: "binary".to_string(),
            platform: "linux".to_string(),
            arch: "x86_64".to_string(),
            data: "base64encoded".to_string(),
            requires: vec![],
            inputs: vec![],
            outputs: vec![],
            tags: vec!["runner".to_string()],
            lexicon: None,
            visuals: None,
            resources: None,
        };

        assert!(validate_nug(&nug).is_ok());
    }

    #[test]
    fn test_validate_invalid_nug() {
        let nug = Nug {
            id: "".to_string(),
            name: "Runner".to_string(),
            version: "1.0.0".to_string(),
            emoji: None,
            glyph: None,
            ascii: None,
            kind: "binary".to_string(),
            platform: "linux".to_string(),
            arch: "x86_64".to_string(),
            data: "base64encoded".to_string(),
            requires: vec![],
            inputs: vec![],
            outputs: vec![],
            tags: vec![],
            lexicon: None,
            visuals: None,
            resources: None,
        };

        assert!(validate_nug(&nug).is_err());
    }

    #[test]
    fn test_validate_nug_file() {
        let nug = Nug {
            id: "R100-U899".to_string(),
            name: "Runner".to_string(),
            version: "1.0.0".to_string(),
            emoji: None,
            glyph: None,
            ascii: None,
            kind: "binary".to_string(),
            platform: "linux".to_string(),
            arch: "x86_64".to_string(),
            data: "base64encoded".to_string(),
            requires: vec![],
            inputs: vec![],
            outputs: vec![],
            tags: vec![],
            lexicon: None,
            visuals: None,
            resources: None,
        };

        let path = PathBuf::from("/tmp/test_nug_validation.yaml");
        nug.save_to_file(&path).unwrap();

        let result = validate_nug_file(&path);
        assert!(result.is_ok());

        std::fs::remove_file(path).unwrap();
    }

    #[test]
    fn test_validate_nug_resources() {
        let nug = Nug {
            id: "R100-U899".to_string(),
            name: "Runner".to_string(),
            version: "1.0.0".to_string(),
            emoji: None,
            glyph: None,
            ascii: None,
            kind: "binary".to_string(),
            platform: "linux".to_string(),
            arch: "x86_64".to_string(),
            data: "base64encoded".to_string(),
            requires: vec![],
            inputs: vec![],
            outputs: vec![],
            tags: vec![],
            lexicon: None,
            visuals: None,
            resources: Some(vec![
                crate::nug::NugResource {
                    r#type: "cell".to_string(),
                    identifier: "L100-BB45-1010-2".to_string(),
                    mode: "read_write".to_string(),
                    description: Some("VIP data storage".to_string()),
                },
            ]),
        };

        assert!(validate_nug_resources(&nug).is_ok());
    }

    #[test]
    fn test_validate_invalid_cell_identifier() {
        let nug = Nug {
            id: "R100-U899".to_string(),
            name: "Runner".to_string(),
            version: "1.0.0".to_string(),
            emoji: None,
            glyph: None,
            ascii: None,
            kind: "binary".to_string(),
            platform: "linux".to_string(),
            arch: "x86_64".to_string(),
            data: "base64encoded".to_string(),
            requires: vec![],
            inputs: vec![],
            outputs: vec![],
            tags: vec![],
            lexicon: None,
            visuals: None,
            resources: Some(vec![
                crate::nug::NugResource {
                    r#type: "cell".to_string(),
                    identifier: "invalid-cell-id".to_string(),
                    mode: "read".to_string(),
                    description: None,
                },
            ]),
        };

        assert!(validate_nug_resources(&nug).is_err());
    }
}
