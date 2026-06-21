# uHOME Server Deployment Guide for Ubuntu 20.04+

**Target**: Ubuntu 20.04 LTS, 22.04 LTS, 24.04 LTS  
**Updated**: 2026-03-10  
**Time Estimate**: 30-45 minutes for fresh install

## Quick Start (5 minutes)

For experienced operators on a pre-configured system:

```bash
# Clone repository
git clone https://github.com/uhome-project/uhome-server.git
cd uhome-server

# Install system dependencies (one-time)
sudo apt-get update && sudo apt-get install -y python3.9 python3-venv

# Create Python virtualenv
python3 -m venv ~/.udos/venv/uhome-server
source ~/.udos/venv/uhome-server/bin/activate

# Install uHOME with dev dependencies
pip install -e '.[dev]'

# Run server
uhome

# In another terminal, verify
curl http://localhost:7890/api/health | jq .
```

## Full Deployment Guide

### Phase 1: System Prerequisites (5 minutes)

**Check Ubuntu version:**

```bash
lsb_release -a
# Expected: Ubuntu 20.04 LTS (Focal), 22.04 LTS (Jammy), or newer
```

**Verify available system resources:**

```bash
# Check CPU cores
nproc  # Should have >= 2 cores recommended

# Check available RAM
free -h  # Should have >= 2GB available (1GB minimum)

# Check disk space
df -h /  # Should have >= 10GB for OS

df -h /media/  # Should plan for media storage (100GB+ recommended)
```

**Update system packages:**

```bash
sudo apt-get update
sudo apt-get upgrade -y
sudo apt-get autoremove
```

### Phase 2: Install Python Runtime (5 minutes)

**Install Python 3.9+ and virtualenv tools:**

```bash
# Install Python and build tools
sudo apt-get install -y \
  python3.9 \
  python3-pip \
  python3-venv \
  build-essential \
  git

# Verify Python version
python3 --version  # Should show 3.9+
python3 -m venv --help  # Verify venv available
```

**Verify pip is up to date:**

```bash
python3 -m pip install --upgrade pip setuptools wheel
```

### Phase 3: Clone Repository and Set Up virtualenv (5 minutes)

**Choose installation directory:**

```bash
# Standard location: /opt/uhome-server
# Or: /home/$USER/uhome-server
# Or: /media/uhome-server (if more space needed)

# Create directory (using /opt as example)
sudo mkdir -p /opt/uhome-server
sudo chown $USER:$USER /opt/uhome-server

# Navigate to it
cd /opt/uhome-server
```

**Clone repository:**

```bash
git clone https://github.com/uhome-project/uhome-server.git .

# Verify repo structure
ls -la
# Should see: src/, tests/, docs/, pyproject.toml, README.md, etc.
```

**Create Python virtualenv:**

```bash
# Create virtualenv
python3 -m venv ~/.udos/venv/uhome-server

# Activate virtualenv
source ~/.udos/venv/uhome-server/bin/activate

# Verify activation
which python  # Should point to ~/.udos/venv/uhome-server/bin/python
```

### Phase 4: Install uHOME Server and Dependencies (10 minutes)

**Install uHOME Server:**

```bash
# Ensure virtualenv is active
source /home/uhome/.udos/venv/uhome-server/bin/activate

# Install uHOME Server with dependencies
cd /opt/uhome-server
pip install -e .

# Verify installation
uhome --version  # Should show version number
```

**Verify all dependencies installed:**

```bash
# List installed packages
pip list | grep -i "fastapi\|pydantic\|jellyfin"

# Check key dependencies
python3 -c "import fastapi; import pydantic; print('Core deps OK')"
```

### Phase 5: Configure Storage and Workspace (5 minutes)

**Create media storage directories:**

```bash
# Create library directory (where media will be indexed)
sudo mkdir -p /media/library
sudo chown $USER:$USER /media/library

# Optional: Create DVR storage directory
sudo mkdir -p /media/dvr-storage
sudo chown $USER:$USER /media/dvr-storage

# Verify permissions
ls -ld /media/library /media/dvr-storage
# Should show: drwxr-xr-x with your user as owner
```

**Initialize uHOME workspace:**

```bash
# Run one-time setup
cd /opt/uhome-server

# This creates ~/.workspace with initial registries
source ~/.udos/venv/uhome-server/bin/activate
uhome init

# Verify workspace created
ls -la ~/.workspace/
# Should see: node-registry.json, storage-registry.json, etc.
```

