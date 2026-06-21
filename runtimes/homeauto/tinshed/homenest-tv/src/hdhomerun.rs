//! HDHomeRun Module — Tuner discovery + channel scanning
//!
//! Discovers HDHomeRun devices on the local network and scans for channels.

use crate::{Channel, ChannelSource};
use serde::{Deserialize, Serialize};
use std::collections::HashMap;

/// An HDHomeRun device on the network
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct HdHomeRunDevice {
    pub id: String,
    pub ip_address: String,
    pub model: String,
    pub firmware: String,
    pub tuner_count: u32,
    pub tuners_available: u32,
}

/// A channel discovered by HDHomeRun
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct HdHomeRunChannel {
    pub guide_number: String,
    pub guide_name: String,
    pub frequency: u32,
    pub modulation: String,
    pub program_number: u32,
    pub enabled: bool,
}

/// HDHomeRun discovery and control module
pub struct HdHomeRunModule {
    devices: Vec<HdHomeRunDevice>,
    channels: HashMap<String, Vec<HdHomeRunChannel>>,
}

impl HdHomeRunModule {
    pub fn new() -> Self {
        Self {
            devices: Vec::new(),
            channels: HashMap::new(),
        }
    }

    /// Discover HDHomeRun devices on the local network via SSDP/UPnP
    pub fn discover_devices(&mut self) -> Result<Vec<HdHomeRunDevice>, String> {
        // In production, this would send an SSDP M-SEARCH request
        // For now, return mock data for testing
        let devices = vec![
            HdHomeRunDevice {
                id: "HDHR-12345678".into(),
                ip_address: "192.168.1.100".into(),
                model: "HDHomeRun CONNECT Quatro".into(),
                firmware: "20250501".into(),
                tuner_count: 4,
                tuners_available: 4,
            },
        ];

        self.devices = devices.clone();
        Ok(devices)
    }

    /// Scan for channels on a specific HDHomeRun device
    pub fn scan_channels(&mut self, device_id: &str) -> Result<Vec<HdHomeRunChannel>, String> {
        // In production, this would call the HDHomeRun API at http://device_ip/lineup.json
        // For now, return mock channel data
        let channels = vec![
            HdHomeRunChannel {
                guide_number: "2".into(),
                guide_name: "ABC HD".into(),
                frequency: 177000000,
                modulation: "8vsb".into(),
                program_number: 1,
                enabled: true,
            },
            HdHomeRunChannel {
                guide_number: "7".into(),
                guide_name: "Seven HD".into(),
                frequency: 191000000,
                modulation: "8vsb".into(),
                program_number: 1,
                enabled: true,
            },
            HdHomeRunChannel {
                guide_number: "9".into(),
                guide_name: "Nine HD".into(),
                frequency: 191000000,
                modulation: "8vsb".into(),
                program_number: 2,
                enabled: true,
            },
            HdHomeRunChannel {
                guide_number: "10".into(),
                guide_name: "10 HD".into(),
                frequency: 219000000,
                modulation: "8vsb".into(),
                program_number: 1,
                enabled: true,
            },
            HdHomeRunChannel {
                guide_number: "SBS".into(),
                guide_name: "SBS HD".into(),
                frequency: 536000000,
                modulation: "8vsb".into(),
                program_number: 1,
                enabled: true,
            },
        ];

        self.channels.insert(device_id.to_string(), channels.clone());
        Ok(channels)
    }

    /// Convert HDHomeRun channels to HomeNest Channel objects
    pub fn to_channels(&self, device_id: &str) -> Vec<Channel> {
        self.channels.get(device_id)
            .map(|channels| {
                channels.iter().map(|c| Channel {
                    id: format!("hdhr-{}", c.guide_number.to_lowercase()),
                    number: c.guide_number.clone(),
                    name: c.guide_name.clone(),
                    icon_url: None,
                    source: ChannelSource::HdHomeRun,
                }).collect()
            })
            .unwrap_or_default()
    }

    /// Get the streaming URL for a channel
    pub fn get_stream_url(&self, device_id: &str, channel_number: &str) -> Option<String> {
        let device = self.devices.iter().find(|d| d.id == device_id)?;
        Some(format!("http://{}/auto/v{}", device.ip_address, channel_number))
    }

    /// Get list of discovered devices
    pub fn get_devices(&self) -> &[HdHomeRunDevice] {
        &self.devices
    }
}

impl Default for HdHomeRunModule {
    fn default() -> Self {
        Self::new()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_discover_devices() {
        let mut hdhr = HdHomeRunModule::new();
        let devices = hdhr.discover_devices().unwrap();
        assert!(!devices.is_empty());
        assert_eq!(devices[0].model, "HDHomeRun CONNECT Quatro");
    }

    #[test]
    fn test_scan_channels() {
        let mut hdhr = HdHomeRunModule::new();
        hdhr.discover_devices().unwrap();
        let channels = hdhr.scan_channels("HDHR-12345678").unwrap();
        assert!(!channels.is_empty());
        assert_eq!(channels[0].guide_name, "ABC HD");
    }

    #[test]
    fn test_to_channels() {
        let mut hdhr = HdHomeRunModule::new();
        hdhr.discover_devices().unwrap();
        hdhr.scan_channels("HDHR-12345678").unwrap();
        let channels = hdhr.to_channels("HDHR-12345678");
        assert!(!channels.is_empty());
        assert_eq!(channels[0].source, ChannelSource::HdHomeRun);
    }

    #[test]
    fn test_get_stream_url() {
        let mut hdhr = HdHomeRunModule::new();
        hdhr.discover_devices().unwrap();
        let url = hdhr.get_stream_url("HDHR-12345678", "2");
        assert_eq!(url, Some("http://192.168.1.100/auto/v2".into()));
    }
}
