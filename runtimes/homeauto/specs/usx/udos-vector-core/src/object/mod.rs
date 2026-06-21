use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use usvg::Tree as SvgTree;

/// Universal Visual Object — the single source of truth for all visual assets.
///
/// Every visual in the uDos system (cell, sprite, BOB, icon, UI element)
/// is represented as a UniversalVisual. The SVG tree is the canonical form;
/// all other representations (rasters, text, semantic) are derived from it.
#[derive(Clone, Serialize, Deserialize)]
pub struct UniversalVisual {
    /// Unique identifier (UUID v4)
    pub id: String,

    /// Human-readable name
    pub name: String,

    /// Vector representation (SVG tree — the source of truth)
    #[serde(skip)]
    pub svg: Option<SvgTree>,

    /// Original SVG string (for serialization/storage)
    pub svg_source: Option<String>,

    /// Optimized SVG string (simplified paths, deduplicated)
    pub svg_optimized: Option<String>,

    /// Raster representations (cached)
    pub rasters: HashMap<RasterType, CellGrid>,

    /// Text representations (ASCII, Teletext, Braille)
    pub texts: HashMap<TextType, String>,

    /// Semantic metadata (description, subjects, layout)
    pub semantic: SemanticMetadata,

    /// Provenance trail (transformations, regenerations)
    pub provenance: Provenance,

    /// Timestamps
    pub created_at: u64,
    pub updated_at: u64,
}

impl UniversalVisual {
    pub fn new(id: String, name: String) -> Self {
        let now = chrono::Utc::now().timestamp() as u64;
        Self {
            id,
            name,
            svg: None,
            svg_source: None,
            svg_optimized: None,
            rasters: HashMap::new(),
            texts: HashMap::new(),
            semantic: SemanticMetadata::default(),
            provenance: Provenance::default(),
            created_at: now,
            updated_at: now,
        }
    }
}

/// Types of raster representations
#[derive(Debug, Clone, Hash, PartialEq, Eq, Serialize, Deserialize)]
pub enum RasterType {
    /// 24×24 pixel cell
    Cell24,
    /// 24×width flexible cell
    Celx { width: u16 },
    /// 64×64 thumbnail
    Thumbnail,
    /// Original size
    Full,
}

/// A grid of pixel cells (the uDos native raster format)
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct CellGrid {
    pub width: u16,
    pub height: u16,
    pub pixels: Vec<u8>,  // RGBA pixel data
}

/// Types of text representations
#[derive(Debug, Clone, Hash, PartialEq, Eq, Serialize, Deserialize)]
pub enum TextType {
    /// ASCII art
    Ascii,
    /// Teletext character grid (40×25)
    Teletext,
    /// Braille for vision-impaired
    Braille,
    /// Natural language description
    Description,
}

/// Semantic metadata for a visual object
#[derive(Debug, Clone, Default, Serialize, Deserialize)]
pub struct SemanticMetadata {
    /// Human-readable description
    pub description: String,

    /// Regeneration prompt (for AI)
    pub prompt: String,

    /// Identified subjects/objects
    pub subjects: Vec<Subject>,

    /// Composition layout
    pub layout: Layout,

    /// Orientation/direction
    pub orientation: Orientation,

    /// Colour palette (hex strings)
    pub palette: Vec<String>,

    /// Tags for search/classification
    pub tags: Vec<String>,

    /// Confidence scores (0.0–1.0)
    pub confidence: HashMap<String, f32>,
}

/// A subject identified within a visual
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Subject {
    pub name: String,
    pub position: BoundingBox,
    pub confidence: f32,
    pub attributes: Vec<String>,
}

/// Bounding box in SVG coordinate space
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct BoundingBox {
    pub x: f64,
    pub y: f64,
    pub width: f64,
    pub height: f64,
}

/// Composition layout analysis
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Layout {
    pub composition: CompositionStyle,
    pub balance: f32,
    pub focal_points: Vec<(f64, f64)>,
}

impl Default for Layout {
    fn default() -> Self {
        Self {
            composition: CompositionStyle::Centered,
            balance: 0.5,
            focal_points: Vec::new(),
        }
    }
}

/// Composition style classification
#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum CompositionStyle {
    Centered,
    RuleOfThirds,
    Diagonal,
    Radial,
    Grid,
    Asymmetric,
    Custom(String),
}

impl Default for CompositionStyle {
    fn default() -> Self {
        CompositionStyle::Centered
    }
}

/// Orientation analysis
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Orientation {
    pub angle: f32,
    pub direction: Direction,
    pub symmetry: Symmetry,
}

impl Default for Orientation {
    fn default() -> Self {
        Self {
            angle: 0.0,
            direction: Direction::None,
            symmetry: Symmetry::None,
        }
    }
}

/// Cardinal/intercardinal direction
#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum Direction {
    North,
    NorthEast,
    East,
    SouthEast,
    South,
    SouthWest,
    West,
    NorthWest,
    Center,
    Random,
    None,
}

/// Symmetry type
#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum Symmetry {
    None,
    Horizontal,
    Vertical,
    Diagonal,
    Radial,
}

/// Provenance trail tracking the history of a visual object
#[derive(Debug, Clone, Default, Serialize, Deserialize)]
pub struct Provenance {
    /// Parent object IDs (if derived from another visual)
    pub parents: Vec<String>,

    /// Child object IDs (if this visual was split)
    pub children: Vec<String>,

    /// Transformations applied
    pub transformations: Vec<Transformation>,

    /// Source format (if imported from external file)
    pub source: Option<Source>,

    /// Regeneration history
    pub regenerations: Vec<RegenerationEvent>,
}

/// A transformation applied to a visual
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Transformation {
    pub timestamp: u64,
    pub operation: String,
    pub params: serde_json::Value,
}

/// Source information for imported visuals
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Source {
    pub format: String,
    pub original_hash: String,
    pub import_timestamp: u64,
}

/// A regeneration event (AI-based regeneration)
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct RegenerationEvent {
    pub timestamp: u64,
    pub prompt_used: String,
    pub model: String,
    pub result_id: String,
    pub quality_score: f32,
}

/// Primitive vector shapes
#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum Primitive {
    Circle {
        cx: f64,
        cy: f64,
        r: f64,
        fill: Option<String>,
        stroke: Option<String>,
        stroke_width: Option<f64>,
    },
    Rect {
        x: f64,
        y: f64,
        width: f64,
        height: f64,
        rx: Option<f64>,
        ry: Option<f64>,
        fill: Option<String>,
        stroke: Option<String>,
    },
    Path {
        data: String,
        fill: Option<String>,
        stroke: Option<String>,
    },
    Text {
        x: f64,
        y: f64,
        content: String,
        font_size: f64,
        font_family: Option<String>,
        fill: Option<String>,
    },
    Group {
        children: Vec<Primitive>,
        transform: Option<String>,
    },
    Line {
        x1: f64,
        y1: f64,
        x2: f64,
        y2: f64,
        stroke: Option<String>,
        stroke_width: Option<f64>,
    },
    Polygon {
        points: Vec<(f64, f64)>,
        fill: Option<String>,
        stroke: Option<String>,
    },
}
