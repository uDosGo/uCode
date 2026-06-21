"""
DVR Rules API endpoints.

Implements CRUD operations for DVR rules based on the design specification.
"""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from enum import Enum
from pathlib import Path

from uhome_server.services.job_queue import get_job_queue, RecordingJob, JobStatus
from uhome_server.services.rules_engine import (
    get_rules_engine, 
    RuleType, 
    TimeBasedRule, 
    SeriesRule, 
    MovieRule, 
    KeywordRule, 
    ChannelRule
)
from uhome_server.config import get_logger

_log = get_logger("uhome.dvr.rules")

router = APIRouter(prefix="/rules", tags=["dvr-rules"])

# Initialize rules engine
_rules_engine = get_rules_engine(persistence_path=Path("/tmp/uhome_rules_engine.json"))


# Enums for rule types and other fixed values
class RuleType(str, Enum):
    time_based = "time-based"
    series = "series"
    movie = "movie"
    keyword = "keyword"
    channel = "channel"


class QualityProfile(str, Enum):
    sd = "sd"
    hd = "hd"
    uhd = "uhd"


class RecurrencePattern(str, Enum):
    daily = "daily"
    weekly = "weekly"
    monthly = "monthly"
    custom = "custom"


# Pydantic models for request/response
class TimeBasedRuleCreate(BaseModel):
    rule_name: str
    rule_type: RuleType = RuleType.time_based
    channel_id: str
    start_time: datetime
    end_time: datetime
    recurrence: Optional[RecurrencePattern] = None
    program_title: Optional[str] = None
    quality_profile: QualityProfile = QualityProfile.hd
    priority: int = 3
    max_episodes: Optional[int] = None
    keep_until: Optional[datetime] = None


class SeriesRuleCreate(BaseModel):
    rule_name: str
    rule_type: RuleType = RuleType.series
    series_id: str
    series_title: str
    season_numbers: Optional[List[int]] = None
    include_specials: bool = False
    avoid_duplicates: bool = True
    quality_profile: QualityProfile = QualityProfile.hd
    priority: int = 3
    keep_until: Optional[datetime] = None


class MovieRuleCreate(BaseModel):
    rule_name: str
    rule_type: RuleType = RuleType.movie
    movie_id: str
    movie_title: str
    year: Optional[int] = None
    quality_profile: QualityProfile = QualityProfile.hd
    priority: int = 3
    keep_until: Optional[datetime] = None


class KeywordRuleCreate(BaseModel):
    rule_name: str
    rule_type: RuleType = RuleType.keyword
    keywords: List[str]
    require_all_keywords: bool = False
    channels: Optional[List[str]] = None
    time_ranges: Optional[List[str]] = None
    quality_profile: QualityProfile = QualityProfile.hd
    priority: int = 3
    keep_until: Optional[datetime] = None


class ChannelRuleCreate(BaseModel):
    rule_name: str
    rule_type: RuleType = RuleType.channel
    channel_id: str
    channel_name: str
    time_ranges: Optional[List[str]] = None
    quality_profile: QualityProfile = QualityProfile.hd
    priority: int = 3
    keep_until: Optional[datetime] = None


class DVRRuleResponse(BaseModel):
    rule_id: str
    rule_name: str
    rule_type: RuleType
    created_at: datetime
    updated_at: datetime
    enabled: bool
    priority: int
    status: str
    next_scheduled: Optional[datetime] = None


class DVRRuleListResponse(BaseModel):
    rules: List[DVRRuleResponse]
    total: int
    active: int
    disabled: int


# Use the new rules engine instead of the old store
# The old store is kept for reference but not used


@router.post("/", response_model=DVRRuleResponse)
async def create_rule(rule_data: dict):
    """
    Create a new DVR rule.
    
    Supports all rule types: time-based, series, movie, keyword, channel
    """
    try:
        # Validate rule type
        rule_type = rule_data.get("rule_type")
        if rule_type not in [rt.value for rt in RuleType]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid rule type"
            )
        
        # Create the rule using the new rules engine
        rule = _rules_engine.create_rule(rule_data)
        
        # Schedule the rule (create job if applicable)
        if rule.rule_type in [RuleType.TIME_BASED, RuleType.SERIES]:
            job_queue = get_job_queue()
            
            # Create a recording job for time-based rules
            if rule.rule_type == RuleType.TIME_BASED:
                recording_job = RecordingJob(
                    job_id=f"job_{rule.rule_id}",
                    job_type="recording",
                    status=JobStatus.QUEUED,
                    priority=rule.priority.value,
                    created_at=datetime.now(),
                    updated_at=datetime.now(),
                    params={},
                    rule_id=rule.rule_id,
                    channel_id=getattr(rule, 'channel_id', 'unknown'),
                    start_time=datetime.fromisoformat(rule_data.get("start_time", datetime.now().isoformat())),
                    end_time=datetime.fromisoformat(rule_data.get("end_time", datetime.now().isoformat())),
                    quality_profile=rule.quality_profile.value
                )
                job_queue.add_job(recording_job)
                _log.info(f"Created recording job for rule {rule.rule_id}")
        
        return DVRRuleResponse(
            rule_id=rule.rule_id,
            rule_name=rule.rule_name,
            rule_type=rule.rule_type.value,
            created_at=rule.created_at,
            updated_at=rule.updated_at,
            enabled=rule.enabled,
            priority=rule.priority.value,
            status="active",
            next_scheduled=datetime.fromisoformat(rule_data.get("start_time", datetime.now().isoformat())) 
                if rule.rule_type == RuleType.TIME_BASED else None
        )
        
    except Exception as e:
        _log.error(f"Failed to create DVR rule: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create rule: {str(e)}"
        )


