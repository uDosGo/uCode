use crate::object::{CompositionStyle, Direction, Layout, Orientation, Symmetry};
use std::collections::HashSet;
use usvg::{Paint, NodeKind, Tree as SvgTree};

/// Analyze the composition layout of an SVG tree.
pub fn analyze_layout(svg: &SvgTree) -> Layout {
    let primitives = crate::svg::extract_primitives(svg);
    let count = primitives.len();

    // Simple heuristic: determine composition based on element count and positions
    let composition = if count <= 1 {
        CompositionStyle::Centered
    } else if count <= 3 {
        CompositionStyle::RuleOfThirds
    } else if count <= 6 {
        CompositionStyle::Grid
    } else {
        CompositionStyle::Asymmetric
    };

    Layout {
        composition,
        balance: 0.5, // Default balanced
        focal_points: Vec::new(),
    }
}

/// Analyze the orientation of an SVG tree.
pub fn analyze_orientation(svg: &SvgTree) -> Orientation {
    let size = &svg.size;
    let is_wide = size.width() > size.height();

    Orientation {
        angle: 0.0,
        direction: if is_wide {
            Direction::East
        } else {
            Direction::North
        },
        symmetry: Symmetry::None,
    }
}

fn paint_to_string(paint: &Paint) -> String {
    match paint {
        Paint::Color(c) => format!("#{:02x}{:02x}{:02x}", c.red, c.green, c.blue),
        Paint::LinearGradient(_) => "linear-gradient".to_string(),
        Paint::RadialGradient(_) => "radial-gradient".to_string(),
        Paint::Pattern(_) => "pattern".to_string(),
    }
}

/// Extract the colour palette from an SVG tree.
pub fn extract_palette(svg: &SvgTree) -> Vec<String> {
    let mut colours = HashSet::new();

    collect_colours(&svg.root, &mut colours);

    let mut palette: Vec<String> = colours.into_iter().collect();
    palette.sort();
    palette
}

fn collect_colours(node: &usvg::Node, colours: &mut HashSet<String>) {
    let kind = node.borrow();
    match &*kind {
        NodeKind::Path(path) => {
            if let Some(ref fill) = path.fill {
                colours.insert(paint_to_string(&fill.paint));
            }
            if let Some(ref stroke) = path.stroke {
                colours.insert(paint_to_string(&stroke.paint));
            }
        }
        NodeKind::Text(_text) => {
            // Text fill is not directly accessible in usvg 0.37 Text struct
        }
        NodeKind::Group(_group) => {
            for child in node.children() {
                collect_colours(&child, colours);
            }
        }
        _ => {}
    }
}

/// Recursively check if any primitive (including nested in groups) matches a predicate.
fn has_primitive_type(primitives: &[crate::object::Primitive], pred: fn(&crate::object::Primitive) -> bool) -> bool {
    primitives.iter().any(|p| {
        if pred(p) {
            return true;
        }
        if let crate::object::Primitive::Group { children, .. } = p {
            has_primitive_type(children, pred)
        } else {
            false
        }
    })
}

/// Generate tags for an SVG tree based on its content.
pub fn generate_tags(svg: &SvgTree) -> Vec<String> {
    let mut tags = Vec::new();
    let primitives = crate::svg::extract_primitives(svg);
    let size = &svg.size;

    // Size-based tags
    if size.width() > 100.0 || size.height() > 100.0 {
        tags.push("large".to_string());
    } else {
        tags.push("small".to_string());
    }

    // Shape-based tags (recursively check inside groups)
    let has_circle = has_primitive_type(&primitives, |p| matches!(p, crate::object::Primitive::Circle { .. }));
    let has_rect = has_primitive_type(&primitives, |p| matches!(p, crate::object::Primitive::Rect { .. }));
    let has_path = has_primitive_type(&primitives, |p| matches!(p, crate::object::Primitive::Path { .. }));
    let has_text = has_primitive_type(&primitives, |p| matches!(p, crate::object::Primitive::Text { .. }));

    if has_circle { tags.push("circle".to_string()); }
    if has_rect { tags.push("rectangle".to_string()); }
    if has_path { tags.push("path".to_string()); }
    if has_text { tags.push("text".to_string()); }

    // Complexity tag
    if primitives.len() > 5 {
        tags.push("complex".to_string());
    } else {
        tags.push("simple".to_string());
    }

    tags
}

#[cfg(test)]
mod tests {
    use super::*;
    use usvg::TreeParsing;

    fn create_test_svg() -> SvgTree {
        let svg_str = r#"<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
            <circle cx="50" cy="50" r="40" fill="red"/>
            <rect x="10" y="10" width="20" height="20" fill="blue"/>
        </svg>"#;
        SvgTree::from_str(svg_str, &usvg::Options::default()).unwrap()
    }

    #[test]
    fn test_extract_palette() {
        let svg = create_test_svg();
        let palette = extract_palette(&svg);
        assert!(palette.contains(&"#ff0000".to_string()));
        assert!(palette.contains(&"#0000ff".to_string()));
    }

    #[test]
    fn test_generate_tags() {
        let svg = create_test_svg();
        let tags = generate_tags(&svg);
        // usvg 0.37 parses shapes into Path nodes
        assert!(tags.contains(&"path".to_string()));
        assert!(tags.contains(&"small".to_string()));
    }
}
