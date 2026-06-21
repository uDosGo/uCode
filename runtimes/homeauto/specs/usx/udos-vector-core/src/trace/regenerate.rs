use crate::object::RegenerationEvent;

/// Configuration for a regeneration operation.
#[derive(Debug, Clone)]
pub struct RegenerationConfig {
    pub prompt: String,
    pub model: String,
    pub quality_threshold: f32,
    pub max_attempts: u32,
}

impl Default for RegenerationConfig {
    fn default() -> Self {
        Self {
            prompt: String::new(),
            model: "default".to_string(),
            quality_threshold: 0.7,
            max_attempts: 3,
        }
    }
}

/// Result of a regeneration operation.
#[derive(Debug, Clone)]
pub struct RegenerationResult {
    pub success: bool,
    pub result_id: String,
    pub quality_score: f32,
    pub events: Vec<RegenerationEvent>,
}

impl RegenerationResult {
    pub fn new(result_id: String, quality_score: f32) -> Self {
        Self {
            success: quality_score >= 0.5,
            result_id,
            quality_score,
            events: Vec::new(),
        }
    }

    pub fn failed(_reason: &str) -> Self {
        Self {
            success: false,
            result_id: String::new(),
            quality_score: 0.0,
            events: Vec::new(),
        }
    }
}

/// Calculate a quality score for a regeneration based on various metrics.
pub fn calculate_quality_score(
    original_description: &str,
    regenerated_description: &str,
    similarity: f32,
) -> f32 {
    // Simple heuristic: combine description similarity with a base score
    let base_score = 0.5;
    let description_bonus = if original_description == regenerated_description {
        0.3
    } else {
        0.1
    };

    (base_score + description_bonus + similarity * 0.2).min(1.0)
}

/// Track a regeneration attempt.
pub fn track_attempt(
    events: &mut Vec<RegenerationEvent>,
    prompt: &str,
    model: &str,
    result_id: &str,
    quality_score: f32,
) {
    events.push(RegenerationEvent {
        timestamp: chrono::Utc::now().timestamp() as u64,
        prompt_used: prompt.to_string(),
        model: model.to_string(),
        result_id: result_id.to_string(),
        quality_score,
    });
}

/// Get the best regeneration event from a list (highest quality score).
pub fn best_regeneration(events: &[RegenerationEvent]) -> Option<&RegenerationEvent> {
    events.iter().max_by(|a, b| {
        a.quality_score.partial_cmp(&b.quality_score).unwrap_or(std::cmp::Ordering::Equal)
    })
}

/// Get the average quality score across all regeneration events.
pub fn average_quality(events: &[RegenerationEvent]) -> f32 {
    if events.is_empty() {
        return 0.0;
    }
    let sum: f32 = events.iter().map(|e| e.quality_score).sum();
    sum / events.len() as f32
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_calculate_quality_score() {
        let score = calculate_quality_score("a red circle", "a red circle", 0.8);
        assert!(score > 0.5);
        assert!(score <= 1.0);
    }

    #[test]
    fn test_best_regeneration() {
        let events = vec![
            RegenerationEvent {
                timestamp: 1,
                prompt_used: "test".into(),
                model: "m1".into(),
                result_id: "r1".into(),
                quality_score: 0.5,
            },
            RegenerationEvent {
                timestamp: 2,
                prompt_used: "test".into(),
                model: "m2".into(),
                result_id: "r2".into(),
                quality_score: 0.9,
            },
        ];

        let best = best_regeneration(&events).unwrap();
        assert_eq!(best.quality_score, 0.9);
    }

    #[test]
    fn test_average_quality() {
        let events = vec![
            RegenerationEvent {
                timestamp: 1,
                prompt_used: "test".into(),
                model: "m1".into(),
                result_id: "r1".into(),
                quality_score: 0.5,
            },
            RegenerationEvent {
                timestamp: 2,
                prompt_used: "test".into(),
                model: "m2".into(),
                result_id: "r2".into(),
                quality_score: 0.9,
            },
        ];

        let avg = average_quality(&events);
        assert!((avg - 0.7).abs() < 0.001);
    }
}
