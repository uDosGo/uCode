# Runbook: Clean Shutdown and State Preservation

**Category**: Maintenance  
**Severity**: Low (planned service termination, state preservation)  
**Frequency**: Occasional (maintenance windows, hardware refresh, migrations)  
**Last Updated**: 2026-03-10  
**Time Estimate**: 2-10 minutes depending on job queue state

## Overview

Clean shutdown ensures uHOME Server terminates gracefully with all state
preserved: in-flight jobs completed or checkpointed, registries synced,
and files properly closed. This prevents data loss or corruption when 
restarting or migrating to new hardware.

Handled Scenarios:
- **Maintenance Window**: Planned downtime (updates, configuration changes)
- **Hardware Migration**: Moving to new server, need state snapshot
- **Graceful Transition**: Passing authority from one node to another
- **Cluster Coordination**: Multi-node shutdown sequence
- **Container/VM Restart**: Kubernetes pod restart or systemd service reload

## Prerequisites and Assumptions

**Assumptions**:
- Operator has SSH access to affected node(s)
- Service is currently running
- No critical in-flight DVR recordings or playback sessions
- Backup of registries will be created if requested
- Operator understands difference between "graceful shutdown" vs forced kill

**Not Within This Runbook**:
- Emergency shutdown (power loss, critical error) — use hard kill/reboot
- Emergency recovery after unclean shutdown (use Registry Corruption Runbook)
- Backup and restore procedures (use Backup/Restore Runbook)

## Problem Statement

Unclean shutdown causes:
- **Incomplete Transactions**: Job queue in inconsistent state
- **Registry Sync Issues**: Node registry not flushed to disk
- **Phantom Jobs**: Services restart but don't know where old jobs left off
- **Lost DVR State**: In-flight recordings corrupted or partially written
- **Multi-Node Confusion**: Peer nodes unaware of clean shutdown, retry operations

Clean shutdown prevents these by:
- Draining job queue (completing or checkpointing work)
- Syncing registries to disk
- Allowing peer nodes to gracefully handle departure
- Preserving audit trail via clean shutdown logs

## Detection

When shutdown is needed:

**Planned Shutdown**:
```bash
# Announced maintenance window
# Example: "Server maintenance 2026-03-11 23:00-23:15 UTC"
# Proceed to Recovery Steps → Step 1
```

**Current State Check** (before initiating):
```bash
# SSH to server
ssh uhome@<server-ip>

# Check if jobs are running
curl http://localhost:7890/api/debug/job-queue-status | jq .

# Check which clients are connected
curl http://localhost:7890/api/debug/active-clients | jq . || echo "(not available)"

# Check if DVR recordings are in progress
curl http://localhost:7890/api/debug/dvr-status | jq '.active_recordings'

# If any active work, decide to wait or force shutdown
# Graceful path: Let jobs complete (3-10 minutes typical)
# Forced path: Checkpoint and stop immediately
```

## Recovery Steps

### Step 1: Notify Clients and Peers

Inform any stakeholders:

```bash
# If using notification system (Phase 6+ feature, may not exist yet)
curl -X POST http://localhost:7890/api/admin/broadcast-message \
  -d '{"message": "Server maintenance in 5 minutes, prepare to disconnect"}'

# For multi-node clusters, notify peers
for peer in 192.168.1.11 192.168.1.12; do
  ssh uhome@$peer \
    curl -X POST http://192.168.1.10:7890/api/admin/node-leaving
done

# Manual notification (if automation not available):
# 1. Slack: "Shutting down primary server for maintenance in 5 min"
# 2. SSH to secondary nodes: "Primary going down, stand by for authority transfer"
```

### Step 2: Allow In-Flight Work to Complete

Wait for current jobs to finish gracefully:

```bash
# SSH to server
ssh uhome@<server-ip>

# Monitor job queue
curl http://localhost:7890/api/debug/job-queue-status | jq '.in_progress'
# Wait for count to reach 0

# Check DVR recordings
curl http://localhost:7890/api/debug/dvr-status | jq '.active_recordings | length'
# Wait for count to reach 0

# Monitor with script (wait up to 5 minutes)
for i in {1..30}; do
  JOBS=$(curl -s http://localhost:7890/api/debug/job-queue-status | jq '.in_progress')
  if [ "$JOBS" -eq 0 ]; then
    echo "All jobs completed"
    break
  fi
  echo "Waiting for $JOBS jobs... ($i/30)"
  sleep 10
done
```

**If jobs don't complete in reasonable time** (>5 minutes):
- Review what's holding them: `journalctl -u uhome-server -n 50 | grep -i job`
- Either continue waiting or proceed to Step 3 (checkpoint and shutdown)

