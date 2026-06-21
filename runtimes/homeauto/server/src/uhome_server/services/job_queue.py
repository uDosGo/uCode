"""Job queue service for uHOME server."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Optional


class JobStatus(Enum):
    PENDING = "pending"
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class Job:
    id: str
    type: str
    status: JobStatus = JobStatus.PENDING
    priority: int = 0
    created: str = ""
    duration: str = ""
    progress: int = 0


@dataclass
class RecordingJob:
    job_id: str
    job_type: str = "recording"
    status: JobStatus = JobStatus.QUEUED
    priority: int = 0
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    params: dict[str, Any] = field(default_factory=dict)
    rule_id: str = ""
    channel_id: str = ""
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    quality_profile: str = "hd"


@dataclass
class JobQueue:
    jobs: list[Job] = field(default_factory=list)
    recording_jobs: list[RecordingJob] = field(default_factory=list)

    def get_queue_status(self) -> dict[str, Any]:
        return {
            "active": sum(1 for j in self.jobs if j.status == JobStatus.RUNNING),
            "completed": sum(1 for j in self.jobs if j.status == JobStatus.COMPLETED),
            "queued": sum(1 for j in self.jobs if j.status == JobStatus.QUEUED),
            "failed": sum(1 for j in self.jobs if j.status == JobStatus.FAILED),
            "pending": sum(1 for j in self.jobs if j.status == JobStatus.PENDING),
            "total": len(self.jobs),
        }

    def add_job(self, job: RecordingJob) -> None:
        self.recording_jobs.append(job)


_queue: JobQueue | None = None


def get_job_queue() -> JobQueue:
    global _queue
    if _queue is None:
        _queue = JobQueue()
    return _queue
