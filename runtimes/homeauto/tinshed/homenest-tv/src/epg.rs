//! EPG Parser — XMLTV format parser for TV guide data

use crate::{Channel, ChannelSource, EpgData, EpgSnapshot, Program};
use chrono::{DateTime, Utc};
use quick_xml::events::Event;
use quick_xml::Reader;
use std::path::Path;
use uuid::Uuid;

/// Parse an XMLTV file from a path
pub fn parse_xmltv_file(path: &Path) -> Result<EpgSnapshot, String> {
    let content = std::fs::read_to_string(path)
        .map_err(|e| format!("Failed to read XMLTV file {:?}: {}", path, e))?;
    parse_xmltv(&content)
}

/// Parse XMLTV content string
pub fn parse_xmltv(xml: &str) -> Result<EpgSnapshot, String> {
    let mut reader = Reader::from_str(xml);
    reader.trim_text(true);

    let mut channels = Vec::new();
    let mut programs = Vec::new();
    let mut buf = Vec::new();

    let mut current_channel_id = String::new();
    let mut current_channel_name = String::new();
    let mut current_channel_icon = None;
    let mut in_channel = false;
    let mut in_program = false;

    let mut current_program = Program {
        id: String::new(),
        channel_id: String::new(),
        title: String::new(),
        subtitle: None,
        description: None,
        start_time: String::new(),
        end_time: String::new(),
        duration_minutes: 0,
        category: None,
        episode_title: None,
        episode_number: None,
        season_number: None,
        year: None,
        rating: None,
        icon_url: None,
        is_live: false,
        is_new: false,
        is_movie: false,
        is_sports: false,
    };

    loop {
        match reader.read_event_into(&mut buf) {
            Ok(Event::Start(ref e)) => {
                match e.name().as_ref() {
                    b"channel" => {
                        in_channel = true;
                        current_channel_id = e.attributes()
                            .filter_map(|a| a.ok())
                            .find(|a| a.key.as_ref() == b"id")
                            .and_then(|a| String::from_utf8(a.value.to_vec()).ok())
                            .unwrap_or_default();
                        current_channel_name.clear();
                        current_channel_icon = None;
                    }
                    b"programme" => {
                        in_program = true;
                        let mut prog_id = String::new();
                        let mut channel_id = String::new();
                        let mut start = String::new();
                        let mut stop = String::new();

                        for attr in e.attributes().filter_map(|a| a.ok()) {
                            match attr.key.as_ref() {
                                b"start" => start = String::from_utf8(attr.value.to_vec()).unwrap_or_default(),
                                b"stop" => stop = String::from_utf8(attr.value.to_vec()).unwrap_or_default(),
                                b"channel" => channel_id = String::from_utf8(attr.value.to_vec()).unwrap_or_default(),
                                _ => {}
                            }
                        }

                        current_program = Program {
                            id: Uuid::new_v4().to_string(),
                            channel_id,
                            title: String::new(),
                            subtitle: None,
                            description: None,
                            start_time: start,
                            end_time: stop,
                            duration_minutes: 0,
                            category: None,
                            episode_title: None,
                            episode_number: None,
                            season_number: None,
                            year: None,
                            rating: None,
                            icon_url: None,
                            is_live: false,
                            is_new: false,
                            is_movie: false,
                            is_sports: false,
                        };
                    }
                    b"icon" => {
                        let src = e.attributes()
                            .filter_map(|a| a.ok())
                            .find(|a| a.key.as_ref() == b"src")
                            .and_then(|a| String::from_utf8(a.value.to_vec()).ok());
                        if in_channel {
                            current_channel_icon = src;
                        } else if in_program {
                            current_program.icon_url = src;
                        }
                    }
                    _ => {}
                }
            }
            Ok(Event::End(ref e)) => {
                match e.name().as_ref() {
                    b"channel" => {
                        if in_channel {
                            channels.push(Channel {
                                id: current_channel_id.clone(),
                                number: current_channel_id.clone(),
                                name: current_channel_name.clone(),
                                icon_url: current_channel_icon.clone(),
                                source: ChannelSource::Custom,
                            });
                            in_channel = false;
                        }
                    }
                    b"programme" => {
                        if in_program {
                            // Calculate duration
                            if let (Some(start), Some(end)) = (
                                parse_xmltv_time(&current_program.start_time),
                                parse_xmltv_time(&current_program.end_time),
                            ) {
                                let dur = (end - start).num_minutes() as u32;
                                current_program.duration_minutes = dur;
                            }

                            programs.push(current_program.clone());
                            in_program = false;
                        }
                    }
                    _ => {}
                }
            }
            Ok(Event::Text(ref e)) => {
                let text = e.unescape().unwrap_or_default().to_string();
                if in_channel {
                    // Check parent element via reader depth
                    current_channel_name = text;
                }
            }
            Ok(Event::Eof) => break,
            Err(e) => return Err(format!("XML parse error: {}", e)),
            _ => {}
        }
        buf.clear();
    }

    Ok(EpgSnapshot {
        channels,
        programs,
        generated_at: Utc::now().to_rfc3339(),
        source: "xmltv".into(),
    })
}

