use crate::object::{Provenance, RegenerationEvent, Source, Transformation};
use chrono::Utc;

pub mod diff;
pub mod provenance;
pub mod regenerate;

/// Create a new provenance record.
pub fn new_provenance() -> Provenance {
    Provenance::default()
}

/// Record a transformation in the provenance trail.
pub fn record_transformation(
    provenance: &mut Provenance,
    operation: &str,
    params: serde_json::Value,
) {
    provenance.transformations.push(Transformation {
        timestamp: Utc::now().timestamp() as u64,
        operation: operation.to_string(),
        params,
    });
}

/// Record a source import in the provenance trail.
pub fn record_source(provenance: &mut Provenance, format: &str, original_hash: &str) {
    provenance.source = Some(Source {
        format: format.to_string(),
        original_hash: original_hash.to_string(),
        import_timestamp: Utc::now().timestamp() as u64,
    });
}

/// Record a regeneration event in the provenance trail.
pub fn record_regeneration(
    provenance: &mut Provenance,
    prompt: &str,
    model: &str,
    result_id: &str,
    quality_score: f32,
) {
    provenance.regenerations.push(RegenerationEvent {
        timestamp: Utc::now().timestamp() as u64,
        prompt_used: prompt.to_string(),
        model: model.to_string(),
        result_id: result_id.to_string(),
        quality_score,
    });
}

/// Link a parent object in the provenance trail.
pub fn link_parent(provenance: &mut Provenance, parent_id: &str) {
    if !provenance.parents.contains(&parent_id.to_string()) {
        provenance.parents.push(parent_id.to_string());
    }
}

/// Link a child object in the provenance trail.
pub fn link_child(provenance: &mut Provenance, child_id: &str) {
    if !provenance.children.contains(&child_id.to_string()) {
        provenance.children.push(child_id.to_string());
    }
}

/// Get the full transformation history as a readable string.
pub fn transformation_history(provenance: &Provenance) -> Vec<String> {
    provenance
        .transformations
        .iter()
        .map(|t| {
            format!(
                "[{}] {}: {}",
                t.timestamp,
                t.operation,
                serde_json::to_string(&t.params).unwrap_or_default()
            )
        })
        .collect()
}

/// Get the regeneration history as a readable string.
pub fn regeneration_history(provenance: &Provenance) -> Vec<String> {
    provenance
        .regenerations
        .iter()
        .map(|r| {
            format!(
                "[{}] Model: {}, Prompt: \"{}\", Score: {:.2}",
                r.timestamp, r.model, r.prompt_used, r.quality_score
            )
        })
        .collect()
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_record_transformation() {
        let mut provenance = Provenance::default();
        record_transformation(
            &mut provenance,
            "scale",
            serde_json::json!({"factor": 2.0}),
        );
        assert_eq!(provenance.transformations.len(), 1);
        assert_eq!(provenance.transformations[0].operation, "scale");
    }

    #[test]
    fn test_link_parent() {
        let mut provenance = Provenance::default();
        link_parent(&mut provenance, "parent-1");
        link_parent(&mut provenance, "parent-2");
        assert_eq!(provenance.parents.len(), 2);
    }

    #[test]
    fn test_record_source() {
        let mut provenance = Provenance::default();
        record_source(&mut provenance, "PNG", "abc123");
        assert!(provenance.source.is_some());
        assert_eq!(provenance.source.unwrap().format, "PNG");
    }
}
