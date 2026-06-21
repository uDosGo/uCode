"""
Thin UI Home routes for uHomeNest kiosk interface.

Provides the main home/index view and navigation for kiosk displays.
"""

import jinja2
from fastapi import APIRouter, Request, Response
from fastapi.templating import Jinja2Templates
from pathlib import Path
from typing import Optional

from uhome_server.config import get_repo_root

router = APIRouter(prefix="/home", tags=["thin-home"])

# Set up templates directory with cache disabled to avoid Jinja2 3.1.6 LRUCache bug
_templates_loader = jinja2.FileSystemLoader(get_repo_root() / "templates")
_templates_env = jinja2.Environment(loader=_templates_loader, autoescape=jinja2.select_autoescape(), cache_size=0)
templates = Jinja2Templates(env=_templates_env)


@router.get("/")
@router.get("/index")
async def home_index(request: Request) -> Response:
    """
    Kiosk home page - main landing page for thin clients.
    
    Returns a lightweight HTML interface optimized for kiosk displays.
    """
    context = {
        "request": request,
        "page_title": "uHomeNest Kiosk",
        "version": "3.9.0",
        "nav_items": [
            {"url": "/api/runtime/thin/home", "label": "Home", "icon": "🏠"},
            {"url": "/api/runtime/thin/media", "label": "Media", "icon": "🎬"},
            {"url": "/api/runtime/thin/automation", "label": "Automation", "icon": "🤖"},
            {"url": "/api/runtime/thin/docs", "label": "Docs", "icon": "📚"},
        ],
        "quick_actions": [
            {
                "title": "Play Media",
                "icon": "▶️",
                "url": "/api/runtime/thin/media/play",
                "description": "Start playback"
            },
            {
                "title": "View Recordings",
                "icon": "📼",
                "url": "/api/runtime/thin/media/recordings",
                "description": "Manage recordings"
            },
            {
                "title": "Automation Status",
                "icon": "⚙️",
                "url": "/api/runtime/thin/automation/status",
                "description": "View automation"
            },
            {
                "title": "System Info",
                "icon": "ℹ️",
                "url": "/api/runtime/thin/system/info",
                "description": "System status"
            },
        ],
        "system_status": {
            "cpu": "Normal",
            "memory": "75%",
            "storage": "42%",
            "services": "All running"
        },
        "recent_activity": [
            {"time": "10:30 AM", "action": "System started", "icon": "🔄"},
            {"time": "10:31 AM", "action": "Media library scanned", "icon": "🔍"},
            {"time": "10:32 AM", "action": "DVR schedule loaded", "icon": "📅"},
        ]
    }
    
    return templates.TemplateResponse(request, "thin/home.html", context)


@router.get("/status")
async def home_status(request: Request) -> Response:
    """
    Home status view - system overview for kiosk.
    """
    context = {
        "request": request,
        "page_title": "System Status",
        "system_info": {
            "version": "3.9.0",
            "uptime": "2 hours 30 minutes",
            "last_update": "2024-04-17"
        },
        "services": [
            {"name": "uHome Server", "status": "running", "icon": "✅"},
            {"name": "Jellyfin", "status": "running", "icon": "✅"},
            {"name": "DVR Service", "status": "running", "icon": "✅"},
            {"name": "Job Queue", "status": "running", "icon": "✅"},
        ],
        "resource_usage": {
            "cpu": {"value": 25, "unit": "%"},
            "memory": {"value": 3840, "unit": "MB"},
            "storage": {"value": 450, "unit": "GB"},
            "network": {"value": "100 Mbps", "unit": "speed"}
        }
    }
    
    return templates.TemplateResponse(request, "thin/status.html", context)


@router.get("/navigate")
async def home_navigate(request: Request, target: Optional[str] = None) -> Response:
    """
    Navigation endpoint for kiosk mode.
    """
    navigation_targets = {
        "media": "/api/runtime/thin/media",
        "automation": "/api/runtime/thin/automation",
        "settings": "/api/runtime/thin/settings",
        "docs": "/api/runtime/thin/docs"
    }
    
    if target and target in navigation_targets:
        return Response(
            content=f"<script>window.location.href='{navigation_targets[target]}';</script>",
            media_type="text/html"
        )
    
    context = {
        "request": request,
        "page_title": "Navigation",
        "targets": list(navigation_targets.keys())
    }
    
    return templates.TemplateResponse(request, "thin/navigate.html", context)
