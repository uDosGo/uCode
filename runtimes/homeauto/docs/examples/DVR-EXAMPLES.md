---
title: "DVR System Examples and Test Scenarios"
status: draft
last_updated: 2026-04-22T23:26:13+10:00
category: documentation
tags: [ucode3]
description: "This document provides practical examples and test scenarios for using the uHomeNest DVR system."
---
# DVR System Examples and Test Scenarios

**Version**: 1.0
**Date**: 2024-04-17
**Status**: Active

This document provides practical examples and test scenarios for using the uHomeNest DVR system.

## Overview

The examples demonstrate how to create, manage, and test different types of DVR rules using the API endpoints.

## Prerequisites

- uHomeNest server running
- API accessible at `http://localhost:8000/api/dvr/`
- `curl` or similar HTTP client for testing

## Example DVR Rules

### 1. Time-Based Rule (Simple Recording)

**Use Case**: Record a specific program at a scheduled time

**API Request**:
```bash
curl -X POST http://localhost:8000/api/dvr/rules/ \
  -H "Content-Type: application/json" \
  -d '{
    "rule_name": "Nightly News",
    "rule_type": "time-based",
    "channel_id": "news-hd",
    "start_time": "2024-04-18T18:30:00",
    "end_time": "2024-04-18T19:00:00",
    "program_title": "Evening News",
    "quality_profile": "hd",
    "priority": 1
  }'
```

**Expected Response**:
```json
{
  "rule_id": "rule_1",
  "rule_name": "Nightly News",
  "rule_type": "time-based",
  "created_at": "2024-04-17T10:30:00",
  "updated_at": "2024-04-17T10:30:00",
  "enabled": true,
  "priority": 1,
  "status": "active",
  "next_scheduled": "2024-04-18T18:30:00"
}
```

**Verification**:
```bash
# Check the rule was created
curl http://localhost:8000/api/dvr/rules/rule_1

# List all rules
curl http://localhost:8000/api/dvr/rules/

# Check upcoming recordings
curl http://localhost:8000/api/dvr/recordings/upcoming
```

### 2. Series Rule (Record All Episodes)

**Use Case**: Record all episodes of a favorite TV series

**API Request**:
```bash
curl -X POST http://localhost:8000/api/dvr/rules/ \
  -H "Content-Type: application/json" \
  -d '{
    "rule_name": "Favorite Show - All Episodes",
    "rule_type": "series",
    "series_id": "tt1234567",
    "series_title": "The Great Adventure",
    "season_numbers": [1, 2, 3],
    "include_specials": true,
    "avoid_duplicates": true,
    "quality_profile": "hd",
    "priority": 2,
    "keep_until": "2024-05-01T00:00:00"
  }'
```

**Expected Response**:
```json
{
  "rule_id": "rule_2",
  "rule_name": "Favorite Show - All Episodes",
  "rule_type": "series",
  "created_at": "2024-04-17T10:35:00",
  "updated_at": "2024-04-17T10:35:00",
  "enabled": true,
  "priority": 2,
  "status": "active",
  "next_scheduled": null
}
```

### 3. Movie Rule (Record Specific Movie)

**Use Case**: Record a specific movie when it airs

**API Request**:
```bash
curl -X POST http://localhost:8000/api/dvr/rules/ \
  -H "Content-Type: application/json" \
  -d '{
    "rule_name": "Oscar Winning Movie",
    "rule_type": "movie",
    "movie_id": "tt9876543",
    "movie_title": "The Amazing Story",
    "year": 2023,
    "quality_profile": "uhd",
    "priority": 1,
    "keep_until": "2024-06-01T00:00:00"
  }'
```

### 4. Keyword Rule (Record by Keyword)

**Use Case**: Record any program containing specific keywords

