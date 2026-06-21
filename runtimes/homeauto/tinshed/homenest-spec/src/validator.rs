//! USX bundle validator
//!
//! Validates USX bundles for correctness and completeness.

use crate::types::*;
use log::{debug, info, warn};

/// USX bundle validator
pub struct UsxValidator;

impl UsxValidator {
    pub fn new() -> Self {
        UsxValidator
    }

    /// Validate a USX bundle, returning warnings and errors
    pub fn validate(&self, bundle: &UsxBundle) -> anyhow::Result<CompilationResult> {
        debug!("Validating USX bundle: {}", bundle.meta.name);

        let mut warnings = Vec::new();
        let mut errors = Vec::new();

        // Validate metadata
        self.validate_meta(&bundle.meta, &mut warnings, &mut errors);

        // Validate surface
        if let Some(ref surface) = bundle.surface {
            self.validate_surface(surface, &mut warnings, &mut errors);
        }

        // Validate actions
        self.validate_actions(&bundle.actions, &mut warnings, &mut errors);

        // Validate bindings
        if let Some(ref bindings) = bundle.bindings {
            self.validate_bindings(bindings, &mut warnings, &mut errors);
        }

        let success = errors.is_empty();
        let result = CompilationResult {
            action_count: bundle.actions.len(),
            surface_count: if bundle.surface.is_some() { 1 } else { 0 },
            tile_count: bundle.surface.as_ref()
                .map(|s| s.tiles.as_ref().map(|t| t.len()).unwrap_or(0))
                .unwrap_or(0),
            warnings,
            errors,
            success,
        };

        if success {
            info!("USX bundle '{}' validated successfully", bundle.meta.name);
        } else {
            warn!("USX bundle '{}' has {} error(s), {} warning(s)",
                bundle.meta.name, result.errors.len(), result.warnings.len());
        }

        Ok(result)
    }

    fn validate_meta(&self, meta: &BundleMeta, warnings: &mut Vec<String>, errors: &mut Vec<String>) {
        if meta.version.is_empty() {
            errors.push("Bundle version is required".to_string());
        }
        if meta.name.is_empty() {
            errors.push("Bundle name is required".to_string());
        }
        if meta.actions.is_none() && meta.surface.is_none() {
            warnings.push("Bundle has no actions or surface defined".to_string());
        }
    }

    fn validate_surface(&self, surface: &SurfaceDef, warnings: &mut Vec<String>, errors: &mut Vec<String>) {
        if surface.id.is_empty() {
            errors.push("Surface ID is required".to_string());
        }

        if let Some(ref tiles) = surface.tiles {
            for tile in tiles {
                if tile.id.is_empty() {
                    errors.push("Tile ID is required".to_string());
                }
                if tile.action.is_none() && tile.label.is_none() {
                    warnings.push(format!("Tile '{}' has no action or label", tile.id));
                }
            }
        }
    }

    fn validate_actions(&self, actions: &[Action], warnings: &mut Vec<String>, errors: &mut Vec<String>) {
        for action in actions {
            if action.id.is_empty() {
                errors.push("Action ID is required".to_string());
            }
        }
    }

    fn validate_bindings(&self, bindings: &std::collections::HashMap<String, String>,
                         _warnings: &mut Vec<String>, _errors: &mut Vec<String>) {
        // Bindings are optional, just log them
        debug!("  Bindings: {} defined", bindings.len());
    }
}
