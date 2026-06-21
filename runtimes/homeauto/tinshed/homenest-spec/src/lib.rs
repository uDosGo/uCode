//! HomeNest USX Compiler
//!
//! Parses USX bundle files into executable automation actions.
//! Supports JSON and YAML formats with validation.

use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::path::Path;

pub mod parser;
pub mod types;
pub mod validator;

pub use parser::UsxParser;
pub use types::*;
pub use validator::UsxValidator;

/// Compile a USX bundle file into executable actions
pub fn compile_usx(path: &Path) -> anyhow::Result<UsxBundle> {
    let content = std::fs::read_to_string(path)?;
    let parser = UsxParser::new();
    let bundle = parser.parse(&content, path)?;
    let validator = UsxValidator::new();
    validator.validate(&bundle)?;
    Ok(bundle)
}

/// Compile a USX bundle from a string
pub fn compile_usx_str(content: &str, source: &str) -> anyhow::Result<UsxBundle> {
    let parser = UsxParser::new();
    let bundle = parser.parse(content, Path::new(source))?;
    let validator = UsxValidator::new();
    validator.validate(&bundle)?;
    Ok(bundle)
}
