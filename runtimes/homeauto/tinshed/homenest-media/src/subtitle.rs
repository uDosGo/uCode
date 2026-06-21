//! Subtitle parser — SRT/ASS parser and overlay support

use serde::{Deserialize, Serialize};
use std::fs;
use std::path::Path;

/// A single subtitle entry
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SubtitleEntry {
    pub index: u32,
    pub start_time: f64,  // seconds
    pub end_time: f64,    // seconds
    pub text: String,
}

/// Parsed subtitle file
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SubtitleFile {
    pub format: SubtitleFormat,
    pub entries: Vec<SubtitleEntry>,
    pub language: Option<String>,
}

/// Supported subtitle formats
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub enum SubtitleFormat {
    Srt,
    Ass,
    Vtt,
    Unknown,
}

impl SubtitleFormat {
    pub fn from_extension(path: &str) -> Self {
        match path.to_lowercase() {
            p if p.ends_with(".srt") => SubtitleFormat::Srt,
            p if p.ends_with(".ass") || p.ends_with(".ssa") => SubtitleFormat::Ass,
            p if p.ends_with(".vtt") => SubtitleFormat::Vtt,
            _ => SubtitleFormat::Unknown,
        }
    }
}

/// Parse a timestamp string (HH:MM:SS,mmm or HH:MM:SS.mmm) to seconds
fn parse_timestamp(ts: &str) -> Option<f64> {
    let ts = ts.trim().replace(',', ".");
    let parts: Vec<&str> = ts.split(':').collect();
    if parts.len() != 3 {
        return None;
    }
    let hours: f64 = parts[0].parse().ok()?;
    let minutes: f64 = parts[1].parse().ok()?;
    let seconds: f64 = parts[2].parse().ok()?;
    Some(hours * 3600.0 + minutes * 60.0 + seconds)
}

/// Parse an SRT subtitle file
fn parse_srt(content: &str) -> Vec<SubtitleEntry> {
    let mut entries = Vec::new();
    let blocks: Vec<&str> = content.split("\n\n").collect();

    for block in blocks {
        let block = block.trim();
        if block.is_empty() {
            continue;
        }

        let lines: Vec<&str> = block.lines().collect();
        if lines.len() < 3 {
            continue;
        }

        // First line: index
        let index: u32 = match lines[0].trim().parse() {
            Ok(i) => i,
            Err(_) => continue,
        };

        // Second line: time range
        let time_parts: Vec<&str> = lines[1].split(" --> ").collect();
        if time_parts.len() != 2 {
            continue;
        }

        let start_time = match parse_timestamp(time_parts[0]) {
            Some(t) => t,
            None => continue,
        };
        let end_time = match parse_timestamp(time_parts[1]) {
            Some(t) => t,
            None => continue,
        };

        // Remaining lines: text
        let text = lines[2..].join("\n");

        entries.push(SubtitleEntry {
            index,
            start_time,
            end_time,
            text,
        });
    }

    entries
}

/// Parse an ASS subtitle file (basic — extracts dialogue events)
fn parse_ass(content: &str) -> Vec<SubtitleEntry> {
    let mut entries = Vec::new();
    let mut index: u32 = 0;

    for line in content.lines() {
        let line = line.trim();
        if !line.starts_with("Dialogue:") {
            continue;
        }

        // ASS format: Dialogue: layer,start,end,style,name,marginL,marginR,marginV,effect,text
        let parts: Vec<&str> = line.splitn(10, ',').collect();
        if parts.len() < 10 {
            continue;
        }

        let start_time = parse_timestamp(parts[1]).unwrap_or(0.0);
        let end_time = parse_timestamp(parts[2]).unwrap_or(0.0);
        let text = parts[9].to_string();

        index += 1;
        entries.push(SubtitleEntry {
            index,
            start_time,
            end_time,
            text,
        });
    }

    entries
}

/// Parse a subtitle file from its content
pub fn parse_subtitles(content: &str, format: SubtitleFormat) -> Vec<SubtitleEntry> {
    match format {
        SubtitleFormat::Srt => parse_srt(content),
        SubtitleFormat::Ass => parse_ass(content),
        SubtitleFormat::Vtt => {
            // VTT is similar to SRT but with optional header
            // Strip the WEBVTT header if present
            let content = if content.starts_with("WEBVTT") {
                let lines: Vec<&str> = content.lines().collect();
                let start = lines.iter().position(|l| l.contains("-->"))
                    .map(|i| i.saturating_sub(1))
                    .unwrap_or(0);
                lines[start..].join("\n")
            } else {
                content.to_string()
            };
            parse_srt(&content)
        }
        SubtitleFormat::Unknown => Vec::new(),
    }
}

