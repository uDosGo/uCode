use crate::error::UvcError;
use crate::object::Primitive;
use usvg::{Paint, Tree as SvgTree, NodeKind};
use usvg::TreeParsing;

/// Parse an SVG string into an SVG tree.
pub fn parse(svg_str: &str) -> Result<SvgTree, UvcError> {
    let tree = SvgTree::from_str(svg_str, &usvg::Options::default())?;
    Ok(tree)
}

/// Extract primitives from an SVG tree by traversing the node tree.
pub fn extract_primitives(tree: &SvgTree) -> Vec<Primitive> {
    let mut primitives = Vec::new();
    traverse_node(&tree.root, &mut primitives);
    primitives
}

fn paint_to_string(paint: &Paint) -> String {
    match paint {
        Paint::Color(c) => format!("#{:02x}{:02x}{:02x}", c.red, c.green, c.blue),
        Paint::LinearGradient(_) => "linear-gradient".to_string(),
        Paint::RadialGradient(_) => "radial-gradient".to_string(),
        Paint::Pattern(_) => "pattern".to_string(),
    }
}

fn traverse_node(node: &usvg::Node, primitives: &mut Vec<Primitive>) {
    let kind = node.borrow();
    match &*kind {
        NodeKind::Path(path) => {
            let fill = path.fill.as_ref().map(|f| paint_to_string(&f.paint));
            let stroke = path.stroke.as_ref().map(|s| paint_to_string(&s.paint));
            let _stroke_width = path.stroke.as_ref().map(|s| s.width.get());

            primitives.push(Primitive::Path {
                data: format!("{:?}", path.data),
                fill,
                stroke,
            });
        }
        NodeKind::Text(text) => {
            // Text position comes from the first chunk's x/y
            let x = text.chunks.first().and_then(|c| c.x).unwrap_or(0.0);
            let y = text.chunks.first().and_then(|c| c.y).unwrap_or(0.0);
            let content = text.chunks.iter()
                .map(|c| c.text.as_str())
                .collect::<Vec<_>>()
                .join("");

            primitives.push(Primitive::Text {
                x: x as f64,
                y: y as f64,
                content,
                font_size: 12.0, // Default font size
                font_family: None,
                fill: None,
            });
        }
        NodeKind::Group(_group) => {
            let mut children = Vec::new();
            for child in node.children() {
                traverse_node(&child, &mut children);
            }
            primitives.push(Primitive::Group {
                children,
                transform: None,
            });
        }
        NodeKind::Image(_) => {}
    }
}
