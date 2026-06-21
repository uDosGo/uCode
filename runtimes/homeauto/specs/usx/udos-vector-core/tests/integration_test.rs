use udos_vector_core::UniversalVectorCore;

/// Integration test: full SVG import pipeline
#[test]
fn test_full_svg_import_pipeline() {
    let core = UniversalVectorCore::new();

    let svg = r#"<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
        <rect x="10" y="10" width="80" height="80" fill="blue" rx="5"/>
        <circle cx="50" cy="50" r="30" fill="red" opacity="0.5"/>
    </svg>"#;

    let visual = core.import_svg("test-shape", svg).unwrap();

    // Verify import
    assert_eq!(visual.name, "test-shape");
    assert!(visual.svg.is_some());
    assert_eq!(visual.svg_source.as_deref(), Some(svg));

    // Verify semantic analysis (auto-analyze is on by default)
    // usvg 0.37 parses shapes into Path nodes, so we check for generic terms
    assert!(!visual.semantic.description.is_empty());
    assert!(visual.semantic.tags.contains(&"path".to_string()));
    assert!(visual.semantic.tags.contains(&"simple".to_string()));
}

/// Integration test: SVG validation
#[test]
fn test_svg_validation() {
    let core = UniversalVectorCore::new();

    // Valid SVG
    let valid_svg = r#"<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
        <circle cx="12" cy="12" r="10" fill="red"/>
    </svg>"#;
    assert!(core.validate_svg(valid_svg).is_ok());

    // Invalid SVG (no namespace)
    let invalid_svg = r#"<svg viewBox="0 0 24 24">
        <circle cx="12" cy="12" r="10" fill="red"/>
    </svg>"#;
    assert!(core.validate_svg(invalid_svg).is_err());

    // Empty string
    assert!(core.validate_svg("").is_err());
}

/// Integration test: rasterization pipeline
#[test]
fn test_rasterization_pipeline() {
    let core = UniversalVectorCore::new();

    let svg = r#"<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
        <circle cx="12" cy="12" r="10" fill="red"/>
    </svg>"#;

    let visual = core.import_svg("raster-test", svg).unwrap();

    // Render to cell
    let cell = core.render_to_cell(&visual).unwrap();
    assert_eq!(cell.width, 24);
    assert_eq!(cell.height, 24);

    // Render to celx
    let celx = core.render_to_celx(&visual, 48).unwrap();
    assert_eq!(celx.width, 48);
    assert_eq!(celx.height, 24);

    // Render to thumbnail
    let thumb = core.render_to_thumbnail(&visual).unwrap();
    assert_eq!(thumb.width, 64);
    assert_eq!(thumb.height, 64);

    // Export to PNG
    let png = core.export_png(&cell).unwrap();
    assert!(!png.is_empty());
    assert_eq!(&png[..8], &[137, 80, 78, 71, 13, 10, 26, 10]);
}

/// Integration test: text representation pipeline
#[test]
fn test_text_representation_pipeline() {
    let core = UniversalVectorCore::new();

    let svg = r#"<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
        <rect x="2" y="2" width="20" height="20" fill="black"/>
    </svg>"#;

    let visual = core.import_svg("text-test", svg).unwrap();

    // ASCII art
    let ascii = core.to_ascii(&visual, 8, 8);
    assert!(!ascii.is_empty());
    assert_eq!(ascii.lines().count(), 8);

    // Teletext
    let teletext = core.to_teletext(&visual).unwrap();
    assert!(!teletext.is_empty());
    assert_eq!(teletext.lines().count(), 25);

    // Braille
    let braille = core.to_braille(&visual).unwrap();
    assert!(!braille.is_empty());
}

/// Integration test: semantic analysis pipeline
#[test]
fn test_semantic_analysis_pipeline() {
    let core = UniversalVectorCore::new();

    let svg = r#"<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
        <circle cx="50" cy="50" r="40" fill="red"/>
        <rect x="10" y="10" width="20" height="20" fill="blue"/>
        <text x="30" y="80" font-size="12" fill="black">Hello</text>
    </svg>"#;

    let visual = core.import_svg("semantic-test", svg).unwrap();

    // Description
    let description = core.describe(&visual);
    // usvg 0.37 parses shapes into Path nodes
    assert!(!description.is_empty());

    // Prompt
    let prompt = core.to_prompt(&visual);
    assert!(!prompt.is_empty());

    // Subjects
    let subjects = core.extract_subjects(&visual);
    assert!(!subjects.is_empty());

    // Full analysis
    let metadata = core.analyze(&visual);
    assert!(!metadata.tags.is_empty());
    assert!(!metadata.palette.is_empty());
}

/// Integration test: provenance trail
#[test]
fn test_provenance_trail_pipeline() {
    let core = UniversalVectorCore::new();

    let svg = r#"<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
        <circle cx="12" cy="12" r="10" fill="red"/>
    </svg>"#;

    let mut visual = core.import_svg("provenance-test", svg).unwrap();

    // Record transformations
    core.record_transformation(&mut visual, "scale", serde_json::json!({"factor": 2.0}));
    core.record_transformation(&mut visual, "rotate", serde_json::json!({"angle": 45}));
    core.record_source(&mut visual, "SVG", "abc123def456");
    core.link_parent(&mut visual, "parent-visual-1");
    core.link_child(&mut visual, "child-visual-1");

    // Verify history
    let history = core.transformation_history(&visual);
    assert_eq!(history.len(), 2);
    assert!(history[0].contains("scale"));
    assert!(history[1].contains("rotate"));

    // Verify parent/child links
    assert!(visual.provenance.parents.contains(&"parent-visual-1".to_string()));
    assert!(visual.provenance.children.contains(&"child-visual-1".to_string()));
}

/// Integration test: diffing
#[test]
fn test_diff_pipeline() {
    let core = UniversalVectorCore::new();

    let svg_a = r#"<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
        <circle cx="12" cy="12" r="10" fill="red"/>
    </svg>"#;

    let svg_b = r#"<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
        <circle cx="12" cy="12" r="10" fill="blue"/>
    </svg>"#;

    let visual_a = core.import_svg("a", svg_a).unwrap();
    let visual_b = core.import_svg("b", svg_b).unwrap();

    let diff = core.diff(&visual_a, &visual_b);
    assert!(diff.svg_changed);
    // Names differ ("a" vs "b")
    assert!(diff.name_changed);

    // Same SVG should be semantically identical
    let visual_c = core.import_svg("c", svg_a).unwrap();
    assert!(core.is_semantically_identical(&visual_a, &visual_c));
}

/// Integration test: custom configuration
#[test]
fn test_custom_configuration() {
    use udos_vector_core::CoreConfig;

    // Disable auto-analysis
    let config = CoreConfig {
        auto_analyze: false,
        auto_rasterize: true,
        ..Default::default()
    };

    let core = udos_vector_core::UniversalVectorCore::with_config(config);

    let svg = r#"<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
        <circle cx="12" cy="12" r="10" fill="red"/>
    </svg>"#;

    let visual = core.import_svg("config-test", svg).unwrap();

    // Auto-analysis disabled
    assert!(visual.semantic.description.is_empty());

    // Auto-rasterize enabled
    assert!(visual.rasters.contains_key(&udos_vector_core::object::RasterType::Cell24));
}

/// Integration test: error handling
#[test]
fn test_error_handling() {
    let core = UniversalVectorCore::new();

    // Invalid SVG should return error
    let result = core.import_svg("bad", "not valid svg");
    assert!(result.is_err());

    // Empty SVG should return error
    let result = core.import_svg("empty", "");
    assert!(result.is_err());
}