### Step 3: Checkpoint and Flush State

Ensure all registries and state are written to disk:

```bash
# SSH to server
ssh uhome@<server-ip>

# Trigger state flush
curl -X POST http://localhost:7890/api/admin/sync-state

# Wait for completion
sleep 2

# Verify registries are current
ls -la ~/.workspace/*.json | awk '{print $6, $7, $8, $9}'
# Check modification times are recent (within last minute)

# Verify no pending writes
journalctl -u uhome-server -n 20 | grep -i "sync\|write\|flush"
```

### Step 4: Graceful Service Termination

Two methods depending on urgency:

**Method A: Systemd Graceful Termination** (Recommended)

```bash
# SSH to server
ssh uhome@<server-ip>

# Send SIGTERM (allows service 30 seconds to clean up)
sudo systemctl stop uhome-server

# This will:
# 1. Send SIGTERM to Python process
# 2. Wait up to 30 seconds for graceful shutdown
# 3. Force SIGKILL if not stopped by then

# Verify it stopped
systemctl status uhome-server
# Should show: inactive (dead)

# Check logs for graceful shutdown message
journalctl -u uhome-server -n 20 | grep -i "shutdown\|terminated"
# Expected: "INFO: Received SIGTERM, shutting down gracefully..."
```

**Method B: REST API Graceful Shutdown** (If available)

```bash
# SSH to server
ssh uhome@<server-ip>

# Trigger API shutdown
curl -X POST http://localhost:7890/api/admin/shutdown-graceful

# Monitor logs
journalctl -u uhome-server -f | tail -20

# Service should shutdown within 10-30 seconds
# After timeout, verify:
systemctl status uhome-server
```

### Step 5: Create State Snapshot (Optional but Recommended)

Backup registries before subsequent restart or reboot:

```bash
# SSH to server
ssh uhome@<server-ip>

# Create snapshot directory
mkdir -p ~/.workspace/snapshots/$(date +%Y%m%d-%H%M%S)
SNAP_DIR="$_"

# Copy registries and state
cp ~/.workspace/node-registry.json $SNAP_DIR/
cp ~/.workspace/storage-registry.json $SNAP_DIR/
cp ~/.workspace/library-index.json $SNAP_DIR/
# Other state files as needed

# Create manifest
cat > $SNAP_DIR/MANIFEST.txt << EOF
Snapshot created: $(date)
Service stopped: yes
Job queue drained: yes
All registries synced: yes
Ready for: migration, backup, or restart
EOF

# Verify snapshot created
ls -la $SNAP_DIR/
```

### Step 6: Perform Maintenance Or Migration

Now the service is safely stopped and state is preserved:

```bash
# Example: System update
sudo apt update && sudo apt upgrade

# Example: Migrate data to new drive
sudo rsync -av /media/old-drive/ /media/new-drive/

# Example: Move to new hardware
# (backup snapshots, physical migration, then restore)

# Example: Configuration change
vi ~/.workspace/settings.json
# Edit as needed

# Service will restart fresh with your changes
```

### Step 7: Restart Service

```bash
# SSH to server
ssh uhome@<server-ip>

# Restart service
sudo systemctl start uhome-server

# Wait 5-10 seconds for startup
sleep 5

# Verify it came up healthy
systemctl status uhome-server
# Should show: active (running)

# Check for startup errors
journalctl -u uhome-server -n 30 | grep -i "error"
# Should be empty or only warnings

# If errors, check detailed logs
journalctl -u uhome-server -n 100 | tail -50
```

### Step 8: Restore Cluster State (Multi-Node Only)

For multi-node deployments, restore peer registry awareness:

```bash
# On restarted primary node
curl -X POST http://localhost:7890/api/debug/resync-registry

# Watch logs
journalctl -u uhome-server -f | grep -i "resync"

# Run on peers as well if they were affected
for peer in 192.168.1.11 192.168.1.12; do
  ssh uhome@$peer \
    curl -X POST http://localhost:7890/api/debug/resync-registry
done
```

### Step 9: Validate Post-Shutdown Consistency

Verify system is fully operational:

```bash
# Test API endpoints
curl http://localhost:7890/api/household/browse | jq '.browse_results | length'
curl http://localhost:7890/api/launcher/status | jq '.available_titles | length'
curl http://localhost:7890/api/playback/status | jq '.now_playing'

# Check registries loaded correctly
curl http://localhost:7890/api/debug/registries | jq '.node_registry | length'

# Verify clients can connect
# (from a client device, try browsing/playing media)

# Monitor for any errors
journalctl -u uhome-server -n 50 | grep -i "error\|critical"
# Should be empty or only expected warnings
```

