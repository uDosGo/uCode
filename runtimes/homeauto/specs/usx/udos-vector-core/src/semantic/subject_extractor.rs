use crate::object::{BoundingBox, Subject};
use usvg::Tree as SvgTree;

/// Extract subjects from an SVG tree.
///
/// Identifies distinct visual elements and classifies them
/// into subject categories based on shape and position.
pub fn extract(svg: &SvgTree) -> Vec<Subject> {
    let primitives = crate::svg::extract_primitives(svg);
    let mut subjects = Vec::new();

    for (_i, primitive) in primitives.iter().enumerate() {
        let (name, bbox) = classify_primitive(primitive);
        subjects.push(Subject {
            name,
            position: bbox,
            confidence: 0.7, // Rule-based confidence
            attributes: Vec::new(),
        });
    }

    subjects
}

/// Classify a primitive into a subject category and compute its bounding box.
fn classify_primitive(primitive: &crate::object::Primitive) -> (String, BoundingBox) {
    match primitive {
        crate::object::Primitive::Circle { cx, cy, r, .. } => {
            ("circle".to_string(), BoundingBox {
                x: cx - r,
                y: cy - r,
                width: r * 2.0,
                height: r * 2.0,
            })
        }
        crate::object::Primitive::Rect { x, y, width, height, .. } => {
            ("rectangle".to_string(), BoundingBox {
                x: *x,
                y: *y,
                width: *width,
                height: *height,
            })
        }
        crate::object::Primitive::Path { .. } => {
            ("path".to_string(), BoundingBox {
                x: 0.0, y: 0.0, width: 0.0, height: 0.0,
            })
        }
        crate::object::Primitive::Text { x, y, content, .. } => {
            ("text".to_string(), BoundingBox {
                x: *x,
                y: *y,
                width: content.len() as f64 * 8.0, // Approximate
                height: 16.0,
            })
        }
        crate::object::Primitive::Group { children, .. } => {
            if children.is_empty() {
                ("group".to_string(), BoundingBox::default())
            } else {
                let (name, _) = classify_primitive(&children[0]);
                (format!("group_of_{}", name), BoundingBox::default())
            }
        }
        crate::object::Primitive::Line { x1, y1, x2, y2, .. } => {
            ("line".to_string(), BoundingBox {
                x: x1.min(*x2),
                y: y1.min(*y2),
                width: (x1 - x2).abs(),
                height: (y1 - y2).abs(),
            })
        }
        crate::object::Primitive::Polygon { points, .. } => {
            let xs: Vec<f64> = points.iter().map(|(x, _)| *x).collect();
            let ys: Vec<f64> = points.iter().map(|(_, y)| *y).collect();
            let min_x = xs.iter().cloned().fold(f64::INFINITY, f64::min);
            let max_x = xs.iter().cloned().fold(f64::NEG_INFINITY, f64::max);
            let min_y = ys.iter().cloned().fold(f64::INFINITY, f64::min);
            let max_y = ys.iter().cloned().fold(f64::NEG_INFINITY, f64::max);

            ("polygon".to_string(), BoundingBox {
                x: min_x,
                y: min_y,
                width: max_x - min_x,
                height: max_y - min_y,
            })
        }
    }
}

impl Default for BoundingBox {
    fn default() -> Self {
        Self {
            x: 0.0,
            y: 0.0,
            width: 0.0,
            height: 0.0,
        }
    }
}