**Configure node role and identity:**

```bash
# Edit workspace settings
vi ~/.workspace/node-settings.json

# Set node identity:
{
  "node_id": "primary-server",
  "hostname": "primary-server",
  "role": "primary",
  "listening_port": 7890
}
```

### Phase 6: Optional Integrations (5-10 minutes)

**Configure Home Assistant integration (optional):**

```bash
# Edit environment or config
vi ~/.workspace/integrations.json

# Add Home Assistant config:
{
  "home_assistant": {
    "enabled": true,
    "url": "http://homeassistant.local:8123",
    "api_token": "YOUR_HA_TOKEN_HERE"
  }
}

# Get Home Assistant token:
# 1. In Home Assistant UI, go to Profile
# 2. Scroll to "Long-lived access tokens"
# 3. Create token, copy to config above
```

**Configure Jellyfin integration (optional):**

```bash
# Edit Jellyfin config
vi ~/.workspace/integrations.json

# Add Jellyfin config:
{
  "jellyfin": {
    "enabled": true,
    "url": "http://jellyfin.local:8096",
    "api_key": "YOUR_JELLYFIN_API_KEY_HERE",
    "library_path": "/media/library"
  }
}

# Get Jellyfin API key:
# 1. In Jellyfin UI, go to Settings → API Keys
# 2. Create key, copy to config above
```

### Phase 7: Set Up systemd Service (5 minutes)

**Create systemd service file:**

```bash
# Create service definition
sudo tee /etc/systemd/system/uhome-server.service > /dev/null << 'EOF'
[Unit]
Description=uHOME Server
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=uhome
Group=uhome
WorkingDirectory=/opt/uhome-server
ExecStart=/home/uhome/.udos/venv/uhome-server/bin/uhome

# Auto-restart if process crashes
Restart=on-failure
RestartSec=10

# Resource limits (adjust for your hardware)
MemoryLimit=2G

# Logging
StandardOutput=journal
StandardError=journal
SyslogIdentifier=uhome-server

[Install]
WantedBy=multi-user.target
EOF
```

**Create uhome system user (if not exists):**

```bash
# Check if uhome user exists
id uhome || sudo useradd -r -s /bin/false -d /opt/uhome-server uhome

# Set ownership of installation
sudo chown -R uhome:uhome /opt/uhome-server
sudo chown -R uhome:uhome /media/library /media/dvr-storage
```

**Enable and start service:**

```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable service to start on boot
sudo systemctl enable uhome-server

# Start service
sudo systemctl start uhome-server

# Check status
sudo systemctl status uhome-server
# Should show: active (running)

# View logs
sudo journalctl -u uhome-server -n 50
# Should see: "INFO: Starting uHOME Server...", "Listening on port 7890"
```

### Phase 8: Validate Installation (5 minutes)

**Test service is running:**

```bash
# Check service status
systemctl is-active uhome-server
# Should print: active

# Check listening port
netstat -tulpn | grep 7890
# Should show: LISTEN on 0.0.0.0:7890
```

**Test API endpoints:**

```bash
# Health check
curl http://localhost:7890/api/health | jq .
# Expected: {"status": "ok", "nodes_online": 1}

# Browse library (should be empty initially)
curl http://localhost:7890/api/household/browse | jq '.browse_results | length'
# Expected: 0 (no media added yet)

# Launcher status
curl http://localhost:7890/api/launcher/status | jq '.available_titles | length'
# Expected: [] (empty)
```

**Add test media (optional):**

```bash
# Copy sample media to library
cp ~/Videos/*.mkv /media/library/ 2>/dev/null || echo "No videos found"

# Trigger library rescan
curl -X POST http://localhost:7890/api/debug/library-rebuild

# Wait 10 seconds for rescan
sleep 10

# Verify media appears
curl http://localhost:7890/api/household/browse | jq '.browse_results | length'
# Expected: > 0
```

**Check logging:**

```bash
# View recent logs
sudo journalctl -u uhome-server -n 20

# Follow logs in real-time
sudo journalctl -u uhome-server -f
# Ctrl+C to exit

# Check for errors
sudo journalctl -u uhome-server | grep -i error | head -10
# Should be empty or only expected warnings
```

### Phase 9: Configure Firewall (if needed)

**If running host firewall, allow uHOME port:**

