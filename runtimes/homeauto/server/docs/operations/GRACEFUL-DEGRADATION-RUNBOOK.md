# Runbook: Graceful Degradation Patterns and Fallback Guidance

**Category**: Operational Guidance  
**Severity**: Informational (explains expected behavior under failure)  
**Frequency**: Reference (consulted when services degrade)  
**Last Updated**: 2026-03-10  
**Last Review**: 2026-03-10

## Overview

Graceful degradation is the expected behavior when uHOME Server encounters
failure conditions. Instead of crashing or becoming completely unavailable,
the system should continue operating with reduced functionality and clear
operator feedback.

This document explains:
- How uHOME degrades with each type of failure
- What clients can and cannot do during degradation
- How to interpret degradation status
- When degradation is acceptable vs when recovery is required
- Fallback paths and workarounds for clients

## Core Principle

**Degrade first, recover later.** The system should:
1. Continue serving all working components (don't crash entire system for one failed node)
2. Report degraded status clearly (via `/api/health` and logs)
3. Allow operator intervention without forced service restart
4. Recover gracefully when components come back online

## Supported Degradation Scenarios

### Scenario 1: Secondary Node Offline

**What fails:**
- Playback handoff through that node
- Media served through that node's storage

**What works:**
- Primary node continues full operation
- Other nodes continue normal operation
- Library browsing still works (served from primary)
- DVR recordings continue (on unaffected nodes)
- Playback of media on other nodes unaffected

**Health Status:**
```json
{
  "status": "degraded",
  "reason": "Secondary node offline",
  "nodes_online": 1,
  "nodes_expected": 2,
  "affected_features": ["playback_on_node_2"],
  "recovery_action": "Restart secondary node or escalate to administrator"
}
```

**Operator Action:**
- Monitor if secondary stays offline > 1 hour → investigate/restart
- If media primarily on secondary → promote secondary to authority or migrate media
- No immediate action required if workload can shift to primary

**Client Experience:**
```
✅ Browse library — works, sees all media
✅ Launch on primary node — works
❌ Launch on secondary node — "That node is unreachable, try primary"
✅ Play media from primary storage — works
❌ Play media from secondary storage — "Source unreachable"
```

### Scenario 2: Primary Node Offline

**What fails:**
- Decentralized authority decisions (who owns new storage? who schedules DVR?)
- Node registration/deregistration
- New storage member discovery
- DVR scheduling

**What works:**
- Secondary node can serve existing content
- Playback continues
- Library browsing uses cached data (may be stale)
- Clients can still query endpoints

**Health Status:**
```json
{
  "status": "degraded",
  "reason": "Primary authority node offline",
  "authority_available": false,
  "nodes_online": 1,
  "nodes_expected": 2,
  "affected_features": ["storage_registration", "dvr_scheduling", "node_authority"],
  "recovery_action": "Restart primary or promote secondary to authority"
}
```

**Operator Action:**
- If expected downtime < 15 minutes → Wait for primary to return
- If expected downtime > 15 minutes → Promote secondary to authority (manual registry edit)
- Critical DVR jobs queued? Consider promoting secondary

**Client Experience:**
```
✅ Browse library — works using cached data (may be stale)
✅ Play existing media — works
✅ Playback on both nodes — works (continues)
❌ Add new storage member — "Authority unavailable, queue for later"
❌ Schedule new DVR job — "Authority unavailable, queue"
```

### Scenario 3: Storage Member Unavailable (Offline Drive, Unmounted, Network Down)

**What fails:**
- Access to that drive's media

**What works:**
- Other storage members and their media unaffected
- Playback of content on available storage works
- Library browsing shows available media only
- DVR recordings can still target available storage

**Health Status:**
```json
{
  "status": "degraded",
  "reason": "Storage member /media/backup offline",
  "storage_members": {
    "healthy": 1,
    "degraded": 1,
    "total": 2
  },
  "affected_storage": [
    {
      "id": "storage-002",
      "path": "/media/backup",
      "status": "offline",
      "estimated_recovery": "manual_required"
    }
  ]
}
```

**Operator Action:**
- Check physical connection (USB, power, network)
- If temporary (loose cable): Reconnect, service auto-detects
- If persistent: Mark as offline in registry, plan replacement
- Service naturally excludes offline storage from catalog

**Client Experience**:
```
✅ Browse library — works, shows only media from online storage
✅ Play content — works if on online storage
❌ Play content — fails if on offline storage ("Cannot locate media")
✅ DVR recordings — continue on online storage
```

### Scenario 4: Jellyfin Unavailable

**What fails:**
- Catalog refresh from Jellyfin
- Playback status from Jellyfin

**What works:**
- Local media catalog (cached from last sync)
- Direct Sonic or uHOME presentation
- DVR scheduling and processing

**Health Status:**
```json
{
  "status": "degraded",
  "reason": "Jellyfin integration offline",
  "jellyfin_status": "unreachable",
  "catalog_source": "cache (2 hours stale)",
  "features_available": ["local_catalog", "dvr", "presentation"],
  "features_unavailable": ["jellyfin_sync", "jellyfin_playback_status"]
}
```

**Operator Action:**
- Check if Jellyfin service is running: `ssh nas systemctl status jellyf…`
- Check network connectivity to Jellyfin: `ping jellyfin-server`
- Restart Jellyfin if hung
- If Jellyfin unavailable > 24 hours, media may become stale

**Client Experience**:
```
✅ Browse library — works, shows cached content
✅ Play local media — works
✅ Launch on presentation mode — works
❌ Sync new Jellyfin content — fails, will retry later
❌ Get Jellyfin playback progress — serves default (0%)
```

### Scenario 5: Service Crashes/Restarts Frequently

**What fails:**
- All API endpoints
- Playback and browsing (temporarily during restart)
- Trust in system reliability

**What works:**
- After restart, system recovers (if underlying issue is transient)
- Peer nodes can serve instead (in multi-node setup)
- Local media still accessible if storage mounted directly

**Health Status** (as seen by monitoring):
```json
{
  "status": "critical",
  "reason": "Service restarting (5 restarts in 10 minutes)",
  "restart_frequency": "High",
  "last_error": "IndexError: list index out of range",
  "stable_for": "3 minutes",
  "recovery_action": "Investigate crash logs, possibly escalate to development"
}
```

**Operator Action**:
- Check logs: `journalctl -u uhome-server -n 100 | grep -i exception`
- Identify the crash: Specific operation? Specific registry?
- Try recovery:
  - Clear corrupted cache: `rm ~/.workspace/library-index.json`
  - Clear job queue: Manual cleanup (Phase 6+ tool)
  - Restart: `sudo systemctl restart uhome-server`
- If crash occurs again: Collect diagnostics and file bug report

**Client Experience**:
```
❌ Browse library — "Connection refused", retry
❌ Play media — times out, connection lost
⏳ After service restarts (30-60 sec) — Retry browsing/playback, works
```

## Degradation State Transitions

```
HEALTHY (all nodes, all storage, Jellyfin OK)
  ↓
  └─→ Storage member offline → Server continues with other storage
  └─→ Secondary node offline → Primary handles all requests
  └─→ Jellyfin unavailable → Use cached catalog
  └─→ Network partition → Each segment operates independently (split-brain)

DEGRADED (one or more issues, but service operational)
  ↓
  └─→ Primary goes offline → Authority lost, secondary may be promoted
  └─→ Crash loop → Critical state, needs investigation

CRITICAL (multiple failures or authority lost)
  ↓
  └─→ Manual recovery required
  └─→ May require registry repair or full restore
```

## Fallback Paths for Clients

### Fallback 1: Primary Node Unreachable

**Client Strategy**:
```
1. Try to query primary node: GET /api/household/browse
   → TIMEOUT after 5 seconds
2. Detect failure, switch to secondary
3. Try secondary node: GET /api/household/browse
   → SUCCESS (cache may be stale)
```

**Implementation**:
```javascript
async function browseLibrary(query) {
  const nodes = ["primary-server:7890", "secondary-server:7890"];
  
  for (const node of nodes) {
    try {
      const response = await fetch(`http://${node}/api/household/browse?q=${query}`, 
        {timeout: 5000});
      return response.json();
    } catch (error) {
      console.log(`Node ${node} failed, trying next...`);
      // Try next node
    }
  }
  
  throw new Error("All servers unreachable");
}
```

### Fallback 2: Intermittent Network Issues

**Client Strategy**:
```
1. Make request
2. If times out or 500 error: retry with exponential backoff
3. After 3 retries: show "temporarily unavailable" UI
4. Retry periodically (every 30 seconds)
```

**Implementation**:
```javascript
async function fetchWithRetry(url, maxRetries = 3) {
  for (let i = 0; i < maxRetries; i++) {
    try {
      const response = await fetch(url, {timeout: 5000});
      if (response.ok) return response.json();
    } catch (error) {
      // Exponential backoff: 100ms, 200ms, 400ms
      await delay(Math.pow(2, i) * 100);
    }
  }
  throw new Error("Request failed after retries");
}
```

### Fallback 3: Stale Catalog During Jellyfin Unavailability

**Client Strategy**:
```
1. Query library via cached catalog
2. Show content (may be outdated)
3. Display notice: "Catalog last updated 2 hours ago"
4. Continue to retry Jellyfin sync in background
5. When Jellyfin recovers, auto-refresh
```

**Implementation**:
```javascript
async function getBrowseCatalog() {
  const cached = localStorage.getItem('catalog');
  const cacheAge = Date.now() - JSON.parse(cached).timestamp;
  
  if (cacheAge > 1_hour) {
    // Try to refresh from server
    try {
      const fresh = await fetch('/api/household/browse');
      localStorage.setItem('catalog', JSON.stringify(fresh));
      return fresh;
    } catch (error) {
      // Fall back to stale cache, show warning
      console.warn("Using stale catalog");
      return cached;
    }
  }
  
  return cached;
}
```

## Monitoring Degradation

### Health Endpoint Interpretation

Check `/api/health`:

```bash
# Every 30 seconds
while true; do
  curl -s http://localhost:7890/api/health | jq '.status'
  sleep 30
