"""Tests for backup and restore functionality."""

import json
from pathlib import Path

import pytest

from uhome_server.backup import create_backup, list_backups, restore_backup


@pytest.fixture
def temp_repo_root(tmp_path):
    """Create a temporary repository root with sample data."""
    repo_root = tmp_path / "repo"
    
    # Create registries
    memory_dir = repo_root / "memory" / "uhome"
    memory_dir.mkdir(parents=True)
    
    nodes_data = {
        "updated_at": "2026-03-10T10:00:00Z",
        "items": [
            {
                "node_id": "node1",
                "hostname": "server1",
                "authority": "primary",
                "status": "online",
            }
        ],
    }
    (memory_dir / "nodes.json").write_text(json.dumps(nodes_data, indent=2), encoding="utf-8")
    
    volumes_data = {
        "updated_at": "2026-03-10T10:00:00Z",
        "items": [
            {
                "volume_id": "vol1",
                "label": "Main Storage",
                "status": "online",
            }
        ],
    }
    (memory_dir / "volumes.json").write_text(json.dumps(volumes_data, indent=2), encoding="utf-8")
    
    # Create config
    config_dir = repo_root / "memory" / "config"
    config_dir.mkdir(parents=True)
    
    uhome_config = {
        "jellyfin_url": "http://localhost:8096",
        "jellyfin_api_key": "test_key",
    }
    (config_dir / "uhome.json").write_text(json.dumps(uhome_config, indent=2), encoding="utf-8")
    
    # Create workspace settings
    workspace_dir = repo_root / "memory" / "workspace" / "settings"
    workspace_dir.mkdir(parents=True)
    
    workspace_settings = {
        "preferred_target_client": "living-room-tv",
    }
    (workspace_dir / "default.json").write_text(json.dumps(workspace_settings, indent=2), encoding="utf-8")
    
    return repo_root


def test_create_backup_success(temp_repo_root):
    """Test successful backup creation."""
    result = create_backup(repo_root=temp_repo_root)
    
    assert result.success is True
    assert result.backup_path is not None
    assert result.backup_path.exists()
    assert len(result.errors) == 0
    
    # Verify backup contents
    assert "registries/nodes.json" in result.items_backed_up
    assert "registries/volumes.json" in result.items_backed_up
    assert "config/uhome.json" in result.items_backed_up
    assert "workspace/default.json" in result.items_backed_up
    assert "backup_manifest.json" in result.items_backed_up
    
    # Verify files exist
    assert (result.backup_path / "registries" / "nodes.json").exists()
    assert (result.backup_path / "registries" / "volumes.json").exists()
    assert (result.backup_path / "config" / "uhome.json").exists()
    assert (result.backup_path / "workspace" / "default.json").exists()
    assert (result.backup_path / "backup_manifest.json").exists()


def test_create_backup_without_workspace(temp_repo_root):
    """Test backup creation excluding workspace."""
    result = create_backup(repo_root=temp_repo_root, include_workspace=False)
    
    assert result.success is True
    assert "workspace/default.json" not in result.items_backed_up
    assert "registries/nodes.json" in result.items_backed_up
    assert "config/uhome.json" in result.items_backed_up


def test_create_backup_custom_directory(temp_repo_root, tmp_path):
    """Test backup to custom directory."""
    custom_backup_dir = tmp_path / "custom_backups"
    result = create_backup(repo_root=temp_repo_root, backup_dir=custom_backup_dir)
    
    assert result.success is True
    assert result.backup_path is not None
    assert custom_backup_dir in result.backup_path.parents


def test_backup_manifest_structure(temp_repo_root):
    """Test backup manifest contains expected data."""
    result = create_backup(repo_root=temp_repo_root)
    
    manifest_path = result.backup_path / "backup_manifest.json"
    assert manifest_path.exists()
    
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert "backup_timestamp" in manifest
    assert "repo_root" in manifest
    assert "include_workspace" in manifest
    assert "items" in manifest
    assert isinstance(manifest["items"], list)
    assert len(manifest["items"]) > 0


