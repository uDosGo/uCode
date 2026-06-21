"""Clone/update/remove git-backed library repos for uHOME."""

from __future__ import annotations

import json
import shutil
import subprocess
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from uhome_server.config import get_repo_root


@dataclass
class ClonedRepo:
    name: str
    owner: str
    url: str
    branch: str
    commit: str
    cloned_at: str
    path: Path
    dependencies: dict[str, list[str]] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["path"] = str(self.path)
        return payload


class LibraryCloneManager:
    def __init__(self, repo_root: Path | None = None):
        self.repo_root = repo_root or get_repo_root()
        self.containers_path = self.repo_root / "library" / "containers"
        self.state_path = self.repo_root / "memory" / "library" / "clones.json"
        self.containers_path.mkdir(parents=True, exist_ok=True)
        self.state_path.parent.mkdir(parents=True, exist_ok=True)
        self.manifest = self._load_manifest()

    def _load_manifest(self) -> dict[str, Any]:
        if not self.state_path.exists():
            return {"repos": {}}
        try:
            payload = json.loads(self.state_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return {"repos": {}}
        if not isinstance(payload, dict):
            return {"repos": {}}
        payload.setdefault("repos", {})
        return payload

    def _save_manifest(self) -> None:
        self.state_path.write_text(json.dumps(self.manifest, indent=2), encoding="utf-8")

    def list_repos(self) -> list[dict[str, Any]]:
        repos: list[dict[str, Any]] = []
        for repo in self.manifest.get("repos", {}).values():
            repos.append(repo)
        return sorted(repos, key=lambda item: item.get("name", ""))

    def _detect_dependencies(self, repo_path: Path) -> dict[str, list[str]]:
        dependencies: dict[str, list[str]] = {"pip": [], "npm": []}
        if (repo_path / "requirements.txt").exists():
            dependencies["pip"] = [
                line.strip()
                for line in (repo_path / "requirements.txt").read_text(encoding="utf-8").splitlines()
                if line.strip() and not line.startswith("#")
            ]
        if (repo_path / "package.json").exists():
            try:
                package_json = json.loads((repo_path / "package.json").read_text(encoding="utf-8"))
                deps = package_json.get("dependencies", {})
                if isinstance(deps, dict):
                    dependencies["npm"] = sorted(deps.keys())
            except json.JSONDecodeError:
                pass
        return {key: value for key, value in dependencies.items() if value}

    def clone(self, repo: str, branch: str = "main") -> ClonedRepo | None:
        if repo.startswith("https://"):
            url = repo
            parts = repo.rstrip("/").split("/")
            owner = parts[-2]
            name = parts[-1].replace(".git", "")
        else:
            parts = repo.split("/")
            if len(parts) != 2:
                return None
            owner, name = parts
            url = f"https://github.com/{owner}/{name}.git"

        repo_path = self.containers_path / name
        if repo_path.exists() and name in self.manifest.get("repos", {}):
            info = self.manifest["repos"][name]
            return ClonedRepo(
                name=name,
                owner=owner,
                url=url,
                branch=info.get("branch", branch),
                commit=info.get("commit", ""),
                cloned_at=info.get("cloned_at", ""),
                path=repo_path,
                dependencies=info.get("dependencies", {}),
            )

        try:
            result = subprocess.run(
                ["git", "clone", "--depth", "1", "--branch", branch, url, str(repo_path)],
                capture_output=True,
                text=True,
                timeout=180,
            )
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return None

        if result.returncode != 0:
            return None

        try:
            commit_result = subprocess.run(
                ["git", "-C", str(repo_path), "rev-parse", "HEAD"],
                capture_output=True,
                text=True,
                timeout=30,
            )
            commit = commit_result.stdout.strip()[:12]
        except Exception:
            commit = "unknown"

        cloned_repo = ClonedRepo(
            name=name,
            owner=owner,
            url=url,
            branch=branch,
            commit=commit,
            cloned_at=datetime.now(timezone.utc).isoformat(),
            path=repo_path,
            dependencies=self._detect_dependencies(repo_path),
        )
        self.manifest["repos"][name] = cloned_repo.to_dict()
        self._save_manifest()
        return cloned_repo

    def update(self, name: str) -> bool:
        repo_path = self.containers_path / name
        if not repo_path.exists():
            return False
        try:
            result = subprocess.run(
                ["git", "-C", str(repo_path), "pull", "--ff-only"],
                capture_output=True,
                text=True,
                timeout=120,
            )
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False
        if result.returncode != 0:
            return False
        try:
            commit_result = subprocess.run(
                ["git", "-C", str(repo_path), "rev-parse", "HEAD"],
                capture_output=True,
                text=True,
                timeout=30,
            )
            commit = commit_result.stdout.strip()[:12]
        except Exception:
            commit = "unknown"
        if name in self.manifest.get("repos", {}):
            self.manifest["repos"][name]["commit"] = commit
            self.manifest["repos"][name]["last_updated"] = datetime.now(timezone.utc).isoformat()
            self._save_manifest()
        return True

    def remove(self, name: str) -> bool:
        repo_path = self.containers_path / name
        if repo_path.exists():
            shutil.rmtree(repo_path, ignore_errors=True)
        if name in self.manifest.get("repos", {}):
            del self.manifest["repos"][name]
            self._save_manifest()
        return True


def get_library_clone_manager(repo_root: Path | None = None) -> LibraryCloneManager:
    return LibraryCloneManager(repo_root=repo_root)
