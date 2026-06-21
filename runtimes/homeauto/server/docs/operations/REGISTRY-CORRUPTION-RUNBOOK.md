# Runbook: Registry Corruption Recovery

**Category**: Operational Recovery  
**Severity**: High (authority/topology broken, cascading failures)  
**Frequency**: Rare (unexpected termination, filesystem corruption)  
**Last Updated**: 2026-03-10  
**Time Estimate**: 5-15 minutes depending on severity

## Overview

This runbook handles scenarios where registry files become corrupted—incomplete
JSON, invalid syntax, or lost data due to unexpected process termination or
filesystem errors. Corrupted registries prevent service startup or cause 
catastrophic failures in node discovery and storage topology.

Handled Scenarios:
- **Truncated JSON**: Registry file cut off mid-write (incomplete JSON object)
- **Invalid Syntax**: Malformed JSON (missing braces, unclosed strings)
- **Data Loss**: Node or storage member records mysteriously missing
- **Multi-Node Desync**: Different nodes have incompatible registry versions
- **Circular Corruption**: One corrupted registry causes cascading updates to peers

## Prerequisites and Assumptions

**Assumptions**:
- Operator has SSH access to nodes with registries
- Operator is comfortable editing JSON manually (or has regex/sed knowledge)
- Backup of registries exists or is recoverably recent
- Git or version history available (if code repo includes workspace backups)

**Not Within This Runbook**:
- Restoring from archived backups (covered in Backup/Restore Runbook)
- Repairing corrupt registry by fetching from peer (Phase 6 feature pending)
- Implementing automatic corruption detection (Phase 6+ feature)

## Problem Statement

Registry corruption occurs when one or more of these files become invalid:
- `~/.workspace/node-registry.json` — Node topology and authority
- `~/.workspace/storage-registry.json` — Storage member locations and status
- `~/.workspace/library-index.json` — Catalog of available media (partial cache)

Corruption causes:
- **Service Won't Start**: JSON parse error on file load
- **Lost Node Authority**: Primary role becomes unrecoverable
- **Lost Storage Members**: uHOME can't see attached volumes
- **Cascading Errors**: Valid nodes push corrupted data to healthy peers
- **Client Outages**: Catalog becomes inaccessible or shows phantom entries

## Detection

### Symptom 1: Service Won't Start

Service fails to start with JSON parsing error.

**Detection Steps**:
```bash
# SSH to affected node
ssh uhome@<node-ip>

# Try to start service
sudo systemctl start uhome-server

# Check immediate error
systemctl status uhome-server
# May show: "Failed to start uhome-server: Main process exited with code 1"

# Check detailed error in logs
journalctl -u uhome-server -n 30
# Expected corruption error pattern:
# json.JSONDecodeError: Expecting value: line 1 column 1 (char 0)
# or: json.JSONDecodeError: Invalid \escape: line X column Y
```

**If error mentions a file path**:
- Note the exact path
- That registry file is corrupted
- Go to Step 2

### Symptom 2: Explicit JSON Validation Error

Check registry files directly:

```bash
# SSH to node
ssh uhome@<node-ip>

# Test parse each registry file
python3 -m json.tool ~/.workspace/node-registry.json > /dev/null
python3 -m json.tool ~/.workspace/storage-registry.json > /dev/null
python3 -m json.tool ~/.workspace/library-index.json > /dev/null

# If any report error like:
# json.decoder.JSONDecodeError: Expecting value: line 4 column 1 (char 45)
# That file is corrupted
```

### Symptom 3: Cascading Corruption Across Cluster

One node corrupts the registry, then pushes it to peers:

```bash
# Check on multiple nodes if registries differ
for ip in 192.168.1.10 192.168.1.11; do
  echo "=== Node $ip ==="
  ssh uhome@$ip md5sum ~/.workspace/node-registry.json
done

# If checksums differ, registries are out of sync
# One is likely corrupted; go to Step 4 (determine which is good)
```

## Recovery Steps

### Step 1: Identify Corrupted File(s)

```bash
# SSH to affected node
ssh uhome@<node-ip>

# Stop service to prevent further writes
sudo systemctl stop uhome-server

# Try to parse each registry file and capture error
for file in node-registry.json storage-registry.json library-index.json; do
  echo "Testing $file..."
  python3 -c "import json; json.load(open('~/.workspace/$file'))" 2>&1 || echo "CORRUPTED: $file"
done
```

**Expected Output**:
```
Testing node-registry.json...
CORRUPTED: node-registry.json
Testing storage-registry.json...
(no output = valid)
Testing library-index.json...
(no output = valid)
```

**If multiple files corrupted**:
- Filesystem or process termination was severe
- May need full restore; go to Backup/Restore Runbook
- If no backup available, proceed with Step 2

### Step 2: Inspect and Attempt Manual Repair (Simple Cases)

For truncated or single-error cases:

