use crate::error::UvcError;
use crate::object::Primitive;
use std::collections::HashMap;
use usvg::Tree as SvgTree;

pub mod ascii;
pub mod teletext;
pub mod braille;

/// Convert an SVG tree to ASCII art.
pub fn to_ascii(svg: &SvgTree, width: usize, height: usize) -> String {
    ascii::render(svg, width, height)
}

/// Convert an SVG tree to a Teletext grid (40×25).
pub fn to_teletext(svg: &SvgTree) -> Result<String, UvcError> {
    teletext::render(svg)
}

/// Convert an SVG tree to Braille.
pub fn to_braille(svg: &SvgTree) -> Result<String, UvcError> {
    braille::render(svg)
}

/// Convert primitives to ASCII art.
pub fn primitives_to_ascii(primitives: &[Primitive], width: usize, height: usize) -> String {
    ascii::render_primitives(primitives, width, height)
}

/// Character-to-shape mapping for ASCII/Teletext conversion.
#[derive(Debug, Clone)]
pub struct CharMapper {
    /// Maps ASCII characters to shape descriptions
    char_to_shape: HashMap<char, Shape>,
}

#[derive(Debug, Clone)]
pub enum Shape {
    Circle { radius: f64, filled: bool },
    Square { size: f64, filled: bool },
    Triangle { orientation: crate::object::Direction },
    Line { angle: f32 },
    Cross { thickness: f64 },
    Dot { radius: f64 },
    Complex(Vec<String>),
}

impl Default for CharMapper {
    fn default() -> Self {
        let mut map = HashMap::new();
        map.insert('◉', Shape::Circle { radius: 3.0, filled: true });
        map.insert('○', Shape::Circle { radius: 3.0, filled: false });
        map.insert('◆', Shape::Square { size: 4.0, filled: true });
        map.insert('◇', Shape::Square { size: 4.0, filled: false });
        map.insert('▲', Shape::Triangle { orientation: crate::object::Direction::North });
        map.insert('▼', Shape::Triangle { orientation: crate::object::Direction::South });
        map.insert('◀', Shape::Triangle { orientation: crate::object::Direction::West });
        map.insert('▶', Shape::Triangle { orientation: crate::object::Direction::East });
        map.insert('─', Shape::Line { angle: 0.0 });
        map.insert('│', Shape::Line { angle: 90.0 });
        map.insert('┌', Shape::Complex(vec!["corner_nw".to_string()]));
        map.insert('┐', Shape::Complex(vec!["corner_ne".to_string()]));
        map.insert('└', Shape::Complex(vec!["corner_sw".to_string()]));
        map.insert('┘', Shape::Complex(vec!["corner_se".to_string()]));
        map.insert('●', Shape::Dot { radius: 1.0 });
        map.insert(' ', Shape::Dot { radius: 0.0 });
        Self { char_to_shape: map }
    }
}

impl CharMapper {
    pub fn new() -> Self {
        Self::default()
    }

    pub fn get_shape(&self, c: char) -> Option<&Shape> {
        self.char_to_shape.get(&c)
    }

    pub fn add_mapping(&mut self, c: char, shape: Shape) {
        self.char_to_shape.insert(c, shape);
    }
}
