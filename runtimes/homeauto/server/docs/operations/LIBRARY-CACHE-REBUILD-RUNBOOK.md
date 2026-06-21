# Runbook: Library Cache Invalidation and Rebuild

**Category**: Maintenance  
**Severity**: Low (temporary loss of catalog availability during rebuild)  
**Frequency**: Occasional (storage changes, corrupted cache, corruption recovery)  
**Last Updated**: 2026-03-10  
**Time Estimate**: 2-10 minutes depending on library size

## Overview

Library cache contains the indexed catalog of all media available across storage
members. This runbook covers scenarios where the cache becomes outdated, 
corrupted, or needs rebuilding to reflect new media or resolve inconsistencies.

Handled Scenarios:
- **New Media Added**: External drive with new content mounted, not yet indexed
- **Media Moved/Deleted**: Files removed but index still shows phantom entries
- **Index Corrupted**: Library index file (`library-index.json`) is invalid or incomplete
- **Jellyfin Out of Sync**: Jellyfin's view differs from uHOME's cached view
- **Forced Rescan**: Operator wants manual re-index (e.g., after large batch import)

## Prerequisites and Assumptions

**Assumptions**:
- All storage members are currently mounted and accessible
- Jellyfin is running and responsive (if using Jellyfin backend)
- Operator has access to the node's REST API
- Service will continue running and accepting requests during rebuild

**Not Within This Runbook**:
- Repairing corrupted library-index.json file (use Registry Corruption Runbook)
- Adding new storage members (use Storage Management runbook when available)

## Problem Statement

Stale or corrupted library cache causes:
- **Phantom Entries**: Clients see media that no longer exists (deleted files)
- **Missing Entries**: New media not visible to clients (recent imports)
- **Slow Browsing**: Corrupted index causes timeouts or wrong results
- **Jellyfin Mismatch**: uHOME shows different library than Jellyfin
- **Playback Errors**: User tries to play missing entry, gets 404

Rebuilding is fast enough to do without service restart.

## Detection

### Symptom 1: New Media Not Visible

Recent additions to storage not showing up in `/api/household/browse` or
`/api/launcher/status`.

**Detection**:
```bash
# Check if media file exists on storage
ls -la /media/library/ | grep "2026-03-10"  # Recent files

# Try browsing API (no results expected if cache stale)
curl "http://localhost:7890/api/household/browse?q=new-show" | jq .browse_results | wc -l
# If 0 results but file exists, cache is stale
```

### Symptom 2: Phantom Entries

Deleted media still appears in browse results.

**Detection**:
```bash
# Check if old file still exists
ls -la /media/library/old-show.mkv
# ls: cannot access '/media/library/old-show.mkv': No such file or directory

# But it appears in browse
curl "http://localhost:7890/api/household/browse?q=old-show" | jq .browse_results
# Expected phantom entry should not be in results after rebuild
```

### Symptom 3: Jellyfin Mismatch

uHOME library count differs from Jellyfin library count.

**Detection**:
```bash
# Get Jellyfin library info
curl -s http://localhost:8096/Libraries | jq '.[] | .ItemCount' | awk '{s+=$1} END {print "Jellyfin total:", s}'

# Get uHOME library info
curl -s http://localhost:7890/api/debug/registries | jq '.library_registry | length'
# If counts differ significantly, rebuild may help
```

## Recovery Steps

### Step 1: Decide Rebuild vs Invalidate

**What type of rebuild do you need?**

- **Quick Rescan**: Catalog entries remain, timestamps updated (10-30 seconds for large libraries)
  - Use when: New metadata needed but structure unchanged
  - Command: `POST /api/debug/library-rebuild`

- **Full Invalidation**: Cache cleared completely, requires full re-index (60-300 seconds)
  - Use when: Cache corrupted, Jellyfin sync needed, major structural changes
  - Command: `DELETE /api/debug/library-cache` (if implemented)
  - Fallback: Manual delete `~/.workspace/library-index.json` + restart

### Step 2: Trigger Quick Rescan (Recommended)

```bash
# SSH to server (or use REST from client with auth)
ssh uhome@<server-ip>

# Trigger rescan via API
curl -X POST http://localhost:7890/api/debug/library-rebuild

# Watch logs for progress
journalctl -u uhome-server -f | grep -i "library\|scan\|catalog"

# Expected output:
# INFO: Beginning library rescan...
# INFO: Scanning /media/library (status=healthy)
# INFO: Found 4,523 items
# INFO: Catalog indexed in 18.5 seconds
# INFO: Library rescan complete
```

**For large libraries (>50k items)**:
- Rescan may take 60-300 seconds
- Service remains available but catalog queries may timeout during rebuild
- Wait for completion before resuming heavy browsing

### Step 3: Verify Rescan Results

```bash
# Check updated catalog size
curl http://localhost:7890/api/debug/registries | jq '.library_registry | length'

# Compare to expected size
# Should match: approx number of media files on storage

# Verify no errors in logs
journalctl -u uhome-server | grep -i "error\|warn" | grep -i "library\|catalog"
# Should be empty or only informational

# Test browse results
curl "http://localhost:7890/api/household/browse?q=test&limit=5" | jq .
# Should return current media, not phantoms
```

### Step 4: Full Invalidation (If Quick Rescan Insufficient)

**Only if Quick Rescan didn't resolve issues:**