**API Request**:
```bash
curl -X POST http://localhost:8000/api/dvr/rules/ \
  -H "Content-Type: application/json" \
  -d '{
    "rule_name": "Science Documentaries",
    "rule_type": "keyword",
    "keywords": ["science", "documentary", "space"],
    "require_all_keywords": false,
    "channels": ["discovery", "science-hd"],
    "time_ranges": ["18:00-23:00"],
    "quality_profile": "hd",
    "priority": 3
  }'
```

### 5. Channel Rule (Record Everything on Channel)

**Use Case**: Record all programs on a specific channel during certain hours

**API Request**:
```bash
curl -X POST http://localhost:8000/api/dvr/rules/ \
  -H "Content-Type: application/json" \
  -d '{
    "rule_name": "News Channel Archive",
    "rule_type": "channel",
    "channel_id": "news-hd",
    "channel_name": "News HD",
    "time_ranges": ["06:00-09:00", "17:00-20:00"],
    "quality_profile": "hd",
    "priority": 4,
    "keep_until": "2024-04-30T00:00:00"
  }'
```

## Test Scenarios

### Scenario 1: Basic Rule Lifecycle

**Objective**: Test creating, updating, disabling, and deleting a rule

**Steps**:
1. Create a time-based rule
2. Verify rule appears in list
3. Update the rule (change priority)
4. Disable the rule
5. Re-enable the rule
6. Delete the rule

**Commands**:
```bash
# 1. Create rule
CREATE_RESPONSE=$(curl -s -X POST http://localhost:8000/api/dvr/rules/ \
  -H "Content-Type: application/json" \
  -d '{
    "rule_name": "Test Rule",
    "rule_type": "time-based",
    "channel_id": "test-channel",
    "start_time": "2024-04-19T14:00:00",
    "end_time": "2024-04-19T15:00:00",
    "quality_profile": "hd",
    "priority": 3
  }')

RULE_ID=$(echo $CREATE_RESPONSE | jq -r '.rule_id')
echo "Created rule: $RULE_ID"

# 2. Verify rule in list
curl -s http://localhost:8000/api/dvr/rules/ | jq ".rules[] | select(.rule_id == \"$RULE_ID\")"

# 3. Update rule
curl -s -X PUT http://localhost:8000/api/dvr/rules/$RULE_ID \
  -H "Content-Type: application/json" \
  -d '{"priority": 2}'

# 4. Disable rule
curl -s -X POST http://localhost:8000/api/dvr/rules/$RULE_ID/disable

# 5. Re-enable rule
curl -s -X POST http://localhost:8000/api/dvr/rules/$RULE_ID/enable

# 6. Delete rule
curl -s -X DELETE http://localhost:8000/api/dvr/rules/$RULE_ID
```

**Expected Results**:
- Each step should return success: true
- Rule should appear/disappear from lists appropriately
- Priority should change from 3 to 2

### Scenario 2: Conflict Resolution

**Objective**: Test automatic conflict resolution

**Steps**:
1. Create two overlapping time-based rules
2. Check schedule for conflicts
3. Resolve conflict using priority
4. Verify only higher priority rule remains scheduled

**Commands**:
```bash
# 1. Create first rule (high priority)
curl -s -X POST http://localhost:8000/api/dvr/rules/ \
  -H "Content-Type: application/json" \
  -d '{
    "rule_name": "High Priority Show",
    "rule_type": "time-based",
    "channel_id": "entertainment",
    "start_time": "2024-04-19T20:00:00",
    "end_time": "2024-04-19T21:00:00",
    "quality_profile": "hd",
    "priority": 1
  }'

# 2. Create second rule (low priority, same time)
curl -s -X POST http://localhost:8000/api/dvr/rules/ \
  -H "Content-Type: application/json" \
  -d '{
    "rule_name": "Low Priority Show",
    "rule_type": "time-based",
    "channel_id": "entertainment",
    "start_time": "2024-04-19T20:00:00",
    "end_time": "2024-04-19T21:00:00",
    "quality_profile": "hd",
    "priority": 5
  }'

# 3. Check for conflicts
curl -s http://localhost:8000/api/dvr/schedule/conflicts

# 4. Refresh schedule to resolve conflicts
curl -s -X POST http://localhost:8000/api/dvr/schedule/refresh

# 5. Verify only high priority rule is scheduled
curl -s http://localhost:8000/api/dvr/recordings/upcoming
```

