//! RSS Poller — Configurable RSS polling for feed ingestion

use crate::types::RssFeed;
use crate::FeedConfig;
use chrono::Utc;
use quick_xml::events::Event;
use quick_xml::Reader;
use std::collections::HashMap;
use std::time::Duration;

/// A configured RSS feed source
#[derive(Debug, Clone)]
pub struct RssSource {
    pub name: String,
    pub url: String,
    pub poll_interval_secs: u64,
    pub last_polled: Option<String>,
    pub enabled: bool,
}

/// RSS poller for managing multiple feed sources
pub struct RssPoller {
    sources: Vec<RssSource>,
    config: FeedConfig,
    client: reqwest::Client,
}

impl RssPoller {
    /// Create a new RSS poller
    pub fn new(config: FeedConfig) -> Self {
        let client = reqwest::Client::builder()
            .timeout(Duration::from_secs(30))
            .user_agent("HomeNest/0.2")
            .build()
            .unwrap_or_default();

        Self {
            sources: Vec::new(),
            config,
            client,
        }
    }

    /// Add an RSS source to poll
    pub fn add_source(&mut self, name: &str, url: &str, poll_interval_secs: u64) {
        self.sources.push(RssSource {
            name: name.to_string(),
            url: url.to_string(),
            poll_interval_secs,
            last_polled: None,
            enabled: true,
        });
    }

    /// Remove an RSS source by name
    pub fn remove_source(&mut self, name: &str) {
        self.sources.retain(|s| s.name != name);
    }

    /// Poll a specific RSS feed URL
    pub async fn poll_url(&self, url: &str) -> Result<RssFeed, String> {
        let response = self.client.get(url)
            .send()
            .await
            .map_err(|e| format!("HTTP request failed: {}", e))?;

        let body = response.text()
            .await
            .map_err(|e| format!("Failed to read response body: {}", e))?;

        Self::parse_rss_xml(&body)
    }

    /// Poll all enabled sources that are due for polling
    pub async fn poll_due(&mut self) -> Vec<(String, Result<RssFeed, String>)> {
        let now = Utc::now();
        let mut results = Vec::new();

        for source in &mut self.sources {
            if !source.enabled {
                continue;
            }

            // Check if due for polling
            let should_poll = match &source.last_polled {
                Some(last) => {
                    let last_time = chrono::DateTime::parse_from_rfc3339(last)
                        .map(|dt| dt.with_timezone(&Utc))
                        .unwrap_or(now - Duration::from_secs(source.poll_interval_secs));
                    (now - last_time).num_seconds() as u64 >= source.poll_interval_secs
                }
                None => true,
            };

            if should_poll {
                let result = self.poll_url(&source.url).await;
                source.last_polled = Some(now.to_rfc3339());
                results.push((source.name.clone(), result));
            }
        }

        results
    }

    /// Parse RSS XML content
    pub fn parse_rss_xml(xml: &str) -> Result<RssFeed, String> {
        let mut reader = Reader::from_str(xml);
        reader.trim_text(true);

        let mut feed = RssFeed {
            title: String::new(),
            description: None,
            link: None,
            items: Vec::new(),
        };

        let mut buf = Vec::new();
        let mut in_channel = false;
        let mut in_item = false;
        let mut current_tag = String::new();
        let mut current_item = crate::types::RssItem {
            title: String::new(),
            link: None,
            description: None,
            pub_date: None,
            author: None,
            categories: Vec::new(),
            guid: None,
        };

        loop {
            match reader.read_event_into(&mut buf) {
                Ok(Event::Start(ref e)) => {
                    current_tag = String::from_utf8_lossy(e.name().as_ref()).to_lowercase();
                    match current_tag.as_str() {
                        "channel" => in_channel = true,
                        "item" => {
                            in_item = true;
                            current_item = crate::types::RssItem {
                                title: String::new(),
                                link: None,
                                description: None,
                                pub_date: None,
                                author: None,
                                categories: Vec::new(),
                                guid: None,
                            };
                        }
                        _ => {}
                    }
                }
                Ok(Event::End(ref e)) => {
                    let tag = String::from_utf8_lossy(e.name().as_ref()).to_lowercase();
                    match tag.as_str() {
                        "channel" => in_channel = false,
                        "item" => {
                            if in_item {
                                feed.items.push(current_item.clone());
                                in_item = false;
                            }
                        }
                        _ => {}
                    }
                    current_tag.clear();
                }
                Ok(Event::Text(ref e)) => {
                    let text = e.unescape().unwrap_or_default().to_string();
                    if in_item {
                        match current_tag.as_str() {
                            "title" => current_item.title = text,
                            "link" => current_item.link = Some(text),
                            "description" => current_item.description = Some(text),
                            "pubdate" => current_item.pub_date = Some(text),
                            "author" => current_item.author = Some(text),
                            "guid" => current_item.guid = Some(text),
                            "category" => current_item.categories.push(text),
                            _ => {}
                        }
                    } else if in_channel {
                        match current_tag.as_str() {
                            "title" => feed.title = text,
                            "description" => feed.description = Some(text),
                            "link" => feed.link = Some(text),
                            _ => {}
                        }
                    }
                }
                Ok(Event::Eof) => break,
                Err(e) => return Err(format!("XML parse error: {}", e)),
                _ => {}
            }
            buf.clear();
        }

        Ok(feed)
    }

    /// Get all configured sources
    pub fn get_sources(&self) -> &[RssSource] {
        &self.sources
    }

    /// Enable or disable a source
    pub fn set_source_enabled(&mut self, name: &str, enabled: bool) -> Result<(), String> {
        let source = self.sources.iter_mut()
            .find(|s| s.name == name)
            .ok_or_else(|| format!("Source not found: {}", name))?;
        source.enabled = enabled;
        Ok(())
    }

    /// Get the number of configured sources
    pub fn source_count(&self) -> usize {
        self.sources.len()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_parse_rss_xml() {
        let xml = r#"<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>Test Feed</title>
    <description>A test RSS feed</description>
    <link>http://example.com</link>
    <item>
      <title>Test Article</title>
      <link>http://example.com/article1</link>
      <description>This is a test article</description>
      <pubDate>Mon, 17 May 2026 10:00:00 GMT</pubDate>
      <category>News</category>
      <category>Tech</category>
      <guid>abc123</guid>
    </item>
    <item>
      <title>Second Article</title>
      <link>http://example.com/article2</link>
      <description>Another test article</description>
    </item>
  </channel>
</rss>"#;

        let feed = RssPoller::parse_rss_xml(xml).unwrap();
        assert_eq!(feed.title, "Test Feed");
        assert_eq!(feed.description, Some("A test RSS feed".into()));
        assert_eq!(feed.items.len(), 2);
        assert_eq!(feed.items[0].title, "Test Article");
        assert_eq!(feed.items[0].categories.len(), 2);
        assert_eq!(feed.items[1].title, "Second Article");
    }

    #[test]
    fn test_parse_empty_feed() {
        let xml = r#"<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>Empty Feed</title>
  </channel>
</rss>"#;

        let feed = RssPoller::parse_rss_xml(xml).unwrap();
        assert_eq!(feed.title, "Empty Feed");
        assert!(feed.items.is_empty());
    }

    #[test]
    fn test_add_and_remove_source() {
        let config = FeedConfig::default();
        let mut poller = RssPoller::new(config);

        poller.add_source("Test", "http://example.com/feed.xml", 900);
        assert_eq!(poller.source_count(), 1);

        poller.remove_source("Test");
        assert_eq!(poller.source_count(), 0);
    }
}
