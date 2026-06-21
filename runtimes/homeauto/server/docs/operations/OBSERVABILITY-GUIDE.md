# uHOME Server Operations: Observability and Monitoring Guide

**Target Audience**: System operators, DevOps engineers, system administrators  
**Updated**: 2026-03-10  
**Scope**: How to observe and monitor uHOME Server health and performance

## Overview

Effective operations require visibility into system health, performance, and degradation. This guide explains:

- What metrics and logs to monitor
- How to interpret health status
- Setting up alerts and dashboards
- Capacity planning and trending
- Debugging operational issues

## Health Status Endpoints

### Primary Health Check

**Endpoint**: `GET /api/health`

```bash
curl http://localhost:7890/api/health | jq .
```

**Response**:
```json
{
  "status": "healthy",
  "timestamp": "2026-03-10T15:30:00Z",
  "version": "1.0.0",
  "uptime_seconds": 3600,
  "nodes_online": 2,
  "nodes_expected": 2,
  "storage_healthy": true,
  "Jellyfin_connected": true
}
```

**Status Values**:
- `"healthy"` — All systems operational, all nodes reachable
- `"degraded"` — One or more component failing, service continues
- `"critical"` — Multiple failures or authority missing, requires attention
- `"starting"` — Service initializing, not yet ready
- `"stopping"` — Service gracefully shutting down

**Interpretation Guide**:

| Status | Meaning | Action |
|--------|---------|--------|
| healthy | No issues | Continue monitoring, no action needed |
| degraded | 1 component down | Review logs, investigate root cause |
| critical | Multiple failures | Escalate, check logs, may need manual intervention |
| starting | Service starting | Wait 10-30 seconds, recheck |
| stopping | Service shutting down | Wait for shutdown to complete, then restart if needed |

### Readiness Check

**Endpoint**: `GET /api/ready`

Used by load balancers and orchestrators to determine if service can accept traffic:

```bash
curl -w "\nHTTP Status: %{http_code}\n" http://localhost:7890/api/ready

# Expected: HTTP 200 if ready, 503 if not ready
```

**Response**: 
```json
{
  "ready": true,
  "registries_loaded": true,
  "Jellyfin_sync_complete": true,
  "library_indexed": true
}
```

### Detailed Registries View

**Endpoint**: `GET /api/debug/registries`

Shows current cluster topology, storage configuration, and library status:

```bash
curl http://localhost:7890/api/debug/registries | jq .
```

**Response Structure**:
```json
{
  "node_registry": [
    {
      "id": "primary-server",
      "role": "primary",
      "status": "online",
      "last_heartbeat": "2026-03-10T15:30:15Z",
      "address": "192.168.1.10"
    },
    {
      "id": "secondary-server",
      "role": "secondary",
      "status": "online",
      "last_heartbeat": "2026-03-10T15:29:50Z",
      "address": "192.168.1.11"
    }
  ],
  "storage_registry": [
    {
      "id": "storage-001",
      "path": "/media/library",
      "status": "healthy",
      "capacity_gb": 2000,
      "used_gb": 1200,
      "last_verified": "2026-03-10T15:30:00Z"
    }
  ],
  "library_registry": 4523
}
```

**What to Monitor**:
- `node_registry`: Are all expected nodes present and online?
- `storage_registry`: Are all storage members available and healthy?
- `library_registry`: Is the library index loaded? (count should be > 0)

## Structured Logging

### Log Location

```bash
# Using systemd journal
sudo journalctl -u uhome-server

# Follow logs in real-time
sudo journalctl -u uhome-server -f

# Last 50 lines
sudo journalctl -u uhome-server -n 50

# Since last boot
sudo journalctl -u uhome-server -b

# Date range
sudo journalctl -u uhome-server --since "2026-03-10 10:00:00" --until "2026-03-10 11:00:00"
```

### Log Levels

```bash
# INFO level (normal operation)
journalctl -u uhome-server | grep "INFO"

# WARNING level (something unusual, may need attention)
journalctl -u uhome-server | grep "WARNING"

# ERROR level (something failed, requires investigation)
journalctl -u uhome-server | grep "ERROR"

# DEBUG level (very verbose, for deep troubleshooting)
# Enable via LOG_LEVEL=DEBUG environment variable
```

