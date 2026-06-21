"""uHOME platform routes."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from uhome_server.config import get_repo_root
from uhome_server.services.uhome_presentation_service import get_uhome_presentation_service
from uhome_server.workspace import get_template_workspace_service


class UHomePresentationStartRequest(BaseModel):
    presentation: str = ""


def create_platform_routes(auth_guard=None) -> APIRouter:
    del auth_guard
    router = APIRouter(prefix="/api/platform", tags=["platform"])
    repo_root = get_repo_root()
    uhome_presentation = get_uhome_presentation_service(repo_root=repo_root)

    @router.get("/uhome/status")
    async def uhome_status():
        workspace = get_template_workspace_service(repo_root)
        return {
            "presentation": uhome_presentation.get_status(),
            "template_workspace": workspace.component_contract("uhome"),
            "template_workspace_state": workspace.component_snapshot("uhome"),
        }

    @router.get("/uhome/presentation/status")
    async def uhome_presentation_status():
        return uhome_presentation.get_status()

    @router.post("/uhome/presentation/start")
    async def uhome_presentation_start(payload: UHomePresentationStartRequest):
        try:
            state = uhome_presentation.start(payload.presentation)
            return {"success": True, "state": state}
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @router.post("/uhome/presentation/stop")
    async def uhome_presentation_stop():
        return {"success": True, "state": uhome_presentation.stop()}

    return router
