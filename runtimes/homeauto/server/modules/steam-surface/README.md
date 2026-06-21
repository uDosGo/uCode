# Steam Surface

Focus:

- Linux presentation launchers
- Steam-console and thin-GUI operation
- direct-display server modes

Current runtime anchors:

- `src/uhome_server/services/uhome_presentation_service.py`
- `src/uhome_server/routes/platform.py`
- `src/uhome_server/cli.py`

Notes:

- this module owns server-side presentation control
- Windows gaming remains auxiliary and belongs to the deployment story, not this
  runtime module