done
```

**Status Meanings**:
- `"healthy"` — All systems operational, no action needed
- `"degraded"` — One component failing, service continues, review logs
- `"critical"` — Multiple failures or authority lost, immediate escalation needed
- `"unknown"` — Service not responding, check if running

### Debug Endpoint Interpretation

Check `/api/debug/registries`:

```bash
# Get detailed status
curl http://localhost:7890/api/debug/registries | jq .

# Common issues and what they mean:
# - "node_registry" has 1 member: secondary offline
# - "storage_registry" has 0 members: all storage offline
# - "library_registry" is empty: cache not loaded or corrupted
```

### Log Pattern Recognition

```bash
# Search for degradation indicators
journalctl -u uhome-server | grep -E "degraded|offline|unreachable|timeout"

# Signs of cascade failure (multiple systems affected)
journalctl -u uhome-server | grep -i "error" | wc -l
# If > 10 errors in last hour: system struggling, investigate

# Signs of crash loop
journalctl -u uhome-server | grep "Service started" | wc -l
# If > 5 restarts in 10 minutes: crash loop, needs investigation
```

## Operator Decision Tree

```
Health check shows "degraded"
  │
  ├─→ Is primary a…
  │    │
  │    ├─→ Node (unreachable) → Offline Node Recovery Runbook
  │    ├─→ Storage → Storage Degradation Recovery Runbook
  │    └─→ Jellyfin → Check Jellyfin service, not urgent
  │
  ├─→ How long has it been degraded?
  │    │
  │    ├─→ < 5 minutes → Wait, may auto-recover
  │    ├─→ 5-30 minutes → Investigate root cause
  │    └─→ > 30 minutes → Escalate to recovery runbook
  │
  └─→ Is service still responsive?
       │
       ├─→ YES → Continue monitoring, clients can fail over
       └─→ NO → Likely crash loop, check logs and restart
