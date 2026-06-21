//! uCode2 Core Library
//!
//! Core functionality for the uCode2 platform

pub mod snack;
pub mod nug;
pub mod binder;
pub mod grid;

/// Get core system version
pub fn version() -> &'static str {
    env!("CARGO_PKG_VERSION")
}