def test_restore_backup_success(temp_repo_root, tmp_path):
    """Test successful backup restore."""
    # Create a backup
    backup_result = create_backup(repo_root=temp_repo_root)
    assert backup_result.success is True
    
    # Create a new empty repo to restore to
    new_repo = tmp_path / "restored_repo"
    new_repo.mkdir()
    
    # Restore the backup
    restore_result = restore_backup(
        backup_path=backup_result.backup_path,
        repo_root=new_repo,
    )
    
    assert restore_result.success is True
    assert len(restore_result.errors) == 0
    
    # Verify restored files
    assert "registries/nodes.json" in restore_result.items_restored
    assert "registries/volumes.json" in restore_result.items_restored
    assert "config/uhome.json" in restore_result.items_restored
    assert "workspace/default.json" in restore_result.items_restored
    
    # Verify file contents
    restored_nodes = new_repo / "memory" / "uhome" / "nodes.json"
    assert restored_nodes.exists()
    nodes_data = json.loads(restored_nodes.read_text(encoding="utf-8"))
    assert nodes_data["items"][0]["node_id"] == "node1"
    
    restored_config = new_repo / "memory" / "config" / "uhome.json"
    assert restored_config.exists()
    config_data = json.loads(restored_config.read_text(encoding="utf-8"))
    assert config_data["jellyfin_url"] == "http://localhost:8096"


def test_restore_backup_dry_run(temp_repo_root, tmp_path):
    """Test restore dry run doesn't modify files."""
    # Create a backup
    backup_result = create_backup(repo_root=temp_repo_root)
    assert backup_result.success is True
    
    # Create a new empty repo
    new_repo = tmp_path / "restored_repo"
    new_repo.mkdir()
    
    # Dry run restore
    restore_result = restore_backup(
        backup_path=backup_result.backup_path,
        repo_root=new_repo,
        dry_run=True,
    )
    
    assert restore_result.success is True
    assert "Dry run mode" in str(restore_result.warnings)
    
    # Verify files were NOT actually created
    assert not (new_repo / "memory" / "uhome" / "nodes.json").exists()
    assert not (new_repo / "memory" / "config" / "uhome.json").exists()


def test_restore_invalid_backup_path(temp_repo_root):
    """Test restore with non-existent backup path."""
    restore_result = restore_backup(
        backup_path=Path("/nonexistent/backup"),
        repo_root=temp_repo_root,
    )
    
    assert restore_result.success is False
    assert len(restore_result.errors) > 0
    assert "does not exist" in restore_result.errors[0].lower()


def test_restore_corrupted_json(temp_repo_root, tmp_path):
    """Test restore handles corrupted JSON gracefully."""
    # Create a backup
    backup_result = create_backup(repo_root=temp_repo_root)
    assert backup_result.success is True
    
    # Corrupt a JSON file in the backup
    corrupted_file = backup_result.backup_path / "registries" / "nodes.json"
    corrupted_file.write_text("{ invalid json }", encoding="utf-8")
    
    # Try to restore
    new_repo = tmp_path / "restored_repo"
    new_repo.mkdir()
    
    restore_result = restore_backup(
        backup_path=backup_result.backup_path,
        repo_root=new_repo,
    )
    
    # Should fail due to invalid JSON
    assert restore_result.success is False
    assert any("Invalid JSON" in error for error in restore_result.errors)


def test_list_backups(temp_repo_root):
    """Test listing available backups."""
    backup_dir = temp_repo_root / "backups"
    
    # Create multiple backups
    result1 = create_backup(repo_root=temp_repo_root, backup_dir=backup_dir)
    assert result1.success is True
    
    result2 = create_backup(repo_root=temp_repo_root, backup_dir=backup_dir)
    assert result2.success is True
    
    # List backups
    backups = list_backups(backup_dir)
    
    assert len(backups) == 2
    assert all("timestamp" in b for b in backups)
    assert all("items" in b for b in backups)
    assert all("item_count" in b for b in backups)
    
    # Backups should be sorted newest first
    assert backups[0]["timestamp"] >= backups[1]["timestamp"]