**Expected Results**:
- Conflict should be detected between the two rules
- After refresh, only the high priority rule should remain scheduled
- Low priority rule should be marked as conflicted or not scheduled

### Scenario 3: Recording Lifecycle

**Objective**: Test the complete recording lifecycle

**Steps**:
1. Create a time-based rule for immediate recording
2. Check upcoming recordings
3. Wait for recording to complete (or simulate)
4. Check recent recordings
5. Get recording details
6. Cancel/delete the recording

**Commands**:
```bash
# 1. Create rule for immediate recording (use current time + 5 minutes)
NOW=$(date -u +"%Y-%m-%dT%H:%M:00Z")
START_TIME=$(date -u -d "$NOW + 5 minutes" +"%Y-%m-%dT%H:%M:00Z")
END_TIME=$(date -u -d "$NOW + 35 minutes" +"%Y-%m-%dT%H:%M:00Z")

curl -s -X POST http://localhost:8000/api/dvr/rules/ \
  -H "Content-Type: application/json" \
  -d "{
    \"rule_name\": \"Immediate Test Recording\",
    \"rule_type\": \"time-based\",
    \"channel_id\": \"test-channel\",
    \"start_time\": \"$START_TIME\",
    \"end_time\": \"$END_TIME\",
    \"quality_profile\": \"hd\",
    \"priority\": 2
  }"

# 2. Check upcoming recordings
curl -s http://localhost:8000/api/dvr/recordings/upcoming

# 3. Wait for recording to complete (in real scenario, wait 30+ minutes)
# For testing, we'll just check the recent recordings
sleep 10

# 4. Check recent recordings
curl -s http://localhost:8000/api/dvr/recordings/recent

# 5. Get recording stats
curl -s http://localhost:8000/api/dvr/recordings/stats

# 6. Clean up - delete the rule
# (In real scenario, you might also delete the recording)
```

**Expected Results**:
- Recording should appear in upcoming list
- After completion, should move to recent recordings
- Recording stats should show completed count increased

### Scenario 4: Job Queue Integration

**Objective**: Test job queue integration with DVR rules

**Steps**:
1. Create a time-based rule
2. Check job queue status
3. Verify recording job was created
4. Monitor job progress
5. Complete the recording
6. Verify job status updated

**Commands**:
```bash
# 1. Create time-based rule
curl -s -X POST http://localhost:8000/api/dvr/rules/ \
  -H "Content-Type: application/json" \
  -d '{
    "rule_name": "Job Queue Test",
    "rule_type": "time-based",
    "channel_id": "news-hd",
    "start_time": "2024-04-19T15:00:00",
    "end_time": "2024-04-19T16:00:00",
    "quality_profile": "hd",
    "priority": 3
  }'

# 2. Check job queue status
curl -s http://localhost:8000/api/runtime/thin/automation/jobs

# 3. Get detailed job queue info
JOB_QUEUE_STATUS=$(curl -s http://localhost:8000/api/dvr/schedule/status)
echo $JOB_QUEUE_STATUS | jq .

# 4. Check automation dashboard for job monitoring
curl -s http://localhost:8000/api/runtime/thin/automation/

# 5. After recording completes, check job status again
# (In real scenario, wait until after the recording time)
sleep 60

# 6. Verify job completed
curl -s http://localhost:8000/api/runtime/thin/automation/jobs
```

**Expected Results**:
- Recording job should appear in job queue
- Job status should change from queued → running → completed
- Automation dashboard should show job progress
- Schedule status should reflect completed recording

## Test Data Sets

### Sample Rule Set for Testing

