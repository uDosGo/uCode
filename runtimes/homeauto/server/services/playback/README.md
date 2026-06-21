# Playback

Purpose:

- report playback readiness and target state
- hand off sessions to household clients
- expose server-side media availability

Current runtime anchors:

- `src/uhome_server/services/uhome_command_handlers.py`
- `src/uhome_server/routes/runtime.py`

Planned next step:

- separate media status, session targeting, and playback control from broader
  command-handler scaffolding
