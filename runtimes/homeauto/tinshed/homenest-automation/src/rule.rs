//! Rule Engine — Condition-based automation rules

use crate::{ActionType, AutomationRule, ConditionOperator, RuleCondition, SceneAction};
use chrono::{Local, Timelike};
use std::collections::HashMap;
use uuid::Uuid;

/// Rule engine for evaluating automation rules
pub struct RuleEngine {
    rules: Vec<AutomationRule>,
}

impl RuleEngine {
    pub fn new() -> Self {
        Self {
            rules: Vec::new(),
        }
    }

    /// Create a new automation rule
    pub fn create_rule(&mut self, name: &str, description: Option<&str>, priority: u32) -> AutomationRule {
        let rule = AutomationRule {
            id: Uuid::new_v4().to_string(),
            name: name.to_string(),
            description: description.map(|s| s.to_string()),
            conditions: Vec::new(),
            actions: Vec::new(),
            enabled: true,
            priority,
        };

        let id = rule.id.clone();
        self.rules.push(rule);
        self.rules.sort_by(|a, b| b.priority.cmp(&a.priority));
        self.rules.iter().find(|r| r.id == id).unwrap().clone()
    }

    /// Add a condition to a rule
    pub fn add_condition(&mut self, rule_id: &str, condition: RuleCondition) -> Result<(), String> {
        let rule = self.rules.iter_mut()
            .find(|r| r.id == rule_id)
            .ok_or_else(|| format!("Rule not found: {}", rule_id))?;
        rule.conditions.push(condition);
        Ok(())
    }

    /// Add an action to a rule
    pub fn add_action(&mut self, rule_id: &str, action: SceneAction) -> Result<(), String> {
        let rule = self.rules.iter_mut()
            .find(|r| r.id == rule_id)
            .ok_or_else(|| format!("Rule not found: {}", rule_id))?;
        rule.actions.push(action);
        Ok(())
    }

    /// Evaluate all enabled rules against current state
    pub fn evaluate(&self, state: &HashMap<String, serde_json::Value>) -> Vec<&AutomationRule> {
        let mut triggered = Vec::new();

        for rule in &self.rules {
            if !rule.enabled {
                continue;
            }

            if self.evaluate_conditions(&rule.conditions, state) {
                triggered.push(rule);
            }
        }

        triggered
    }

    /// Evaluate a set of conditions (AND logic)
    fn evaluate_conditions(&self, conditions: &[RuleCondition], state: &HashMap<String, serde_json::Value>) -> bool {
        if conditions.is_empty() {
            return true;
        }

        conditions.iter().all(|condition| {
            let current_value = match state.get(&condition.field) {
                Some(v) => v,
                None => return false,
            };

            match condition.operator {
                ConditionOperator::Equals => current_value == &condition.value,
                ConditionOperator::NotEquals => current_value != &condition.value,
                ConditionOperator::GreaterThan => compare_values(current_value, &condition.value, |a, b| a > b),
                ConditionOperator::LessThan => compare_values(current_value, &condition.value, |a, b| a < b),
                ConditionOperator::Contains => {
                    current_value.as_str()
                        .map(|s| s.contains(condition.value.as_str().unwrap_or("")))
                        .unwrap_or(false)
                }
                ConditionOperator::Between => {
                    if let (Some(arr), Some(val)) = (condition.value.as_array(), current_value.as_f64()) {
                        arr.len() == 2
                            && arr[0].as_f64().map(|min| val >= min).unwrap_or(false)
                            && arr[1].as_f64().map(|max| val <= max).unwrap_or(false)
                    } else {
                        false
                    }
                }
                ConditionOperator::TimeRange => {
                    if let (Some(arr), Some(now)) = (condition.value.as_array(), Some(Local::now())) {
                        let current_minutes = now.hour() as u32 * 60 + now.minute() as u32;
                        arr.len() == 2
                            && arr[0].as_str().and_then(parse_time_to_minutes)
                            .map(|start| current_minutes >= start)
                            .unwrap_or(false)
                            && arr[1].as_str().and_then(parse_time_to_minutes)
                            .map(|end| current_minutes <= end)
                            .unwrap_or(false)
                    } else {
                        false
                    }
                }
            }
        })
    }

    /// Enable or disable a rule
    pub fn set_rule_enabled(&mut self, rule_id: &str, enabled: bool) -> Result<(), String> {
        let rule = self.rules.iter_mut()
            .find(|r| r.id == rule_id)
            .ok_or_else(|| format!("Rule not found: {}", rule_id))?;
        rule.enabled = enabled;
        Ok(())
    }

    /// Delete a rule
    pub fn delete_rule(&mut self, rule_id: &str) -> Result<(), String> {
        let idx = self.rules.iter().position(|r| r.id == rule_id)
            .ok_or_else(|| format!("Rule not found: {}", rule_id))?;
        self.rules.remove(idx);
        Ok(())
    }

    /// Get all rules
    pub fn get_all_rules(&self) -> &[AutomationRule] {
        &self.rules
    }

