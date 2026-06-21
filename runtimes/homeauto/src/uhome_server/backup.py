"""Backup and restore utilities for uHOME Server state."""

from __future__ import annotations

import json
import shutil
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


@dataclass
class BackupResult:
    """Result of a backup operation."""
    
    success: bool
    backup_path: Path | None
    timestamp: str
    items_backed_up: list[str]
    errors: list[str]
    
    def to_dict(self) -> dict[str, Any]:
        return {
            "success": self.success,
            "backup_path": str(self.backup_path) if self.backup_path else None,
            "timestamp": self.timestamp,
            "items_backed_up": self.items_backed_up,
            "errors": self.errors,
        }


@dataclass
class RestoreResult:
    """Result of a restore operation."""
    
    success: bool
    timestamp: str
    items_restored: list[str]
    errors: list[str]
    warnings: list[str]
    
    def to_dict(self) -> dict[str, Any]:
        return {
            "success": self.success,
            "timestamp": self.timestamp,
            "items_restored": self.items_restored,
            "errors": self.errors,
            "warnings": self.warnings,
        }


def _utc_now_iso() -> str:
    """Get current UTC timestamp in ISO format."""
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _utc_timestamp_filename() -> str:
    """Get UTC timestamp suitable for a filename with microseconds."""
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S_%f")


def create_backup(
    repo_root: Path,
    backup_dir: Path | None = None,
    include_workspace: bool = True,
) -> BackupResult:
    """Create a backup of uHOME Server state.
    
    Args:
        repo_root: Repository root directory
        backup_dir: Directory to store backups (defaults to repo_root/backups)
        include_workspace: Whether to include workspace settings
    
    Returns:
        BackupResult with details of the backup operation
    """
    errors = []
    items_backed_up = []
    timestamp = _utc_now_iso()
    
    # Default backup directory
    if backup_dir is None:
        backup_dir = repo_root / "backups"
    
    backup_dir.mkdir(parents=True, exist_ok=True)
    
    # Create timestamped backup directory
    backup_name = f"uhome_backup_{_utc_timestamp_filename()}"
    backup_path = backup_dir / backup_name
    
    try:
        backup_path.mkdir(parents=True, exist_ok=True)
        
        # Backup registries
        memory_dir = repo_root / "memory" / "uhome"
        if memory_dir.exists():
            registries_backup = backup_path / "registries"
            registries_backup.mkdir(parents=True, exist_ok=True)
            
            for registry_file in ["nodes.json", "volumes.json"]:
                source = memory_dir / registry_file
                if source.exists():
                    shutil.copy2(source, registries_backup / registry_file)
                    items_backed_up.append(f"registries/{registry_file}")
        else:
            errors.append(f"Registry directory not found: {memory_dir}")
        
        # Backup configuration
        config_dir = repo_root / "memory" / "config"
        if config_dir.exists():
            config_backup = backup_path / "config"
            config_backup.mkdir(parents=True, exist_ok=True)
            
            for config_file in ["uhome.json", "legacy-uhome.json", "wizard.json"]:
                source = config_dir / config_file
                if source.exists():
                    shutil.copy2(source, config_backup / config_file)
                    items_backed_up.append(f"config/{config_file}")
        else:
            errors.append(f"Config directory not found: {config_dir}")
        
        # Backup workspace settings
        if include_workspace:
            workspace_dir = repo_root / "memory" / "workspace" / "settings"
            if workspace_dir.exists():
                workspace_backup = backup_path / "workspace"
                workspace_backup.mkdir(parents=True, exist_ok=True)
                
                for workspace_file in workspace_dir.glob("*.json"):
                    shutil.copy2(workspace_file, workspace_backup / workspace_file.name)
                    items_backed_up.append(f"workspace/{workspace_file.name}")
        
        # Create backup manifest
        manifest = {
            "backup_timestamp": timestamp,
            "repo_root": str(repo_root),
            "include_workspace": include_workspace,
            "items": items_backed_up,
        }
        manifest_path = backup_path / "backup_manifest.json"
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        items_backed_up.append("backup_manifest.json")
        
        success = len(errors) == 0
        
    except Exception as e:
        errors.append(f"Backup failed: {str(e)}")
        success = False
        backup_path = None
    
    return BackupResult(
        success=success,
        backup_path=backup_path if success else None,
        timestamp=timestamp,
        items_backed_up=items_backed_up,
        errors=errors,
    )


