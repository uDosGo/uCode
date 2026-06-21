# uHOME Server Operations

**Version**: 1.0  
**Updated**: 2026-03-10  
**Audience**: System operators, administrators, DevOps engineers

This directory contains operational guides, runbooks, and troubleshooting procedures for running and maintaining uHOME Server in production.

## Quick Reference

### For Deployment
- **First Time Setup**: Read [../DEPLOYMENT-GUIDE.md](../DEPLOYMENT-GUIDE.md)
  - 11-phase step-by-step guide for Ubuntu 20.04+
  - 30-45 minutes from zero to operational
  - Includes systemd service setup and validation

- **Container Deployment**: Use [../docker-compose.yml](../docker-compose.yml)
  - Quick-start with Docker Compose
  - Includes optional Home Assistant and Jellyfin
  - 5 minutes to running

### For Validation
- **Post-Install Checks**: Run [../scripts/validate-install.sh](../scripts/validate-install.sh)
  - Automated validation of all critical components
  - Tests system requirements, service status, API endpoints
  - Run after deployment or when troubleshooting

### For Console Launch
- **uHOME Console Launch Path**: Read [UHOME-CONSOLE-LAUNCH-PATH.md](UHOME-CONSOLE-LAUNCH-PATH.md)
  - End-to-end local runtime launch and console surface checks
  - Includes API route probes and CLI status commands

## Operational Runbooks

The following runbooks provide step-by-step recovery procedures for common failure modes. **Read the runbook matching your problem**, follow the numbered steps in order.

### When Storage is Missing or Unavailable

**File**: [STORAGE-DEGRADATION-RUNBOOK.md](STORAGE-DEGRADATION-RUNBOOK.md)
**Read Time**: 5-10 minutes  
**Typical Recovery Time**: 5-20 minutes

Handles:
- USB external drive not responding
- NAS on network unreachable
- Partition corrupted or read-only
- Drive complete failure

**Quick Start**: 
```bash
# Step 1: Check what's mounted
mount | grep /media

# Step 2: Reconnect or remount missing storage
sudo mount /dev/sdX1 /media/library

# Step 3: Trigger library rescan
curl -X POST http://localhost:7890/api/debug/library-rebuild

# Step 4: Verify with health check
curl http://localhost:7890/api/health | jq .
```

### When a Cluster Node Goes Offline

**File**: [OFFLINE-NODE-RUNBOOK.md](OFFLINE-NODE-RUNBOOK.md)
**Read Time**: 10-15 minutes  
**Typical Recovery Time**: 10-30 minutes

Handles:
- Secondary node offline (power loss, network)
- Primary authority node offline (failover needed)
- Network partition (split-brain)
- Complete node failure

**Quick Start**:
```bash
# Step 1: Detect offline node
ping <node-hostname>

# Step 2: For primary offline: Promote secondary
ssh uhome@<secondary>
# Edit ~/.workspace/node-registry.json, change role to "primary"
sudo systemctl restart uhome-server

# Step 3: Resync cluster registries
curl -X POST http://primary:7890/api/debug/resync-registry

# Step 4: Verify all nodes online
curl http://primary:7890/api/debug/registries | jq '.node_registry'
```

### When Registry Files Are Corrupted

**File**: [REGISTRY-CORRUPTION-RUNBOOK.md](REGISTRY-CORRUPTION-RUNBOOK.md)
**Read Time**: 5-10 minutes  
**Typical Recovery Time**: 5-15 minutes

Handles:
- Truncated JSON registry files
- Invalid JSON syntax  
- Corrupted node or storage registry
- Multi-node registry desync

**Quick Start**:
```bash
# Step 1: Validate registries
python3 -m json.tool ~/.workspace/node-registry.json > /dev/null
python3 -m json.tool ~/.workspace/storage-registry.json > /dev/null

# Step 2: Restore from backup or peer
cp ~/.workspace/backups/node-registry.json.backup ~/.workspace/node-registry.json

# Step 3: Restart service
sudo systemctl restart uhome-server

# Step 4: Verify recovery
curl http://localhost:7890/api/health
```

### When Library Cache is Stale or Corrupted

