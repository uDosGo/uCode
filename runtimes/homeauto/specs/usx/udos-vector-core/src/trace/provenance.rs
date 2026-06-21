use crate::object::Provenance;
use serde::{Deserialize, Serialize};

/// A serializable provenance record for storage/transmission.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ProvenanceRecord {
    pub id: String,
    pub provenance: Provenance,
    pub created_at: u64,
    pub updated_at: u64,
}

impl ProvenanceRecord {
    pub fn new(id: String, provenance: Provenance) -> Self {
        let now = chrono::Utc::now().timestamp() as u64;
        Self {
            id,
            provenance,
            created_at: now,
            updated_at: now,
        }
    }
}

/// Validate a provenance trail for consistency.
pub fn validate_provenance(provenance: &Provenance) -> Result<(), String> {
    // Check for circular dependencies
    for parent in &provenance.parents {
        if provenance.children.contains(parent) {
            return Err(format!(
                "Circular dependency detected: {} is both parent and child",
                parent
            ));
        }
    }

    // Check transformation timestamps are in order
    for window in provenance.transformations.windows(2) {
        if window[0].timestamp > window[1].timestamp {
            return Err("Transformations are not in chronological order".to_string());
        }
    }

    Ok(())
}

/// Merge two provenance trails (for when visuals are combined).
pub fn merge_provenance(a: &Provenance, b: &Provenance) -> Provenance {
    let mut merged = Provenance::default();

    // Merge parents
    for parent in &a.parents {
        if !merged.parents.contains(parent) {
            merged.parents.push(parent.clone());
        }
    }
    for parent in &b.parents {
        if !merged.parents.contains(parent) {
            merged.parents.push(parent.clone());
        }
    }

    // Merge transformations (sorted by timestamp)
    let mut all_transformations = a.transformations.clone();
    all_transformations.extend(b.transformations.clone());
    all_transformations.sort_by_key(|t| t.timestamp);
    merged.transformations = all_transformations;

    // Merge regenerations
    let mut all_regenerations = a.regenerations.clone();
    all_regenerations.extend(b.regenerations.clone());
    all_regenerations.sort_by_key(|r| r.timestamp);
    merged.regenerations = all_regenerations;

    merged
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::object::Transformation;

    #[test]
    fn test_validate_provenance_ok() {
        let provenance = Provenance::default();
        assert!(validate_provenance(&provenance).is_ok());
    }

    #[test]
    fn test_validate_provenance_circular() {
        let mut provenance = Provenance::default();
        provenance.parents.push("obj-1".to_string());
        provenance.children.push("obj-1".to_string());
        assert!(validate_provenance(&provenance).is_err());
    }

    #[test]
    fn test_merge_provenance() {
        let mut a = Provenance::default();
        a.parents.push("parent-a".to_string());

        let mut b = Provenance::default();
        b.parents.push("parent-b".to_string());

        let merged = merge_provenance(&a, &b);
        assert_eq!(merged.parents.len(), 2);
        assert!(merged.parents.contains(&"parent-a".to_string()));
        assert!(merged.parents.contains(&"parent-b".to_string()));
    }
}
