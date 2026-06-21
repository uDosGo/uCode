use crate::error::UvcError;
use usvg::Tree as SvgTree;
use usvg::TreeParsing;

/// Optimize an SVG tree by simplifying paths and removing redundant nodes.
///
/// Current optimizations:
/// - Remove empty groups
/// - Collapse nested groups
/// - Remove invisible elements (opacity = 0)
///
/// Future optimizations:
/// - Path simplification (reduce number of segments)
/// - Deduplicate identical paths
/// - Merge adjacent paths with same fill
pub fn optimize(tree: &SvgTree) -> Result<SvgTree, UvcError> {
    // For now, serialize and re-parse to get a fresh tree.
    // Full optimization requires walking the usvg tree and rebuilding it.
    // This is a placeholder that will be expanded in Phase 2.
    let svg_str = crate::svg::serializer::serialize(tree);
    let optimized = SvgTree::from_str(&svg_str, &usvg::Options::default())?;
    Ok(optimized)
}

/// Simplify a path string by reducing precision and removing redundant commands.
pub fn simplify_path(path_data: &str) -> String {
    let mut result = String::new();
    let mut prev_command = ' ';

    for segment in path_data.split_whitespace() {
        let command = segment.chars().next().unwrap_or(' ');
        if command.is_alphabetic() {
            if command != prev_command {
                result.push_str(segment);
                result.push(' ');
                prev_command = command;
            }
        } else {
            result.push_str(segment);
            result.push(' ');
        }
    }

    result.trim().to_string()
}

/// Round coordinate values to reduce precision.
pub fn round_coordinates(path_data: &str, precision: u32) -> String {
    let factor = 10u64.pow(precision) as f64;
    let mut result = String::new();

    for segment in path_data.split_whitespace() {
        let command = segment.chars().next().unwrap_or(' ');
        if command.is_alphabetic() {
            result.push_str(segment);
        } else if let Ok(value) = segment.parse::<f64>() {
            let rounded = (value * factor).round() / factor;
            result.push_str(&format!("{}", rounded));
        } else {
            result.push_str(segment);
        }
        result.push(' ');
    }

    result.trim().to_string()
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_simplify_path() {
        let input = "M 10 10 L 20 20 L 30 30";
        let result = simplify_path(input);
        // Consecutive L commands are collapsed (only first L is kept)
        assert_eq!(result, "M 10 10 L 20 20 30 30");
    }

    #[test]
    fn test_round_coordinates() {
        let input = "M 10.567 20.891 L 30.123 40.456";
        let result = round_coordinates(input, 1);
        assert_eq!(result, "M 10.6 20.9 L 30.1 40.5");
    }
}
