"""Library management routes for git-backed uHOME containers."""

from __future__ import annotations

from urllib.parse import urlparse

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from uhome_server.library.clone_manager import get_library_clone_manager

router = APIRouter(prefix="/api/library", tags=["library"])


class RepoInstallWizardRequest(BaseModel):
    repo: str
    branch: str = "main"


def _normalize_repo_input(repo: str) -> dict[str, str]:
    raw = (repo or "").strip()
    if not raw:
        raise HTTPException(status_code=400, detail="repo is required")
    if "/" in raw and not raw.startswith("https://"):
        owner, name = raw.split("/", 1)
        return {
            "input": raw,
            "owner": owner,
            "name": name,
            "clone_target": f"https://github.com/{owner}/{name}.git",
            "display": raw,
        }
    parsed = urlparse(raw)
    if parsed.scheme != "https" or not parsed.netloc:
        raise HTTPException(status_code=400, detail="Repository must be owner/name or a valid https URL")
    path_parts = [part for part in parsed.path.split("/") if part]
    if len(path_parts) < 2:
        raise HTTPException(status_code=400, detail="Repository URL must include owner and repository name")
    owner = path_parts[-2]
    name = path_parts[-1].removesuffix(".git")
    return {
        "input": raw,
        "owner": owner,
        "name": name,
        "clone_target": f"https://{parsed.netloc}/{'/'.join([*path_parts[:-1], f'{name}.git'])}",
        "display": f"{owner}/{name}",
    }


@router.get("/repos")
async def list_repos():
    return {"success": True, "repos": get_library_clone_manager().list_repos()}


@router.post("/repos/clone")
async def clone_repo(repo: str = Query(...), branch: str = Query("main")):
    normalized = _normalize_repo_input(repo)
    cloned = get_library_clone_manager().clone(normalized["clone_target"], branch=branch)
    if not cloned:
        raise HTTPException(status_code=400, detail="Clone failed")
    return {"success": True, "repo": cloned.to_dict(), "normalized_repo": normalized}


@router.post("/repos/{name}/update")
async def update_repo(name: str):
    if not get_library_clone_manager().update(name):
        raise HTTPException(status_code=400, detail="Update failed")
    return {"success": True, "name": name}


@router.delete("/repos/{name}")
async def delete_repo(name: str):
    get_library_clone_manager().remove(name)
    return {"success": True, "name": name}
