# Runbook: Offline Node Recovery

**Category**: Operational Recovery  
**Severity**: Medium-High (secondary node offline, failover needed)  
**Frequency**: Occasional (power loss, network issue, crash)  
**Last Updated**: 2026-03-10  
**Time Estimate**: 10-30 minutes depending on failure type

## Overview

This runbook handles scenarios where a uHOME Server node goes offline—either
the primary authority node or a secondary/satellite node. Recovery depends on
which node is affected and whether failover to a secondary is needed.

Handled Scenarios:
- **Secondary Node Offline**: Reduces available compute but library remains accessible
- **Primary Authority Offline**: Requires manual failover to secondary node  
- **Network Partition**: Node unreachable but may still be running
- **Complete Power Loss**: All nodes offline; recovery involves restart sequence

## Prerequisites and Assumptions

**Assumptions**:
- Multi-node LAN topology with primary + secondary nodes
- Operator has SSH access to all known nodes
- Primary authority node is documented (e.g., `primary-server`, IP: 192.168.1.10)
- Secondary nodes are listed in node registry
- systemd is used for service management on all nodes

**Not Within This Runbook**:
- Distributed consensus or automatic leader election (Phase 7+)
- Network infrastructure repair (contact network admin)
- Data replication or cache synchronization (covered in node bootstrap docs)

## Problem Statement

Node failure occurs when a uHOME Server becomes unreachable or crashes. This
can cause:

- **Reduced Availability**: If secondary, library browsing still works but playback
  handoff may fail
- **Lost Authority**: If primary is offline, other nodes cannot make decentralized
  decisions (storage member registration, DVR scheduling)
- **Stale Node Registry**: Other nodes retain cached view of offline node
- **DVR Job Failure**: If primary is offline and offline node held the authority

The server should **continue operating with known secondaries** and allow operator
to manually promote a secondary or restart the primary, then re-sync node registry.

## Detection

### Symptom 1: Node Unreachable

Clients cannot connect to expected node or get timeouts.

**Detection Steps**:
```bash
# From any node with network access
ping primary-node.local
nslookup primary-node.local

# Try SSH connection
ssh uhome@primary-node.local
# if timeout, node is offline

# Check current node's view of registry
curl http://localhost:7890/api/debug/registries | jq .node_registry
```

**Expected Healthy Output**:
```json
{
  "node_registry": {
    "members": [
      {
        "role": "primary",
        "hostname": "primary-server",
        "address": "192.168.1.10",
        "status": "online",
        "last_heartbeat": "2026-03-10T15:45:00Z"
      },
      {
        "role": "secondary",
        "hostname": "media-server-2",
        "address": "192.168.1.11",
        "status": "online",
        "last_heartbeat": "2026-03-10T15:44:55Z"
      }
    ]
  }
}
```

**Degraded Output** (primary offline):
```json
{
  "node_registry": {
    "members": [
      {
        "role": "primary",
        "hostname": "primary-server",
        "address": "192.168.1.10",
        "status": "offline",
        "last_heartbeat": "2026-03-10T14:30:00Z"
      },
      {
        "role": "secondary",
        "hostname": "media-server-2",
        "address": "192.168.1.11",
        "status": "online",
        "last_heartbeat": "2026-03-10T15:44:55Z"
      }
    ]
  }
}
```

### Symptom 2: Health Endpoint Reports Offline Node

```bash
# From any running node
curl http://localhost:7890/api/health | jq .

# Expected degraded response:
# {
#   "status": "degraded",
#   "reason": "Primary node offline for 75 minutes",
#   "nodes_online": 1,
#   "nodes_expected": 2
# }
```

### Symptom 3: DVR or Library Operations Fail

```bash
# Check logs on remaining node
journalctl -u uhome-server -n 100 | grep -i "node\|authority\|offline"

# Expected error pattern:
# ERROR: Cannot register storage member (primary authority offline)
# ERROR: Cannot schedule DVR job (primary authority offline)
```

## Recovery Steps

### Step 1: Determine Failure Scope

**Is the node responding on network?**

```bash
# From any machine on LAN
ping <node-ip>
nslookup <node-hostname>.local

# Also try SSH
ssh -o ConnectTimeout=5 uhome@<node-ip>
```

**If reachable**: 
- Node is online but service may be crashed; go to Step 3

**If unreachable**:
- Network problem or node powered off; go to Step 2

### Step 2: Restore Network Connectivity or Power

**Is the node powered on?**

```bash
# Check power indicator on node hardware
# If powered off:
# - Press power button
# - Wait 30-60 seconds for boot
# - Try SSH again: ssh uhome@<node-ip>
```

**If powered on but unreachable**:

```bash
# Check physical network cable is connected
# Check switch port has link lights (green/amber)
# Restart node networking:
#   (on the node directly or via IPMI/serial console if available)
ssh uhome@<node-ip>
sudo systemctl restart networking      # or 'netplan apply' on Ubuntu
# Wait 10 seconds, verify connectivity
```

