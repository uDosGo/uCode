# Runbook: Storage Degradation Recovery

**Category**: Operational Recovery  
**Severity**: Medium (service continues with reduced availability)  
**Frequency**: Occasional (failed drives, unmounted volumes)  
**Last Updated**: 2026-03-10  
**Time Estimate**: 5-20 minutes depending on failure type

## Overview

This runbook handles scenarios where storage volumes become unavailable—either
missing from the LAN, unmounted from the local host, or failed entirely. 
uHOME Server should continue running with reduced library availability, not 
crash or hang.

Handled Scenarios:
- **Missing Volume**: External drive or NAS unreachable (network/power loss)
- **Unmounted Volume**: Drive attached but not mounted at expected path
- **Corrupted Partition**: Non-readable filesystem on an otherwise healthy drive
- **Failed Drive**: Physical failure or data loss

## Prerequisites and Assumptions

**Assumptions**:
- Operator has SSH access to the primary uHOME Server host
- Operator has basic Linux knowledge (checking mount points, restart services)
- systemd is used for service management (standard on Ubuntu 20.04+)
- uHOME Server config specifies which storage paths should be available

**Not Within This Runbook**:
- Physical drive replacement (defer to hardware maintenance docs)
- RAID recovery or advanced data restoration
- NAS network troubleshooting (contact NAS vendor or network admin)

## Problem Statement

Storage degradation occurs when one or more library volumes become unavailable. 
This can cause:

- **Partial Library Loss**: Catalog entries mapping to missing volumes become inaccessible
- **Jellyfin Sync Failures**: If Jellyfin's media path is affected
- **Slow Catalog Queries**: If service still tries to access missing paths
- **Background Job Failures**: DVR recordings targeting missing volumes fail

The server should **degrade gracefully**: continue serving other library entries,
report degraded status, and allow operator recovery without server restart.

## Detection

### Symptom 1: Catalog Entries Missing

Clients browse `/api/household/browse` or `/api/launcher/status` and see
fewer entries than expected.

**Detection Steps**:
```bash
# SSH to server
ssh uhome@server-host

# Check if service is running
systemctl status uhome-server

# Check recent logs for mount errors  
journalctl -u uhome-server -n 100 | grep -i "mount\|missing\|storage"

# Verify expected storage paths are mounted
mount | grep storage
df -h
df -h /media/library/  # replace with actual mount path
```

**Expected Output** (healthy):
```
Filesystem      Size  Used Avail Use% Mounted on
/dev/sdag1      2.0T  1.2T  800G  60% /media/library
/dev/sdbh1      4.0T  2.5T  1.5T  62% /media/dvr-storage
```

**Degraded Output**:
```
/media/library   GONE (unmounted)
/media/dvr-storage  mounted but inaccessible
```

### Symptom 2: Storage Health Endpoint Degraded

Check the health/debug endpoints:

```bash
# Get storage registry status
curl http://localhost:7890/api/debug/registries | jq .storage_registry

# Get full health check
curl http://localhost:7890/api/health | jq .storage
```

**Expected Degraded Response**:
```json
{
  "storage_registry": {
    "members": [
      {
        "id": "storage-001",
        "path": "/media/library",
        "status": "degraded",
        "error": "Device not mounted",
        "last_seen": "2026-03-10T15:22:00Z"
      }
    ]
  }
}
```

### Symptom 3: Jellyfin Integration Broken

If Jellyfin media path is affected:

```bash
# Check if Jellyfin is reachable
curl http://localhost:8096/System/Info

# Common error: "Jellyfin-managed library path is missing"
journalctl -u uhome-server -n 50 | grep -i jellyfin
```

## Recovery Steps

### Step 1: Determine Failure Type

**Is the volume physically attached?**

```bash
# List all disks
lsblk
# or for USB/external drives
lsusb
# or for NAS/network shares
mount -t nfs  # shows NFS mounts
```

**If NOT attached**: 
- Physically reconnect USB drive, power on NAS, reconnect network
- Wait 10 seconds for device discovery
- Go to Step 2

**If attached but not mounted**:
- Go to Step 2

**If mounted but inaccessible**:
- Go to Step 3

### Step 2: Re-Mount Missing Volume

