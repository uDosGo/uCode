# LAN Discovery

Purpose:

- track household server nodes
- track storage members and partial availability
- expose topology health to dashboards and clients

Current runtime anchors:

- `src/uhome_server/cluster/registry.py`
- `src/uhome_server/routes/network.py`

Notes:

- this is currently a file-backed registry scaffold, not a full discovery or
  election system
