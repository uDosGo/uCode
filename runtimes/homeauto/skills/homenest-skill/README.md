# HomeNest Skill

The `udo home` CLI command for managing HomeNest — media playback, automation, TV/DVR, and system status.

## Usage

```bash
# System status
udo home status

# Media
udo home media list
udo home media play <id>
udo home media pause
udo home media stop

# Automation
udo home scene list
udo home scene trigger <name>

# TV
udo home tv epg
udo home tv tune <channel>
udo home tv record <channel> [duration]

# USX compilation
udo home compile <path/to/bundle.usx.json>
```

## Architecture

- Communicates with `homenest-mcp` via Unix socket (`/tmp/homenest-mcp.sock`)
- Uses JSON-RPC over the MCP protocol
- Integrates with `udo` CLI via the skill system
