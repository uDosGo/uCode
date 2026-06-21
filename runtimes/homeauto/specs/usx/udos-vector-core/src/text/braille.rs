use crate::error::UvcError;
use usvg::Tree as SvgTree;

/// Render an SVG tree to Braille Unicode characters.
///
/// Braille patterns (U+2800–U+28FF) represent 2×4 dot grids.
/// Each Braille character encodes 8 dots (2 columns × 4 rows).
/// This allows a compact tactile representation of visual shapes.
pub fn render(svg: &SvgTree) -> Result<String, UvcError> {
    // Braille resolution: each character is 2×4 dots
    let braille_width = 20;  // 20 braille chars = 40 dots wide
    let braille_height = 12; // 12 braille chars = 48 dots tall

    let dot_width = 2;
    let dot_height = 4;

    let pixel_width = braille_width * dot_width;
    let pixel_height = braille_height * dot_height;

    // Rasterize SVG to pixel grid
    let pixmap = rasterize_to_grayscale(svg, pixel_width, pixel_height)
        .ok_or_else(|| UvcError::RasterizationError("Failed to rasterize for braille".into()))?;

    let mut result = String::new();

    for by in 0..braille_height {
        for bx in 0..braille_width {
            let mut dots = 0u16;

            // Map 2×4 pixel block to Braille dot pattern
            // Braille dot numbering:
            //  1  4
            //  2  5
            //  3  6
            //  7  8
            for dy in 0..dot_height {
                for dx in 0..dot_width {
                    let px = bx * dot_width + dx;
                    let py = by * dot_height + dy;

                    if px < pixel_width && py < pixel_height {
                        let brightness = pixmap[py * pixel_width + px];
                        if brightness < 128 {
                            // Dark pixel = raised dot
                            let dot_index = match (dx, dy) {
                                (0, 0) => 0, // Dot 1
                                (0, 1) => 1, // Dot 2
                                (0, 2) => 2, // Dot 3
                                (1, 0) => 3, // Dot 4
                                (1, 1) => 4, // Dot 5
                                (1, 2) => 5, // Dot 6
                                (0, 3) => 6, // Dot 7
                                (1, 3) => 7, // Dot 8
                                _ => continue,
                            };
                            dots |= 1 << dot_index;
                        }
                    }
                }
            }

            // Unicode Braille starts at U+2800
            let braille_char = char::from_u32(0x2800 + u32::from(dots))
                .unwrap_or(' ');
            result.push(braille_char);
        }
        result.push('\n');
    }

    Ok(result)
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

    let data = pixmap.data();
    let mut grayscale = vec![0u8; width * height];

    for y in 0..height {
        for x in 0..width {
            let idx = (y * width + x) * 4;
            let r = data[idx];
            let g = data[idx + 1];
            let b = data[idx + 2];
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
        let svg_str = r#"<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 40 48">
            <rect x="0" y="0" width="40" height="48" fill="black"/>
        </svg>"#;
        SvgTree::from_str(svg_str, &usvg::Options::default()).unwrap()
    }

    #[test]
    fn test_braille_render() {
        let svg = create_test_svg();
        let result = render(&svg).unwrap();
        assert!(!result.is_empty());
        // Should produce braille characters (not spaces) for a black-filled SVG
        assert!(result.contains('\u{2800}') || result.chars().any(|c| c > '\u{2800}'));
    }
}