**File**: [LIBRARY-CACHE-REBUILD-RUNBOOK.md](LIBRARY-CACHE-REBUILD-RUNBOOK.md)
**Read Time**: 3-5 minutes  
**Typical Recovery Time**: 2-10 minutes (longer for large libraries)

Handles:
- New media not appearing in browse results
- Deleted media still showing in results
- Library index corrupted or phantom entries
- Need to sync with Jellyfin

**Quick Start**:
```bash
# Step 1: Trigger quick rescan (recommended)
curl -X POST http://localhost:7890/api/debug/library-rebuild

# Step 2: Wait for completion (~30 secs for typical libraries)
sleep 30

# Step 3: Verify results
curl "http://localhost:7890/api/household/browse?q=test&limit=5" | jq .

# Step 4: If issues persist, full invalidation
rm ~/.workspace/library-index.json
sudo systemctl restart uhome-server
```

### When Planning Maintenance or Migration

**File**: [CLEAN-SHUTDOWN-RUNBOOK.md](CLEAN-SHUTDOWN-RUNBOOK.md)
**Read Time**: 5 minutes  
**Typical Recovery Time**: 2-10 minutes

Handles:
- Graceful service termination
- State preservation before migration
- Creating backup snapshots
- Multi-node shutdown coordination

**Quick Start**:
```bash
# Step 1: Notify clients and peers
echo "Server maintenance in 5 minutes"

# Step 2: Drain and checkpoint
curl -X POST http://localhost:7890/api/admin/sync-state

# Step 3: Graceful stop
sudo systemctl stop uhome-server

# Step 4: Perform maintenance (updates, config changes, etc.)
sudo apt update && sudo apt upgrade

# Step 5: Restart
sudo systemctl start uhome-server
```

### Understanding System Degradation

**File**: [GRACEFUL-DEGRADATION-RUNBOOK.md](GRACEFUL-DEGRADATION-RUNBOOK.md)
**Read Time**: 10-15 minutes (reference guide)  
**Use When**: You see "degraded" status but aren't sure what fails

Covers:
- What happens during each failure scenario
- What clients can/cannot do
- Health status interpretation
- Fallback paths for clients
- Operator decision trees

**Quick Reference**:
```bash
# Check health status
curl http://localhost:7890/api/health | jq .

# Status meanings:
# "healthy" = all systems ok
# "degraded" = one component down, service continues
# "critical" = multiple failures, needs immediate action

# If degraded, check what's down:
curl http://localhost:7890/api/debug/registries | jq .

# Monitor logs for cascade effects
journalctl -u uhome-server -f | grep -i "degraded\|offline"
```

## Operator Workflows

### Weekly Monitoring

```bash
# Check service is healthy
curl http://localhost:7890/api/health | jq .

# Check node registry for disconnected peers
curl http://localhost:7890/api/debug/registries | jq '.node_registry[] | {id, status}'

# Check job queue depth (if DVR enabled)
curl http://localhost:7890/api/debug/job-queue | jq '.pending | length'

# Look for any error spam in last 24 hours
journalctl -u uhome-server --since "24 hours ago" | grep -i error | wc -l
# If > 10: investigate
```

### Monthly Maintenance

```bash
# Create registry backup before changes
mkdir -p ~/.workspace/backups/$(date +%Y-%m)
cp ~/.workspace/*.json ~/.workspace/backups/$(date +%Y-%m)/

# Clean old DVR recordings (if applicable)
find /media/dvr-storage -mtime +30 -delete

# Check disk usage growth
du -h /media/library | tail -1

# Run library rescan (auto-cleanup phantom entries)
curl -X POST http://localhost:7890/api/debug/library-rebuild
```

### Pre-Update Checklist

```bash
# 1. Current state snapshot
mkdir -p ~/.workspace/snapshots/pre-update
cp ~/.workspace/*.json ~/.workspace/snapshots/pre-update/

# 2. Job queue status
curl http://localhost:7890/api/debug/job-queue-status | jq .

# 3. No clients actively using
# (manual check - notify users)

# 4. Wait for jobs to drain
sleep 60

# 5. Graceful shutdown
curl -X POST http://localhost:7890/api/admin/sync-state
sudo systemctl stop uhome-server

# 6. Perform update
cd /opt/uhome-server && git pull && pip install -e .

# 7. Restart
sudo systemctl start uhome-server

# 8. Verify
curl http://localhost:7890/api/health
```

