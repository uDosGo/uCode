//! # uDos Vector Core (UVC)
//!
//! The universal vector engine for the uDos visual system.
//!
//! UVC provides a complete pipeline for working with vector graphics:
//!
//! - **Object Model**: UniversalVisual — the single source of truth for all visual assets
//! - **SVG Pipeline**: Parse, optimize, serialize, and validate SVG content
//! - **Rasterization**: Render SVG to uDos Cell (24×24), CELX, thumbnails, and PNG export
//! - **Text Mapping**: Convert visuals to ASCII art, Teletext (40×25), and Braille
//! - **Semantic Analysis**: Describe, classify, tag, and extract subjects from visuals
//! - **Provenance Trail**: Track transformations, regenerations, and lineage
//!
//! ## Quick Start
//!
//! ```rust,no_run
//! use udos_vector_core::UniversalVectorCore;
//!
//! let svg_str = r#"<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
//!     <circle cx="12" cy="12" r="10" fill="red"/>
//! </svg>"#;
//!
//! let core = UniversalVectorCore::new();
//! let visual = core.import_svg("my-visual", svg_str).unwrap();
//!
//! // Get a description
//! let description = core.describe(&visual);
//!
//! // Render to a uDos Cell
//! let cell = core.render_to_cell(&visual).unwrap();
//!
//! // Export to PNG
//! let png = core.export_png(&cell).unwrap();
//! ```

pub mod error;
pub mod object;
pub mod raster;
pub mod semantic;
pub mod svg;
pub mod text;
pub mod trace;

use error::UvcError;
use object::{CellGrid, UniversalVisual};

/// The main API for the uDos Vector Core system.
///
/// Provides a unified interface for all vector processing operations.
pub struct UniversalVectorCore {
    /// Configuration options
    pub config: CoreConfig,
}

/// Configuration for the UniversalVectorCore.
#[derive(Debug, Clone)]
pub struct CoreConfig {
    /// Default rasterization width for cells
    pub cell_width: u16,
    /// Default rasterization height for cells
    pub cell_height: u16,
    /// Whether to auto-generate semantic metadata on import
    pub auto_analyze: bool,
    /// Whether to auto-generate text representations on import
    pub auto_generate_text: bool,
    /// Whether to auto-generate raster cache on import
    pub auto_rasterize: bool,
}

impl Default for CoreConfig {
    fn default() -> Self {
        Self {
            cell_width: 24,
            cell_height: 24,
            auto_analyze: true,
            auto_generate_text: false,
            auto_rasterize: false,
        }
    }
}

impl UniversalVectorCore {
    /// Create a new UniversalVectorCore with default configuration.
    pub fn new() -> Self {
        Self {
            config: CoreConfig::default(),
        }
    }

    /// Create a new UniversalVectorCore with custom configuration.
    pub fn with_config(config: CoreConfig) -> Self {
        Self { config }
    }

    // ── SVG Pipeline ──

    /// Import an SVG string into a UniversalVisual.
    pub fn import_svg(&self, name: &str, svg_str: &str) -> Result<UniversalVisual, UvcError> {
        let id = uuid_v4();
        let tree = svg::parse_svg(svg_str)?;
        let optimized = svg::optimize_svg(&tree)?;
        let optimized_str = svg::serialize_svg(&optimized);

        let mut visual = UniversalVisual::new(id, name.to_string());
        visual.svg = Some(tree);
        visual.svg_source = Some(svg_str.to_string());
        visual.svg_optimized = Some(optimized_str);

        // Auto-analyze if configured
        if self.config.auto_analyze {
            if let Some(ref svg_tree) = visual.svg {
                visual.semantic = semantic::analyze(svg_tree);
            }
        }

        // Auto-rasterize if configured
        if self.config.auto_rasterize {
            if let Some(ref svg_tree) = visual.svg {
                let cell = raster::render_to_cell(svg_tree)?;
                visual.rasters.insert(object::RasterType::Cell24, cell);
            }
        }

        Ok(visual)
    }

    /// Validate an SVG string.
    pub fn validate_svg(&self, svg_str: &str) -> Result<(), UvcError> {
        svg::validate_svg(svg_str)
    }

    /// Optimize an SVG string.
    pub fn optimize_svg(&self, svg_str: &str) -> Result<String, UvcError> {
        let tree = svg::parse_svg(svg_str)?;
        let optimized = svg::optimize_svg(&tree)?;
        Ok(svg::serialize_svg(&optimized))
    }

    // ── Rasterization ──

    /// Render a visual to a uDos Cell (24×24).
    pub fn render_to_cell(&self, visual: &UniversalVisual) -> Result<CellGrid, UvcError> {
        match &visual.svg {
            Some(svg_tree) => raster::render_to_cell(svg_tree),
            None => Err(UvcError::RasterizationError("No SVG tree available".into())),
        }
    }

