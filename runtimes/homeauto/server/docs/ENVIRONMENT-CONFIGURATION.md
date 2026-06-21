# Environment Configuration

This guide covers the runtime environment variables that `uHomeNest`
actually reads today and the checked-in example files that operators can copy
into service-managed environments.

## Active Runtime Variables

`uHomeNest` currently reads these environment variables from the process
environment:

- `JELLYFIN_URL`: base URL for the local Jellyfin instance
- `JELLYFIN_API_KEY`: API key used for Jellyfin requests
- `HDHOMERUN_HOST`: optional HDHomeRun tuner hostname or IP
- `UHOME_TUNER_DISCOVERY_EXTRA_HOSTS`: optional comma-separated hostnames or IPs
  probed by `uhome.tuner.discover` after the explicit `host` param, `HDHOMERUN_HOST`,
  and before `hdhomerun.local`
- `HA_BRIDGE_ENABLED`: `true`/`false` toggle for Home Assistant bridge behavior
- `UHOME_SYNC_RECORD_CONTRACT_PATH` / `UHOME_SYNC_RECORD_SCHEMA_PATH`: override paths
  to bundled sync-record JSON contract and JSON Schema (defaults under
  `src/uhome_server/contracts/`)
- `UHOME_NETWORK_POLICY_CONTRACT_PATH` / `UHOME_NETWORK_POLICY_SCHEMA_PATH`: override
  paths for the uHOME LAN policy contract and schema

Those values are resolved in [`src/uhome_server/config.py`](../src/uhome_server/config.py)
and override values stored in `memory/config/uhome.json`.

## Checked-In Example

The canonical example file is [`config/environment.example.env`](../config/environment.example.env).

Copy it into an operator-managed location such as `/etc/uhome/uhome-server.env`
and edit the values for the target host:

```bash
sudo install -d -m 0755 /etc/uhome
sudo cp config/environment.example.env /etc/uhome/uhome-server.env
sudoedit /etc/uhome/uhome-server.env
```

Example:

```env
JELLYFIN_URL=http://127.0.0.1:8096
JELLYFIN_API_KEY=replace-with-real-key
HDHOMERUN_HOST=192.168.1.50
HA_BRIDGE_ENABLED=false
```

## systemd Integration

Reference the environment file from the service unit:

```ini
[Service]
EnvironmentFile=/etc/uhome/uhome-server.env
WorkingDirectory=/opt/uhome-server
ExecStart=/home/uhome/.udos/venv/uhome-server/bin/python -m uvicorn uhome_server.app:app --host 0.0.0.0 --port 7890
```

After editing the service or environment file:

```bash
sudo systemctl daemon-reload
sudo systemctl restart uhome-server
```

## Validation

Run the prerequisite checker before first start:

```bash
bash scripts/check-prereqs.sh --storage-path /media/library --workspace-path ~/.workspace
```

Run the post-install validator after the service is up:

```bash
bash scripts/validate-install.sh
```
