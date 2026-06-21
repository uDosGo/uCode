# Home Ops

Focus:

- household operational status
- node and storage visibility
- admin and operator control surfaces

Current runtime anchors:

- `src/uhome_server/routes/dashboard.py`
- `src/uhome_server/routes/network.py`
- `src/uhome_server/routes/runtime.py`

Notes:

- this is the server-side operations lane, not the deployment lane
- deployment and bootstrap remain the responsibility of
  `sonic-screwdriver`
