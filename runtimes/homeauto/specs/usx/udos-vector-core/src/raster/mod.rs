use crate::error::UvcError;
use crate::object::CellGrid;
use usvg::Tree as SvgTree;

/// Rasterize an SVG tree to a uDos Cell (24×24 pixels).
pub fn render_to_cell(svg: &SvgTree) -> Result<CellGrid, UvcError> {
    render_to_size(svg, 24, 24)
}

/// Rasterize an SVG tree to a CELX (24×width pixels).
pub fn render_to_celx(svg: &SvgTree, width: u16) -> Result<CellGrid, UvcError> {
    render_to_size(svg, width, 24)
}

/// Rasterize an SVG tree to a thumbnail (64×64 pixels).
pub fn render_to_thumbnail(svg: &SvgTree) -> Result<CellGrid, UvcError> {
    render_to_size(svg, 64, 64)
}

/// Rasterize an SVG tree to a specific pixel size.
///
/// Uses resvg to render the SVG tree to an RGBA pixel buffer.
/// The output is a CellGrid with width × height RGBA pixels.
fn render_to_size(svg: &SvgTree, width: u16, height: u16) -> Result<CellGrid, UvcError> {
    // Create a pixmap and render
    let mut pixmap = resvg::tiny_skia::Pixmap::new(width as u32, height as u32)
        .ok_or_else(|| UvcError::RasterizationError(
            format!("Failed to create pixmap {}x{}", width, height)
        ))?;

    // Fit the SVG into the target viewport
    let svg_size = &svg.size;
    let transform = resvg::tiny_skia::Transform::from_scale(
        width as f32 / svg_size.width(),
        height as f32 / svg_size.height(),
    );

    // Create a resvg Tree from the usvg tree and render
    let rtree = resvg::Tree::from_usvg(svg);
    rtree.render(transform, &mut pixmap.as_mut());

    // Extract RGBA pixels
    let pixels = pixmap.data().to_vec();

    Ok(CellGrid {
        width,
        height,
        pixels,
    })
}

/// Export a CellGrid to PNG bytes.
pub fn export_png(grid: &CellGrid) -> Result<Vec<u8>, UvcError> {
    use image::{ImageBuffer, Rgba};

    let img: ImageBuffer<Rgba<u8>, Vec<u8>> =
        ImageBuffer::from_raw(grid.width as u32, grid.height as u32, grid.pixels.clone())
            .ok_or_else(|| UvcError::RasterizationError(
                format!("Failed to create image from grid {}x{}", grid.width, grid.height)
            ))?;

    let mut bytes = Vec::new();
    img.write_to(&mut std::io::Cursor::new(&mut bytes), image::ImageFormat::Png)?;

    Ok(bytes)
}

/// Quantize a CellGrid to a limited palette (for uDos cell storage).
pub fn quantize_to_palette(grid: &CellGrid, palette: &[[u8; 4]]) -> CellGrid {
    let mut quantized = grid.pixels.clone();

    for chunk in quantized.chunks_exact_mut(4) {
        let mut best_dist = f64::MAX;
        let mut best_color = [0u8; 4];

        for color in palette {
            let dr = f64::from(chunk[0]) - f64::from(color[0]);
            let dg = f64::from(chunk[1]) - f64::from(color[1]);
            let db = f64::from(chunk[2]) - f64::from(color[2]);
            let da = f64::from(chunk[3]) - f64::from(color[3]);
            let dist = dr * dr + dg * dg + db * db + da * da;

            if dist < best_dist {
                best_dist = dist;
                best_color = *color;
            }
        }

        chunk.copy_from_slice(&best_color);
    }

    CellGrid {
        width: grid.width,
        height: grid.height,
        pixels: quantized,
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use usvg::TreeParsing;

    fn create_test_svg() -> SvgTree {
        let svg_str = r#"<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
            <circle cx="12" cy="12" r="10" fill="red"/>
        </svg>"#;
        SvgTree::from_str(svg_str, &usvg::Options::default()).unwrap()
    }

    #[test]
    fn test_render_to_cell() {
        let svg = create_test_svg();
        let cell = render_to_cell(&svg).unwrap();
        assert_eq!(cell.width, 24);
        assert_eq!(cell.height, 24);
        assert_eq!(cell.pixels.len(), 24 * 24 * 4); // RGBA
    }

    #[test]
    fn test_render_to_celx() {
        let svg = create_test_svg();
        let celx = render_to_celx(&svg, 48).unwrap();
        assert_eq!(celx.width, 48);
        assert_eq!(celx.height, 24);
    }

    #[test]
    fn test_export_png() {
        let svg = create_test_svg();
        let cell = render_to_cell(&svg).unwrap();
        let png = export_png(&cell).unwrap();
        assert!(!png.is_empty());
        // PNG header
        assert_eq!(&png[..8], &[137, 80, 78, 71, 13, 10, 26, 10]);
    }
}
