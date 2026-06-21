"""
DVR EPG (Electronic Program Guide) API endpoints.

Provides EPG data management and channel information.
"""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timedelta

from uhome_server.config import get_logger

_log = get_logger("uhome.dvr.epg")

router = APIRouter(prefix="/epg", tags=["dvr-epg"])


class EPGChannel(BaseModel):
    channel_id: str
    name: str
    number: int
    icon: Optional[str] = None
    category: str


class EPGProgram(BaseModel):
    program_id: str
    channel_id: str
    title: str
    description: Optional[str] = None
    start_time: datetime
    end_time: datetime
    genre: str
    rating: Optional[float] = None


class EPGSource(BaseModel):
    source_id: str
    name: str
    type: str
    last_updated: datetime
    next_update: datetime


@router.get("/channels")
async def list_channels():
    """
    List available EPG channels.
    """
    # Sample channel data
    channels = [
        {
            "channel_id": "news-hd",
            "name": "News HD",
            "number": 101,
            "icon": "📰",
            "category": "News"
        },
        {
            "channel_id": "entertainment",
            "name": "Entertainment",
            "number": 102,
            "icon": "🎬",
            "category": "Entertainment"
        },
        {
            "channel_id": "discovery",
            "name": "Discovery",
            "number": 103,
            "icon": "🔬",
            "category": "Documentary"
        },
    ]
    
    return {
        "channels": [EPGChannel(**c) for c in channels],
        "total": len(channels)
    }


@router.get("/channels/{channel_id}")
async def get_channel_programs(channel_id: str, hours: int = 24):
    """
    Get programs for a specific channel.
    
    Parameters:
    - channel_id: ID of the channel
    - hours: Number of hours to show (default: 24)
    """
    # Sample program data
    now = datetime.now()
    programs = [
        {
            "program_id": "prog_001",
            "channel_id": channel_id,
            "title": "Morning News",
            "description": "Daily morning news program",
            "start_time": now.replace(hour=7, minute=0, second=0, microsecond=0),
            "end_time": now.replace(hour=8, minute=0, second=0, microsecond=0),
            "genre": "News",
            "rating": 8.5
        },
        {
            "program_id": "prog_002",
            "channel_id": channel_id,
            "title": "Documentary Special",
            "description": "Nature documentary",
            "start_time": now.replace(hour=20, minute=0, second=0, microsecond=0),
            "end_time": now.replace(hour=21, minute=0, second=0, microsecond=0),
            "genre": "Documentary",
            "rating": 9.1
        },
    ]
    
    return {
        "channel_id": channel_id,
        "programs": [EPGProgram(**p) for p in programs],
        "total": len(programs)
    }


@router.get("/sources")
async def list_epg_sources():
    """
    List configured EPG sources.
    """
    sources = [
        {
            "source_id": "xmltv_main",
            "name": "XMLTV Main",
            "type": "xmltv",
            "last_updated": datetime.now() - timedelta(hours=1),
            "next_update": datetime.now() + timedelta(hours=23)
        }
    ]
    
    return {
        "sources": [EPGSource(**s) for s in sources],
        "total": len(sources)
    }


@router.post("/sources/{source_id}/refresh")
async def refresh_epg_source(source_id: str):
    """
    Manually refresh an EPG source.
    """
    _log.info(f"Refreshing EPG source {source_id}")
    
    return {
        "success": True,
        "message": f"EPG source {source_id} refresh initiated",
        "programs_updated": 145,
        "channels_updated": 42,
        "next_update": (datetime.now() + timedelta(hours=24)).isoformat()
    }


@router.get("/search")
async def search_epg(query: str, limit: int = 10):
    """
    Search EPG data.
    
    Parameters:
    - query: Search query
    - limit: Maximum results
    """
    # Sample search results
    results = [
        {
            "program_id": "prog_001",
            "channel_id": "news-hd",
            "title": "News Program",
            "description": "Matching news program",
            "start_time": datetime.now().replace(hour=18, minute=0),
            "end_time": datetime.now().replace(hour=19, minute=0),
            "channel_name": "News HD"
        }
    ]
    
    return {
        "query": query,
        "results": results,
        "total": len(results)
    }


@router.get("/status")
async def get_epg_status():
    """
    Get EPG system status.
    """
    return {
        "sources": 1,
        "channels": 42,
        "programs": 145,
        "last_update": (datetime.now() - timedelta(hours=1)).isoformat(),
        "next_update": (datetime.now() + timedelta(hours=23)).isoformat(),
        "status": "healthy"
    }