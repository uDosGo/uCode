use crate::error::UvcError;
use usvg::Tree as SvgTree;

/// Teletext colour values
#[derive(Debug, Clone, Copy, PartialEq)]
pub enum TeletextColour {
    Black,
    Red,
    Green,
    Yellow,
    Blue,
    Magenta,
    Cyan,
    White,
}

impl TeletextColour {
    pub fn from_rgb(r: u8, g: u8, b: u8) -> Self {
        // Find the closest teletext colour
        let colours = [
            (0, 0, 0, TeletextColour::Black),
            (255, 0, 0, TeletextColour::Red),
            (0, 255, 0, TeletextColour::Green),
            (255, 255, 0, TeletextColour::Yellow),
            (0, 0, 255, TeletextColour::Blue),
            (255, 0, 255, TeletextColour::Magenta),
            (0, 255, 255, TeletextColour::Cyan),
            (255, 255, 255, TeletextColour::White),
        ];

        colours
            .iter()
            .min_by_key(|(cr, cg, cb, _)| {
                let dr = (r as i32) - (*cr as i32);
                let dg = (g as i32) - (*cg as i32);
                let db = (b as i32) - (*cb as i32);
                dr * dr + dg * dg + db * db
            })
            .map(|(_, _, _, col)| *col)
            .unwrap_or(TeletextColour::White)
    }
}

/// A single teletext cell
#[derive(Debug, Clone)]
pub struct TeletextCell {
    pub character: char,
    pub foreground: TeletextColour,
    pub background: TeletextColour,
    pub flash: bool,
    pub inverse: bool,
    pub double_height: bool,
    pub double_width: bool,
    pub concealed: bool,
}

impl Default for TeletextCell {
    fn default() -> Self {
        Self {
            character: ' ',
            foreground: TeletextColour::White,
            background: TeletextColour::Black,
            flash: false,
            inverse: false,
            double_height: false,
            double_width: false,
            concealed: false,
        }
    }
}

/// A teletext grid (standard 40×25)
#[derive(Debug, Clone)]
pub struct TeletextGrid {
    pub width: usize,
    pub height: usize,
    pub cells: Vec<TeletextCell>,
}

impl TeletextGrid {
    pub fn new(width: usize, height: usize) -> Self {
        Self {
            width,
            height,
            cells: vec![TeletextCell::default(); width * height],
        }
    }

    /// Get a cell at (x, y)
    pub fn get(&self, x: usize, y: usize) -> Option<&TeletextCell> {
        if x < self.width && y < self.height {
            Some(&self.cells[y * self.width + x])
        } else {
            None
        }
    }

    /// Set a cell at (x, y)
    pub fn set(&mut self, x: usize, y: usize, cell: TeletextCell) {
        if x < self.width && y < self.height {
            self.cells[y * self.width + x] = cell;
        }
    }

    /// Render the grid to a string (for display)
    pub fn to_string(&self) -> String {
        let mut result = String::new();
        for y in 0..self.height {
            for x in 0..self.width {
                if let Some(cell) = self.get(x, y) {
                    result.push(cell.character);
                }
            }
            result.push('\n');
        }
        result
    }
}

/// Render an SVG tree to a Teletext grid (40×25).
pub fn render(svg: &SvgTree) -> Result<String, UvcError> {
    let width = 40;
    let height = 25;

    // Rasterize SVG to 40×25 pixel grid
    let pixmap = rasterize_to_rgba(svg, width, height)
        .ok_or_else(|| UvcError::RasterizationError("Failed to rasterize for teletext".into()))?;

    let mut grid = TeletextGrid::new(width, height);

    for y in 0..height {
        for x in 0..width {
            let idx = (y * width + x) * 4;
            let r = pixmap[idx];
            let g = pixmap[idx + 1];
            let b = pixmap[idx + 2];
            let a = pixmap[idx + 3];

            let brightness = (0.299 * r as f32 + 0.587 * g as f32 + 0.114 * b as f32) as u8;

            let character = if a < 128 {
                ' '  // Transparent
            } else if brightness > 200 {
                '█'  // Bright
            } else if brightness > 150 {
                '▓'  // Medium bright
            } else if brightness > 100 {
                '▒'  // Medium
            } else if brightness > 50 {
                '░'  // Medium dark
            } else {
                ' '  // Dark
            };

            grid.set(x, y, TeletextCell {
                character,
                foreground: TeletextColour::from_rgb(r, g, b),
                background: TeletextColour::Black,
                ..Default::default()
            });
        }
    }

    Ok(grid.to_string())
}

/// Rasterize an SVG to an RGBA pixel buffer.
fn rasterize_to_rgba(svg: &SvgTree, width: usize, height: usize) -> Option<Vec<u8>> {
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

    Some(pixmap.data().to_vec())
}

#[cfg(test)]
mod tests {
    use super::*;
    use usvg::TreeParsing;

    fn create_test_svg() -> SvgTree {
        let svg_str = r#"<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 40 25">
            <rect x="0" y="0" width="40" height="25" fill="white"/>
            <circle cx="20" cy="12" r="8" fill="red"/>
        </svg>"#;
        SvgTree::from_str(svg_str, &usvg::Options::default()).unwrap()
    }

    #[test]
    fn test_teletext_render() {
        let svg = create_test_svg();
        let result = render(&svg).unwrap();
        assert!(!result.is_empty());
        assert_eq!(result.lines().count(), 25);
        for line in result.lines() {
            // Use chars().count() because teletext uses multi-byte Unicode block characters
            assert_eq!(line.chars().count(), 40);
        }
    }
}
