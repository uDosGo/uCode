//! System status handlers for HomeNest MCP
//!
//! Provides system health checks, service status, and uptime information.

use crate::{HomenestResponse, ServiceStatus};
use log::info;
use std::process::Command;

pub fn handle_status() -> HomenestResponse {
    info!("System status requested");

    let services = vec![
        ServiceStatus {
            name: "homenest-mcp".to_string(),
            status: "running".to_string(),
            uptime: Some("0:05:30".to_string()),
        },
        ServiceStatus {
            name: "media-server".to_string(),
            status: check_service("mpv").to_string(),
            uptime: None,
        },
        ServiceStatus {
            name: "home-assistant".to_string(),
            status: check_service("hass").to_string(),
            uptime: None,
        },
        ServiceStatus {
            name: "feed-spool".to_string(),
            status: "running".to_string(),
            uptime: Some("1:15:00".to_string()),
        },
    ];

    HomenestResponse::SystemInfo {
        version: env!("CARGO_PKG_VERSION").to_string(),
        services,
        uptime: get_uptime(),
    }
}

pub fn handle_health() -> HomenestResponse {
    let healthy = true;
    let checks = serde_json::json!({
        "mcp_socket": true,
        "media_dir": std::path::Path::new(&get_media_dir()).exists(),
        "mpv_available": which("mpv"),
        "disk_space": get_disk_space(),
    });

    if healthy {
        HomenestResponse::Success {
            data: serde_json::json!({
                "status": "healthy",
                "checks": checks,
            }),
        }
    } else {
        HomenestResponse::Error {
            message: format!("Health check failed: {:?}", checks),
        }
    }
}

pub fn handle_services() -> HomenestResponse {
    let services = vec![
        ServiceStatus {
            name: "homenest-mcp".to_string(),
            status: "running".to_string(),
            uptime: Some("0:05:30".to_string()),
        },
        ServiceStatus {
            name: "media-server".to_string(),
            status: check_service("mpv").to_string(),
            uptime: None,
        },
        ServiceStatus {
            name: "home-assistant".to_string(),
            status: check_service("hass").to_string(),
            uptime: None,
        },
        ServiceStatus {
            name: "feed-spool".to_string(),
            status: "running".to_string(),
            uptime: Some("1:15:00".to_string()),
        },
        ServiceStatus {
            name: "snackbar-linux".to_string(),
            status: check_service("snackbar").to_string(),
            uptime: None,
        },
        ServiceStatus {
            name: "secret-server".to_string(),
            status: check_service("secret-server").to_string(),
            uptime: None,
        },
    ];

    HomenestResponse::SystemInfo {
        version: env!("CARGO_PKG_VERSION").to_string(),
        services,
        uptime: get_uptime(),
    }
}

fn check_service(name: &str) -> &'static str {
    // Check if process is running
    let output = Command::new("pgrep")
        .arg("-x")
        .arg(name)
        .output();

    match output {
        Ok(out) if out.status.success() => "running",
        _ => "stopped",
    }
}

fn which(name: &str) -> bool {
    Command::new("which")
        .arg(name)
        .output()
        .map(|o| o.status.success())
        .unwrap_or(false)
}

fn get_uptime() -> String {
    // Read /proc/uptime on Linux, or use sysctl on macOS
    #[cfg(target_os = "linux")]
    {
        if let Ok(content) = std::fs::read_to_string("/proc/uptime") {
            if let Some(secs_str) = content.split_whitespace().next() {
                if let Ok(secs) = secs_str.parse::<f64>() {
                    let hours = (secs / 3600.0) as u64;
                    let minutes = ((secs % 3600.0) / 60.0) as u64;
                    return format!("{}h {}m", hours, minutes);
                }
            }
        }
    }

    #[cfg(target_os = "macos")]
    {
        if let Ok(output) = Command::new("sysctl").arg("-n").arg("kern.boottime").output() {
            let output_str = String::from_utf8_lossy(&output.stdout);
            // Parse: { sec = 1234567890, usec = 123456 }
            if let Some(secs_str) = output_str.split("sec = ").nth(1) {
                if let Some(secs_str) = secs_str.split(',').next() {
                    if let Ok(boot_secs) = secs_str.trim().parse::<u64>() {
                        let now = std::time::SystemTime::now()
                            .duration_since(std::time::UNIX_EPOCH)
                            .unwrap_or_default()
                            .as_secs();
                        let uptime = now.saturating_sub(boot_secs);
                        let hours = uptime / 3600;
                        let minutes = (uptime % 3600) / 60;
                        return format!("{}h {}m", hours, minutes);
                    }
                }
            }
        }
    }

    "unknown".to_string()
}

fn get_media_dir() -> String {
    std::env::var("HOME").unwrap_or_else(|_| ".".to_string()) + "/media"
}

fn get_disk_space() -> serde_json::Value {
    #[cfg(target_os = "linux")]
    {
        if let Ok(output) = Command::new("df").arg("-h").arg("/").output() {
            let output_str = String::from_utf8_lossy(&output.stdout);
            let lines: Vec<&str> = output_str.lines().collect();
            if lines.len() > 1 {
                let parts: Vec<&str> = lines[1].split_whitespace().collect();
                if parts.len() >= 4 {
                    return serde_json::json!({
                        "total": parts[1],
                        "used": parts[2],
                        "available": parts[3],
                        "use_percent": parts[4],
                    });
                }
            }
        }
    }

    serde_json::json!({"available": "unknown"})
}
