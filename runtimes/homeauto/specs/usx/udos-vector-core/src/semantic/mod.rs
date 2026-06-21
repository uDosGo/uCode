use crate::object::{Layout, Orientation, Subject};
use usvg::Tree as SvgTree;

pub mod classifier;
pub mod describer;
pub mod prompter;
pub mod subject_extractor;

/// Generate a natural language description from an SVG tree.
pub fn describe(svg: &SvgTree) -> String {
    describer::describe(svg)
}

/// Generate a regeneration prompt from an SVG tree.
pub fn to_prompt(svg: &SvgTree) -> String {
    prompter::to_prompt(svg)
}

/// Extract subjects from an SVG tree.
pub fn extract_subjects(svg: &SvgTree) -> Vec<Subject> {
    subject_extractor::extract(svg)
}

/// Analyze the composition layout of an SVG tree.
pub fn analyze_layout(svg: &SvgTree) -> Layout {
    classifier::analyze_layout(svg)
}

/// Analyze the orientation of an SVG tree.
pub fn analyze_orientation(svg: &SvgTree) -> Orientation {
    classifier::analyze_orientation(svg)
}

/// Extract the colour palette from an SVG tree.
pub fn extract_palette(svg: &SvgTree) -> Vec<String> {
    classifier::extract_palette(svg)
}

/// Generate tags for an SVG tree.
pub fn generate_tags(svg: &SvgTree) -> Vec<String> {
    classifier::generate_tags(svg)
}

/// Full semantic analysis of an SVG tree.
pub fn analyze(svg: &SvgTree) -> crate::object::SemanticMetadata {
    let description = describe(svg);
    let prompt = to_prompt(svg);
    let subjects = extract_subjects(svg);
    let layout = analyze_layout(svg);
    let orientation = analyze_orientation(svg);
    let palette = extract_palette(svg);
    let tags = generate_tags(svg);

    crate::object::SemanticMetadata {
        description,
        prompt,
        subjects,
        layout,
        orientation,
        palette,
        tags,
        ..Default::default()
    }
}