```bash
# For UFW (Ubuntu's default firewall)
sudo ufw allow 7890/tcp
sudo ufw allow 7890/udp

# Verify
sudo ufw status | grep 7890
```

**If running iptables:**

```bash
# Allow port 7890
sudo iptables -A INPUT -p tcp --dport 7890 -j ACCEPT
sudo ip6tables -A INPUT -p tcp --dport 7890 -j ACCEPT

# Save rules (use iptables-persistent or iptables-save)
```

### Phase 10: Configure Multi-Node Cluster (Optional)

**For multi-node deployments:**

```bash
# On secondary node, repeat phases 1-8 with different config:
# Set NODE_ROLE: "secondary" instead of  "primary"
# Set NODE_ID: different hostname

# After both nodes running, register peer
# Edit node-registry.json on both nodes to include each other:
{
  "members": [
    {
      "id": "primary-server",
      "role": "primary",
      "address": "192.168.1.10",
      "status": "online"
    },
    {
      "id": "secondary-server",
      "role": "secondary",
      "address": "192.168.1.11",
      "status": "online"
    }
  ]
}

# Restart both services
sudo systemctl restart uhome-server  # On both
```

### Phase 11: Backup and Recovery Setup

**Create backup script:**

```bash
# Create backup directory
mkdir -p ~/.workspace/backups

# Create backup script
cat > /opt/uhome-server/backup-workspace.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="$HOME/.workspace/backups/$(date +%Y%m%d-%H%M%S)"
mkdir -p "$BACKUP_DIR"
cp "$HOME/.workspace/"*.json "$BACKUP_DIR/"
echo "Backup created: $BACKUP_DIR"
EOF

chmod +x /opt/uhome-server/backup-workspace.sh

# Run backup
/opt/uhome-server/backup-workspace.sh

# Create cron job for nightly backups
(crontab -l 2>/dev/null; echo "0 2 * * * /opt/uhome-server/backup-workspace.sh") | crontab -
```

## Troubleshooting

### Service Won't Start

```bash
# Check service logs
sudo journalctl -u uhome-server -n 50

# Check Python virtualenv
source /home/uhome/.udos/venv/uhome-server/bin/activate
python3 -c "import uhome_server; print('Import OK')"

# Check workspace permissions
ls -la ~/.workspace/
# Should be readable/writable by uhome user

# Test manual startup
/home/uhome/.udos/venv/uhome-server/bin/uhome --debug
```

### Port 7890 in Use

```bash
# Find what's using port 7890
sudo lsof -i :7890

# Kill conflicting process
sudo kill -9 <PID>

# Or change port (edit and restart with PORT=7891)
PORT=7891 uhome
```

### Library Not Indexing

```bash
# Check storage is mounted
mount | grep /media/library
# If not mounted: add to /etc/fstab and mount -a

# Check permissions
ls -ld /media/library
# Should be accessible by uhome user

# Trigger manual rescan
curl -X POST http://localhost:7890/api/debug/library-rebuild

# Check logs
journalctl -u uhome-server | grep -i library
```

### Out of Memory

```bash
# Check memory usage
free -h

# Check uHOME process memory
ps aux | grep uhome

# Reduce memory limit or add more RAM
# Edit /etc/systemd/system/uhome-server.service
# Change: MemoryLimit=2G to higher value
```

## Next Steps

1. **Add Media**: Copy media files to `/media/library`, trigger rescan
2. **Connect Clients**: Point Android/iOS apps to your server IP:7890
3. **Set Up Home Assistant**: Create automation rules integrating uHOME
4. **Configure DVR**: If supported, set up recording schedules
5. **Monitor Health**: Periodically check `/api/health` and logs
6. **Backup Registries**: Use backup script to preserve configuration

## Related Documentation

- [Docker Deployment](../docker-compose.yml) — Container-based deployment
- [Operational Runbooks](operations/) — Troubleshooting and recovery
- [Client Integration Guide](clients/INTEGRATION-GUIDE.md) — API usage
- [Architecture / dev entry (v4)](architecture/UHOME-SERVER-DEV-PLAN.md) — System design

## Support

For issues or questions:
- Check logs: `journalctl -u uhome-server`
- Review [Troubleshooting Guide](operations/TROUBLESHOOTING.md)
- File issue on GitHub with logs and configuration
- Contact system administrator or project maintainers
