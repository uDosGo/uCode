use usvg::Tree as SvgTree;

/// Generate a regeneration prompt from an SVG tree.
///
/// Creates a text prompt that could be used to regenerate the visual
/// with an AI image generator.
pub fn to_prompt(svg: &SvgTree) -> String {
    let primitives = crate::svg::extract_primitives(svg);
    let palette = super::classifier::extract_palette(svg);
    let tags = super::classifier::generate_tags(svg);
    let size = &svg.size;

    let mut parts: Vec<String> = Vec::new();

    // Describe the visual style
    parts.push("A visual composition".to_string());

    // Add shape descriptions
    let shape_descriptions: Vec<String> = primitives
        .iter()
        .map(|p| describe_primitive_for_prompt(p))
        .collect();

    if !shape_descriptions.is_empty() {
        parts.push(format!("featuring {}", shape_descriptions.join(", ")));
    }

    // Add colour palette
    if !palette.is_empty() {
        parts.push(format!("in {} colours", palette.join(", ")));
    }

    // Add style tags
    if tags.contains(&"simple".to_string()) {
        parts.push("minimalist style".to_string());
    } else if tags.contains(&"complex".to_string()) {
        parts.push("detailed style".to_string());
    }

    // Add dimensions
    parts.push(format!(
        "at {:.0}×{:.0} resolution",
        size.width() as f64,
        size.height() as f64
    ));

    parts.join(", ")
}

fn describe_primitive_for_prompt(primitive: &crate::object::Primitive) -> String {
    match primitive {
        crate::object::Primitive::Circle { r, fill, .. } => {
            let colour = fill.as_deref().unwrap_or("transparent");
            format!("a {} circle (radius {:.0})", colour, r)
        }
        crate::object::Primitive::Rect { width, height, fill, .. } => {
            let colour = fill.as_deref().unwrap_or("transparent");
            format!("a {} rectangle ({:.0}×{:.0})", colour, width, height)
        }
        crate::object::Primitive::Path { fill, .. } => {
            let colour = fill.as_deref().unwrap_or("transparent");
            format!("a {} curved shape", colour)
        }
        crate::object::Primitive::Text { content, .. } => {
            format!("text \"{}\"", content)
        }
        crate::object::Primitive::Group { children, .. } => {
            let descs: Vec<String> = children.iter().map(|c| describe_primitive_for_prompt(c)).collect();
            format!("group [{}]", descs.join(", "))
        }
        crate::object::Primitive::Line { .. } => "a line".to_string(),
        crate::object::Primitive::Polygon { points, .. } => {
            format!("a polygon ({} sides)", points.len())
        }
    }
}
