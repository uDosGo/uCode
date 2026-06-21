# Home Assistant Bridge

Focus:

- Home Assistant gateway integration
- device discovery and command execution
- local automation bridge patterns
- transitional runtime support for the dedicated `uHOME-matter` extension lane

Current runtime anchors:

- `src/uhome_server/services/home_assistant/`
- `src/uhome_server/services/home_assistant_service.py`
- `src/uhome_server/routes/home_assistant.py`
- `docs/services/home-assistant/`

Notes:

- this is the clearest current example of a module plus service split in the
  repo
- new contract definitions and clone profiles should land in `uHOME-matter`
