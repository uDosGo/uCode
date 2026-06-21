//! User Guide — Console navigation, media setup, TV guide, automation

use crate::DocSection;

/// Generate the user guide documentation
pub fn generate() -> DocSection {
    DocSection {
        title: "User Guide".into(),
        content: include_str!("../docs/user-guide.md"),
        subsections: vec![
            DocSection {
                title: "Getting Started".into(),
                content: "HomeNest is a home automation console designed for 10-foot viewing with controller navigation.".into(),
                subsections: vec![
                    DocSection {
                        title: "Hardware Requirements".into(),
                        content: "- Linux Mint 22 or macOS 14+\n- 4GB RAM minimum, 8GB recommended\n- Gamepad (Xbox, PlayStation, or generic)\n- HDHomeRun tuner (optional, for live TV)\n- Home Assistant instance (optional, for automation)".into(),
                        subsections: vec![],
                    },
                    DocSection {
                        title: "Installation".into(),
                        content: "```bash\n# Install via Flatpak\nflatpak install homenest.flatpakref\n\n# Or via APT\nsudo apt install homenest\n\n# Or run from source\ncargo run --bin homenest-console\n```".into(),
                        subsections: vec![],
                    },
                ],
            },
            DocSection {
                title: "Controller Navigation".into(),
                content: "HomeNest is designed for controller-first navigation.".into(),
                subsections: vec![
                    DocSection {
                        title: "Basic Controls".into(),
                        content: "| Button | Action |\n|--------|--------|\n| D-Pad / Left Stick | Navigate between tiles |\n| A / Cross | Select / Confirm |\n| B / Circle | Back / Cancel |\n| X / Square | Context menu |\n| Y / Triangle | Toggle sidebar |\n| Start / Menu | Open main menu |\n| Select / View | System overlay |\n| LB / L1 | Previous tab |\n| RB / R1 | Next tab |".into(),
                        subsections: vec![],
                    },
                    DocSection {
                        title: "Keyboard Shortcuts".into(),
                        content: "| Key | Action |\n|-----|--------|\n| Arrow keys | Navigate |\n| Enter | Select |\n| Escape | Back |\n| Tab / Shift+Tab | Next/Previous |\n| Space | Play/Pause |\n| F11 | Fullscreen |".into(),
                        subsections: vec![],
                    },
                ],
            },
            DocSection {
                title: "Media Setup".into(),
                content: "Configure your media library for playback.".into(),
                subsections: vec![
                    DocSection {
                        title: "Media Vault".into(),
                        content: "HomeNest scans `~/media/` for media files. Supported formats:\n- Video: MP4, MKV, AVI, MOV\n- Audio: MP3, FLAC, WAV, AAC\n- Subtitles: SRT, ASS, VTT\n\nTo add media, simply place files in `~/media/` and run:\n```bash\nudo home scan\n```".into(),
                        subsections: vec![],
                    },
                    DocSection {
                        title: "Metadata Workflow".into(),
                        content: "When new media is detected:\n1. Scanner finds file → Feed spool entry\n2. Console notification appears\n3. User confirms → TMDB search\n4. \"Do you own this?\" prompt\n5. Yes: Download metadata, mark playable → Grid cell\n6. No: Add as browsable-only → Visual-only slot".into(),
                        subsections: vec![],
                    },
                    DocSection {
                        title: "YouTube Playback".into(),
                        content: "HomeNest supports YouTube playback via yt-dlp:\n```bash\nudo home play https://youtube.com/watch?v=...\n```".into(),
                        subsections: vec![],
                    },
                ],
            },
            DocSection {
                title: "TV Guide".into(),
                content: "Live TV and EPG guide.".into(),
                subsections: vec![
                    DocSection {
                        title: "Setting Up TV Sources".into(),
                        content: "1. Connect HDHomeRun to your network\n2. Run channel scan from Settings\n3. EPG data loads automatically from XMLTV sources\n4. Browse channels in the TV Guide surface".into(),
                        subsections: vec![],
                    },
                    DocSection {
                        title: "Recording".into(),
                        content: "To schedule a recording:\n1. Navigate to a program in the EPG\n2. Press A to select\n3. Choose \"Record\" or \"Record Series\"\n4. Recording appears in the Recordings list\n\n```bash\nudo home record \"Channel Name\" --start \"2026-05-17 20:00\" --end \"2026-05-17 21:00\"\n```".into(),
                        subsections: vec![],
                    },
                ],
            },
            DocSection {
                title: "Automation".into(),
                content: "Scene and automation management.".into(),
                subsections: vec![
                    DocSection {
                        title: "Running a Scene".into(),
                        content: "1. Navigate to the Automation panel\n2. Select a scene tile\n3. Press A to activate\n\nOr via CLI:\n```bash\nudo home automate goodnight.usx.json\n```".into(),
                        subsections: vec![],
                    },
                    DocSection {
                        title: "Creating OBF Sheets".into(),
                        content: "OBF (Open Bridge Format) sheets define automation scenes:\n```markdown\n# OBF: Movie Time\n# @spec version=1.0\n# @target: homenest-console\n\n## Environment Setup\n- @ha:scene.movie_mode\n- @ha:climate.living_room?temperature=68\n\n## Media Playback\n- @media:resume?position=last\n- @media:volume?level=65\n\n## Delayed Actions\n- @delay:duration=movie\n- @ha:light.living_room?brightness=50\n```".into(),
                        subsections: vec![],
                    },
                ],
            },
            DocSection {
                title: "Voice Control".into(),
                content: "Voice assistant integration.".into(),
                subsections: vec![
                    DocSection {
                        title: "Setting Up Voice".into(),
                        content: "1. Enable voice in Settings\n2. Configure HomeKit bridge or Wyoming STT server\n3. Say \"Hey HomeNest\" followed by a command\n\nSupported commands:\n- \"Play some music\"\n- \"Volume up\" / \"Volume down\" / \"Set volume to 50\"\n- \"Turn on the living room light\"\n- \"Activate movie night scene\"\n- \"What is the status\"\n- \"Search for interstellar\"".into(),
                        subsections: vec![],
                    },
                ],
            },
        ],
    }
}