### Key Log Patterns to Watch For

| Log Pattern | Meaning | Action |
|-------------|---------|--------|
| `"Starting uHOME Server"` | Service startup complete | Normal |
| `"Registries loaded"` | Configuration ready | Normal |
| `"Storage member online: ..."` | Storage attached and working | Normal |
| `"Node.*offline"` | Peer node unreachable | Investigate connectivity |
| `"Registry desync detected"` | Cluster state mismatch | Run registry resync |
| `"Job queue depth"` | Background jobs queued | Normal if < 100 |
| `"Jellyfin sync failed"` | Can't reach Jellyfin | Check Jellyfin service |
| `"Disk space low"` | Storage nearly full | Add storage or delete old content |
| `"CRITICAL"` or `"ErrorException"` | Unexpected error | Escalate, collect full logs |

### Error Analysis

```bash
# Count errors in last 24 hours
journalctl -u uhome-server --since "24 hours ago" | grep -i "ERROR\|CRITICAL" | wc -l
# If > 10: Investigate

# Show all errors with context
journalctl -u uhome-server --since "1 hour ago" | grep -B2 -A2 "ERROR"

# Find specific error type
journalctl -u uhome-server | grep "IndexError\|KeyError\|Timeout\|Connection refused"

# Export logs for analysis
journalctl -u uhome-server -n 1000 > uhome-logs.txt
```

## Key Metrics to Monitor

### Real-Time Metrics

**CPU Usage**:
```bash
# Get uHOME process CPU %
ps aux | grep uhome | grep -v grep | awk '{print $3}'

# Watch CPU over time
watch -n 2 'ps aux | grep [u]home | awk "{print \$3}"'

# Expected: < 30% during normal operation
```

**Memory Usage**:
```bash
# Get uHOME process memory
ps aux | grep uhome | grep -v grep | awk '{printf "%.0f MB\n", $6/1024}'

# Watch memory over time
watch -n 5 'ps aux | grep [u]home | awk "{printf \"%.0f MB\n\", \$6/1024}"'

# Expected: 100-500 MB for typical deployments
```

**Disk I/O**:
```bash
# Monitor disk operations
iostat -x 1 5

# Focus on service storage
iotop -n 1 -o | grep uhome

# Expected: < 10 MB/s avg during normal operation
```

**Network Connections**:
```bash
# Active connections to port 7890
netstat -an | grep :7890 | grep ESTABLISHED | wc -l

# Expected: Match number of connected clients
```

### Library Size and Growth

```bash
# Current library size
du -h /media/library | tail -1

# Growth over time (run monthly)
date >> ~/media-size.log
du -h /media/library | tail -1 >> ~/media-size.log

# Analyze growth rate
awk 'NR%2==1 {date=$0; next} {print date, $1}' ~/media-size.log

# Expected: Growth of 0-50 GB/month depending on recording habits
```

### Job Queue Depth

```bash
# Current queue status
curl http://localhost:7890/api/debug/job-queue-status | jq .

# Monitor queue over time
echo "$(date): $(curl -s http://localhost:7890/api/debug/job-queue | jq '.pending | length')" >> ~/job-queue.log

# Watch for stalled jobs
watch -n 10 'curl -s http://localhost:7890/api/debug/job-queue | jq ".pending | length"'

# Expected: Queue depth should trend toward 0 over time
```

## Alerting Rules

### Critical Alerts

Alert immediately if any of these occur:

```
Status = "critical"
  → Escalate immediately, manual intervention needed

Any Node Status = "offline"
  → If primary: promote secondary or restart primary
  → If secondary: monitor, but service continues

Storage Status = "unavailable" and all storage members down
  → Critical, library completely inaccessible

Journal contains "CRITICAL" or "FATAL"
  → Investigate and restart if needed

Disk Usage on / > 90%
  → Add storage or clean up, risk of crash

Disk Usage on /media > 95%
  → Add storage, DVR recording may fail

Memory Usage > 2GB sustained
  → Memory leak, restart service

Process CPU > 80% sustained > 5 min
  → Performance issue, investigate or restart
```