    /// Get a rule by ID
    pub fn get_rule(&self, rule_id: &str) -> Option<&AutomationRule> {
        self.rules.iter().find(|r| r.id == rule_id)
    }

    /// Get rule count
    pub fn rule_count(&self) -> usize {
        self.rules.len()
    }
}

impl Default for RuleEngine {
    fn default() -> Self {
        Self::new()
    }
}

/// Compare two JSON values numerically
fn compare_values<F>(a: &serde_json::Value, b: &serde_json::Value, cmp: F) -> bool
where
    F: Fn(f64, f64) -> bool,
{
    match (a.as_f64(), b.as_f64()) {
        (Some(av), Some(bv)) => cmp(av, bv),
        _ => false,
    }
}

/// Parse a time string (HH:MM) to minutes since midnight
fn parse_time_to_minutes(time: &str) -> Option<u32> {
    let parts: Vec<&str> = time.split(':').collect();
    if parts.len() != 2 {
        return None;
    }
    let hours: u32 = parts[0].parse().ok()?;
    let minutes: u32 = parts[1].parse().ok()?;
    Some(hours * 60 + minutes)
}

#[cfg(test)]
mod tests {
    use super::*;
    use serde_json::json;

    #[test]
    fn test_create_rule() {
        let mut engine = RuleEngine::new();
        let rule = engine.create_rule("Test Rule", Some("A test"), 10);
        assert_eq!(rule.name, "Test Rule");
        assert!(rule.enabled);
    }

    #[test]
    fn test_evaluate_equals() {
        let mut engine = RuleEngine::new();
        let rule = engine.create_rule("Equals Test", None, 10);

        engine.add_condition(&rule.id, RuleCondition {
            field: "temperature".into(),
            operator: ConditionOperator::Equals,
            value: json!(25),
        }).unwrap();

        let mut state = HashMap::new();
        state.insert("temperature".into(), json!(25));
        let triggered = engine.evaluate(&state);
        assert_eq!(triggered.len(), 1);

        state.insert("temperature".into(), json!(30));
        let triggered = engine.evaluate(&state);
        assert_eq!(triggered.len(), 0);
    }

    #[test]
    fn test_evaluate_greater_than() {
        let mut engine = RuleEngine::new();
        let rule = engine.create_rule("GT Test", None, 10);

        engine.add_condition(&rule.id, RuleCondition {
            field: "temperature".into(),
            operator: ConditionOperator::GreaterThan,
            value: json!(30),
        }).unwrap();

        let mut state = HashMap::new();
        state.insert("temperature".into(), json!(35));
        let triggered = engine.evaluate(&state);
        assert_eq!(triggered.len(), 1);

        state.insert("temperature".into(), json!(25));
        let triggered = engine.evaluate(&state);
        assert_eq!(triggered.len(), 0);
    }

    #[test]
    fn test_evaluate_between() {
        let mut engine = RuleEngine::new();
        let rule = engine.create_rule("Between Test", None, 10);

        engine.add_condition(&rule.id, RuleCondition {
            field: "humidity".into(),
            operator: ConditionOperator::Between,
            value: json!([30, 60]),
        }).unwrap();

        let mut state = HashMap::new();
        state.insert("humidity".into(), json!(45));
        let triggered = engine.evaluate(&state);
        assert_eq!(triggered.len(), 1);

        state.insert("humidity".into(), json!(70));
        let triggered = engine.evaluate(&state);
        assert_eq!(triggered.len(), 0);
    }

    #[test]
    fn test_multiple_conditions_and() {
        let mut engine = RuleEngine::new();
        let rule = engine.create_rule("Multi Test", None, 10);

        engine.add_condition(&rule.id, RuleCondition {
            field: "motion".into(),
            operator: ConditionOperator::Equals,
            value: json!("detected"),
        }).unwrap();

        engine.add_condition(&rule.id, RuleCondition {
            field: "luminance".into(),
            operator: ConditionOperator::LessThan,
            value: json!(50),
        }).unwrap();

        let mut state = HashMap::new();
        state.insert("motion".into(), json!("detected"));
        state.insert("luminance".into(), json!(30));
        let triggered = engine.evaluate(&state);
        assert_eq!(triggered.len(), 1);

        state.insert("luminance".into(), json!(70));
        let triggered = engine.evaluate(&state);
        assert_eq!(triggered.len(), 0);
    }

    #[test]
    fn test_priority_ordering() {
        let mut engine = RuleEngine::new();
        engine.create_rule("Low", None, 1);
        engine.create_rule("High", None, 100);
        engine.create_rule("Medium", None, 50);

        let rules = engine.get_all_rules();
        assert_eq!(rules[0].name, "High");
        assert_eq!(rules[1].name, "Medium");
        assert_eq!(rules[2].name, "Low");
    }

    #[test]
    fn test_parse_time() {
        assert_eq!(parse_time_to_minutes("08:30"), Some(510));
        assert_eq!(parse_time_to_minutes("23:45"), Some(1425));
        assert_eq!(parse_time_to_minutes("invalid"), None);
    }
}
