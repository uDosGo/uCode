"""
Thin UI Media routes for uHomeNest kiosk interface.

Provides media-related views including playback, recordings, and library browsing.
"""

import jinja2
from fastapi import APIRouter, Request, Response
from fastapi.templating import Jinja2Templates
from typing import Optional

from uhome_server.config import get_repo_root

router = APIRouter(prefix="/media", tags=["thin-media"])

# Set up templates directory with cache disabled to avoid Jinja2 3.1.6 LRUCache bug
_templates_loader = jinja2.FileSystemLoader(get_repo_root() / "templates")
_templates_env = jinja2.Environment(loader=_templates_loader, autoescape=jinja2.select_autoescape(), cache_size=0)
templates = Jinja2Templates(env=_templates_env)


@router.get("/")
async def media_index(request: Request) -> Response:
    """
    Media home page - overview of media library and playback options.
    """
    context = {
        "request": request,
        "page_title": "Media Center",
        "media_stats": {
            "movies": 128,
            "tv_shows": 45,
            "music_albums": 32,
            "total_hours": 845
        },
        "recent_media": [
            {
                "title": "The Grand Adventure",
                "type": "movie",
                "year": 2023,
                "poster": "/static/images/posters/adventure.jpg",
                "rating": 8.5
            },
            {
                "title": "Tech Innovations",
                "type": "tv",
                "season": "Season 3",
                "poster": "/static/images/posters/tech.jpg",
                "rating": 9.1
            },
            {
                "title": "Jazz Classics",
                "type": "music",
                "artist": "Various Artists",
                "poster": "/static/images/posters/jazz.jpg",
                "rating": 7.8
            },
        ],
        "quick_actions": [
            {
                "title": "Play Now",
                "icon": "▶️",
                "url": "/api/runtime/thin/media/play",
                "description": "Start playback"
            },
            {
                "title": "Recordings",
                "icon": "📼",
                "url": "/api/runtime/thin/media/recordings",
                "description": "View recordings"
            },
            {
                "title": "Library",
                "icon": "📚",
                "url": "/api/runtime/thin/media/library",
                "description": "Browse library"
            },
            {
                "title": "DVR Schedule",
                "icon": "📅",
                "url": "/api/runtime/thin/media/dvr",
                "description": "View schedule"
            },
        ]
    }
    
    return templates.TemplateResponse(request, "thin/media.html", context)


@router.get("/play")
async def media_play(request: Request) -> Response:
    """
    Media playback interface.
    """
    context = {
        "request": request,
        "page_title": "Media Playback",
        "current_playback": {
            "title": "Selected Media",
            "type": "movie",
            "progress": 45,
            "duration": "2h 15m",
            "status": "playing"
        },
        "playback_controls": [
            {"icon": "⏮️", "action": "rewind", "label": "Rewind"},
            {"icon": "⏸️", "action": "pause", "label": "Pause"},
            {"icon": "▶️", "action": "play", "label": "Play"},
            {"icon": "⏭️", "action": "forward", "label": "Forward"},
            {"icon": "⏹️", "action": "stop", "label": "Stop"}
        ],
        "playback_queue": [
            {"title": "Next Episode", "type": "tv", "duration": "42m"},
            {"title": "Feature Presentation", "type": "movie", "duration": "1h 58m"},
            {"title": "Music Track", "type": "music", "duration": "3m 45s"},
        ]
    }
    
    return templates.TemplateResponse(request, "thin/media_play.html", context)


@router.get("/recordings")
async def media_recordings(request: Request) -> Response:
    """
    Recordings management interface.
    """
    context = {
        "request": request,
        "page_title": "Recordings",
        "recordings": [
            {
                "id": "rec_001",
                "title": "News Broadcast - April 17",
                "channel": "News HD",
                "date": "2024-04-17",
                "time": "18:30",
                "duration": "30m",
                "size": "1.2 GB",
                "status": "completed"
            },
            {
                "id": "rec_002",
                "title": "Documentary: Nature Wonders",
                "channel": "Discovery",
                "date": "2024-04-16",
                "time": "20:00",
                "duration": "1h",
                "size": "2.8 GB",
                "status": "completed"
            },
            {
                "id": "rec_003",
                "title": "Sports Highlights",
                "channel": "Sports Plus",
                "date": "2024-04-15",
                "time": "22:30",
                "duration": "15m",
                "size": "450 MB",
                "status": "completed"
            },
        ],
        "upcoming_recordings": [
            {
                "title": "Morning News",
                "channel": "News HD",
                "date": "2024-04-18",
                "time": "07:00",
                "duration": "30m"
            },
            {
                "title": "Favorite Show",
                "channel": "Entertainment",
                "date": "2024-04-18",
                "time": "20:00",
                "duration": "42m"
            },
        ]
    }
    
    return templates.TemplateResponse(request, "thin/media_recordings.html", context)


@router.get("/dvr")
async def media_dvr(request: Request) -> Response:
    """
    DVR schedule and management.
    """
    context = {
        "request": request,
        "page_title": "DVR Schedule",
        "active_rules": [
            {
                "id": "rule_001",
                "name": "Nightly News",
                "type": "Time-Based",
                "channel": "News HD",
                "schedule": "Mon-Fri at 18:30",
                "priority": 1,
                "next_recording": "Today, 18:30"
            },
            {
                "id": "rule_002",
                "name": "Favorite Series",
                "type": "Series",
                "channel": "Entertainment",
                "schedule": "Weekly, new episodes",
                "priority": 2,
                "next_recording": "Thu, 20:00"
            },
        ],
        "upcoming_schedule": [
            {
                "time": "18:30",
                "title": "Nightly News",
                "channel": "News HD",
                "duration": "30m",
                "status": "scheduled"
            },
            {
                "time": "20:00",
                "title": "Documentary",
                "channel": "Discovery",
                "duration": "1h",
                "status": "scheduled"
            },
        ],
        "dvr_stats": {
            "total_rules": 8,
            "active_rules": 5,
            "upcoming_recordings": 12,
            "storage_used": "45 GB",
            "storage_free": "205 GB"
        }
    }
    
    return templates.TemplateResponse(request, "thin/media_dvr.html", context)