/// Parse XMLTV time format (YYYYMMDDHHMMSS +offset)
fn parse_xmltv_time(time_str: &str) -> Option<DateTime<Utc>> {
    // XMLTV format: 20260517183000 +1000
    let time_str = time_str.trim();
    if time_str.len() < 14 {
        return None;
    }

    let date_part = &time_str[..14];
    let offset_part = if time_str.len() > 14 { &time_str[14..].trim() } else { "" };

    let year: i32 = date_part[0..4].parse().ok()?;
    let month: u32 = date_part[4..6].parse().ok()?;
    let day: u32 = date_part[6..8].parse().ok()?;
    let hour: u32 = date_part[8..10].parse().ok()?;
    let min: u32 = date_part[10..12].parse().ok()?;
    let sec: u32 = date_part[12..14].parse().ok()?;

    // Parse offset
    let offset_hours: i32 = if offset_part.len() >= 3 {
        offset_part[..3].parse().unwrap_or(0)
    } else {
        0
    };
    let offset_minutes: i32 = if offset_part.len() >= 5 {
        offset_part[3..5].parse().unwrap_or(0)
    } else {
        0
    };

    let total_offset = chrono::FixedOffset::east_opt(offset_hours * 3600 + offset_minutes * 60)?;
    let naive = chrono::NaiveDate::from_ymd_opt(year, month, day)?
        .and_hms_opt(hour, min, sec)?;
    let dt = total_offset.from_utc_datetime(&naive);
    Some(dt.with_timezone(&Utc))
}

/// Get EPG data for a specific channel
pub fn get_channel_epg(snapshot: &EpgSnapshot, channel_id: &str) -> Option<EpgData> {
    let channel = snapshot.channels.iter().find(|c| c.id == channel_id)?.clone();
    let programs: Vec<Program> = snapshot.programs.iter()
        .filter(|p| p.channel_id == channel_id)
        .cloned()
        .collect();

    Some(EpgData { channel, programs })
}

/// Get currently airing programs
pub fn get_current_programs(snapshot: &EpgSnapshot) -> Vec<&Program> {
    let now = Utc::now().to_rfc3339();
    snapshot.programs.iter()
        .filter(|p| p.start_time <= now && p.end_time > now)
        .collect()
}

/// Search programs by title
pub fn search_programs<'a>(snapshot: &'a EpgSnapshot, query: &str) -> Vec<&'a Program> {
    let q = query.to_lowercase();
    snapshot.programs.iter()
        .filter(|p| p.title.to_lowercase().contains(&q)
            || p.subtitle.as_ref().map(|s| s.to_lowercase().contains(&q)).unwrap_or(false)
            || p.description.as_ref().map(|d| d.to_lowercase().contains(&q)).unwrap_or(false))
        .collect()
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_parse_xmltv_time() {
        let dt = parse_xmltv_time("20260517183000 +1000");
        assert!(dt.is_some());
    }

    #[test]
    fn test_parse_basic_xmltv() {
        let xml = r#"<?xml version="1.0" encoding="UTF-8"?>
<tv>
  <channel id="ABC">
    <display-name>ABC HD</display-name>
    <icon src="http://example.com/abc.png"/>
  </channel>
  <programme start="20260517180000 +1000" stop="20260517183000 +1000" channel="ABC">
    <title>Evening News</title>
    <desc>Today's top stories</desc>
    <category>News</category>
  </programme>
</tv>"#;

        let snapshot = parse_xmltv(xml).unwrap();
        assert_eq!(snapshot.channels.len(), 1);
        assert_eq!(snapshot.channels[0].name, "ABC HD");
        assert_eq!(snapshot.programs.len(), 1);
        assert_eq!(snapshot.programs[0].title, "Evening News");
    }

    #[test]
    fn test_search_programs() {
        let xml = r#"<?xml version="1.0" encoding="UTF-8"?>
<tv>
  <channel id="ABC"><display-name>ABC</display-name></channel>
  <programme start="20260517180000 +1000" stop="20260517183000 +1000" channel="ABC">
    <title>Evening News</title>
  </programme>
  <programme start="20260517183000 +1000" stop="20260517190000 +1000" channel="ABC">
    <title>Movie Night</title>
  </programme>
</tv>"#;

        let snapshot = parse_xmltv(xml).unwrap();
        let results = search_programs(&snapshot, "news");
        assert_eq!(results.len(), 1);
        assert_eq!(results[0].title, "Evening News");
    }
}
