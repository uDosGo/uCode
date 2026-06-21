use usvg::Tree as SvgTree;

/// Generate a natural language description from an SVG tree.
///
/// Uses rule-based analysis of the SVG structure to produce
/// a human-readable description of the visual content.
pub fn describe(svg: &SvgTree) -> String {
    let primitives = crate::svg::extract_primitives(svg);
    let size = &svg.size;
    let palette = super::classifier::extract_palette(svg);
    let tags = super::classifier::generate_tags(svg);

    let mut parts: Vec<String> = Vec::new();

    // Describe the composition
    let count = primitives.len();
    if count == 0 {
        return "An empty canvas.".to_string();
    }

    // Describe shapes
    let shape_descriptions: Vec<String> = primitives
        .iter()
        .map(|p| describe_primitive(p))
        .collect();

    if shape_descriptions.len() <= 3 {
        parts.push(format!(
            "A composition containing {}.",
            shape_descriptions.join(", ")
        ));
    } else {
        parts.push(format!(
            "A complex composition with {} elements including {}.",
            count,
            shape_descriptions[..3].join(", ")
        ));
    }

    // Describe colours
    if !palette.is_empty() {
        parts.push(format!(
            "Colour palette: {}.",
            palette.join(", ")
        ));
    }

    // Describe dimensions
    parts.push(format!(
        "Dimensions: {:.0}×{:.0} pixels.",
        size.width() as f64,
        size.height() as f64
    ));

    // Tags
    if !tags.is_empty() {
        parts.push(format!(
            "Tags: {}.",
            tags.join(", ")
        ));
    }

    parts.join(" ")
}

fn describe_primitive(primitive: &crate::object::Primitive) -> String {
    match primitive {
        crate::object::Primitive::Circle { cx, cy, r, fill, .. } => {
            let colour = fill.as_deref().unwrap_or("transparent");
            format!("a {} circle at ({:.0}, {:.0}) with radius {:.0}", colour, cx, cy, r)
        }
        crate::object::Primitive::Rect { x, y, width, height, fill, .. } => {
            let colour = fill.as_deref().unwrap_or("transparent");
            format!("a {} rectangle at ({:.0}, {:.0}) size {:.0}×{:.0}", colour, x, y, width, height)
        }
        crate::object::Primitive::Path { fill, .. } => {
            let colour = fill.as_deref().unwrap_or("transparent");
            format!("a {} path", colour)
        }
        crate::object::Primitive::Text { content, .. } => {
            format!("text \"{}\"", content)
        }
        crate::object::Primitive::Group { children, .. } => {
            let descs: Vec<String> = children.iter().map(|c| describe_primitive(c)).collect();
            format!("a group containing [{}]", descs.join(", "))
        }
        crate::object::Primitive::Line { x1, y1, x2, y2, .. } => {
            format!("a line from ({:.0}, {:.0}) to ({:.0}, {:.0})", x1, y1, x2, y2)
        }
        crate::object::Primitive::Polygon { points, .. } => {
            format!("a polygon with {} vertices", points.len())
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use usvg::TreeParsing;

    #[test]
    fn test_describe_simple_svg() {
        let svg_str = r#"<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
            <rect x="10" y="10" width="80" height="80" fill="red"/>
        </svg>"#;
        let svg = SvgTree::from_str(svg_str, &usvg::Options::default()).unwrap();
        let desc = describe(&svg);
        // usvg 0.37 parses shapes into Path nodes, so we check for generic terms
        assert!(!desc.is_empty());
        assert!(desc.contains("red") || desc.contains("#ff0000"));
    }
}