Common missing mount points: `/media/library`, `/media/storage`, `/mnt/nas`

```bash
# Find the device
sudo fdisk -l | grep -A5 "missing-device"
# or look for it in dmesg
sudo dmesg | tail -50

# For USB/SATA drives, check if detected
ls -la /dev/sd*
ls -la /dev/nvme*

# Try to mount it
sudo mkdir -p /media/library  # if directory doesn't exist
sudo mount /dev/sdX1 /media/library

# Verify it mounted
df -h /media/library
```

**If mount succeeds**: Go to Step 4

**If mount fails with "Device is read-only"**:
```bash
# Try read-only mount as temporary measure
sudo mount -o ro /dev/sdX1 /media/library
# Wait for uHOME to detect and re-index
# Then go to Step 4
```

**If mount fails with "Invalid filesystem"**:
- Drive may be corrupted; go to Step 3

### Step 3: Verify Drive Health and Attempt Repair

**Check filesystem for errors** (DANGEROUS—stops I/O to drive):

```bash
# **WARNING**: Do NOT run while drive is mounted!

# First, unmount if necessary
sudo umount /media/library

# Run filesystem check (choose based on filesystem type)
# For ext4:
sudo fsck.ext4 -v /dev/sdX1
# For btrfs:
sudo btrfs check /dev/sdX1
# For XFS:
sudo xfs_repair -v /dev/sdX1

# This may take 10-30 minutes
# Accept repairs when prompted (type 'y')
```

**If repair succeeds**:
- Remount the drive: `sudo mount /dev/sdX1 /media/library`
- Go to Step 4

**If repair fails**:
- Drive is likely failed; mark it as offline and proceed with degraded operation
- Update storage registry to mark this volume as unavailable:
  ```bash
  # Edit storage registry manually (if operator is comfortable)
  vi /home/uhome/.workspace/storage-registry.json
  # Find the failed volume
  # Set "status": "offline" or remove from active members
  ```
- Go to Step 4

### Step 4: Clear Stale Catalog Entries

After re-mounting or accepting degra data, clear the library cache so uHOME
re-scans available volumes:

```bash
# SSH to server
ssh uhome@server-host

# Option A: Via REST API (preferred)
curl -X POST http://localhost:7890/api/debug/library-rebuild

# Option B: Restart service to trigger automatic re-scan
sudo systemctl restart uhome-server

# Wait 30-60 seconds for service to come back up
systemctl status uhome-server
```

**Monitor re-scan progress**:
```bash
# Watch logs in real-time
journalctl -u uhome-server -f

# Or check updated catalog count
curl http://localhost:7890/api/debug/registries | jq '.library_registry | length'
```

Expected log output:
```
INFO: Beginning library rescan
INFO: Scanning /media/library (status=healthy)
INFO: Skipping /media/old-drive (status=offline)
INFO: Catalog indexed: 4,523 items (was 5,100)
INFO: Library rescan complete
```

### Step 5: Validate Restored Service

**Check that clients can browse updated library**:

```bash
# Test household browse endpoint
curl "http://localhost:7890/api/household/browse?q=test&limit=5" | jq .

# Check launcher status (should not list entries from missing drive)
curl http://localhost:7890/api/launcher/status | jq .available_titles

# Verify no crash loops in logs
journalctl -u uhome-server -n 20 | grep -i "error\|exception"
```

**Expected Response**:
```json
{
  "browse_results": [
    {
      "id": "item-123",
      "title": "Test Show",
      "storage_member": "storage-001"
    }
  ]
}
```

**If 0 results after re-scan**:
- This is expected if entire volume is offline
- Verify other drives are still accessible
- Go to Step 6

### Step 6: Update Monitoring and Documentation

**If drive is permanently failed**:

Create a note in the workshop so future operators know:

```bash
# Edit or create a degradation log
echo "2026-03-10: /media/library (sdag1) failed due to drive power loss. Replaced with new 2TB WD drive. Re-scan complete." >> ~/.workspace/DEGRADATION_LOG.txt
```

**If drive is recovered**:

Update storage registry if needed:

```bash
uhome storage-status  # if command exists
# or check Registry manually
cat ~/.workspace/storage-registry.json | jq '.members[] | {id, status}'
```