```

## Expected Degradation Recovery Times

| Scenario | Time to Detect | Time to Recover | Operator Action Needed? |
|----------|---|---|---|
| Secondary node, power cycled | 10 sec | Device boots (60-120 sec) | Monitor |
| Storage member, cable loose | 5 sec | Reconnect + rescan (30 sec) | Non-local: remote restart |
| Jellyfin down, will restart | 30 sec | Jellyfin boots (60 sec) | Wait, or try restart |
| Primary hard reboot | 30 sec | System boots (120+ sec) | Physical reboot or IPMI |
| Network partition | 10 sec | Detect + failover (60 sec) | Network repair |
| Disk full (DVR target) | 60 sec | Cleanup or reroute (30 sec) | Manual: delete old recordings |

## Thresholds for Escalation

**When degradation requires immediate operator action**:

- **Duration** > 1 hour: Investigate and fix or escalate
- **Components affected** ≥ 2: Multiple failures, likely cascading issue
- **Service availability** < 50%: Clients unable to connect, critical
- **Crash rate** > 1 per minute: Likely infinite loop or corruption
- **Error rate** > 50% of requests: Data integrity risk

**When degradation is acceptable** (continue monitoring):

- **Duration** < 5 minutes: Likely transient, give time to recover
- **Single component** down: Fault isolation ok, others work
- **No cascading failures**: Issue is contained
- **Service still responsive**: Clients can work around
- **Peer nodes available**: Alternative access path exists

## Related Runbooks

- [Storage Degradation Recovery](STORAGE-DEGRADATION-RUNBOOK.md)
- [Offline Node Recovery](OFFLINE-NODE-RUNBOOK.md)
- [Registry Corruption Recovery](REGISTRY-CORRUPTION-RUNBOOK.md)
- [Library Cache Rebuild](LIBRARY-CACHE-REBUILD-RUNBOOK.md)
- [Clean Shutdown](CLEAN-SHUTDOWN-RUNBOOK.md)

## Appendix: Simulation and Testing

### Test Degradation Scenarios

```bash
# Simulate secondary node offline
ssh uhome@secondary-node sudo systemctl stop uhome-server

# Monitor primary's view
curl http://primary:7890/api/debug/registries | jq '.node_registry'
# Should show secondary as offline after heartbeat timeout (~30 sec)

# Check health
curl http://primary:7890/api/health

# Test clients can still browse
curl http://primary:7890/api/household/browse | jq '.browse_results | length'

# Restart secondary
ssh uhome@secondary-node sudo systemctl start uhome-server

# Verify recovery
curl http://primary:7890/api/health
# Should return to "healthy"
```

This runbook is primarily references. Keep it alongside other runbooks for
operators to understand expected behavior and make informed decisions during
degraded conditions.