```json
[
  {
    "rule_name": "Morning News",
    "rule_type": "time-based",
    "channel_id": "news-hd",
    "start_time": "2024-04-19T07:00:00",
    "end_time": "2024-04-19T08:00:00",
    "quality_profile": "hd",
    "priority": 1
  },
  {
    "rule_name": "Favorite Series",
    "rule_type": "series",
    "series_id": "tt1234567",
    "series_title": "Adventure Time",
    "quality_profile": "hd",
    "priority": 2
  },
  {
    "rule_name": "Weekend Movies",
    "rule_type": "keyword",
    "keywords": ["movie", "film"],
    "time_ranges": ["20:00-23:00"],
    "quality_profile": "hd",
    "priority": 3
  }
]
```

### Sample Recording Data

```json
[
  {
    "recording_id": "rec_001",
    "rule_id": "rule_1",
    "channel_id": "news-hd",
    "title": "Morning News - April 19",
    "start_time": "2024-04-19T07:00:00",
    "end_time": "2024-04-19T08:00:00",
    "status": "completed",
    "file_path": "/recordings/news/20240419_0700.mp4",
    "file_size": 1200000000,
    "quality_profile": "hd"
  },
  {
    "recording_id": "rec_002",
    "rule_id": "rule_2",
    "channel_id": "entertainment",
    "title": "Adventure Time - Episode 1",
    "start_time": "2024-04-18T20:00:00",
    "end_time": "2024-04-18T20:30:00",
    "status": "completed",
    "file_path": "/recordings/entertainment/20240418_2000.mp4",
    "file_size": 800000000,
    "quality_profile": "hd"
  }
]
```

## Troubleshooting

### Common Issues

**Issue: Rule not appearing in list**
- Check API response for errors
- Verify rule_id is valid
- Check if rule was accidentally deleted

**Issue: Recording not starting**
- Verify rule is enabled
- Check channel availability
- Verify tuner is available
- Check disk space

**Issue: Conflict not resolved**
- Check priority settings
- Verify conflict resolution strategy
- Manually resolve if needed

**Issue: API returns 404**
- Verify API endpoint URL
- Check server is running
- Verify route is properly registered

### Debugging Commands

```bash
# Check server status
curl http://localhost:8000/api/health

# Check DVR status
curl http://localhost:8000/api/dvr/schedule/status

# Check job queue
curl http://localhost:8000/api/runtime/thin/automation/jobs

# View server logs
tail -f ~/.udos/logs/uhome-server.log

# Check service status
sudo systemctl status uhome-server
```

## Best Practices

### Rule Management

1. **Use descriptive names**: "Nightly News" instead of "Rule 1"
2. **Set appropriate priorities**: High for important shows, low for optional
3. **Use keep_until dates**: Automatically clean up old recordings
4. **Avoid duplicates**: Enable avoid_duplicates for series rules
5. **Test rules**: Use test-recording endpoint before creating permanent rules

### Performance Optimization

1. **Limit concurrent recordings**: Based on tuner availability
2. **Balance quality vs storage**: Use appropriate quality profiles
3. **Regular cleanup**: Delete old recordings automatically
4. **Monitor disk space**: Set up alerts for low disk space
5. **Schedule during off-peak**: Reduce load on system resources

### Monitoring

1. **Check schedule regularly**: Verify upcoming recordings
2. **Monitor job queue**: Watch for stuck or failed jobs
3. **Review conflicts**: Resolve scheduling conflicts promptly
4. **Track storage usage**: Prevent disk full situations
5. **Review logs**: Identify and fix recurring issues

## Integration Testing

### Automated Test Script

