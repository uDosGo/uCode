use crate::error::UvcError;
use crate::object::Primitive;
use usvg::Tree as SvgTree;

pub mod parser;
pub mod optimizer;
pub mod serializer;
pub mod validator;

/// Parse an SVG string into an SVG tree.
pub fn parse_svg(svg_str: &str) -> Result<SvgTree, UvcError> {
    parser::parse(svg_str)
}

/// Optimize an SVG tree (simplify paths, deduplicate).
pub fn optimize_svg(tree: &SvgTree) -> Result<SvgTree, UvcError> {
    optimizer::optimize(tree)
}

/// Serialize an SVG tree back to a string.
pub fn serialize_svg(tree: &SvgTree) -> String {
    serializer::serialize(tree)
}

/// Validate an SVG string for correctness.
pub fn validate_svg(svg_str: &str) -> Result<(), UvcError> {
    validator::validate(svg_str)
}

/// Extract primitives from an SVG tree.
pub fn extract_primitives(tree: &SvgTree) -> Vec<Primitive> {
    parser::extract_primitives(tree)
}
