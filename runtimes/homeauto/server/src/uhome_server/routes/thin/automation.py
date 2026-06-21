"""
Thin UI Automation routes for uHomeNest kiosk interface.

Provides automation status, job queue monitoring, and home control views.
"""

import jinja2
from fastapi import APIRouter, Request, Response
from fastapi.templating import Jinja2Templates
from typing import Optional

from uhome_server.config import get_repo_root
from uhome_server.services.job_queue import get_job_queue, JobStatus

router = APIRouter(prefix="/automation", tags=["thin-automation"])

# Set up templates directory with cache disabled to avoid Jinja2 3.1.6 LRUCache bug
_templates_loader = jinja2.FileSystemLoader(get_repo_root() / "templates")
_templates_env = jinja2.Environment(loader=_templates_loader, autoescape=jinja2.select_autoescape(), cache_size=0)
templates = Jinja2Templates(env=_templates_env)


@router.get("/")
async def automation_index(request: Request) -> Response:
    """
    Automation home page - overview of automation status and controls.
    """
    # Get job queue status
    job_queue = get_job_queue()
    queue_status = job_queue.get_queue_status()
    
    context = {
        "request": request,
        "page_title": "Automation Center",
        "job_queue_status": queue_status,
        "automation_stats": {
            "active_jobs": queue_status.get("active", 0),
            "completed_jobs": queue_status.get("completed", 0),
            "queued_jobs": queue_status.get("queued", 0),
            "failed_jobs": queue_status.get("failed", 0)
        },
        "quick_actions": [
            {
                "title": "View Job Queue",
                "icon": "📋",
                "url": "/api/runtime/thin/automation/jobs",
                "description": "Monitor jobs"
            },
            {
                "title": "System Status",
                "icon": "📊",
                "url": "/api/runtime/thin/automation/status",
                "description": "View status"
            },
            {
                "title": "Home Control",
                "icon": "🏠",
                "url": "/api/runtime/thin/automation/home",
                "description": "Control home"
            },
            {
                "title": "Settings",
                "icon": "⚙️",
                "url": "/api/runtime/thin/automation/settings",
                "description": "Configure automation"
            },
        ],
        "recent_automation": [
            {
                "time": "10:45 AM",
                "action": "Media library scan completed",
                "status": "success",
                "icon": "🔍"
            },
            {
                "time": "10:40 AM",
                "action": "DVR schedule updated",
                "status": "success",
                "icon": "📅"
            },
            {
                "time": "10:35 AM",
                "action": "System health check passed",
                "status": "success",
                "icon": "✅"
            },
        ]
    }
    
    return templates.TemplateResponse(request, "thin/automation.html", context)


@router.get("/jobs")
async def automation_jobs(request: Request) -> Response:
    """
    Job queue monitoring interface.
    """
    job_queue = get_job_queue()
    queue_status = job_queue.get_queue_status()
    
    # Get sample jobs (in a real implementation, you'd get actual jobs)
    sample_jobs = [
        {
            "id": "job_001",
            "type": "Recording",
            "status": "completed",
            "priority": 1,
            "created": "10:30 AM",
            "duration": "30m"
        },
        {
            "id": "job_002",
            "type": "Post-Processing",
            "status": "running",
            "priority": 2,
            "created": "10:45 AM",
            "progress": 65
        },
        {
            "id": "job_003",
            "type": "Metadata Extraction",
            "status": "queued",
            "priority": 3,
            "created": "11:00 AM",
            "estimated_start": "Soon"
        },
    ]
    
    context = {
        "request": request,
        "page_title": "Job Queue Monitor",
        "queue_status": queue_status,
        "active_jobs": [job for job in sample_jobs if job["status"] == "running"],
        "queued_jobs": [job for job in sample_jobs if job["status"] == "queued"],
        "completed_jobs": [job for job in sample_jobs if job["status"] == "completed"],
        "job_types": ["Recording", "Post-Processing", "Cleanup", "Transcoding", "Metadata"]
    }
    
    return templates.TemplateResponse(request, "thin/automation_jobs.html", context)


@router.get("/status")
async def automation_status(request: Request) -> Response:
    """
    Detailed automation status view.
    """
    context = {
        "request": request,
        "page_title": "Automation Status",
        "system_health": {
            "cpu_usage": 25,
            "memory_usage": 68,
            "disk_usage": 42,
            "network_status": "online"
        },
        "service_status": [
            {"name": "uHome Server", "status": "running", "uptime": "2h 30m"},
            {"name": "Job Queue", "status": "running", "uptime": "2h 30m"},
            {"name": "DVR Service", "status": "running", "uptime": "2h 25m"},
            {"name": "Jellyfin", "status": "running", "uptime": "2h 30m"},
        ],
        "recent_events": [
            {
                "timestamp": "2024-04-17 10:30:15",
                "event": "System started",
                "component": "core",
                "status": "success"
            },
            {
                "timestamp": "2024-04-17 10:30:45",
                "event": "Media library scan initiated",
                "component": "media",
                "status": "success"
            },
            {
                "timestamp": "2024-04-17 10:31:20",
                "event": "DVR schedule loaded",
                "component": "dvr",
                "status": "success"
            },
            {
                "timestamp": "2024-04-17 10:32:10",
                "event": "Job queue initialized",
                "component": "jobs",
                "status": "success"
            },
        ],
        "performance_metrics": {
            "jobs_processed": 42,
            "average_processing_time": "12.5s",
            "success_rate": "98.7%",
            "current_load": "Low"
        }
    }
    
    return templates.TemplateResponse(request, "thin/automation_status.html", context)


@router.get("/home")
async def automation_home(request: Request) -> Response:
    """
    Home automation control interface.
    """
    context = {
        "request": request,
        "page_title": "Home Automation",
        "rooms": [
            {
                "name": "Living Room",
                "devices": [
                    {"name": "Main TV", "type": "media_player", "state": "off"},
                    {"name": "Lights", "type": "light", "state": "on", "brightness": 75},
                    {"name": "Thermostat", "type": "climate", "state": "heating", "temperature": 22}
                ]
            },
            {
                "name": "Kitchen",
                "devices": [
                    {"name": "Kitchen Lights", "type": "light", "state": "on", "brightness": 100},
                    {"name": "Coffee Maker", "type": "switch", "state": "off"}
                ]
            },
            {
                "name": "Bedroom",
                "devices": [
                    {"name": "Bedroom TV", "type": "media_player", "state": "off"},
                    {"name": "Night Light", "type": "light", "state": "off"}
                ]
            },
        ],
        "scenes": [
            {"name": "Movie Night", "icon": "🎬", "devices_affected": 8},
            {"name": "Good Morning", "icon": "☀️", "devices_affected": 6},
            {"name": "Away Mode", "icon": "🏠", "devices_affected": 12},
            {"name": "Sleep Mode", "icon": "🌙", "devices_affected": 5},
        ]
    }
    
    return templates.TemplateResponse(request, "thin/automation_home.html", context)