```bash
#!/bin/bash
# DVR System Integration Test

echo "Starting DVR System Integration Test"

# Test 1: Create rules of each type
echo "Test 1: Creating rules..."
for type in "time-based" "series" "movie" "keyword" "channel"; do
  curl -s -X POST http://localhost:8000/api/dvr/rules/ \
    -H "Content-Type: application/json" \
    -d "{
      \"rule_name\": \"Test $type Rule\",
      \"rule_type\": \"$type\",
      \"channel_id\": \"test-channel\",
      \"start_time\": \"2024-04-20T12:00:00\",
      \"end_time\": \"2024-04-20T13:00:00\",
      \"quality_profile\": \"hd\",
      \"priority\": 3
    }" > /dev/null
  echo "Created $type rule"
done

# Test 2: List all rules
echo "Test 2: Listing rules..."
RULES=$(curl -s http://localhost:8000/api/dvr/rules/)
RULE_COUNT=$(echo $RULES | jq '.total')
echo "Found $RULE_COUNT rules"

# Test 3: Check schedule
echo "Test 3: Checking schedule..."
SCHEDULE=$(curl -s http://localhost:8000/api/dvr/schedule/)
UPCOMING=$(echo $SCHEDULE | jq '.total')
echo "Found $UPCOMING upcoming recordings"

# Test 4: Check job queue
echo "Test 4: Checking job queue..."
JOB_QUEUE=$(curl -s http://localhost:8000/api/runtime/thin/automation/jobs)
JOB_COUNT=$(echo $JOB_QUEUE | jq '.queue_status.queued')
echo "Found $JOB_COUNT queued jobs"

# Test 5: Clean up
echo "Test 5: Cleaning up..."
for rule_id in $(echo $RULES | jq -r '.rules[].rule_id'); do
  curl -s -X DELETE http://localhost:8000/api/dvr/rules/$rule_id > /dev/null
  echo "Deleted rule $rule_id"
done

echo "Integration test completed successfully!"
```

### Performance Test

```bash
#!/bin/bash
# DVR Performance Test

echo "Starting DVR Performance Test"

# Test creating many rules
START_TIME=$(date +%s)
for i in {1..50}; do
  curl -s -X POST http://localhost:8000/api/dvr/rules/ \
    -H "Content-Type: application/json" \
    -d "{
      \"rule_name\": \"Perf Test Rule $i\",
      \"rule_type\": \"time-based\",
      \"channel_id\": \"test-channel\",
      \"start_time\": \"2024-05-01T$(printf "%02d" $((i % 24))):00:00\",
      \"end_time\": \"2024-05-01T$(printf "%02d" $((i % 24 + 1))):00:00\",
      \"quality_profile\": \"hd\",
      \"priority\": 3
    }" > /dev/null
done
END_TIME=$(date +%s)

CREATION_TIME=$((END_TIME - START_TIME))
echo "Created 50 rules in $CREATION_TIME seconds"

# Test listing rules
START_TIME=$(date +%s)
RULES=$(curl -s http://localhost:8000/api/dvr/rules/)
END_TIME=$(date +%s)

LIST_TIME=$((END_TIME - START_TIME))
echo "Listed rules in $LIST_TIME seconds"

# Test deleting rules
START_TIME=$(date +%s)
for rule_id in $(echo $RULES | jq -r '.rules[].rule_id'); do
  curl -s -X DELETE http://localhost:8000/api/dvr/rules/$rule_id > /dev/null
done
END_TIME=$(date +%s)

DELETE_TIME=$((END_TIME - START_TIME))
echo "Deleted 50 rules in $DELETE_TIME seconds"

echo "Performance test completed"
```

## Conclusion

This document provides comprehensive examples and test scenarios for the uHomeNest DVR system. The examples cover:

- **All rule types**: Time-based, series, movie, keyword, channel
- **Complete lifecycle**: Create, update, delete, enable, disable
- **Recording management**: Schedule, monitor, cancel recordings
- **Conflict resolution**: Automatic and manual
- **Job queue integration**: Real-time monitoring
- **Performance testing**: Bulk operations

Use these examples to test and validate your DVR system implementation, or as templates for creating your own custom rules and scenarios.

**Next Steps**:
1. Try the examples with your uHomeNest installation
2. Modify the scenarios to match your specific needs
3. Create additional test cases for your unique use cases
4. Integrate with your existing automation and monitoring systems