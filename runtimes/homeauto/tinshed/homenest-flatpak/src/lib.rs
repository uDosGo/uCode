//! homenest-flatpak — Flatpak packaging for HomeNest on Linux Mint
//!
//! Generates Flatpak manifest and build scripts for distribution.

use serde::{Deserialize, Serialize};

/// Flatpak manifest structure
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct FlatpakManifest {
    pub id: String,
    pub runtime: String,
    pub runtime_version: String,
    pub sdk: String,
    pub command: String,
    pub finish_args: Vec<String>,
    pub modules: Vec<FlatpakModule>,
}

/// A Flatpak module (build step)
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct FlatpakModule {
    pub name: String,
    pub buildsystem: String,
    pub sources: Vec<FlatpakSource>,
    pub build_options: Option<FlatpakBuildOptions>,
}

/// Source definition for a module
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct FlatpakSource {
    pub source_type: String, // "archive", "git", "dir"
    pub url: Option<String>,
    pub path: Option<String>,
    pub tag: Option<String>,
    pub commit: Option<String>,
    pub sha256: Option<String>,
}

/// Build options for a module
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct FlatpakBuildOptions {
    pub build_args: Option<Vec<String>>,
    pub install_dir: Option<String>,
    pub env: Option<Vec<String>>,
}

/// Generate the default HomeNest Flatpak manifest
pub fn generate_manifest() -> FlatpakManifest {
    FlatpakManifest {
        id: "io.udos.homenest".to_string(),
        runtime: "org.freedesktop.Platform".to_string(),
        runtime_version: "24.08".to_string(),
        sdk: "org.freedesktop.Sdk".to_string(),
        command: "homenest-console".to_string(),
        finish_args: vec![
            "--socket=wayland".to_string(),
            "--socket=fallback-x11".to_string(),
            "--socket=pulseaudio".to_string(),
            "--device=dri".to_string(),
            "--share=network".to_string(),
            "--share=ipc".to_string(),
            "--filesystem=~/media".to_string(),
            "--filesystem=~/.local/share/udos".to_string(),
            "--filesystem=~/.config/udos".to_string(),
            "--talk-name=org.freedesktop.Flatpak".to_string(),
        ],
        modules: vec![
            FlatpakModule {
                name: "mpv".to_string(),
                buildsystem: "meson".to_string(),
                sources: vec![FlatpakSource {
                    source_type: "archive".to_string(),
                    url: Some("https://github.com/mpv-player/mpv/archive/refs/tags/v0.39.0.tar.gz".to_string()),
                    path: None,
                    tag: None,
                    commit: None,
                    sha256: None,
                }],
                build_options: Some(FlatpakBuildOptions {
                    build_args: Some(vec![
                        "-Dlibmpv=true".to_string(),
                        "-Dcplayer=false".to_string(),
                    ]),
                    install_dir: None,
                    env: None,
                }),
            },
            FlatpakModule {
                name: "homenest".to_string(),
                buildsystem: "simple".to_string(),
                sources: vec![FlatpakSource {
                    source_type: "dir".to_string(),
                    url: None,
                    path: Some("..".to_string()),
                    tag: None,
                    commit: None,
                    sha256: None,
                }],
                build_options: Some(FlatpakBuildOptions {
                    build_args: Some(vec![
                        "cargo build --release --bin homenest-mcp".to_string(),
                        "cp target/release/homenest-mcp /app/bin/".to_string(),
                    ]),
                    install_dir: None,
                    env: Some(vec!["CARGO_HOME=/run/build/homenest/cargo".to_string()]),
                }),
            },
        ],
    }
}

impl FlatpakManifest {
    /// Render as YAML string
    pub fn to_yaml(&self) -> String {
        format!(
            r#"id: {}
runtime: {}
runtime-version: {}
sdk: {}
command: {}
finish-args:
{}
modules:
  - name: mpv
    buildsystem: meson
    sources:
      - type: archive
        url: https://github.com/mpv-player/mpv/archive/refs/tags/v0.39.0.tar.gz
    build-options:
      build-args:
        - -Dlibmpv=true
        - -Dcplayer=false

  - name: homenest
    buildsystem: simple
    sources:
      - type: dir
        path: ..
    build-options:
      build-args:
        - cargo build --release --bin homenest-mcp
        - cp target/release/homenest-mcp /app/bin/
      env:
        - CARGO_HOME=/run/build/homenest/cargo
"#,
            self.id,
            self.runtime,
            self.runtime_version,
            self.sdk,
            self.command,
            self.finish_args
                .iter()
                .map(|a| format!("    - {}", a))
                .collect::<Vec<_>>()
                .join("\n"),
        )
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_manifest_generation() {
        let manifest = generate_manifest();
        assert_eq!(manifest.id, "io.udos.homenest");
        assert_eq!(manifest.runtime, "org.freedesktop.Platform");
        assert_eq!(manifest.modules.len(), 2);
    }

    #[test]
    fn test_yaml_output() {
        let manifest = generate_manifest();
        let yaml = manifest.to_yaml();
        assert!(yaml.contains("io.udos.homenest"));
        assert!(yaml.contains("org.freedesktop.Platform"));
        assert!(yaml.contains("homenest-mcp"));
    }
}