### Warning Alerts

Alert for investigation if:

```
Status = "degraded" > 30 minutes
  → Investigate root cause and recover

Any Node Status = "offline" > 1 hour
  → Should be recovered or marked permanent

Storage Status = "degraded" (partial availability)
  → File system issue or connection problem

Disk Usage trending rapidly upward
  → May run out of space soon

Job Queue Depth > 100
  → Jobs being created faster than processed

Jellyfin connection lost > 10 minutes
  → Media library sync disabled, cache may stale

Error Rate > 5 errors/hour
  → Investigate if pattern or transient
```

### Info-Level Monitoring

Just log (no alert), but track trends:

```
Service uptime (restart events)
Job queue completion times
Library size and growth
Node heartbeat patterns
Storage usage by member
```

## Setting Up Monitoring

### Manual Monitoring (No External Tools)

**Hourly Check**:
```bash
#!/bin/bash
# Place in cron: 0 * * * * /usr/local/bin/check-uhome.sh

curl -s http://localhost:7890/api/health | jq '
  if .status != "healthy" then
    "ALERT: " + .status
  else
    "OK"
  end
'
```

**Daily Report**:
```bash
#!/bin/bash
# Run at 9 AM each day: 0 9 * * * /usr/local/bin/uhome-daily-report.sh

echo "=== Daily uHOME Report $(date) ===" >> /var/log/uhome-report.log
echo "Status: $(curl -s http://localhost:7890/api/health | jq -r .status)" >> /var/log/uhome-report.log
echo "Nodes: $(curl -s http://localhost:7890/api/debug/registries | jq '.node_registry | length')" >> /var/log/uhome-report.log
echo "Storage: $(curl -s http://localhost:7890/api/debug/registries | jq '.storage_registry | length')" >> /var/log/uhome-report.log
echo "Errors (24h): $(journalctl -u uhome-server --since '24 hours ago' | grep -i error | wc -l)" >> /var/log/uhome-report.log
```

### Integration with External Monitoring (Prometheus, Grafana, etc.)

**Prometheus Scrape Config** (if metrics endpoints available):
```yaml
scrape_configs:
  - job_name: 'uhome-server'
    static_configs:
      - targets: ['localhost:7890']
    metrics_path: '/api/metrics'
    scrape_interval: 30s
```

**Generic HTTP Check** (health endpoint):
```yaml
scrape_configs:
  - job_name: 'uhome-health'
    static_configs:
      - targets: ['localhost:7890']
    metrics_path: '/api/health'
    scrape_interval: 60s
```

### Integration with Alerting (PagerDuty, Slack, etc.)

**Bash Script Template**:
```bash
#!/bin/bash
HEALTH=$(curl -s http://localhost:7890/api/health)
STATUS=$(echo "$HEALTH" | jq -r '.status')

if [ "$STATUS" = "critical" ]; then
  # Send to Slack
  curl -X POST https://hooks.slack.com/services/YOUR/WEBHOOK \
    -H 'Content-Type: application/json' \
    -d "{\"text\":\"uHOME CRITICAL: $HEALTH\"}"
  
  # Send SMS via PagerDuty
  curl -X POST https://api.pagerduty.com/incidents \
    --header "Authorization: Token token=$PD_TOKEN" \
    --header 'Content-Type: application/json' \
    -d "{\"incident\":{\"type\":\"incident\",\"title\":\"uHOME Critical\"}}"
fi
```

## Capacity Planning

### Storage Capacity

**Growth Factors**:
- DVR recordings: 5-10 GB per hour of video (depending on bitrate)
- Manual imports: Variable, depends on user activity
- Jellyfin transcodes: Temporary, caches cleaned periodically

**Planning Formula**:
```
Required Storage (GB) = Current Media (GB) 
                      + DVR Recording Rate (GB/day) × 30 days
                      + Growth Buffer (20%)
```

**Example**:
```
2TB current media
+ 500 GB/month DVR  
+ 400 GB growth buffer
= 2.9 TB recommended storage (plan for 4TB total)
```

### CPU and Memory Capacity