def restore_backup(
    backup_path: Path,
    repo_root: Path,
    dry_run: bool = False,
) -> RestoreResult:
    """Restore uHOME Server state from a backup.
    
    Args:
        backup_path: Path to backup directory
        repo_root: Repository root directory to restore to
        dry_run: If True, validate but don't actually restore
    
    Returns:
        RestoreResult with details of the restore operation
    """
    errors = []
    warnings = []
    items_restored = []
    timestamp = _utc_now_iso()
    
    try:
        # Validate backup exists
        if not backup_path.exists() or not backup_path.is_dir():
            errors.append(f"Backup path does not exist or is not a directory: {backup_path}")
            return RestoreResult(
                success=False,
                timestamp=timestamp,
                items_restored=[],
                errors=errors,
                warnings=warnings,
            )
        
        # Read and validate manifest
        manifest_path = backup_path / "backup_manifest.json"
        if not manifest_path.exists():
            errors.append("Backup manifest not found")
            return RestoreResult(
                success=False,
                timestamp=timestamp,
                items_restored=[],
                errors=errors,
                warnings=warnings,
            )
        
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            errors.append(f"Invalid backup manifest JSON: {str(e)}")
            return RestoreResult(
                success=False,
                timestamp=timestamp,
                items_restored=[],
                errors=errors,
                warnings=warnings,
            )
        
        if dry_run:
            warnings.append("Dry run mode: no files will be modified")
        
        # Restore registries
        registries_backup = backup_path / "registries"
        if registries_backup.exists():
            memory_dir = repo_root / "memory" / "uhome"
            if not dry_run:
                memory_dir.mkdir(parents=True, exist_ok=True)
            
            for registry_file in registries_backup.glob("*.json"):
                target = memory_dir / registry_file.name
                
                # Validate JSON before restoring
                try:
                    json.loads(registry_file.read_text(encoding="utf-8"))
                except json.JSONDecodeError as e:
                    errors.append(f"Invalid JSON in backup {registry_file.name}: {str(e)}")
                    continue
                
                if not dry_run:
                    shutil.copy2(registry_file, target)
                items_restored.append(f"registries/{registry_file.name}")
        
        # Restore configuration
        config_backup = backup_path / "config"
        if config_backup.exists():
            config_dir = repo_root / "memory" / "config"
            if not dry_run:
                config_dir.mkdir(parents=True, exist_ok=True)
            
            for config_file in config_backup.glob("*.json"):
                target = config_dir / config_file.name
                
                # Validate JSON before restoring
                try:
                    json.loads(config_file.read_text(encoding="utf-8"))
                except json.JSONDecodeError as e:
                    errors.append(f"Invalid JSON in backup {config_file.name}: {str(e)}")
                    continue
                
                if not dry_run:
                    shutil.copy2(config_file, target)
                items_restored.append(f"config/{config_file.name}")
        
        # Restore workspace settings
        workspace_backup = backup_path / "workspace"
        if workspace_backup.exists():
            workspace_dir = repo_root / "memory" / "workspace" / "settings"
            if not dry_run:
                workspace_dir.mkdir(parents=True, exist_ok=True)
            
            for workspace_file in workspace_backup.glob("*.json"):
                target = workspace_dir / workspace_file.name
                
                # Validate JSON before restoring
                try:
                    json.loads(workspace_file.read_text(encoding="utf-8"))
                except json.JSONDecodeError as e:
                    warnings.append(f"Skipping invalid workspace file {workspace_file.name}: {str(e)}")
                    continue
                
                if not dry_run:
                    shutil.copy2(workspace_file, target)
                items_restored.append(f"workspace/{workspace_file.name}")
        
        success = len(errors) == 0
        
    except Exception as e:
        errors.append(f"Restore failed: {str(e)}")
        success = False
    
    return RestoreResult(
        success=success,
        timestamp=timestamp,
        items_restored=items_restored,
        errors=errors,
        warnings=warnings,
    )


def list_backups(backup_dir: Path) -> list[dict[str, Any]]:
    """List available backups in a directory.
    
    Args:
        backup_dir: Directory containing backups
    
    Returns:
        List of backup info dictionaries
    """
    backups = []
    
    if not backup_dir.exists():
        return backups
    
    for backup_path in sorted(backup_dir.glob("uhome_backup_*"), reverse=True):
        if not backup_path.is_dir():
            continue
        
        manifest_path = backup_path / "backup_manifest.json"
        if not manifest_path.exists():
            continue
        
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            backups.append({
                "path": str(backup_path),
                "name": backup_path.name,
                "timestamp": manifest.get("backup_timestamp", "unknown"),
                "items": manifest.get("items", []),
                "item_count": len(manifest.get("items", [])),
            })
        except (json.JSONDecodeError, OSError):
            continue
    
    return backups
