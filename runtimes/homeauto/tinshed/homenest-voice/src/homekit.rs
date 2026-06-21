//! HomeKit Bridge — Apple HomeKit bridge configuration and management

use crate::{HomeKitConfig, VoiceResult};
use std::collections::HashMap;

/// HomeKit bridge for exposing HomeNest devices to Apple Home
pub struct HomeKitBridge {
    config: HomeKitConfig,
    accessories: HashMap<String, HomeKitAccessory>,
    is_running: bool,
}

/// A HomeKit accessory exposed by the bridge
#[derive(Debug, Clone)]
pub struct HomeKitAccessory {
    pub id: String,
    pub name: String,
    pub accessory_type: AccessoryType,
    pub characteristics: HashMap<String, serde_json::Value>,
    pub reachable: bool,
}

/// Types of HomeKit accessories
#[derive(Debug, Clone, PartialEq)]
pub enum AccessoryType {
    Lightbulb,
    Switch,
    Thermostat,
    Lock,
    Speaker,
    Television,
    Fan,
    Sensor,
    Outlet,
    WindowCovering,
}

impl HomeKitBridge {
    pub fn new(config: HomeKitConfig) -> Self {
        Self {
            config,
            accessories: HashMap::new(),
            is_running: false,
        }
    }

    /// Start the HomeKit bridge (advertise via Bonjour/mDNS)
    pub fn start(&mut self) -> Result<(), String> {
        if self.is_running {
            return Err("Bridge is already running".into());
        }

        log::info!(
            "Starting HomeKit bridge '{}' on port {}",
            self.config.bridge_name,
            self.config.advertise_port
        );

        // In production, this would:
        // 1. Start an HAP (HomeKit Accessory Protocol) server
        // 2. Advertise via Bonjour/mDNS
        // 3. Handle pairings and encrypted connections

        self.is_running = true;
        Ok(())
    }

    /// Stop the HomeKit bridge
    pub fn stop(&mut self) -> Result<(), String> {
        if !self.is_running {
            return Err("Bridge is not running".into());
        }

        log::info!("Stopping HomeKit bridge");
        self.is_running = false;
        Ok(())
    }

    /// Register an accessory with the bridge
    pub fn register_accessory(&mut self, accessory: HomeKitAccessory) -> Result<(), String> {
        if self.accessories.contains_key(&accessory.id) {
            return Err(format!("Accessory already registered: {}", accessory.id));
        }

        log::info!("Registering accessory: {} ({})", accessory.name, accessory.id);
        self.accessories.insert(accessory.id.clone(), accessory);
        Ok(())
    }

    /// Remove an accessory from the bridge
    pub fn remove_accessory(&mut self, accessory_id: &str) -> Result<(), String> {
        self.accessories.remove(accessory_id)
            .ok_or_else(|| format!("Accessory not found: {}", accessory_id))?;
        Ok(())
    }

    /// Update a characteristic value for an accessory
    pub fn update_characteristic(
        &mut self,
        accessory_id: &str,
        characteristic: &str,
        value: serde_json::Value,
    ) -> Result<(), String> {
        let accessory = self.accessories.get_mut(accessory_id)
            .ok_or_else(|| format!("Accessory not found: {}", accessory_id))?;

        accessory.characteristics.insert(characteristic.to_string(), value);
        Ok(())
    }

    /// Get all registered accessories
    pub fn get_accessories(&self) -> Vec<&HomeKitAccessory> {
        self.accessories.values().collect()
    }

    /// Get a specific accessory
    pub fn get_accessory(&self, accessory_id: &str) -> Option<&HomeKitAccessory> {
        self.accessories.get(accessory_id)
    }

    /// Check if the bridge is running
    pub fn is_running(&self) -> bool {
        self.is_running
    }

    /// Get the bridge configuration
    pub fn config(&self) -> &HomeKitConfig {
        &self.config
    }

    /// Get accessory count
    pub fn accessory_count(&self) -> usize {
        self.accessories.len()
    }
}

impl std::fmt::Display for AccessoryType {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            AccessoryType::Lightbulb => write!(f, "lightbulb"),
            AccessoryType::Switch => write!(f, "switch"),
            AccessoryType::Thermostat => write!(f, "thermostat"),
            AccessoryType::Lock => write!(f, "lock"),
            AccessoryType::Speaker => write!(f, "speaker"),
            AccessoryType::Television => write!(f, "television"),
            AccessoryType::Fan => write!(f, "fan"),
            AccessoryType::Sensor => write!(f, "sensor"),
            AccessoryType::Outlet => write!(f, "outlet"),
            AccessoryType::WindowCovering => write!(f, "window_covering"),
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use serde_json::json;

    #[test]
    fn test_create_bridge() {
        let config = HomeKitConfig::default();
        let bridge = HomeKitBridge::new(config);
        assert!(!bridge.is_running());
        assert_eq!(bridge.accessory_count(), 0);
    }

    #[test]
    fn test_start_stop() {
        let config = HomeKitConfig::default();
        let mut bridge = HomeKitBridge::new(config);

        bridge.start().unwrap();
        assert!(bridge.is_running());

        bridge.stop().unwrap();
        assert!(!bridge.is_running());
    }

    #[test]
    fn test_register_accessory() {
        let config = HomeKitConfig::default();
        let mut bridge = HomeKitBridge::new(config);

        let accessory = HomeKitAccessory {
            id: "light.living_room".into(),
            name: "Living Room Light".into(),
            accessory_type: AccessoryType::Lightbulb,
            characteristics: HashMap::new(),
            reachable: true,
        };

        bridge.register_accessory(accessory).unwrap();
        assert_eq!(bridge.accessory_count(), 1);
    }

    #[test]
    fn test_update_characteristic() {
        let config = HomeKitConfig::default();
        let mut bridge = HomeKitBridge::new(config);

        let accessory = HomeKitAccessory {
            id: "light.living_room".into(),
            name: "Living Room Light".into(),
            accessory_type: AccessoryType::Lightbulb,
            characteristics: HashMap::new(),
            reachable: true,
        };

        bridge.register_accessory(accessory).unwrap();
        bridge.update_characteristic("light.living_room", "On", json!(true)).unwrap();

        let acc = bridge.get_accessory("light.living_room").unwrap();
        assert_eq!(acc.characteristics.get("On"), Some(&json!(true)));
    }

    #[test]
    fn test_remove_accessory() {
        let config = HomeKitConfig::default();
        let mut bridge = HomeKitBridge::new(config);

        let accessory = HomeKitAccessory {
            id: "light.test".into(),
            name: "Test Light".into(),
            accessory_type: AccessoryType::Lightbulb,
            characteristics: HashMap::new(),
            reachable: true,
        };

        bridge.register_accessory(accessory).unwrap();
        assert_eq!(bridge.accessory_count(), 1);

        bridge.remove_accessory("light.test").unwrap();
        assert_eq!(bridge.accessory_count(), 0);
    }

    #[test]
    fn test_duplicate_accessory() {
        let config = HomeKitConfig::default();
        let mut bridge = HomeKitBridge::new(config);

        let accessory = HomeKitAccessory {
            id: "light.test".into(),
            name: "Test".into(),
            accessory_type: AccessoryType::Lightbulb,
            characteristics: HashMap::new(),
            reachable: true,
        };

        bridge.register_accessory(accessory).unwrap();
        let duplicate = HomeKitAccessory {
            id: "light.test".into(),
            name: "Duplicate".into(),
            accessory_type: AccessoryType::Switch,
            characteristics: HashMap::new(),
            reachable: true,
        };

        assert!(bridge.register_accessory(duplicate).is_err());
    }
}
