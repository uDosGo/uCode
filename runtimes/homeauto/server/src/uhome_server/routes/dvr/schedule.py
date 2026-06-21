"""
DVR Schedule API endpoints.

Provides schedule management and conflict resolution.
"""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timedelta

from uhome_server.config import get_logger

_log = get_logger("uhome.dvr.schedule")

router = APIRouter(prefix="/schedule", tags=["dvr-schedule"])


class ScheduleItem(BaseModel):
    rule_id: str
    rule_name: str
    start_time: datetime
    end_time: datetime
    channel: str
    status: str
    priority: int


class ScheduleResponse(BaseModel):
    items: List[ScheduleItem]
    total: int
    conflicts: int
    next_recording: Optional[ScheduleItem] = None


class ConflictResolutionResponse(BaseModel):
    conflict_id: str
    resolution: str
    affected_rules: List[str]


@router.get("/", response_model=ScheduleResponse)
async def get_schedule(days: int = 7):
    """
    Get the current DVR schedule.
    
    Parameters:
    - days: Number of days to show (default: 7)
    """
    # In a real implementation, this would query the actual schedule
    # For now, return sample data
    
    now = datetime.now()
    sample_schedule = [
        {
            "rule_id": "rule_001",
            "rule_name": "Nightly News",
            "start_time": now.replace(hour=18, minute=30, second=0, microsecond=0),
            "end_time": now.replace(hour=19, minute=0, second=0, microsecond=0),
            "channel": "News HD",
            "status": "scheduled",
            "priority": 1
        },
        {
            "rule_id": "rule_002",
            "rule_name": "Favorite Show",
            "start_time": now.replace(hour=20, minute=0, second=0, microsecond=0),
            "end_time": now.replace(hour=20, minute=30, second=0, microsecond=0),
            "channel": "Entertainment",
            "status": "scheduled",
            "priority": 2
        },
    ]
    
    # Find next recording
    next_recording = None
    for item in sample_schedule:
        if item["start_time"] > now:
            next_recording = item
            break
    
    return ScheduleResponse(
        items=[ScheduleItem(**item) for item in sample_schedule],
        total=len(sample_schedule),
        conflicts=0,
        next_recording=ScheduleItem(**next_recording) if next_recording else None
    )


@router.post("/refresh")
async def refresh_schedule():
    """
    Manually refresh the DVR schedule.
    """
    # In a real implementation, this would:
    # 1. Fetch updated EPG data
    # 2. Recalculate all rule schedules
    # 3. Resolve any conflicts
    # 4. Update the job queue
    
    _log.info("Manually refreshing DVR schedule")
    
    return {
        "success": True,
        "message": "Schedule refreshed successfully",
        "rules_processed": 8,
        "conflicts_resolved": 0,
        "next_update": (datetime.now() + timedelta(hours=24)).isoformat()
    }


@router.get("/conflicts")
async def get_conflicts():
    """
    Get current schedule conflicts.
    """
    # Sample conflict data
    conflicts = [
        {
            "conflict_id": "conflict_001",
            "time": "2024-04-18T20:00:00",
            "channel": "Entertainment",
            "rules": ["rule_002", "rule_005"],
            "severity": "high",
            "resolution": "priority"
        }
    ]
    
    return {
        "conflicts": conflicts,
        "total": len(conflicts),
        "resolved": 0,
        "unresolved": len(conflicts)
    }


@router.post("/conflicts/{conflict_id}/resolve")
async def resolve_conflict(conflict_id: str, resolution: str):
    """
    Resolve a specific schedule conflict.
    
    Parameters:
    - conflict_id: ID of the conflict
    - resolution: How to resolve (priority, manual, cancel)
    """
    # In a real implementation, this would apply the resolution
    _log.info(f"Resolving conflict {conflict_id} with resolution: {resolution}")
    
    return {
        "success": True,
        "message": f"Conflict {conflict_id} resolved with {resolution}",
        "affected_rules": ["rule_002", "rule_005"],
        "resolution": resolution
    }


@router.get("/status")
async def get_schedule_status():
    """
    Get DVR schedule status.
    """
    return {
        "last_refresh": datetime.now().isoformat(),
        "next_refresh": (datetime.now() + timedelta(hours=24)).isoformat(),
        "rules_loaded": 8,
        "active_rules": 5,
        "upcoming_recordings": 12,
        "conflicts": 0,
        "status": "healthy"
    }