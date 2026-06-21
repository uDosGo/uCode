//! homenest-grid — Grid cell mapping system for HomeNest
//!
//! Provides a 24x24 coordinate space for organizing media and automation items
//! across multiple layers (Movies, Music, TV, Recordings, Bookmarks, Automation).

use serde::{Deserialize, Serialize};
use std::collections::HashMap;

/// Grid coordinate in LLLL-QQ-XXXX-Z format
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq, Hash)]
pub struct GridCoord {
    pub layer: String,    // e.g. "L1000"
    pub quadrant: String, // e.g. "AA10"
    pub x: u16,           // 0-23
    pub y: u16,           // 0-23
    pub z: u8,            // temporal layer index
}

/// A cell in the grid
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct GridCell {
    pub coord: GridCoord,
    pub media_id: Option<String>,
    pub title: Option<String>,
    pub cell_type: CellType,
    pub metadata: HashMap<String, String>,
}

/// Type of content in a grid cell
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub enum CellType {
    Movie,
    Music,
    TvEpisode,
    Recording,
    Bookmark,
    Automation,
    Empty,
}

/// A grid layer (e.g. Movies, Music, TV)
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct GridLayer {
    pub id: String,
    pub name: String,
    pub cells: HashMap<String, GridCell>,
}

/// The complete grid system
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct GridSystem {
    pub layers: HashMap<String, GridLayer>,
    pub grid_size: u16, // 24
}

impl GridCoord {
    /// Parse a coordinate string like "L1000-AA10-0317-2"
    pub fn parse(s: &str) -> Option<Self> {
        let parts: Vec<&str> = s.split('-').collect();
        if parts.len() != 4 {
            return None;
        }
        let layer = parts[0].to_string();
        let quadrant = parts[1].to_string();
        let xy = parts[2];
        let z: u8 = parts[3].parse().ok()?;

        if xy.len() != 4 {
            return None;
        }
        let x: u16 = xy[0..2].parse().ok()?;
        let y: u16 = xy[2..4].parse().ok()?;

        Some(GridCoord { layer, quadrant, x, y, z })
    }

    /// Format as string
    pub fn format(&self) -> String {
        format!("{}-{}-{:02}{:02}-{}", self.layer, self.quadrant, self.x, self.y, self.z)
    }
}

impl GridSystem {
    /// Create a new grid system with default layers
    pub fn new() -> Self {
        let mut layers = HashMap::new();
        for (id, name) in &[
            ("L1000", "Movies"),
            ("L2000", "Music"),
            ("L3000", "TV"),
            ("L4000", "Recordings"),
            ("L5000", "Bookmarks"),
            ("L6000", "Automation"),
        ] {
            layers.insert(
                id.to_string(),
                GridLayer {
                    id: id.to_string(),
                    name: name.to_string(),
                    cells: HashMap::new(),
                },
            );
        }
        GridSystem {
            layers,
            grid_size: 24,
        }
    }

    /// Place an item at a specific coordinate
    pub fn place(&mut self, coord: GridCoord, media_id: String, title: String, cell_type: CellType) -> Result<(), String> {
        if coord.x >= self.grid_size || coord.y >= self.grid_size {
            return Err(format!("Coordinates out of bounds: ({}, {})", coord.x, coord.y));
        }
        let layer = self.layers.get_mut(&coord.layer)
            .ok_or_else(|| format!("Unknown layer: {}", coord.layer))?;

        let key = coord.format();
        layer.cells.insert(key, GridCell {
            coord,
            media_id: Some(media_id),
            title: Some(title),
            cell_type,
            metadata: HashMap::new(),
        });
        Ok(())
    }

    /// Get a cell at a coordinate
    pub fn get(&self, coord: &GridCoord) -> Option<&GridCell> {
        let layer = self.layers.get(&coord.layer)?;
        layer.cells.get(&coord.format())
    }

    /// Remove a cell
    pub fn remove(&mut self, coord: &GridCoord) -> Option<GridCell> {
        let layer = self.layers.get_mut(&coord.layer)?;
        layer.cells.remove(&coord.format())
    }

    /// Count total cells across all layers
    pub fn total_cells(&self) -> usize {
        self.layers.values().map(|l| l.cells.len()).sum()
    }
}

impl Default for GridSystem {
    fn default() -> Self {
        Self::new()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_coord_parse() {
        let coord = GridCoord::parse("L1000-AA10-0317-2").unwrap();
        assert_eq!(coord.layer, "L1000");
        assert_eq!(coord.quadrant, "AA10");
        assert_eq!(coord.x, 3);
        assert_eq!(coord.y, 17);
        assert_eq!(coord.z, 2);
    }

    #[test]
    fn test_coord_format() {
        let coord = GridCoord {
            layer: "L1000".into(),
            quadrant: "AA10".into(),
            x: 3,
            y: 17,
            z: 2,
        };
        assert_eq!(coord.format(), "L1000-AA10-0317-2");
    }

    #[test]
    fn test_grid_place_and_get() {
        let mut grid = GridSystem::new();
        let coord = GridCoord::parse("L1000-AA10-0000-0").unwrap();
        grid.place(coord.clone(), "movie/42".into(), "Interstellar".into(), CellType::Movie).unwrap();
        let cell = grid.get(&coord).unwrap();
        assert_eq!(cell.media_id, Some("movie/42".to_string()));
        assert_eq!(cell.title, Some("Interstellar".to_string()));
    }

    #[test]
    fn test_grid_remove() {
        let mut grid = GridSystem::new();
        let coord = GridCoord::parse("L1000-AA10-0000-0").unwrap();
        grid.place(coord.clone(), "movie/42".into(), "Interstellar".into(), CellType::Movie).unwrap();
        assert_eq!(grid.total_cells(), 1);
        grid.remove(&coord);
        assert_eq!(grid.total_cells(), 0);
    }

    #[test]
    fn test_out_of_bounds() {
        let mut grid = GridSystem::new();
        let coord = GridCoord {
            layer: "L1000".into(),
            quadrant: "AA10".into(),
            x: 99,
            y: 99,
            z: 0,
        };
        assert!(grid.place(coord, "test".into(), "test".into(), CellType::Movie).is_err());
    }

    #[test]
    fn test_default_layers() {
        let grid = GridSystem::new();
        assert_eq!(grid.layers.len(), 6);
        assert!(grid.layers.contains_key("L1000"));
        assert!(grid.layers.contains_key("L6000"));
    }
}
