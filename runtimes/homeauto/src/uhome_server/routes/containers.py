"""Container catalog and launcher routes for uHOME library entries."""

from __future__ import annotations

import asyncio
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import httpx
from fastapi import APIRouter, BackgroundTasks, HTTPException
from fastapi.responses import StreamingResponse

from uhome_server.config import get_repo_root
from uhome_server.library.catalog import get_container_catalog_service


class ContainerLauncher:
    def __init__(self, repo_root: Path | None = None):
        self.repo_root = repo_root or get_repo_root()
        self.library_root = self.repo_root / "library"
        self.processes: dict[str, subprocess.Popen] = {}

    def _catalog(self):
        return get_container_catalog_service(self.repo_root)

    def _read_container_metadata(self, container_id: str) -> dict[str, Any] | None:
        entry = self._catalog().get_entry(container_id)
        if not entry:
            return None
        manifest_path = entry.metadata.get("manifest_path")
        if not isinstance(manifest_path, str):
            return None
        candidate = self.repo_root / manifest_path
        if not candidate.exists():
            return None
        try:
            payload = json.loads(candidate.read_text(encoding="utf-8"))
        except Exception:
            return None
        return payload if isinstance(payload, dict) else None

    def get_container_config(self, container_id: str) -> dict[str, Any] | None:
        entry = self._catalog().get_entry(container_id)
        if not entry or entry.kind != "library":
            return None
        if not entry.metadata.get("port"):
            return None
        return {
            "name": entry.label,
            "port": entry.metadata.get("port"),
            "health_check_url": entry.metadata.get("health_check_url"),
            "browser_route": entry.metadata.get("browser_route") or f"/ui/{container_id}",
            "container_path": entry.metadata.get("resolved_repo_path") or str(self.repo_root / entry.path),
            "manifest_path": entry.metadata.get("manifest_path"),
        }

    def list_available(self) -> list[dict[str, Any]]:
        containers = []
        for entry in self._catalog().list_by_kind("library"):
            if not entry.metadata.get("port"):
                continue
            state = self._container_state(entry.entry_id)
            containers.append(
                {
                    "id": entry.entry_id,
                    "name": entry.label,
                    "port": entry.metadata.get("port"),
                    "browser_route": entry.metadata.get("browser_route"),
                    "state": state,
                    "running": state == "running",
                }
            )
        return containers

    def is_running(self, container_id: str) -> bool:
        proc = self.processes.get(container_id)
        return proc is not None and proc.poll() is None

    def _resolve_runtime_path(self, container_id: str) -> Path:
        config = self.get_container_config(container_id) or {}
        runtime_path = config.get("container_path")
        return Path(runtime_path) if isinstance(runtime_path, str) else self.library_root / container_id

    def _container_state(self, container_id: str) -> str:
        config = self.get_container_config(container_id)
        if not config:
            return "not_found"
        metadata = self._read_container_metadata(container_id)
        if metadata is None:
            return "no_metadata"
        container_section = metadata.get("container", {})
        if container_section.get("type", "local") == "git":
            git_dir_inplace = self.library_root / container_id / ".git"
            git_dir_clone = self.library_root / "containers" / container_id / ".git"
            if not container_section.get("cloned_at") and not git_dir_inplace.exists() and not git_dir_clone.exists():
                return "not_cloned"
        if self.is_running(container_id):
            return "running"
        return "not_running"

    def _get_clone_params(self, container_id: str) -> tuple[str, str, Path]:
        metadata = self._read_container_metadata(container_id)
        if metadata is None:
            raise HTTPException(status_code=404, detail=f"container.json missing for {container_id}")
        container_section = metadata.get("container", {})
        if container_section.get("type", "local") != "git":
            raise HTTPException(status_code=400, detail=f"Container {container_id} is not type 'git'")
        source = container_section.get("source", "")
        ref = container_section.get("ref") or "main"
        clone_dest = self.library_root / "containers" / container_id
        return source, ref, clone_dest

    def _stamp_cloned_at(self, container_id: str) -> None:
        manifest_path = self.library_root / container_id / "container.json"
        if not manifest_path.exists():
            return
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
        payload.setdefault("container", {})["cloned_at"] = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        manifest_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    async def clone_container(self, container_id: str) -> dict[str, Any]:
        source, ref, clone_dest = self._get_clone_params(container_id)
        if clone_dest.exists() and (clone_dest / ".git").exists():
            self._stamp_cloned_at(container_id)
            return {"success": True, "container_id": container_id, "clone_path": str(clone_dest), "status": "already_cloned"}
        try:
            result = subprocess.run(
                ["git", "clone", "--depth", "1", "--branch", ref, source, str(clone_dest)],
                capture_output=True,
                text=True,
                timeout=180,
            )
        except FileNotFoundError as exc:
            raise HTTPException(status_code=500, detail="git not found in PATH") from exc
        except subprocess.TimeoutExpired as exc:
            raise HTTPException(status_code=504, detail=f"git clone timed out for {source}") from exc
        if result.returncode != 0:
            raise HTTPException(status_code=500, detail=f"git clone failed: {result.stderr.strip()[:200]}")
        self._stamp_cloned_at(container_id)
        return {"success": True, "container_id": container_id, "clone_path": str(clone_dest), "status": "cloned"}

    async def stream_clone(self, container_id: str):
        source, ref, clone_dest = self._get_clone_params(container_id)

        async def generate():
            yield f"data: {json.dumps({'progress': 0, 'status': 'starting', 'message': f'Preparing to clone {container_id}'})}\n\n"
            if clone_dest.exists() and (clone_dest / ".git").exists():
                self._stamp_cloned_at(container_id)
                yield f"data: {json.dumps({'progress': 100, 'status': 'complete', 'message': 'Already cloned'})}\n\n"
                return
            proc = await asyncio.create_subprocess_exec(
                "git",
                "clone",
                "--depth",
                "1",
                "--branch",
                ref,
                "--progress",
                source,
                str(clone_dest),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            progress = 5
            async for line in proc.stderr:
                text = line.decode(errors="replace").strip()
                if not text:
                    continue
                progress = min(progress + 3, 90)
                yield f"data: {json.dumps({'progress': progress, 'status': 'cloning', 'message': text[:120]})}\n\n"
            await proc.wait()
            if proc.returncode != 0:
                yield f"data: {json.dumps({'progress': progress, 'status': 'failed', 'error': f'git exited {proc.returncode}'})}\n\n"
                return
            self._stamp_cloned_at(container_id)
            yield f"data: {json.dumps({'progress': 100, 'status': 'complete', 'clone_path': str(clone_dest)})}\n\n"

        return StreamingResponse(generate(), media_type="text/event-stream")

    async def launch_container(self, container_id: str, background_tasks: BackgroundTasks) -> dict[str, Any]:
        config = self.get_container_config(container_id)
        if not config:
            raise HTTPException(status_code=404, detail=f"Container not found: {container_id}")
        state = self._container_state(container_id)
        if state == "running":
            return {"success": True, "status": "already_running", "container_id": container_id}
        if state == "not_cloned":
            raise HTTPException(status_code=409, detail=f"Container {container_id} has not been cloned yet.")
        metadata = self._read_container_metadata(container_id) or {}
        launch_config = metadata.get("launch_config", {})
        runtime_path = self._resolve_runtime_path(container_id)
        background_tasks.add_task(self._launch_service, container_id, config, launch_config, runtime_path)
        return {
            "success": True,
            "status": "launching",
            "container_id": container_id,
            "port": config["port"],
            "browser_route": config["browser_route"],
        }

    async def _launch_service(self, container_id: str, config: dict[str, Any], launch_config: dict[str, Any], runtime_path: Path):
        launch_cwd = runtime_path
        custom_cwd = launch_config.get("cwd")
        if custom_cwd:
            cwd_path = Path(custom_cwd)
            if not cwd_path.is_absolute():
                cwd_path = self.repo_root / cwd_path
            launch_cwd = cwd_path
        cmd = launch_config.get("command") or ["python", "-m", f"uhome_server.services.{container_id.replace('-', '_')}"]
        proc = subprocess.Popen(cmd, cwd=str(launch_cwd), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.processes[container_id] = proc
        await self._wait_for_health(config)

    async def _wait_for_health(self, config: dict[str, Any], retries: int = 30):
        health_url = config.get("health_check_url")
        if not health_url:
            await asyncio.sleep(2)
            return
        for _ in range(retries):
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.get(health_url, timeout=2.0)
                if response.status_code < 500:
                    return
            except Exception:
                pass
            await asyncio.sleep(1)

    async def stop_container(self, container_id: str) -> dict[str, Any]:
        if not self.is_running(container_id):
            return {"success": True, "status": "not_running"}
        proc = self.processes[container_id]
        proc.terminate()
        proc.wait(timeout=5)
        del self.processes[container_id]
        return {"success": True, "status": "stopped"}

    async def get_status(self, container_id: str) -> dict[str, Any]:
        config = self.get_container_config(container_id)
        if not config:
            raise HTTPException(status_code=404, detail=f"Container not found: {container_id}")
        state = self._container_state(container_id)
        return {
            "success": True,
            "container_id": container_id,
            "name": config["name"],
            "state": state,
            "running": state == "running",
            "port": config["port"],
            "browser_route": config["browser_route"],
        }


_launcher: ContainerLauncher | None = None


def get_launcher() -> ContainerLauncher:
    global _launcher
    if _launcher is None:
        _launcher = ContainerLauncher()
    return _launcher


router = APIRouter(prefix="/api/containers", tags=["containers"])


@router.get("/list/available")
async def list_available_containers():
    return {"success": True, "containers": get_launcher().list_available()}


@router.get("/{container_id}/status")
async def get_container_status(container_id: str):
    return await get_launcher().get_status(container_id)


@router.post("/{container_id}/clone")
async def clone_container(container_id: str):
    return await get_launcher().clone_container(container_id)


@router.get("/{container_id}/clone/stream")
async def stream_clone_container(container_id: str):
    return await get_launcher().stream_clone(container_id)


@router.post("/{container_id}/launch")
async def launch_container(container_id: str, background_tasks: BackgroundTasks):
    return await get_launcher().launch_container(container_id, background_tasks)


@router.post("/{container_id}/stop")
async def stop_container(container_id: str):
    return await get_launcher().stop_container(container_id)