```bash
# Backup corrupted file first
cp ~/.workspace/node-registry.json ~/.workspace/node-registry.json.corrupted

# View file to identify corruption
cat ~/.workspace/node-registry.json | tail -50

# Common pattern: file ends abruptly mid-object
# Example: file ends with:
# [
#   { "id": "primary", "role": "primary",
#
# (missing closing } and ])

# Manual fix procedure:
# 1. Open file with editor
vi ~/.workspace/node-registry.json

# 2. Go to end of file (Shift+G in vi)
# 3. Complete missing JSON structure (add } and ])
# 4. Save

# 3. Validate repair
python3 -m json.tool ~/.workspace/node-registry.json > /dev/null
```

**If validation succeeds**:
- Go to Step 4 (restart service)

**If validation still fails**:
- Corruption is too severe for manual repair
- Go to Step 3 (rebuild from known-good state)

### Step 3: Rebuild Registry from Known-Good State

**Option A: Restore from Backup** (recommended)

```bash
# Check if backups directory exists
ls -la ~/.workspace/backups/

# If backups available
cp ~/.workspace/backups/node-registry.json.backup ~/.workspace/node-registry.json

# Validate
python3 -m json.tool ~/.workspace/node-registry.json > /dev/null

# If valid, go to Step 4
```

**Option B: Fetch from Peer Node** (if in multi-node cluster)

```bash
# SSH to another (healthy) node
ssh uhome@<peer-node-ip>

# Copy registries from peer to this node
scp uhome@<peer-node-ip>:~/.workspace/node-registry.json \
    ~/.workspace/node-registry.json.peer
scp uhome@<peer-node-ip>:~/.workspace/storage-registry.json \
    ~/.workspace/storage-registry.json.peer

# Validate peer copies
python3 -m json.tool ~/.workspace/node-registry.json.peer > /dev/null

# If valid, restore them
cp ~/.workspace/node-registry.json.peer ~/.workspace/node-registry.json
cp ~/.workspace/storage-registry.json.peer ~/.workspace/storage-registry.json

# Note: This assumes peer is healthy and not the source of corruption
# If both are corrupted, escalate to full restore
```

**Option C: Rebuild from Empty/Minimal State** (last resort)

```bash
# If no backup and no healthy peer, rebuild minimal registry

# Create minimal valid node-registry.json for THIS node
cat > ~/.workspace/node-registry.json << 'EOF'
{
  "members": [
    {
      "id": "this-node",
      "hostname": "$(hostname)",
      "role": "secondary",
      "status": "online",
      "last_heartbeat": "2026-03-10T00:00:00Z"
    }
  ]
}
EOF

# Create minimal storage-registry.json
cat > ~/.workspace/storage-registry.json << 'EOF'
{
  "members": []
}
EOF

# Validate
python3 -m json.tool ~/.workspace/node-registry.json > /dev/null

# Note: After restart, node will re-discover peers and storage via heartbeats
# This is degraded operation but allows service startup
```

### Step 4: Restart Service and Monitor Recovery

```bash
# Restart service with rebuilt/restored registries
sudo systemctl start uhome-server

# Wait a few seconds, then check status
sleep 3
systemctl status uhome-server

# Watch logs for rebuild/resync activity
journalctl -u uhome-server -f
# Expected output:
# INFO: Loading registries...
# INFO: Node registry loaded (N members)
# INFO: Storage registry loaded (M members)
# INFO: Service startup complete
```

**If service starts successfully**:
- Go to Step 5 (validate cluster state)

**If service crashes on startup**:
- Restored registry may still be invalid
- Check error in logs: `journalctl -u uhome-server -n 50`
- Try Option C (minimal rebuild) if Option A/B failed

### Step 5: Validate Cluster State and Resync Registry

Once service is running:

```bash
# On recovered node
curl http://localhost:7890/api/debug/registries | jq . > current-state.json

# Check if node/storage registries look reasonable
cat current-state.json | jq '.node_registry | length'
cat current-state.json | jq '.storage_registry | length'

# If counts look very low (0 nodes or 0 storage), resync with peers
curl -X POST http://localhost:7890/api/debug/resync-registry

# Watch logs during resync
journalctl -u uhome-server -f | grep -i "resync\|registry\|sync"

# After resync completes, check updated state
curl http://localhost:7890/api/debug/registries | jq . > resync-state.json
```

**Compare before/after**:
```bash
# Check if new nodes/storage were discovered
diff <(cat current-state.json | jq .node_registry | jq -S .) \
     <(cat resync-state.json | jq .node_registry | jq -S .)
# Should see MORE members after resync
```

### Step 6: Handle Cascading Corruption

If other nodes also have corrupted registries:

```bash
# For each other node that had corruption
for node in media-server-2 media-server-3; do
  ssh uhome@$node
  sudo systemctl stop uhome-server
  
  # Use recovered registry from primary
  scp uhome@<primary>:~/.workspace/node-registry.json \
      ~/.workspace/node-registry.json
  scp uhome@<primary>:~/.workspace/storage-registry.json \
      ~/.workspace/storage-registry.json
  
  # Restart
  sudo systemctl start uhome-server
done

# Await all nodes online
sleep 5

# Run cluster-wide resync from primary
ssh uhome@<primary> \
  curl -X POST http://localhost:7890/api/debug/resync-registry

# Monitor completion
journalctl -u uhome-server -f | grep "resync.*complete"
```