**If still unreachable**:
- Network infrastructure issue; contact network admin
- Proceed with known-good nodes; go to Step 4

### Step 3: Check Service Status on Node

Once node is network-reachable via SSH:

```bash
# SSH to offline node
ssh uhome@<node-ip>

# Check if service is running
systemctl status uhome-server

# If running, check for recent errors
journalctl -u uhome-server -n 50
```

**If service is running and healthy**:
- Node is actually online; update registry if stale
- Go to Step 5

**If service crashed**:

```bash
# Restart it
sudo systemctl restart uhome-server

# Wait 10 seconds and verify
systemctl status uhome-server

# Check logs for startup errors
journalctl -u uhome-server -n 20
```

**If restart succeeds**: 
- Go to Step 5 (registry resync)

**If service won't start**:
- Check disk space: `df -h`
- Check storage mounts: `df /media/library`
- Check logs for fatal errors: `journalctl -u uhome-server -n 100`
- If issues found, escalate to Step 6

### Step 4: Evaluate Failover Decision

**Which node is offline?**

**If secondary node (not authority)**:
- Library browsing and playback continue on primary
- No failover needed; just wait for secondary to recover
- Document the offline incident and proceed to Step 5
- Timeline: Can delay recovery a few hours if needed

**If primary authority node**:
- Decentralized decisions cannot proceed
- Must manually promote a secondary to authority role OR restart primary
- Decision point:
  - **Option A**: Restart primary (if likely to recover quickly)
  - **Option B**: Promote secondary to authority (if primary failure is prolonged)

**For Option A (Restart Primary)**:

```bash
# Check if node is physically accessible
# If remote, you may need IPMI, KVM-over-IP, or ask someone to restart
# Force restart via hard reboot:
ssh uhome@<primary-ip>
sudo /sbin/shutdown -r now   # or use IPMI remote power cycle

# Wait 2-5 minutes for reboot
# Verify it came back up
ssh uhome@<primary-ip> systemctl is-active uhome-server

# Proceed to Step 5
```

**For Option B (Promote Secondary)**:

```bash
# This requires manual registry update on secondary node
# SSH to any running secondary node
ssh uhome@<secondary-ip>

# Edit node registry to promote this node to primary
vi ~/.workspace/node-registry.json

# Find this node's entry, change role from "secondary" to "primary"
# Also change primary entry to "offline"

# Example:
# BEFORE:
# {
#   "role": "primary",
#   "hostname": "primary-server",
#   "status": "offline"
# },
# {
#   "role": "secondary",
#   "hostname": "media-server-2",
#   "status": "online"
# }

# AFTER:
# {
#   "role": "primary",
#   "hostname": "primary-server",
#   "status": "offline"
# },
# {
#   "role": "primary",
#   "hostname": "media-server-2",
#   "status": "online"
# }

# Restart service to apply
sudo systemctl restart uhome-server

# Watch logs
journalctl -u uhome-server -f
# Should see: "Promoted to primary authority role"

# Verify authority is established
curl http://localhost:7890/api/health | jq .authority_role
# Expected: "primary"

# Proceed to Step 5
```

### Step 5: Resynchronize Node Registry Across Cluster

After primary recovery or promotion, all nodes must agree on latest registry:

```bash
# On any running node (preferably now-primary)
curl -X POST http://localhost:7890/api/debug/resync-registry

# Watch logs
journalctl -u uhome-server -f | grep -i "registry\|sync"

# Expected output:
# Resyncing node registry...
# Node 'primary-server' (192.168.1.10) confirmed online
# Node 'media-server-2' (192.168.1.11) confirmed online
# Registry resync complete: 2 nodes, 3 storage members
```

**Verify all nodes have updated view**:

```bash
# From each running node
for ip in 192.168.1.10 192.168.1.11; do
  echo "=== Node $ip ==="
  curl -s http://$ip:7890/api/debug/registries | jq .node_registry.members[].status
done
```

**Expected Output**:
```
=== Node 192.168.1.10 (primary) ===
"online"
"online"

=== Node 192.168.1.11 (secondary) ===
"online"
"online"
```

### Step 6: Clear Stale Caches and Verify

After registry is synced, clear any stale caches:

```bash
# On primary node
ssh uhome@<primary-ip>

# Rebuild node view of storage topology
curl -X POST http://localhost:7890/api/debug/topology-rebuild

# Restart any background jobs that were waiting for authority
curl -X POST http://localhost:7890/api/debug/job-queue-resume

# Watch logs
journalctl -u uhome-server -f
# Should see: "Topology rebuilt", "Job queue resumed"
```

### Step 7: Validate Recovered Cluster

Test all main client APIs from a working client:

```bash
# From any client device or test machine
# Browse household library
curl "http://primary-ip:7890/api/household/browse?q=test"

# Check launcher status
curl "http://primary-ip:7890/api/launcher/status"

# Check playback capabilities
curl "http://primary-ip:7890/api/playback/status"

# All should return valid responses (may be empty if no content)
```

**Expected Response** (all successful):
```json
{
  "status": "ok",
  "items": [...],
  "nodes_serving": ["primary-server", "media-server-2"]
}
```

## Validation Checklist

After completing recovery steps, verify:

- [ ] `systemctl status uhome-server` shows **running** on primary
- [ ] `curl http://primary:7890/api/health` shows **healthy** (no degraded warnings about nodes)
- [ ] Node registry shows all expected nodes as **online**
- [ ] Primary node authority role is **confirmed** via health endpoint
- [ ] Clients can browse library without timeout
- [ ] No error spam in logs about offline nodes or authority conflicts
- [ ] DVR job queue is resumed and can accept new recordings
- [ ] Any interrupted DVR jobs have been requeued or marked failed

## Known Limitations

**Current Limitations**:
- No automatic node failure detection or failover
- Registry resync is manual; no background gossip protocol yet
- Stale caches not automatically purged (may see phantom entries briefly)
- Network partitions (split-brain) not handled—operator must choose which node is "correct"

**Workarounds**:
- Monitor node health periodically (ops tools coming in Phase 6)
- Keep primary in stable location (avoid frequent reboots)
- Document which nodes are authority-candidates

## Escalation

**If recovery steps fail**:

1. **Node never responds to SSH**:
   - Hardware failure or network completely down
   - Physical inspection or network diagnostic needed
   - Can continue with remaining nodes if not last one

2. **Service won't restart** (even after reboot):
   - Check disk space: `df -h`
   - Check corrupted files: `journalctl -u uhome-server -n 50 | grep -i "error"`
   - If registry corrupt, go to [Registry Corruption Runbook](REGISTRY-CORRUPTION-RUNBOOK.md)

3. **Registry resync hangs or times out**:
   - Possible network connectivity issue between nodes
   - Try pinging peers: `ping <peer-ip>`
   - Check firewall rules allow port 7890

4. **Promoted secondary crashes immediately**:
   - May not have enough resources to be primary
   - Revert to original primary once recovered
   - Or adjust configuration to reduce secondary load

**Contact Points**:
- For network issues: Network infrastructure admin
- For hardware issues: Server vendor support
- For uHOME bugs: GitHub issues with diagnostic logs

## Related Runbooks

- [Storage Degradation Recovery](STORAGE-DEGRADATION-RUNBOOK.md) — when storage unavailable
- [Registry Corruption Recovery](REGISTRY-CORRUPTION-RUNBOOK.md) — when registry files corrupt
- [Clean Shutdown](CLEAN-SHUTDOWN-RUNBOOK.md) — graceful multi-node shutdown

## Appendix: Example Scenarios

### Scenario A: Secondary Node Power Loss (Brief)

**Problem**: Media server in basement loses power for 10 minutes, comes back up.

**Steps**:
1. Detect: Ping timeout to secondary, others notice it offline
2. Failover: None needed—primary remains authority
3. Recovery: Secondary reboots and rejoins
4. Resync: Run `curl -X POST http://primary:7890/api/debug/resync-registry`
5. Verify: Node registry shows both online
6. Done: No authority change, just cluster rejoined

**Time**: 15 minutes (mostly automatic after reboot)

### Scenario B: Primary Authority Loss (Extended)

**Problem**: Primary server is moved to new location, offline for 2 hours.

**Steps**:
1. Detect: Operators notice primary.local unreachable for > 5 min
2. Decision: Monitor waits, decides to promote secondary after 15 min
3. Promotion: Secondary node registry updated, role → primary
4. Restart: `systemctl restart uhome-server` on secondary
5. Authority: Secondary now makes DVR scheduling decisions
6. Recovery: When original primary comes back online, it rejoins as secondary via registry resync
7. Done: Original primary can be re-promoted manually later if desired

**Time**: 20 minutes (mostly waiting for decision)

### Scenario C: Network Partition

**Problem**: LAN switch fails; primary (192.168.1.10) and secondary (192.168.1.11)
can't reach each other, but both think they're okay.

**Steps**:
1. Detect: Clients from one segment can't reach other segment nodes
2. Decision: Operator (or monitoring) must decide which segment to trust
3. Fix: Restart switch, or manually disconnect one node from network
4. Resync: Once fixed, run registry resync on remaining nodes
5. Recovery: Disconnected node rejoins when network restored

**Time**: 10-30 minutes (depends on detection/decision speed)

**Note**: This is split-brain scenario; current system requires operator judgment.
Phase 7 consensus algorithm will automate this.
