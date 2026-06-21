//! homenest-debian — Debian packaging for HomeNest
//!
//! Generates DEB package structure and APT repository configuration.

use serde::{Deserialize, Serialize};

/// Debian package control file structure
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct DebControl {
    pub package: String,
    pub version: String,
    pub section: String,
    pub priority: String,
    pub architecture: String,
    pub depends: Vec<String>,
    pub recommends: Vec<String>,
    pub suggests: Vec<String>,
    pub maintainer: String,
    pub description: String,
    pub homepage: String,
}

/// Systemd service definition for the package
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SystemdService {
    pub name: String,
    pub description: String,
    pub exec_start: String,
    pub service_type: String,
    pub user_service: bool,
}

/// Generate the default HomeNest DEB control file
pub fn generate_control() -> DebControl {
    DebControl {
        package: "homenest".to_string(),
        version: "0.5.0".to_string(),
        section: "utils".to_string(),
        priority: "optional".to_string(),
        architecture: "amd64".to_string(),
        depends: vec![
            "libmpv2 (>= 0.39)".to_string(),
            "libc6 (>= 2.35)".to_string(),
            "libssl3 (>= 3.0)".to_string(),
        ],
        recommends: vec![
            "yt-dlp".to_string(),
            "ffmpeg".to_string(),
            "flatpak".to_string(),
        ],
        suggests: vec![
            "homeassistant".to_string(),
            "hdhomerun".to_string(),
        ],
        maintainer: "uDos Team <team@udos.io>".to_string(),
        description: "HomeNest — home automation console for 10-foot viewing with controller navigation".to_string(),
        homepage: "https://github.com/uDosGo/uCode3".to_string(),
    }
}

/// Generate systemd service files for HomeNest
pub fn generate_services() -> Vec<SystemdService> {
    vec![
        SystemdService {
            name: "homenest-mcp".to_string(),
            description: "HomeNest MCP server — Unix socket JSON-RPC".to_string(),
            exec_start: "/usr/bin/homenest-mcp".to_string(),
            service_type: "simple".to_string(),
            user_service: true,
        },
        SystemdService {
            name: "homenest-feed".to_string(),
            description: "HomeNest feed spool — RSS polling and event management".to_string(),
            exec_start: "/usr/bin/homenest-feed".to_string(),
            service_type: "simple".to_string(),
            user_service: true,
        },
    ]
}

impl DebControl {
    /// Render as Debian control file format
    pub fn to_control_string(&self) -> String {
        format!(
            r#"Package: {}
Version: {}
Section: {}
Priority: {}
Architecture: {}
Depends: {}
Recommends: {}
Suggests: {}
Maintainer: {}
Description: {}
Homepage: {}
"#,
            self.package,
            self.version,
            self.section,
            self.priority,
            self.architecture,
            self.depends.join(", "),
            self.recommends.join(", "),
            self.suggests.join(", "),
            self.maintainer,
            self.description,
            self.homepage,
        )
    }
}

impl SystemdService {
    /// Render as systemd unit file
    pub fn to_unit_string(&self) -> String {
        let prefix = if self.user_service { "--user" } else { "" };
        format!(
            r#"[Unit]
Description={}

[Service]
Type={}
ExecStart={}
Restart=on-failure
RestartSec=5

[Install]
WantedBy={}-default.target
"#,
            self.description,
            self.service_type,
            self.exec_start,
            if self.user_service { "default" } else { "multi-user" },
        )
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_control_generation() {
        let control = generate_control();
        assert_eq!(control.package, "homenest");
        assert!(control.depends.contains(&"libmpv2 (>= 0.39)".to_string()));
    }

    #[test]
    fn test_control_string() {
        let control = generate_control();
        let s = control.to_control_string();
        assert!(s.contains("Package: homenest"));
        assert!(s.contains("Architecture: amd64"));
    }

    #[test]
    fn test_service_unit() {
        let service = SystemdService {
            name: "homenest-mcp".to_string(),
            description: "MCP server".to_string(),
            exec_start: "/usr/bin/homenest-mcp".to_string(),
            service_type: "simple".to_string(),
            user_service: true,
        };
        let unit = service.to_unit_string();
        assert!(unit.contains("Description=MCP server"));
        assert!(unit.contains("ExecStart=/usr/bin/homenest-mcp"));
        assert!(unit.contains("WantedBy=default.target"));
    }
}
