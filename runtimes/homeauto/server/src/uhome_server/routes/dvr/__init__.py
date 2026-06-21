"""
DVR API routes for uHomeNest.

Implements the DVR system API endpoints based on the design specification.
"""

from fastapi import APIRouter
from . import rules, recordings, schedule, epg, channels

router = APIRouter(prefix="/api/dvr", tags=["dvr"])

router.include_router(rules.router)
router.include_router(recordings.router)
router.include_router(schedule.router)
router.include_router(epg.router)
router.include_router(channels.router)