@router.get("/", response_model=DVRRuleListResponse)
async def list_rules(enabled: Optional[bool] = None, rule_type: Optional[str] = None):
    """
    List all DVR rules.
    
    Optional filters: enabled status, rule type
    """
    # Get rules from the new engine
    rules = _rules_engine.list_rules()
    
    # Apply filters
    if enabled is not None:
        rules = [r for r in rules if r.enabled == enabled]
    
    if rule_type:
        rules = [r for r in rules if r.rule_type.value == rule_type]
    
    # Count active/disabled
    active_count = sum(1 for r in rules if r.enabled)
    disabled_count = len(rules) - active_count
    
    return DVRRuleListResponse(
        rules=[DVRRuleResponse(
            rule_id=r.rule_id,
            rule_name=r.rule_name,
            rule_type=r.rule_type.value,
            created_at=r.created_at,
            updated_at=r.updated_at,
            enabled=r.enabled,
            priority=r.priority.value,
            status="active" if r.enabled else "disabled",
            next_scheduled=getattr(r, 'start_time', None) if hasattr(r, 'start_time') else None
        ) for r in rules],
        total=len(rules),
        active=active_count,
        disabled=disabled_count
    )


@router.get("/{rule_id}", response_model=DVRRuleResponse)
async def get_rule(rule_id: str):
    """
    Get a specific DVR rule by ID.
    """
    rule = _rules_engine.get_rule(rule_id)
    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rule not found"
        )
    
    return DVRRuleResponse(
        rule_id=rule.rule_id,
        rule_name=rule.rule_name,
        rule_type=rule.rule_type.value,
        created_at=rule.created_at,
        updated_at=rule.updated_at,
        enabled=rule.enabled,
        priority=rule.priority.value,
        status="active" if rule.enabled else "disabled",
        next_scheduled=getattr(rule, 'start_time', None) if hasattr(rule, 'start_time') else None
    )


@router.put("/{rule_id}", response_model=DVRRuleResponse)
async def update_rule(rule_id: str, updates: dict):
    """
    Update a DVR rule.
    """
    rule = _rules_engine.get_rule(rule_id)
    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rule not found"
        )
    
    # Update the rule
    updated_rule = _rules_engine.update_rule(rule_id, updates)
    if not updated_rule:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update rule"
        )
    
    return DVRRuleResponse(
        rule_id=updated_rule.rule_id,
        rule_name=updated_rule.rule_name,
        rule_type=updated_rule.rule_type.value,
        created_at=updated_rule.created_at,
        updated_at=updated_rule.updated_at,
        enabled=updated_rule.enabled,
        priority=updated_rule.priority.value,
        status="active" if updated_rule.enabled else "disabled",
        next_scheduled=getattr(updated_rule, 'start_time', None) if hasattr(updated_rule, 'start_time') else None
    )


@router.delete("/{rule_id}")
async def delete_rule(rule_id: str):
    """
    Delete a DVR rule.
    """
    rule = _rules_engine.get_rule(rule_id)
    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rule not found"
        )
    
    # Delete the rule
    success = _rules_engine.delete_rule(rule_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete rule"
        )
    
    return {"success": True, "message": "Rule deleted successfully"}


@router.post("/{rule_id}/enable")
async def enable_rule(rule_id: str):
    """
    Enable a DVR rule.
    """
    success = _rules_engine.enable_rule(rule_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rule not found"
        )
    
    return {"success": True, "message": "Rule enabled"}


@router.post("/{rule_id}/disable")
async def disable_rule(rule_id: str):
    """
    Disable a DVR rule.
    """
    success = _rules_engine.disable_rule(rule_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rule not found"
        )
    
    return {"success": True, "message": "Rule disabled"}


@router.post("/test-recording")
async def test_recording(test_data: dict):
    """
    Test recording endpoint for debugging.
    """
    channel = test_data.get("channel", "test-channel")
    duration = test_data.get("duration", 60)  # seconds
    
    _log.info(f"Starting test recording on {channel} for {duration} seconds")
    
    # In a real implementation, this would start an actual recording
    # For now, we'll just log and return success
    
    return {
        "success": True,
        "message": f"Test recording started on {channel}",
        "duration": duration,
        "recording_id": f"test_rec_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    }