    /// Render a visual to a CELX (24×width).
    pub fn render_to_celx(&self, visual: &UniversalVisual, width: u16) -> Result<CellGrid, UvcError> {
        match &visual.svg {
            Some(svg_tree) => raster::render_to_celx(svg_tree, width),
            None => Err(UvcError::RasterizationError("No SVG tree available".into())),
        }
    }

    /// Render a visual to a thumbnail (64×64).
    pub fn render_to_thumbnail(&self, visual: &UniversalVisual) -> Result<CellGrid, UvcError> {
        match &visual.svg {
            Some(svg_tree) => raster::render_to_thumbnail(svg_tree),
            None => Err(UvcError::RasterizationError("No SVG tree available".into())),
        }
    }

    /// Export a CellGrid to PNG bytes.
    pub fn export_png(&self, grid: &CellGrid) -> Result<Vec<u8>, UvcError> {
        raster::export_png(grid)
    }

    // ── Text Representations ──

    /// Convert a visual to ASCII art.
    pub fn to_ascii(&self, visual: &UniversalVisual, width: usize, height: usize) -> String {
        match &visual.svg {
            Some(svg_tree) => text::to_ascii(svg_tree, width, height),
            None => String::from("[No SVG available]"),
        }
    }

    /// Convert a visual to Teletext (40×25).
    pub fn to_teletext(&self, visual: &UniversalVisual) -> Result<String, UvcError> {
        match &visual.svg {
            Some(svg_tree) => text::to_teletext(svg_tree),
            None => Err(UvcError::RasterizationError("No SVG tree available".into())),
        }
    }

    /// Convert a visual to Braille.
    pub fn to_braille(&self, visual: &UniversalVisual) -> Result<String, UvcError> {
        match &visual.svg {
            Some(svg_tree) => text::to_braille(svg_tree),
            None => Err(UvcError::RasterizationError("No SVG tree available".into())),
        }
    }

    // ── Semantic Analysis ──

    /// Describe a visual in natural language.
    pub fn describe(&self, visual: &UniversalVisual) -> String {
        match &visual.svg {
            Some(svg_tree) => semantic::describe(svg_tree),
            None => "No SVG content available.".to_string(),
        }
    }

    /// Generate a regeneration prompt from a visual.
    pub fn to_prompt(&self, visual: &UniversalVisual) -> String {
        match &visual.svg {
            Some(svg_tree) => semantic::to_prompt(svg_tree),
            None => String::new(),
        }
    }

    /// Extract subjects from a visual.
    pub fn extract_subjects(&self, visual: &UniversalVisual) -> Vec<object::Subject> {
        match &visual.svg {
            Some(svg_tree) => semantic::extract_subjects(svg_tree),
            None => Vec::new(),
        }
    }

    /// Analyze the semantic content of a visual.
    pub fn analyze(&self, visual: &UniversalVisual) -> object::SemanticMetadata {
        match &visual.svg {
            Some(svg_tree) => semantic::analyze(svg_tree),
            None => object::SemanticMetadata::default(),
        }
    }

    // ── Provenance ──

    /// Record a transformation in the provenance trail.
    pub fn record_transformation(
        &self,
        visual: &mut UniversalVisual,
        operation: &str,
        params: serde_json::Value,
    ) {
        trace::record_transformation(&mut visual.provenance, operation, params);
    }

    /// Record a source import in the provenance trail.
    pub fn record_source(&self, visual: &mut UniversalVisual, format: &str, hash: &str) {
        trace::record_source(&mut visual.provenance, format, hash);
    }

    /// Link a parent visual in the provenance trail.
    pub fn link_parent(&self, visual: &mut UniversalVisual, parent_id: &str) {
        trace::link_parent(&mut visual.provenance, parent_id);
    }

    /// Link a child visual in the provenance trail.
    pub fn link_child(&self, visual: &mut UniversalVisual, child_id: &str) {
        trace::link_child(&mut visual.provenance, child_id);
    }

    /// Get the transformation history as readable strings.
    pub fn transformation_history(&self, visual: &UniversalVisual) -> Vec<String> {
        trace::transformation_history(&visual.provenance)
    }

    /// Get the regeneration history as readable strings.
    pub fn regeneration_history(&self, visual: &UniversalVisual) -> Vec<String> {
        trace::regeneration_history(&visual.provenance)
    }

    // ── Diffing ──

    /// Compute a diff between two visuals.
    pub fn diff(&self, before: &UniversalVisual, after: &UniversalVisual) -> trace::diff::VisualDiff {
        trace::diff::diff(before, after)
    }