## Validation Checklist

After shutdown and restart, verify:

- [ ] Service is **running**: `systemctl status uhome-server` shows **active**
- [ ] Registries are **valid**: `python3 -m json.tool ~/.workspace/*-registry.json` succeeds
- [ ] No **unhandled exceptions** in logs: `journalctl | grep -i exception | wc -l`
- [ ] Job queue is **empty**: `curl http://localhost:7890/api/debug/job-queue-status`
- [ ] Clients can **browse** library without errors
- [ ] Library size **matches** expected count: `curl http://localhost:7890/api/debug/registries`
- [ ] Node registry shows **all cluster nodes**: `curl http://localhost:7890/api/debug/registries`
- [ ] No **error spam** in logs (check 50 recent lines)**
- [ ] If multi-node: peers are **reachable** and synchronized

## Known Limitations

**Current Limitations**:
- No automatic job checkpointing (jobs either complete or are lost)
- API graceful shutdown endpoint may not exist yet
- No automated multi-node coordination (manual notification required)
- No broadcast message system for client disconnect warnings

**Workarounds**:
- Stop long-running jobs manually before shutdown
- Monitor job queue during shutdown to ensure completion
- For clusters, manually coordinate with peers via SSH

## Escalation

**If shutdown is not clean**:

1. **Service won't terminate** after 30 seconds:
   - Check for blocked I/O or network operations
   - View logs: `journalctl -u uhome-server -n 30`
   - Force kill if needed: `sudo killall -9 uhome-server` (risky, use only as last resort)

2. **Registries corrupted after restart**:
   - Unclean shutdown may have partially written files
   - Use Registry Corruption Runbook to repair
   - Restore snapshot from backup if available

3. **Job queue in inconsistent state**:
   - Some jobs marked in-progress but not running
   - Check: `curl http://localhost:7890/api/debug/job-queue-status`
   - May need manual cleanup or database repair (Phase 6+ tool)

4. **Peer nodes don't reconnect after multi-node cluster restart**:
   - Manually trigger registry resync: `curl -X POST http://primary:7890/api/debug/resync-registry`
   - Check network connectivity between nodes

**Contact Points**:
- For job queue issues: GitHub issue with queue state dump
- For registry corruption: Registry Corruption Runbook or data recovery service
- For network issues: Network admin or infrastructure team

## Related Runbooks

- [Registry Corruption Recovery](REGISTRY-CORRUPTION-RUNBOOK.md) — if shutdown leaves corrupted state
- [Offline Node Recovery](OFFLINE-NODE-RUNBOOK.md) — recovering from unclean shutdown
- [Backup And Restore](BACKUP-RESTORE-RUNBOOK.md) — restore from snapshots

## Appendix: Example Scenarios

### Scenario A: Quick Maintenance Window

**Problem**: Need to update OS packages (5 minute window).

**Steps**:
1. Notify: "Maintenance in 2 minutes"
2. Wait: Job queue empties (usually instant if no DVR in progress)
3. Checkpoint: `curl -X POST http://localhost:7890/api/admin/sync-state`
4. Stop: `sudo systemctl stop uhome-server`
5. Update: `sudo apt update && sudo apt upgrade -y`
6. Restart: `sudo systemctl start uhome-server`
7. Verify: Clients reconnect and browse normally
8. Done: Maintenance complete

**Time**: 10-15 minutes

### Scenario B: State Snapshot Before Backup

**Problem**: Want to backup registry state before making changes.

**Steps**:
1. Wait: Let current jobs complete (`curl http://localhost:7890/api/debug/job-queue-status`)
2. Flush: `curl -X POST http://localhost:7890/api/admin/sync-state`
3. Snapshot: `mkdir -p ~/.workspace/snapshots/pre-change && cp ~/.workspace/*.json snapshots/pre-change/`
4. Document: `echo "Pre-change snapshot" > snapshots/pre-change/NOTES.txt`
5. Proceed: Make changes (config, storage, etc.)
6. Restart: Service picks up changes
7. Recovery: If needed, restore from snapshot

**Time**: 2-5 minutes

### Scenario C: Hardware Migration

**Problem**: Moving service to new server, need zero data loss.

**Steps**:
1. Notify: Cluster of planned downtime
2. Wait: Jobs complete + registry synced
3. Shutdown: Stop all nodes gracefully
4. Snapshot: Full backup of state and media
5. Migrate: Copy media and configs to new hardware
6. Restore: Restore registry snapshots
7. Boot: Start service on new hardware
8. Verify: Full system test
9. Deprecate: Old hardware offline

**Time**: 30 minutes - 2 hours (mostly data transfer)