```bash
# Option A: Delete cache file and restart
ssh uhome@<server-ip>

# Stop service
sudo systemctl stop uhome-server

# Remove corrupted cache
rm ~/.workspace/library-index.json

# Restart service (will auto-rebuild)
sudo systemctl start uhome-server

# Wait 60+ seconds for rebuild
sleep 60

# Verify service is running
systemctl status uhome-server

# Check logs for completion
journalctl -u uhome-server -n 100 | grep -i "library.*complete"
```

**Option B: Sync with Jellyfin (If available)**

```bash
# If using Jellyfin backend, force full sync
curl -X POST http://localhost:7890/api/debug/jellyfin-resync

# This replaces library cache with current Jellyfin library
# Watch logs
journalctl -u uhome-server -f | grep -i "jellyfin"
```

### Step 5: Validate Cache is Current

```bash
# Random sampling: pick a recent file you know exists
# Check it's found in catalog
curl "http://localhost:7890/api/household/browse?q=recent-show" | jq '.browse_results[] | .title'

# Check a deleted file is NOT found
curl "http://localhost:7890/api/household/browse?q=deleted-old-show" | jq '.browse_results | length'
# Should be 0 if properly removed

# Check total catalog size matches filesystem
FILE_COUNT=$(find /media/library -type f -name "*.mkv" -o -name "*.mp4" | wc -l)
CACHE_COUNT=$(curl -s http://localhost:7890/api/debug/registries | jq '.library_registry | length')
echo "Files: $FILE_COUNT, Cache: $CACHE_COUNT"
# Should be approximately equal (within 1-2 of each other is normal)
```

## Validation Checklist

After completing rebuild steps, verify:

- [ ] `/api/debug/registries` returns **valid JSON** with library entries
- [ ] `systemctl status uhome-server` shows **running** (not restarting)
- [ ] `/api/household/browse` returns **current media** (no phantoms) 
- [ ] `/api/household/browse` finds **recently added content**
- [ ] Logs show **no errors** during rebuild (completion message present)
- [ ] Catalog size is **reasonable** compared to storage contents
- [ ] Clients can **successfully browse** without timeouts
- [ ] **Playback works** for entries in updated catalog

## Known Limitations

**Current Limitations**:
- Library cache rebuild always rebuilds entire index (no incremental updates)
- No background invalidation of phantom entries (requires manual rebuild)
- Jellyfin sync is manual (no automatic periodic sync)
- Large libraries (>100k items) may timeout during rebuild

**Workarounds**:
- Keep storage clean (periodically delete old/unwanted media)
- Run builds during off-peak hours (not during client browsing)
- Split very large libraries across multiple storage members if timeouts occur

## Escalation

**If rebuild fails or doesn't resolve issues**:

1. **Library rebuild times out**:
   - Very large library (>100k items) taking too long
   - Workaround: Split library across multiple storage members
   - Try invalidation during low-traffic window

2. **Catalog size doesn't match files on disk**:
   - Some files may be in non-indexed directories
   - Library scanner has directory filters (e.g., ignores `.*` hidden dirs)
   - Check which directories are configured for scanning

3. **Jellyfin resync fails**:
   - Jellyfin may be unreachable or misconfigured
   - Check Jellyfin status: `curl http://localhost:8096/System/Info`
   - Verify authentication if Jellyfin has passwords

4. **Phantom entries persist after rebuild**:
   - May indicate a bug in cache invalidation
   - Report to developers with library-index.json dump
   - Workaround: Full invalidation (delete + restart)

**Contact Points**:
- For large library performance: uHOME GitHub (may need optimization)
- For Jellyfin sync issues: Check Jellyfin server logs and configuration
- For persistent phantom entries: GitHub issue with reproduction steps

## Related Runbooks

- [Registry Corruption Recovery](REGISTRY-CORRUPTION-RUNBOOK.md) — if library-index.json corrupted
- [Clean Shutdown](CLEAN-SHUTDOWN-RUNBOOK.md) — graceful termination with cache preservation
- [Storage Degradation Recovery](STORAGE-DEGRADATION-RUNBOOK.md) — if storage unavailable

## Appendix: Example Scenarios

### Scenario A: New Media Recently Added

**Problem**: Added 50 new movies to `/media/library` but `/api/household/browse` 
doesn't show them.

**Steps**:
1. Detect: `curl http://localhost:7890/api/household/browse?q=new-movie` returns 0 results
2. Fix: `curl -X POST http://localhost:7890/api/debug/library-rebuild`
3. Wait: 15-30 seconds for rebuild
4. Verify: `curl http://localhost:7890/api/household/browse?q=new-movie` returns results
5. Done: New media visible

**Time**: 2-3 minutes

### Scenario B: Old Cache After Jellyfin Import

**Problem**: Jellyfin imported large batch of media (500+ items) but uHOME shows old data.

**Steps**:
1. Detect: `curl http://localhost:8096/Libraries` shows new items, but uHOME browse doesn't
2. Fix: `curl -X POST http://localhost:7890/api/debug/jellyfin-resync`
3. Wait: 60+ seconds for full sync
4. Verify: Counts match between Jellyfin and uHOME
5. Done: Full sync complete

**Time**: 5-10 minutes

### Scenario C: Corrupted Cache After Crash

**Problem**: Service crashed unexpectedly. Library-index.json is truncated.

**Steps**:
1. Detect: Service won't start or catalog is empty
2. Fix: `rm ~/.workspace/library-index.json && systemctl restart uhome-server`
3. Wait: 90+ seconds for full rebuild
4. Verify: `curl http://localhost:7890/api/debug/registries | jq '.library_registry | length'`
5. Done: Cache rebuilt from scratch

**Time**: 2-5 minutes (mostly waiting for rebuild)
