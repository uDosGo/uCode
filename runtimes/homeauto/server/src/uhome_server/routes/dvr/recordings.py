"""
DVR Recordings API endpoints.

Implements CRUD operations for recordings and playback management.
"""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from enum import Enum

from uhome_server.config import get_logger

_log = get_logger("uhome.dvr.recordings")

router = APIRouter(prefix="/recordings", tags=["dvr-recordings"])


# Enums for recording status
class RecordingStatus(str, Enum):
    scheduled = "scheduled"
    recording = "recording"
    completed = "completed"
    failed = "failed"
    cancelled = "cancelled"


# Pydantic models
class RecordingResponse(BaseModel):
    recording_id: str
    rule_id: str
    channel_id: str
    program_id: Optional[str] = None
    title: str
    description: Optional[str] = None
    start_time: datetime
    end_time: datetime
    status: RecordingStatus
    file_path: Optional[str] = None
    file_size: Optional[int] = None
    quality_profile: str


class RecordingListResponse(BaseModel):
    recordings: List[RecordingResponse]
    total: int
    by_status: dict


# In-memory storage for recordings
class RecordingStore:
    def __init__(self):
        self.recordings = {}
        self.next_id = 1
        
    def create_recording(self, recording_data: dict) -> str:
        """Create a new recording."""
        recording_id = f"rec_{self.next_id}"
        self.next_id += 1
        
        recording = {
            "recording_id": recording_id,
            "created_at": datetime.now(),
            "status": RecordingStatus.scheduled,
            **recording_data
        }
        
        self.recordings[recording_id] = recording
        return recording_id
        
    def get_recording(self, recording_id: str) -> Optional[dict]:
        """Get a recording by ID."""
        return self.recordings.get(recording_id)
        
    def list_recordings(self) -> List[dict]:
        """List all recordings."""
        return list(self.recordings.values())
        
    def update_recording(self, recording_id: str, updates: dict) -> bool:
        """Update a recording."""
        if recording_id not in self.recordings:
            return False
        
        self.recordings[recording_id].update(updates)
        return True
        
    def delete_recording(self, recording_id: str) -> bool:
        """Delete a recording."""
        if recording_id not in self.recordings:
            return False
        
        del self.recordings[recording_id]
        return True


# Global recording store instance
recording_store = RecordingStore()


@router.get("/", response_model=RecordingListResponse)
async def list_recordings(status: Optional[str] = None, limit: int = 50):
    """
    List all recordings.
    
    Optional filters: status, limit
    """
    recordings = recording_store.list_recordings()
    
    # Apply filters
    if status:
        recordings = [r for r in recordings if r["status"] == status]
    
    # Limit results
    recordings = recordings[:limit]
    
    # Count by status
    status_counts = {}
    for r in recordings:
        status_counts[r["status"]] = status_counts.get(r["status"], 0) + 1
    
    return RecordingListResponse(
        recordings=[RecordingResponse(
            recording_id=r["recording_id"],
            rule_id=r.get("rule_id", ""),
            channel_id=r["channel_id"],
            program_id=r.get("program_id"),
            title=r["title"],
            description=r.get("description"),
            start_time=r["start_time"],
            end_time=r["end_time"],
            status=r["status"],
            file_path=r.get("file_path"),
            file_size=r.get("file_size"),
            quality_profile=r.get("quality_profile", "hd")
        ) for r in recordings],
        total=len(recordings),
        by_status=status_counts
    )


@router.get("/{recording_id}", response_model=RecordingResponse)
async def get_recording(recording_id: str):
    """
    Get a specific recording by ID.
    """
    recording = recording_store.get_recording(recording_id)
    if not recording:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recording not found"
        )
    
    return RecordingResponse(
        recording_id=recording["recording_id"],
        rule_id=recording.get("rule_id", ""),
        channel_id=recording["channel_id"],
        program_id=recording.get("program_id"),
        title=recording["title"],
        description=recording.get("description"),
        start_time=recording["start_time"],
        end_time=recording["end_time"],
        status=recording["status"],
        file_path=recording.get("file_path"),
        file_size=recording.get("file_size"),
        quality_profile=recording.get("quality_profile", "hd")
    )


@router.delete("/{recording_id}")
async def delete_recording(recording_id: str):
    """
    Delete a recording.
    """
    success = recording_store.delete_recording(recording_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recording not found"
        )
    
    return {"success": True, "message": "Recording deleted successfully"}


@router.post("/{recording_id}/cancel")
async def cancel_recording(recording_id: str):
    """
    Cancel an active or scheduled recording.
    """
    recording = recording_store.get_recording(recording_id)
    if not recording:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recording not found"
        )
    
    # Only allow cancellation of scheduled or recording status
    if recording["status"] not in [RecordingStatus.scheduled, RecordingStatus.recording]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only scheduled or active recordings can be cancelled"
        )
    
    # Update status to cancelled
    success = recording_store.update_recording(recording_id, {
        "status": RecordingStatus.cancelled,
        "ended_at": datetime.now()
    })
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to cancel recording"
        )
    
    return {"success": True, "message": "Recording cancelled"}


@router.get("/upcoming")
async def get_upcoming_recordings(limit: int = 10):
    """
    Get upcoming recordings.
    """
    recordings = recording_store.list_recordings()
    upcoming = [
        r for r in recordings 
        if r["status"] == RecordingStatus.scheduled and r["start_time"] > datetime.now()
    ]
    
    # Sort by start time
    upcoming.sort(key=lambda x: x["start_time"])
    
    return {
        "upcoming": upcoming[:limit],
        "total": len(upcoming)
    }


@router.get("/recent")
async def get_recent_recordings(limit: int = 10):
    """
    Get recent recordings.
    """
    recordings = recording_store.list_recordings()
    recent = [
        r for r in recordings 
        if r["status"] in [RecordingStatus.completed, RecordingStatus.failed, RecordingStatus.cancelled]
    ]
    
    # Sort by end time (newest first)
    recent.sort(key=lambda x: x["end_time"], reverse=True)
    
    return {
        "recent": recent[:limit],
        "total": len(recent)
    }


@router.get("/stats")
async def get_recording_stats():
    """
    Get recording statistics.
    """
    recordings = recording_store.list_recordings()
    
    # Count by status
    by_status = {}
    for r in recordings:
        by_status[r["status"]] = by_status.get(r["status"], 0) + 1
    
    # Calculate storage usage (simplified)
    total_size = sum(r.get("file_size", 0) for r in recordings if r.get("file_size"))
    
    return {
        "total_recordings": len(recordings),
        "by_status": by_status,
        "total_storage": total_size,
        "average_duration": "N/A"  # Would calculate in real implementation
    }