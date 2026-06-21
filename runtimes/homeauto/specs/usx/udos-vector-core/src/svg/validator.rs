use crate::error::UvcError;
use usvg::Tree as SvgTree;
use usvg::TreeParsing;

/// Validate an SVG string.
pub fn validate(svg_str: &str) -> Result<(), UvcError> {
    if svg_str.trim().is_empty() {
        return Err(UvcError::ValidationError("Empty SVG string".into()));
    }

    // Try to parse the SVG
    let tree = SvgTree::from_str(svg_str, &usvg::Options::default())?;

    // Check that the tree has a valid size
    let size = &tree.size;
    if size.width() <= 0.0 || size.height() <= 0.0 {
        return Err(UvcError::ValidationError(
            "SVG has invalid dimensions".into(),
        ));
    }

    // Check that the tree has a root node with children
    if tree.root.children().count() == 0 {
        return Err(UvcError::ValidationError("SVG has no content".into()));
    }

    Ok(())
}

/// Check if an SVG has a valid namespace.
pub fn has_valid_namespace(svg_str: &str) -> bool {
    svg_str.contains("xmlns=\"http://www.w3.org/2000/svg\"")
        || svg_str.contains("xmlns='http://www.w3.org/2000/svg'")
}

/// Get the dimensions of an SVG.
pub fn get_dimensions(svg_str: &str) -> Result<(f64, f64), UvcError> {
    let tree = SvgTree::from_str(svg_str, &usvg::Options::default())?;
    let size = &tree.size;
    Ok((size.width() as f64, size.height() as f64))
}