## Validation Checklist

After completing recovery steps, verify:

- [ ] `systemctl status uhome-server` shows **running** (not restarting)
- [ ] `journalctl` shows **no error spam** about missing volumes
- [ ] `/api/health` reports **all healthy** or **degraded** (not critical)
- [ ] `/api/household/browse` returns results without timing out
- [ ] `/api/launcher/status` lists available titles (fewer than before if drive still offline)
- [ ] Clients can play media from remaining volumes without errors
- [ ] No background DVR jobs are hung or error-looping
- [ ] Operator documentation updated with what happened

## Known Limitations

**Current Limitations**:
- Server does **not** automatically fail over to secondary node (manual promotion)
- Server does **not** reroute active DVR recordings to alternate volume
- Service may log warnings continuously if drive remains offline; see Step 6
- Large library re-scans (>100k items) may take several minutes

**Workarounds**:
- To silence warnings: mark volume as permanently offline in registry
- To speed re-scan: stop all playback first
- To preserve recordings: immediately assign free volume in DVR config

## Escalation

**If recovery steps fail**:

1. **Storage never re-mounts**:
   - Drive is failed or controllers not detected
   - Physical inspection may be needed; contact hardware vendor

2. **Filesystem repair fails**:
   - Drive data is corrupted beyond recovery
   - Consider drive a loss; mark offline permanently

3. **uHOME service crashes after recovery**:
   - Possible bug in rescan logic
   - Report issue to developers with:
     - ServiceLog (20 lines before/after crash)
     - Storage registry dump (`storage-registry.json`)
     - Catalog size before/after failure

4. **Clients time out during re-scan**:
   - Expected for very large libraries (>50k items)
   - Wait for re-scan to complete before troubleshooting further
   - Check with: `journalctl -u uhome-server | tail -50`

**Contact Points**:
- For hardware issues: Server vendor or drive manufacturer support
- For uHOME bugs: GitHub issues with diagnostic logs

## Related Runbooks

- [Offline Node Recovery](OFFLINE-NODE-RUNBOOK.md) — when entire server is down
- [Registry Corruption Recovery](REGISTRY-CORRUPTION-RUNBOOK.md) — when registry files corrupt
- [Clean Shutdown](CLEAN-SHUTDOWN-RUNBOOK.md) — graceful service termination

## Appendix: Example Scenarios

### Scenario A: USB External Drive Unplugged

**Problem**: User accidentally unplugged `/media/backup` USB drive.

**Steps**:
1. Detect: `df -h` shows no `/media/backup`
2. Fix: User re-plugs USB drive
3. Remount: `sudo mount /dev/sdg1 /media/backup`
4. Rescan: `curl -X POST http://localhost:7890/api/debug/library-rebuild`
5. Verify: `curl http://localhost:7890/api/household/browse`
6. Done: Library restored

**Time**: 2 minutes

### Scenario B: NAS Network Timeout

**Problem**: NAS on LAN lost network connectivity. `/media/nas-library` shows
inaccessible (mounted but no response).

**Steps**:
1. Detect: `df -h` shows mounted but `ls /media/nas-library` times out
2. Fix: IT admin restarts NAS or network switch
3. Remount: `sudo umount /media/nas-library && sudo mount /media/nas-library`
4. Rescan: Restart service with `sudo systemctl restart uhome-server`
5. Verify: Clients see re-indexed library
6. Done: Full recovery expected

**Time**: 5-10 minutes

### Scenario C: Drive Failure Detected

**Problem**: `/media/removable` consistently fails to mount; device shows as
read-only.

**Steps**:
1. Detect: Mount fails with permission error
2. Fix: Try fsck: `sudo fsck.ext4 /dev/sde1` (unmount first)
3. Accept repairs; if repairs fail, drive is failed
4. Mark offline: Edit storage-registry.json and set status→offline
5. Rescan: Restart service
6. Verify: Library shows degraded, other drives accessible
7. Document: Add to DEGRADATION_LOG.txt

**Time**: 10-20 minutes (depending on drive size)

**Note**: This drive will need physical replacement; order is not urgent if
other drives cover needed library content.