    /// Check if two visuals are semantically identical.
    pub fn is_semantically_identical(&self, a: &UniversalVisual, b: &UniversalVisual) -> bool {
        trace::diff::is_semantically_identical(a, b)
    }
}

impl Default for UniversalVectorCore {
    fn default() -> Self {
        Self::new()
    }
}

/// Generate a simple UUID v4-like identifier.
fn uuid_v4() -> String {
    use std::time::{SystemTime, UNIX_EPOCH};
    let now = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .unwrap_or_default();
    format!(
        "uvc-{:08x}-{:04x}-{:04x}-{:04x}-{:012x}",
        now.as_secs(),
        now.subsec_nanos() as u16,
        rand::random::<u16>(),
        rand::random::<u16>(),
        rand::random::<u64>()
    )
}

#[cfg(test)]
mod tests {
    use super::*;

    fn create_test_svg() -> &'static str {
        r#"<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
            <circle cx="12" cy="12" r="10" fill="red"/>
        </svg>"#
    }

    #[test]
    fn test_import_svg() {
        let core = UniversalVectorCore::new();
        let visual = core.import_svg("test", create_test_svg()).unwrap();
        assert_eq!(visual.name, "test");
        assert!(visual.svg.is_some());
        assert!(visual.svg_source.is_some());
    }

    #[test]
    fn test_validate_svg() {
        let core = UniversalVectorCore::new();
        assert!(core.validate_svg(create_test_svg()).is_ok());
        assert!(core.validate_svg("invalid").is_err());
    }

    #[test]
    fn test_describe() {
        let core = UniversalVectorCore::new();
        let visual = core.import_svg("test", create_test_svg()).unwrap();
        let description = core.describe(&visual);
        // usvg 0.37 parses shapes into Path nodes
        assert!(!description.is_empty());
        assert!(description.contains("red") || description.contains("#ff0000"));
    }

    #[test]
    fn test_render_to_cell() {
        let core = UniversalVectorCore::new();
        let visual = core.import_svg("test", create_test_svg()).unwrap();
        let cell = core.render_to_cell(&visual).unwrap();
        assert_eq!(cell.width, 24);
        assert_eq!(cell.height, 24);
        assert_eq!(cell.pixels.len(), 24 * 24 * 4);
    }

    #[test]
    fn test_export_png() {
        let core = UniversalVectorCore::new();
        let visual = core.import_svg("test", create_test_svg()).unwrap();
        let cell = core.render_to_cell(&visual).unwrap();
        let png = core.export_png(&cell).unwrap();
        assert!(!png.is_empty());
        assert_eq!(&png[..8], &[137, 80, 78, 71, 13, 10, 26, 10]);
    }

    #[test]
    fn test_to_ascii() {
        let core = UniversalVectorCore::new();
        let visual = core.import_svg("test", create_test_svg()).unwrap();
        let ascii = core.to_ascii(&visual, 8, 8);
        assert!(!ascii.is_empty());
        assert_eq!(ascii.lines().count(), 8);
    }

    #[test]
    fn test_provenance_trail() {
        let core = UniversalVectorCore::new();
        let mut visual = core.import_svg("test", create_test_svg()).unwrap();

        core.record_transformation(&mut visual, "scale", serde_json::json!({"factor": 2.0}));
        core.record_source(&mut visual, "SVG", "abc123");
        core.link_parent(&mut visual, "parent-1");

        let history = core.transformation_history(&visual);
        assert_eq!(history.len(), 1);
        assert!(history[0].contains("scale"));
    }

    #[test]
    fn test_diff() {
        let core = UniversalVectorCore::new();
        let visual_a = core.import_svg("a", create_test_svg()).unwrap();
        let mut visual_b = core.import_svg("b", create_test_svg()).unwrap();
        visual_b.name = "renamed".to_string();

        let diff = core.diff(&visual_a, &visual_b);
        assert!(diff.name_changed);
        assert!(!diff.svg_changed);
    }

    #[test]
    fn test_extract_subjects() {
        let core = UniversalVectorCore::new();
        let visual = core.import_svg("test", create_test_svg()).unwrap();
        let subjects = core.extract_subjects(&visual);
        assert!(!subjects.is_empty());
        // usvg 0.37 wraps everything in a root Group containing Path nodes
        assert_eq!(subjects[0].name, "group_of_path");
    }

    #[test]
    fn test_auto_analyze() {
        let config = CoreConfig {
            auto_analyze: true,
            ..Default::default()
        };
        let core = UniversalVectorCore::with_config(config);
        let visual = core.import_svg("test", create_test_svg()).unwrap();
        assert!(!visual.semantic.description.is_empty());
        assert!(!visual.semantic.tags.is_empty());
    }
}