/// Load and parse a subtitle file from disk
pub fn load_subtitle_file(path: &Path) -> Result<SubtitleFile, String> {
    let content = fs::read_to_string(path)
        .map_err(|e| format!("Failed to read subtitle file {:?}: {}", path, e))?;

    let format = SubtitleFormat::from_extension(
        path.to_string_lossy().as_ref()
    );

    let entries = parse_subtitles(&content, format.clone());

    Ok(SubtitleFile {
        format,
        entries,
        language: None,
    })
}

/// Find subtitle entries at a given time position
pub fn get_subtitles_at_time(entries: &[SubtitleEntry], time_secs: f64) -> Vec<&SubtitleEntry> {
    entries.iter()
        .filter(|e| time_secs >= e.start_time && time_secs <= e.end_time)
        .collect()
}

/// Convert subtitle entries to ASS format for mpv overlay
pub fn to_ass_overlay(entries: &[SubtitleEntry]) -> String {
    let mut ass = String::from("[Script Info]\nScriptType: v4.00+\n\n[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n");

    for entry in entries {
        let start = format_time_ass(entry.start_time);
        let end = format_time_ass(entry.end_time);
        let text = entry.text.replace('\n', "\\N");
        ass.push_str(&format!("Dialogue: 0,{},{},Default,,0,0,0,,{}\n", start, end, text));
    }

    ass
}

/// Format seconds to ASS time format (H:MM:SS.cc)
fn format_time_ass(secs: f64) -> String {
    let hours = (secs / 3600.0) as u32;
    let minutes = ((secs % 3600.0) / 60.0) as u32;
    let seconds = (secs % 60.0) as u32;
    let centiseconds = ((secs % 1.0) * 100.0) as u32;
    format!("{}:{:02}:{:02}.{:02}", hours, minutes, seconds, centiseconds)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_parse_srt() {
        let srt = "1\n00:00:01,000 --> 00:00:04,000\nHello world\n\n2\n00:00:05,000 --> 00:00:08,500\nThis is a test\nSecond line";
        let entries = parse_srt(srt);
        assert_eq!(entries.len(), 2);
        assert_eq!(entries[0].text, "Hello world");
        assert_eq!(entries[0].start_time, 1.0);
        assert_eq!(entries[0].end_time, 4.0);
        assert_eq!(entries[1].text, "This is a test\nSecond line");
    }

    #[test]
    fn test_parse_ass() {
        let ass = "[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\nDialogue: 0,0:00:01.00,0:00:04.00,Default,,0,0,0,,Hello from ASS\nDialogue: 0,0:00:05.00,0:00:08.50,Default,,0,0,0,,Second line";
        let entries = parse_ass(ass);
        assert_eq!(entries.len(), 2);
        assert_eq!(entries[0].text, "Hello from ASS");
    }

    #[test]
    fn test_get_subtitles_at_time() {
        let entries = vec![
            SubtitleEntry { index: 1, start_time: 0.0, end_time: 5.0, text: "First".into() },
            SubtitleEntry { index: 2, start_time: 5.0, end_time: 10.0, text: "Second".into() },
        ];

        let at_3 = get_subtitles_at_time(&entries, 3.0);
        assert_eq!(at_3.len(), 1);
        assert_eq!(at_3[0].text, "First");

        let at_5 = get_subtitles_at_time(&entries, 5.0);
        assert_eq!(at_5.len(), 1);
        assert_eq!(at_5[0].text, "Second");
    }

    #[test]
    fn test_format_detection() {
        assert_eq!(SubtitleFormat::from_extension("file.srt"), SubtitleFormat::Srt);
        assert_eq!(SubtitleFormat::from_extension("file.ass"), SubtitleFormat::Ass);
        assert_eq!(SubtitleFormat::from_extension("file.vtt"), SubtitleFormat::Vtt);
        assert_eq!(SubtitleFormat::from_extension("file.txt"), SubtitleFormat::Unknown);
    }
}
