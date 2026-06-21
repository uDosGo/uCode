//! homenest-docs — HomeNest documentation generator
//!
//! Generates documentation from crate metadata and source annotations:
//! - User guide (console navigation, media setup)
//! - API docs (MCP methods, feed schema)
//! - OBF reference (directives, segments, examples)
//! - Architecture docs (grid, temporal, feed/spool)

pub mod user_guide;
pub mod api_docs;
pub mod obf_reference;
pub mod architecture;

use serde::{Deserialize, Serialize};

/// Documentation section
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct DocSection {
    pub title: String,
    pub content: String,
    pub subsections: Vec<DocSection>,
}

/// Complete documentation set
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct DocumentationSet {
    pub name: String,
    pub version: String,
    pub sections: Vec<DocSection>,
}

impl DocumentationSet {
    pub fn new(name: &str, version: &str) -> Self {
        Self {
            name: name.to_string(),
            version: version.to_string(),
            sections: Vec::new(),
        }
    }

    pub fn add_section(&mut self, section: DocSection) {
        self.sections.push(section);
    }

    /// Render as Markdown
    pub fn to_markdown(&self) -> String {
        let mut md = format!("# {} v{}\n\n", self.name, self.version);
        for section in &self.sections {
            md.push_str(&render_section(&section, 1));
        }
        md
    }

    /// Render as HTML
    pub fn to_html(&self) -> String {
        let mut html = format!(
            "<!DOCTYPE html><html><head><meta charset='utf-8'>\
             <title>{} v{}</title>\
             <style>body{{font-family:sans-serif;max-width:800px;margin:auto;padding:2em}}\
             h1{{border-bottom:2px solid #333}}h2{{color:#444}}code{{background:#f4f4f4;padding:2px 4px}}\
             pre{{background:#f4f4f4;padding:1em;overflow-x:auto}}</style></head><body>",
            self.name, self.version
        );
        html.push_str(&format!("<h1>{} v{}</h1>\n", self.name, self.version));
        for section in &self.sections {
            html.push_str(&render_section_html(&section, 2));
        }
        html.push_str("</body></html>");
        html
    }
}

fn render_section(section: &DocSection, level: usize) -> String {
    let mut md = format!("{} {}\n\n", "#".repeat(level + 1), section.title);
    md.push_str(&section.content);
    md.push('\n');
    for sub in &section.subsections {
        md.push_str(&render_section(sub, level + 1));
    }
    md
}

fn render_section_html(section: &DocSection, level: usize) -> String {
    let mut html = format!("<h{}>{}</h{}>\n", level, section.title, level);
    html.push_str(&format!("<p>{}</p>\n", section.content.replace('\n', "<br>")));
    for sub in &section.subsections {
        html.push_str(&render_section_html(sub, level + 1));
    }
    html
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_documentation_set() {
        let mut docs = DocumentationSet::new("HomeNest", "0.5.0");
        docs.add_section(DocSection {
            title: "Getting Started".into(),
            content: "Welcome to HomeNest.".into(),
            subsections: vec![],
        });
        let md = docs.to_markdown();
        assert!(md.contains("HomeNest v0.5.0"));
        assert!(md.contains("Getting Started"));
    }

    #[test]
    fn test_html_output() {
        let mut docs = DocumentationSet::new("HomeNest", "0.5.0");
        docs.add_section(DocSection {
            title: "API".into(),
            content: "MCP methods.".into(),
            subsections: vec![],
        });
        let html = docs.to_html();
        assert!(html.contains("<h1>HomeNest v0.5.0</h1>"));
        assert!(html.contains("<h2>API</h2>"));
    }
}