## API Reference for Operators

### Health and Status

- `GET /api/health` — Overall system health (healthy/degraded/critical)
- `GET /api/ready` — Readiness check (for load balancers)
- `GET /api/debug/registries` — View node, storage, and library registries
- `GET /api/debug/job-queue` — Check background job queue status
- `GET /api/debug/metrics` — System metrics (if available)

### Diagnostic Operations

- `POST /api/debug/library-rebuild` — Trigger library rescan
- `POST /api/debug/resync-registry` — Resync node registry across cluster
- `POST /api/debug/topology-rebuild` — Rebuild storage topology
- `POST /api/debug/job-queue-resume` — Resume paused jobs

### Admin Operations

- `POST /api/admin/sync-state` — Flush all state to disk
- `POST /api/admin/shutdown-graceful` — Graceful shutdown via API

## Observability

### Structured Logs

View logs in real-time:
```bash
sudo journalctl -u uhome-server -f

# Filter for specific issues
sudo journalctl -u uhome-server | grep -i "error\|critical"
sudo journalctl -u uhome-server | grep -i "node.*offline"
sudo journalctl -u uhome-server | grep -i "storage"
```

### Performance Monitoring

```bash
# Memory usage
ps aux | grep [u]home

# Disk I/O
iostat -x 1 5

# Network connections
netstat -an | grep 7890

# Process CPU/memory over time
watch -n 5 'ps aux | grep uhome | grep -v grep'
```

## Emergency Procedures

### Service Won't Start

```bash
# Check logs for error
sudo journalctl -u uhome-server -n 50

# Try manual startup to see error
source /home/uhome/.udos/venv/uhome-server/bin/activate
uhome --debug

# Common fixes:
# - Disk full: df -h /
# - Corrupted registry: mv ~/.workspace/node-registry.json ~/.workspace/node-registry.json.broken
# - Permission denied: sudo chown -R uhome:uhome /opt/uhome-server
```

### Port Conflict (7890 in use)

```bash
# Find what's using port
sudo lsof -i :7890

# Kill conflicting process
sudo kill -9 <PID>

# Or start on different port
PORT=7891 uhome
```

### Out of Memory

```bash
# Check memory
free -h
ps aux | sort -k4 -rn | head -5

# Increase memory limit
sudo -e /etc/systemd/system/uhome-server.service
# Change: MemoryLimit=2G to higher value
sudo systemctl daemon-reload
sudo systemctl restart uhome-server
```

### Disk Full

```bash
# Check usage
df -h /

# Find large files/dirs
du -h --max-depth=1 / | sort -rh

# Clean old DVR recordings
find /media/dvr-storage -mtime +30 -delete

# Or, move media to external drive
```

## Support Resources

- **Deployment**: [../DEPLOYMENT-GUIDE.md](../DEPLOYMENT-GUIDE.md)
- **Client Integration**: [../clients/INTEGRATION-GUIDE.md](../clients/INTEGRATION-GUIDE.md)
- **Architecture**: [../architecture/UHOME-SERVER-DEV-PLAN.md](../architecture/UHOME-SERVER-DEV-PLAN.md)
- **Issue Tracker**: GitHub Issues (with logs from `journalctl`)

## Checklist: When Everything is Broken

1. Is the service running? `systemctl status uhome-server`
2. Is port 7890 responding? `netstat -tulpn | grep 7890`
3. Check recent logs: `journalctl -u uhome-server -n 100`
4. Check storage mounts: `mount | grep /media`
5. Check workspace exists: `ls ~/.workspace/`
6. Try restart: `sudo systemctl restart uhome-server`
7. Try full state reset (destructive!): Delete `~/.workspace/*.json` and restart
8. File GitHub issue with logs from `journalctl -u uhome-server | head -200`

## Questions?

For operational guidance, consult the appropriate runbook above. For code issues or feature requests, file an issue on GitHub with:
- Output of `systemctl status uhome-server`
- Recent logs: `sudo journalctl -u uhome-server -n 100`
- Output of `curl http://localhost:7890/api/debug/registries | jq .`
- What you were trying to do when the failure occurred
