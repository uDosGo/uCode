"""
Thin UI routes for uHomeNest kiosk interface.

This module provides lightweight, server-rendered UI views for kiosk displays
and thin clients, optimized for low-resource devices and embedded systems.
"""

from fastapi import APIRouter
from . import home, media, automation

router = APIRouter(prefix="/api/runtime/thin", tags=["thin"])

router.include_router(home.router)
router.include_router(media.router)
router.include_router(automation.router)