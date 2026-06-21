"""
DVR Channels API endpoints.

Provides channel management and tuning information.
"""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional

from uhome_server.config import get_logger

_log = get_logger("uhome.dvr.channels")

router = APIRouter(prefix="/channels", tags=["dvr-channels"])


class ChannelResponse(BaseModel):
    channel_id: str
    name: str
    number: int
    source: str
    tuner: Optional[str] = None
    quality: Optional[float] = None


class TunerResponse(BaseModel):
    tuner_id: str
    name: str
    type: str
    status: str
    current_channel: Optional[str] = None


@router.get("/")
async def list_channels():
    """
    List available channels.
    """
    channels = [
        {
            "channel_id": "news-hd",
            "name": "News HD",
            "number": 101,
            "source": "antenna",
            "tuner": "tuner_1",
            "quality": 95.5
        },
        {
            "channel_id": "entertainment",
            "name": "Entertainment",
            "number": 102,
            "source": "antenna",
            "tuner": "tuner_1",
            "quality": 92.3
        },
        {
            "channel_id": "discovery",
            "name": "Discovery",
            "number": 103,
            "source": "antenna",
            "tuner": "tuner_2",
            "quality": 89.7
        },
    ]
    
    return {
        "channels": [ChannelResponse(**c) for c in channels],
        "total": len(channels)
    }


@router.get("/{channel_id}")
async def get_channel(channel_id: str):
    """
    Get detailed information about a channel.
    """
    # Sample channel data
    channel_data = {
        "channel_id": channel_id,
        "name": "Sample Channel",
        "number": 101,
        "source": "antenna",
        "frequency": "500 MHz",
        "tuner": "tuner_1",
        "quality": 95.5,
        "signal_strength": 88.2,
        "available": True
    }
    
    return channel_data


@router.get("/tuners")
async def list_tuners():
    """
    List available tuners.
    """
    tuners = [
        {
            "tuner_id": "tuner_1",
            "name": "Tuner 1",
            "type": "ATSC",
            "status": "idle",
            "current_channel": None
        },
        {
            "tuner_id": "tuner_2",
            "name": "Tuner 2",
            "type": "ATSC",
            "status": "recording",
            "current_channel": "news-hd"
        },
    ]
    
    return {
        "tuners": [TunerResponse(**t) for t in tuners],
        "total": len(tuners),
        "available": 1,
        "in_use": 1
    }


@router.get("/tuners/{tuner_id}")
async def get_tuner(tuner_id: str):
    """
    Get detailed information about a tuner.
    """
    tuner_data = {
        "tuner_id": tuner_id,
        "name": f"Tuner {tuner_id[-1]}",
        "type": "ATSC",
        "status": "idle",
        "capabilities": ["HD", "Dolby Digital", "Closed Captioning"],
        "current_channel": None,
        "signal_quality": 92.5,
        "uptime": "24h 30m"
    }
    
    return tuner_data


@router.get("/status")
async def get_channel_status():
    """
    Get overall channel system status.
    """
    return {
        "total_channels": 42,
        "available_channels": 42,
        "tuners": 2,
        "available_tuners": 1,
        "signal_quality": 92.5,
        "status": "healthy"
    }