## Validation Checklist

After completing recovery steps, verify:

- [ ] `systemctl status uhome-server` shows **running** (not restarting)
- [ ] `journalctl -u uhome-server` shows **no JSON parse errors**
- [ ] `/api/debug/registries` returns valid JSON with expected members
- [ ] `/api/health` shows **healthy** or **degraded** (not critical)
- [ ] Node registry has **all expected nodes** listed
- [ ] Storage registry has **all expected volumes** listed (or noted offline)
- [ ] Clients can browse library without "corrupt data" errors
- [ ] No error spam about registry conflicts or sync failures
- [ ] If in cluster, all nodes have **same** registry checksums (after resync)

**Manual Verification**:
```bash
# Check registry file is valid JSON
python3 -m json.tool ~/.workspace/node-registry.json > /dev/null && echo "VALID"

# Check parsed registries on startup (look for errors)
journalctl -u uhome-server | grep "registry\|error" | head -10
```

## Known Limitations

**Current Limitations**:
- No automatic corruption detection on write
- No cyclic-redundancy (CRC) checks on registry files
- Peer-to-peer registry merkle tree not yet implemented
- Library index corruption can't be repaired (only rebuilds on next scan)

**Workarounds**:
- Always maintain backups (see Backup/Restore Runbook)
- On multi-node clusters, one node's good registry can recover peers
- Library index rebuilds automatically on next library scan if corrupted

## Escalation

**If recovery steps fail**:

1. **All recovery methods return invalid JSON**:
   - All registries and backups are corrupted
   - File system may have broader issues
   - Run filesystem check: `fsck` or equivalent
   - Escalate to hardware support if filesystem is corrupt

2. **Service starts but crashes on first client request**:
   - Registry loaded but has invalid structure (e.g., missing required fields)
   - Check error in logs: `journalctl -u uhome-server -n 50`
   - May need manual editing to add missing fields

3. **Cluster enters split-brain after corruption recovery**:
   - Nodes disagree on registry state
   - Operator must manually select which version is "correct"
   - Shut down disagree nodes until consensus restored:
     ```bash
     ssh uhome@disagreeing-node sudo systemctl stop uhome-server
     ```
   - Then restart once primary authority is established

4. **Library index corrupted and can't be rebuilt**:
   - Delete corrupted library-index.json
   - Service will rebuild automatically on next scan:
     ```bash
     rm ~/.workspace/library-index.json
     sudo systemctl restart uhome-server
     # Wait 30-60 seconds
     # Catalog will be re-indexed
     ```

**Contact Points**:
- For filesystem corruption: Filesystem vendor or Linux support
- For uHOME registry logic bugs: GitHub issues with corrupted registry dump
- For data recovery: Professional data recovery service if disks are failing

## Related Runbooks

- [Storage Degradation Recovery](STORAGE-DEGRADATION-RUNBOOK.md) — missing volumes
- [Offline Node Recovery](OFFLINE-NODE-RUNBOOK.md) — unreachable nodes
- [Backup And Restore](BACKUP-RESTORE-RUNBOOK.md) — restore from backups
- [Clean Shutdown](CLEAN-SHUTDOWN-RUNBOOK.md) — preventative state preservation

## Appendix: Example Scenarios

### Scenario A: Truncated Node Registry (Crash During Write)

**Problem**: Service crashed while writing node-registry.json update. File is now
missing closing brace.

**File Content** (before fix):
```json
{
  "members": [
    {
      "id": "primary",
      "role": "primary",
      "hostname": "server-1"
```

**Recovery**:
1. Detect: `python3 -m json.tool` returns `JSONDecodeError: Expecting value`
2. Repair: Add `}` and `]}` to close structure
3. Validate: `python3 -m json.tool node-registry.json` succeeds
4. Restart: `sudo systemctl start uhome-server`
5. Done: Service restarts normally

**Time**: 2 minutes

### Scenario B: Multi-Node Desync After Peer Corruption

**Problem**: Primary node crashed while updating registries. Secondary node
received corrupted update and has invalid JSON now.

**Recovery**:
1. Detect: Secondary fails to start with JSON error
2. Identify: Only secondary is corrupted; primary is healthy
3. Fetch: Copy healthy registry from primary to secondary
4. Restart: Secondary comes back online
5. Resync: Run `curl -X POST http://primary:7890/api/debug/resync-registry`
6. Done: Cluster agrees on state

**Time**: 5 minutes

### Scenario C: Catastrophic Library Index Corruption

**Problem**: library-index.json is 50% truncated. Clients see phantom entries
or crashes when browsing.

**Recovery**:
1. Detect: Clients report full catalog is broken; no entries show
2. Repair: Delete `rm ~/.workspace/library-index.json`
3. Rescan: Trigger library rebuild via API or restart
4. Wait: Service rescans all available volumes (5-30 minutes depending on size)
5. Verify: `/api/household/browse` returns healthy entries
6. Done: Library operational

**Time**: 30-60 minutes (mostly automatic scanning)

**Note**: If source media is remote (NAS), ensure it's reachable before triggering
rescan or it will fail to re-index.
