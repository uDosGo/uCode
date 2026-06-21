use crate::object::Primitive;
use usvg::Tree as SvgTree;

/// Render an SVG tree to ASCII art.
///
/// Rasterizes the SVG to a pixel grid, then maps each pixel block
/// to an ASCII character based on brightness.
pub fn render(svg: &SvgTree, width: usize, height: usize) -> String {
    // Rasterize to a small grid
    let pixmap = match rasterize_to_grayscale(svg, width, height) {
        Some(p) => p,
        None => return String::from("[ASCII render failed]"),
    };

    // ASCII gradient (dark to light)
    let gradient = [' ', '.', ':', '-', '=', '+', '*', '#', '%', '@'];
    let mut result = String::new();

    for y in 0..height {
        for x in 0..width {
            let idx = y * width + x;
            let brightness = pixmap[idx];
            let char_idx = (brightness as f32 / 255.0 * (gradient.len() - 1) as f32).round() as usize;
            result.push(gradient[char_idx.min(gradient.len() - 1)]);
        }
        result.push('\n');
    }

    result
}

/// Render primitives to ASCII art.
pub fn render_primitives(primitives: &[Primitive], width: usize, height: usize) -> String {
    // Create a temporary SVG from primitives, then render
    let svg = crate::svg::serializer::serialize_primitives(primitives, width as f64, height as f64);
    match crate::svg::parser::parse(&svg) {
        Ok(tree) => render(&tree, width, height),
        Err(_) => String::from("[ASCII render failed]"),
    }
}

/// Rasterize an SVG to a grayscale pixel buffer.
fn rasterize_to_grayscale(svg: &SvgTree, width: usize, height: usize) -> Option<Vec<u8>> {
    let w = width as u32;
    let h = height as u32;

    let mut pixmap = resvg::tiny_skia::Pixmap::new(w, h)?;

    let svg_size = &svg.size;
    let transform = resvg::tiny_skia::Transform::from_scale(
        width as f32 / svg_size.width(),
        height as f32 / svg_size.height(),
    );

    let rtree = resvg::Tree::from_usvg(svg);
    rtree.render(transform, &mut pixmap.as_mut());

    // Convert RGBA to grayscale
    let data = pixmap.data();
    let mut grayscale = vec![0u8; width * height];

    for y in 0..height {
        for x in 0..width {
            let idx = (y * width + x) * 4;
            let r = data[idx];
            let g = data[idx + 1];
            let b = data[idx + 2];
            // Standard luminance weights
            let luminance = (0.299 * r as f32 + 0.587 * g as f32 + 0.114 * b as f32) as u8;
            grayscale[y * width + x] = luminance;
        }
    }

    Some(grayscale)
}

#[cfg(test)]
mod tests {
    use super::*;
    use usvg::TreeParsing;

    fn create_test_svg() -> SvgTree {
        let svg_str = r#"<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
            <rect x="2" y="2" width="20" height="20" fill="black"/>
        </svg>"#;
        SvgTree::from_str(svg_str, &usvg::Options::default()).unwrap()
    }

    #[test]
    fn test_ascii_render() {
        let svg = create_test_svg();
        let ascii = render(&svg, 8, 8);
        assert!(!ascii.is_empty());
        assert_eq!(ascii.lines().count(), 8);
    }
}
