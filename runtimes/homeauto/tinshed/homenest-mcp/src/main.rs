//! HomeNest MCP Server Binary
//!
//! Standalone MCP server for HomeNest operations.
//! Provides Unix socket-based access to media playback, automation, TV/DVR, and system status.

use clap::Parser;
use log::{info, error};
use homenest_mcp::HomenestMcpServer;

#[derive(Parser)]
#[command(name = "homenest-mcp")]
#[command(about = "HomeNest MCP Server — media, automation, TV/DVR")]
#[command(version)]
struct Cli {
    /// Path to media directory
    #[arg(short, long, default_value = "~/media")]
    media_dir: String,

    /// Socket path (default: XDG_DATA_HOME/udos/mcp/homenest.sock)
    #[arg(short, long)]
    socket: Option<String>,

    /// Enable verbose logging
    #[arg(short, long)]
    verbose: bool,
}

#[tokio::main]
async fn main() {
    let cli = Cli::parse();

    // Initialize logging
    if cli.verbose {
        std::env::set_var("RUST_LOG", "debug");
    } else {
        std::env::set_var("RUST_LOG", "info");
    }
    env_logger::init();

    // Expand ~ in media_dir
    let media_dir = if cli.media_dir.starts_with("~/") {
        let home = std::env::var("HOME").unwrap_or_else(|_| ".".to_string());
        cli.media_dir.replacen("~/", &format!("{}/", home), 1)
    } else {
        cli.media_dir.clone()
    };

    info!("Starting HomeNest MCP Server");
    info!("Media directory: {}", media_dir);

    let mut server = HomenestMcpServer::new(&media_dir);

    match server.start().await {
        Ok(_) => {
            info!("HomeNest MCP server started successfully");
            // Keep server running
            tokio::signal::ctrl_c().await.expect("Failed to install Ctrl+C handler");
            info!("Shutting down HomeNest MCP server...");
            server.stop().await;
        }
        Err(e) => {
            error!("Failed to start HomeNest MCP server: {}", e);
            std::process::exit(1);
        }
    }
}