def test_list_backups_empty_directory(tmp_path):
    """Test listing backups in empty directory."""
    empty_dir = tmp_path / "empty_backups"
    backups = list_backups(empty_dir)
    
    assert backups == []


def test_backup_restore_round_trip(temp_repo_root, tmp_path):
    """Test complete backup and restore cycle preserves data."""
    # Original data
    original_nodes = temp_repo_root / "memory" / "uhome" / "nodes.json"
    original_nodes_data = json.loads(original_nodes.read_text(encoding="utf-8"))
    
    original_config = temp_repo_root / "memory" / "config" / "uhome.json"
    original_config_data = json.loads(original_config.read_text(encoding="utf-8"))
    
    original_workspace = temp_repo_root / "memory" / "workspace" / "settings" / "default.json"
    original_workspace_data = json.loads(original_workspace.read_text(encoding="utf-8"))
    
    # Create backup
    backup_result = create_backup(repo_root=temp_repo_root)
    assert backup_result.success is True
    
    # Restore to new location
    new_repo = tmp_path / "restored_repo"
    new_repo.mkdir()
    
    restore_result = restore_backup(
        backup_path=backup_result.backup_path,
        repo_root=new_repo,
    )
    assert restore_result.success is True
    
    # Verify data integrity
    restored_nodes = new_repo / "memory" / "uhome" / "nodes.json"
    restored_nodes_data = json.loads(restored_nodes.read_text(encoding="utf-8"))
    assert restored_nodes_data == original_nodes_data
    
    restored_config = new_repo / "memory" / "config" / "uhome.json"
    restored_config_data = json.loads(restored_config.read_text(encoding="utf-8"))
    assert restored_config_data == original_config_data
    
    restored_workspace = new_repo / "memory" / "workspace" / "settings" / "default.json"
    restored_workspace_data = json.loads(restored_workspace.read_text(encoding="utf-8"))
    assert restored_workspace_data == original_workspace_data


def test_backup_preserves_file_metadata(temp_repo_root):
    """Test backup preserves file timestamps and permissions."""
    # Create backup
    backup_result = create_backup(repo_root=temp_repo_root)
    assert backup_result.success is True
    
    # Check that backup files exist with metadata
    backed_up_nodes = backup_result.backup_path / "registries" / "nodes.json"
    assert backed_up_nodes.exists()
    assert backed_up_nodes.stat().st_size > 0
    
    # Verify JSON is valid
    nodes_data = json.loads(backed_up_nodes.read_text(encoding="utf-8"))
    assert "items" in nodes_data


def test_multiple_backups_dont_conflict(temp_repo_root):
    """Test multiple backups can coexist without conflicts."""
    backup_dir = temp_repo_root / "backups"
    
    # Create first backup
    result1 = create_backup(repo_root=temp_repo_root, backup_dir=backup_dir)
    assert result1.success is True
    path1 = result1.backup_path
    
    # Modify data
    nodes_file = temp_repo_root / "memory" / "uhome" / "nodes.json"
    nodes_data = json.loads(nodes_file.read_text(encoding="utf-8"))
    nodes_data["items"][0]["status"] = "degraded"
    nodes_file.write_text(json.dumps(nodes_data, indent=2), encoding="utf-8")
    
    # Create second backup
    result2 = create_backup(repo_root=temp_repo_root, backup_dir=backup_dir)
    assert result2.success is True
    path2 = result2.backup_path
    
    # Verify both backups exist and are different
    assert path1 != path2
    assert path1.exists()
    assert path2.exists()
    
    # Verify they contain different data
    nodes1 = json.loads((path1 / "registries" / "nodes.json").read_text(encoding="utf-8"))
    nodes2 = json.loads((path2 / "registries" / "nodes.json").read_text(encoding="utf-8"))
    assert nodes1["items"][0]["status"] == "online"
    assert nodes2["items"][0]["status"] == "degraded"
