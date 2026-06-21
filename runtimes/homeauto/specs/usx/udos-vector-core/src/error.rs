use thiserror::Error;

#[derive(Error, Debug)]
pub enum UvcError {
    #[error("SVG parsing error: {0}")]
    SvgParse(#[from] usvg::Error),

    #[error("IO error: {0}")]
    Io(#[from] std::io::Error),

    #[error("Image error: {0}")]
    Image(#[from] image::ImageError),

    #[error("Serialization error: {0}")]
    Serde(#[from] serde_json::Error),

    #[error("Bundle not found: {0}")]
    BundleNotFound(String),

    #[error("Circular dependency detected: {0}")]
    CircularDependency(String),

    #[error("Missing dependency: {0}")]
    MissingDependency(String),

    #[error("Invalid dimensions: width={width}, height={height}")]
    InvalidDimensions { width: u16, height: u16 },

    #[error("Unsupported format: {0}")]
    UnsupportedFormat(String),

    #[error("Semantic analysis failed: {0}")]
    SemanticError(String),

    #[error("Vectorization failed: {0}")]
    VectorizationError(String),

    #[error("Rasterization failed: {0}")]
    RasterizationError(String),

    #[error("Validation error: {0}")]
    ValidationError(String),

    #[error("Not implemented: {0}")]
    NotImplemented(String),
}
