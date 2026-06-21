use crate::object::UniversalVisual;

/// A diff between two UniversalVisual objects.
#[derive(Debug, Clone)]
pub struct VisualDiff {
    pub id_changed: bool,
    pub name_changed: bool,
    pub svg_changed: bool,
    pub rasters_changed: bool,
    pub texts_changed: bool,
    pub semantic_changed: bool,
    pub provenance_changed: bool,
    pub changes: Vec<String>,
}

/// Compute a diff between two UniversalVisual objects.
pub fn diff(before: &UniversalVisual, after: &UniversalVisual) -> VisualDiff {
    let mut changes = Vec::new();
    let mut diff = VisualDiff {
        id_changed: false,
        name_changed: false,
        svg_changed: false,
        rasters_changed: false,
        texts_changed: false,
        semantic_changed: false,
        provenance_changed: false,
        changes: Vec::new(),
    };

    if before.id != after.id {
        diff.id_changed = true;
        changes.push(format!("ID: {} -> {}", before.id, after.id));
    }

    if before.name != after.name {
        diff.name_changed = true;
        changes.push(format!("Name: {} -> {}", before.name, after.name));
    }

    if before.svg_source != after.svg_source {
        diff.svg_changed = true;
        changes.push("SVG content changed".to_string());
    }

    if before.rasters != after.rasters {
        diff.rasters_changed = true;
        changes.push("Raster cache changed".to_string());
    }

    if before.texts != after.texts {
        diff.texts_changed = true;
        changes.push("Text representations changed".to_string());
    }

    if before.semantic.description != after.semantic.description {
        diff.semantic_changed = true;
        changes.push("Semantic description changed".to_string());
    }

    if before.provenance.transformations.len() != after.provenance.transformations.len() {
        diff.provenance_changed = true;
        changes.push("Provenance trail updated".to_string());
    }

    diff.changes = changes;
    diff
}

/// Check if two visuals are semantically identical.
pub fn is_semantically_identical(a: &UniversalVisual, b: &UniversalVisual) -> bool {
    a.svg_source == b.svg_source
        && a.semantic.description == b.semantic.description
        && a.semantic.tags == b.semantic.tags
}

/// Check if two visuals are visually identical (same SVG).
pub fn is_visually_identical(a: &UniversalVisual, b: &UniversalVisual) -> bool {
    a.svg_source == b.svg_source
}
