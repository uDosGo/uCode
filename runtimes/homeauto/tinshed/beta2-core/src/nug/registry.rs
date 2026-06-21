//! Nug registry implementation

use super::Nug;
use std::collections::HashMap;

/// Nug registry for managing multiple nugs
#[derive(Debug, Default)]
pub struct NugRegistry {
    nugs: HashMap<String, Nug>,
}

impl NugRegistry {
    /// Create a new empty registry
    pub fn new() -> Self {
        NugRegistry {
            nugs: HashMap::new(),
        }
    }

    /// Add a nug to the registry
    pub fn add_nug(&mut self, nug: Nug) {
        self.nugs.insert(nug.id.clone(), nug);
    }

    /// Get a nug by ID
    pub fn get_nug(&self, id: &str) -> Option<&Nug> {
        self.nugs.get(id)
    }

    /// Remove a nug by ID
    pub fn remove_nug(&mut self, id: &str) -> Option<Nug> {
        self.nugs.remove(id)
    }

    /// List all nug IDs
    pub fn list_nugs(&self) -> Vec<String> {
        self.nugs.keys().cloned().collect()
    }

    /// Find nugs by tag
    pub fn find_by_tag(&self, tag: &str) -> Vec<&Nug> {
        self.nugs
            .values()
            .filter(|nug| nug.tags.contains(&tag.to_string()))
            .collect()
    }

    /// Check if a nug exists
    pub fn contains(&self, id: &str) -> bool {
        self.nugs.contains_key(id)
    }

    /// Get the number of nugs in the registry
    pub fn count(&self) -> usize {
        self.nugs.len()
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::nug::Nug;

    #[test]
    fn test_nug_registry() {
        let mut registry = NugRegistry::new();
        
        let nug1 = Nug::new("R100-U899", "Runner", "1.0.0", "data1");
        let nug2 = Nug::new("R101-U900", "Builder", "1.0.0", "data2");

        // Add nugs
        registry.add_nug(nug1.clone());
        registry.add_nug(nug2.clone());

        // Test count
        assert_eq!(registry.count(), 2);

        // Test get
        let retrieved = registry.get_nug("R100-U899").unwrap();
        assert_eq!(retrieved.name, "Runner");

        // Test contains
        assert!(registry.contains("R100-U899"));
        assert!(!registry.contains("R999-U999"));

        // Test list
        let ids = registry.list_nugs();
        assert!(ids.contains(&"R100-U899".to_string()));
        assert!(ids.contains(&"R101-U900".to_string()));

        // Test remove
        let removed = registry.remove_nug("R100-U899").unwrap();
        assert_eq!(removed.id, "R100-U899");
        assert_eq!(registry.count(), 1);
    }

    #[test]
    fn test_find_by_tag() {
        let mut registry = NugRegistry::new();
        
        let mut nug1 = Nug::new("R100-U899", "Runner", "1.0.0", "data1");
        nug1.tags = vec!["execution".to_string(), "fast".to_string()];
        
        let mut nug2 = Nug::new("R101-U900", "Builder", "1.0.0", "data2");
        nug2.tags = vec!["build".to_string(), "slow".to_string()];
        
        let mut nug3 = Nug::new("R102-U901", "Compiler", "1.0.0", "data3");
        nug3.tags = vec!["execution".to_string(), "build".to_string()];

        registry.add_nug(nug1);
        registry.add_nug(nug2);
        registry.add_nug(nug3);

        let execution_nugs = registry.find_by_tag("execution");
        assert_eq!(execution_nugs.len(), 2);
        let nug_ids: Vec<&str> = execution_nugs.iter().map(|r| r.id.as_str()).collect();
        assert!(nug_ids.contains(&"R100-U899"));
        assert!(nug_ids.contains(&"R102-U901"));
    }
}