**Typical Resource Usage**:
- **Base Idle**: ~50-100 MB RAM, 0-5% CPU
- **Single Client Browsing**: +20-50 MB RAM, +5% CPU
- **Playback Status**: +10 MB RAM, +2% CPU
- **DVR Recording**: +100 MB RAM, +5-10% CPU
- **Library Rescan**: +200-500 MB RAM, +50-80% CPU (temporary)

**Planning**: 
- Minimum: 1GB RAM (tight), 2-core CPU
- Recommended: 2-4GB RAM, 4-core CPU
- Large deployments: 8GB RAM, 8-core CPU

### Network Bandwidth

**Typical Bandwidth**:
- Library Browse: < 1 Mbps
- Playback Status: < 0.5 Mbps
- Remote Playback (streaming): 5-25 Mbps (depends on bitrate)
- DVR Recording (local): 2-10 Mbps

**Plan**: Ensure 100 Mbps LAN for local, sufficient WAN for remote access

## Troubleshooting with Observability

### Service Is Slow

1. Check health endpoint:
   ```bash
   curl http://localhost:7890/api/health
   ```

2. Check recent errors:
   ```bash
   journalctl -u uhome-server --since "30 minutes ago" | grep -i error
   ```

3. Check resource usage:
   ```bash
   ps aux | grep [u]home
   free -h
   iostat -x 1 3
   ```

4. Check network connections:
   ```bash
   netstat -an | grep 7890 | wc -l
   ```

### Library Not Updating

1. Check Jellyfin connection:
   ```bash
   journalctl -u uhome-server | grep -i jellyfin
   curl http://localhost:8096/System/Info  # if using Jellyfin
   ```

2. Check library rebuild status:
   ```bash
   curl http://localhost:7890/api/debug/registries | jq '.library_registry | length'
   ```

3. Trigger manual rescan:
   ```bash
   curl -X POST http://localhost:7890/api/debug/library-rebuild
   ```

### Node Not Responsive

1. Check node status:
   ```bash
   ping <node-ip>
   curl http://<node-ip>:7890/api/health
   ```

2. Check cluster view:
   ```bash
   curl http://localhost:7890/api/debug/registries | jq '.node_registry[]'
   ```

3. Check node logs:
   ```bash
   ssh uhome@<node-ip> journalctl -u uhome-server -n 50
   ```

## Logs Export for Support

When requesting technical support, provide:

```bash
# Collect all diagnostic data
mkdir -p uhome-diag-$(date +%Y%m%d)
cd uhome-diag-$(date +%Y%m%d)

# Service logs (last 500 lines)
journalctl -u uhome-server -n 500 > service-logs.txt

# Current status
curl http://localhost:7890/api/health | jq . > health-status.json
curl http://localhost:7890/api/debug/registries | jq . > registries.json

# System info
systemctl status uhome-server > service-status.txt
ps aux | grep uhome >> service-status.txt
free -h >> service-status.txt
df -h >> service-status.txt

# Tar for sharing
cd ..
tar -czf uhome-diag-$(date +%Y%m%d).tar.gz uhome-diag-$(date +%Y%m%d)/
# Share .tar.gz with support team
```

## Related Documentation

- [Operational Runbooks](README.md) — Step-by-step recovery procedures
- [Clean Shutdown](CLEAN-SHUTDOWN-RUNBOOK.md) — Graceful service management
- [Graceful Degradation](GRACEFUL-DEGRADATION-RUNBOOK.md) — Understanding partial failures

## Quick Reference Card

Keep this handy for operators:

```
Health Check:              curl http://localhost:7890/api/health
View Logs:                 journalctl -u uhome-server -f
Restart Service:           sudo systemctl restart uhome-server
Rebuild Library:           curl -X POST http://localhost:7890/api/debug/library-rebuild
Resync Registry:           curl -X POST http://localhost:7890/api/debug/resync-registry
Check Storage:             curl http://localhost:7890/api/debug/registries | jq .
List Nodes:                journalctl -u uhome-server | grep "Node"
Memory Usage:              ps aux | grep uhome
Sensor Health:             curl http://localhost:7890/api/ready

If everything fails:       sudo systemctl restart uhome-server && sleep 10 && curl http://localhost:7890/api/health
```
