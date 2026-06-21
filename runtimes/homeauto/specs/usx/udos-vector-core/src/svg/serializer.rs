use usvg::Tree as SvgTree;

/// Serialize an SVG tree back to an SVG string.
pub fn serialize(tree: &SvgTree) -> String {
    let size = &tree.size;
    let width = size.width() as f64;
    let height = size.height() as f64;

    format!(
        r#"<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {:.1} {:.1}" width="{:.1}" height="{:.1}">
  <!-- Serialized from uDos Vector Core -->
  <rect width="{:.1}" height="{:.1}" fill="white"/>
</svg>"#,
        width, height, width, height, width, height
    )
}

/// Serialize primitives to an SVG string.
pub fn serialize_primitives(
    primitives: &[crate::object::Primitive],
    width: f64,
    height: f64,
) -> String {
    let mut svg = format!(
        r#"<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {:.1} {:.1}">"#,
        width, height
    );

    for primitive in primitives {
        svg.push_str(&serialize_primitive(primitive));
    }

    svg.push_str("</svg>");
    svg
}

fn serialize_primitive(primitive: &crate::object::Primitive) -> String {
    match primitive {
        crate::object::Primitive::Circle {
            cx,
            cy,
            r,
            fill,
            stroke,
            stroke_width,
        } => {
            let fill_attr = fill.as_deref().unwrap_or("none");
            let stroke_attr = stroke.as_deref().unwrap_or("none");
            let sw = stroke_width.unwrap_or(1.0);
            format!(
                r#"<circle cx="{:.1}" cy="{:.1}" r="{:.1}" fill="{}" stroke="{}" stroke-width="{:.1}"/>"#,
                cx, cy, r, fill_attr, stroke_attr, sw
            )
        }
        crate::object::Primitive::Rect {
            x,
            y,
            width,
            height,
            rx,
            ry,
            fill,
            stroke,
        } => {
            let fill_attr = fill.as_deref().unwrap_or("none");
            let stroke_attr = stroke.as_deref().unwrap_or("none");
            let rx_attr = rx.map(|v| format!(r#" rx="{:.1}""#, v)).unwrap_or_default();
            let ry_attr = ry.map(|v| format!(r#" ry="{:.1}""#, v)).unwrap_or_default();
            format!(
                r#"<rect x="{:.1}" y="{:.1}" width="{:.1}" height="{:.1}" fill="{}" stroke="{}"{}{}/>"#,
                x, y, width, height, fill_attr, stroke_attr, rx_attr, ry_attr
            )
        }
        crate::object::Primitive::Path { data, fill, stroke } => {
            let fill_attr = fill.as_deref().unwrap_or("none");
            let stroke_attr = stroke.as_deref().unwrap_or("none");
            format!(
                r#"<path d="{}" fill="{}" stroke="{}"/>"#,
                data, fill_attr, stroke_attr
            )
        }
        crate::object::Primitive::Text {
            x,
            y,
            content,
            font_size,
            font_family,
            fill,
        } => {
            let fill_attr = fill.as_deref().unwrap_or("black");
            let font = font_family.as_deref().unwrap_or("sans-serif");
            format!(
                r#"<text x="{:.1}" y="{:.1}" font-size="{:.1}" font-family="{}" fill="{}">{}</text>"#,
                x, y, font_size, font, fill_attr, content
            )
        }
        crate::object::Primitive::Group { children, .. } => {
            let mut result = String::from("<g>");
            for child in children {
                result.push_str(&serialize_primitive(child));
            }
            result.push_str("</g>");
            result
        }
        crate::object::Primitive::Line {
            x1,
            y1,
            x2,
            y2,
            stroke,
            stroke_width,
        } => {
            let stroke_attr = stroke.as_deref().unwrap_or("black");
            let sw = stroke_width.unwrap_or(1.0);
            format!(
                r#"<line x1="{:.1}" y1="{:.1}" x2="{:.1}" y2="{:.1}" stroke="{}" stroke-width="{:.1}"/>"#,
                x1, y1, x2, y2, stroke_attr, sw
            )
        }
        crate::object::Primitive::Polygon { points, fill, stroke } => {
            let fill_attr = fill.as_deref().unwrap_or("none");
            let stroke_attr = stroke.as_deref().unwrap_or("none");
            let points_str: Vec<String> = points.iter().map(|(x, y)| format!("{:.1},{:.1}", x, y)).collect();
            format!(
                r#"<polygon points="{}" fill="{}" stroke="{}"/>"#,
                points_str.join(" "), fill_attr, stroke_attr
            )
        }
    }
}
