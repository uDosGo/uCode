"""
Integration tests for uHomeNest Thin UI routes.

Tests the thin UI endpoints including home, media, and automation views.
"""

import pytest
from fastapi.testclient import TestClient
from pathlib import Path

from uhome_server.app import create_app
from uhome_server.services.job_queue import get_job_queue, JobType, JobStatus, RecordingJob
from datetime import datetime, timedelta


@pytest.fixture
def client():
    """Create test client for thin UI routes."""
    app = create_app()
    return TestClient(app)


@pytest.fixture
def job_queue():
    """Get job queue instance for testing."""
    return get_job_queue()


def test_home_index_route(client):
    """Test that home index route returns successfully."""
    response = client.get("/api/runtime/thin/home/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "uHomeNest Kiosk" in response.text
    assert "Quick Actions" in response.text


def test_home_index_alias(client):
    """Test that home index alias route works."""
    response = client.get("/api/runtime/thin/home/index")
    assert response.status_code == 200
    assert "uHomeNest Kiosk" in response.text


def test_home_status_route(client):
    """Test that home status route returns successfully."""
    response = client.get("/api/runtime/thin/home/status")
    assert response.status_code == 200
    assert "System Status" in response.text
    assert "System Information" in response.text


def test_home_navigate_route(client):
    """Test that home navigation route works."""
    response = client.get("/api/runtime/thin/home/navigate")
    assert response.status_code == 200
    assert "Navigation" in response.text


def test_home_navigate_with_target(client):
    """Test that home navigation with target redirects."""
    response = client.get("/api/runtime/thin/home/navigate?target=media")
    assert response.status_code == 200
    assert "<script>window.location.href='/api/runtime/thin/media';</script>" in response.text


def test_media_index_route(client):
    """Test that media index route returns successfully."""
    response = client.get("/api/runtime/thin/media/")
    assert response.status_code == 200
    assert "Media Center" in response.text
    assert "Movies" in response.text
    assert "TV Shows" in response.text


def test_media_play_route(client):
    """Test that media play route returns successfully."""
    response = client.get("/api/runtime/thin/media/play")
    assert response.status_code == 200
    assert "Media Playback" in response.text
    assert "Play" in response.text
    assert "Pause" in response.text


def test_media_recordings_route(client):
    """Test that media recordings route returns successfully."""
    response = client.get("/api/runtime/thin/media/recordings")
    assert response.status_code == 200
    assert "Recordings" in response.text
    assert "News Broadcast" in response.text


def test_media_dvr_route(client):
    """Test that media DVR route returns successfully."""
    response = client.get("/api/runtime/thin/media/dvr")
    assert response.status_code == 200
    assert "DVR Schedule" in response.text
    assert "Nightly News" in response.text


def test_automation_index_route(client):
    """Test that automation index route returns successfully."""
    response = client.get("/api/runtime/thin/automation/")
    assert response.status_code == 200
    assert "Automation Center" in response.text
    assert "Job Queue" in response.text


def test_automation_jobs_route(client, job_queue):
    """Test that automation jobs route returns successfully and shows queue status."""
    # Add a test job to the queue
    test_job = RecordingJob(
        job_id="test_job_001",
        job_type=JobType.RECORDING,
        status=JobStatus.QUEUED,
        priority=2,
        created_at=datetime.now(),
        updated_at=datetime.now(),
        params={},
        rule_id="rule_001",
        channel_id="test-channel",
        start_time=datetime.now() + timedelta(minutes=5),
        end_time=datetime.now() + timedelta(minutes=35),
        quality_profile="hd"
    )
    job_queue.add_job(test_job)
    
    response = client.get("/api/runtime/thin/automation/jobs")
    assert response.status_code == 200
    assert "Job Queue Monitor" in response.text
    assert "Active Jobs" in response.text
    
    # Clean up
    job_queue.cancel_job("test_job_001")


def test_automation_status_route(client):
    """Test that automation status route returns successfully."""
    response = client.get("/api/runtime/thin/automation/status")
    assert response.status_code == 200
    assert "Automation Status" in response.text
    assert "System Health" in response.text


def test_automation_home_route(client):
    """Test that automation home route returns successfully."""
    response = client.get("/api/runtime/thin/automation/home")
    assert response.status_code == 200
    assert "Home Automation" in response.text
    assert "Living Room" in response.text


def test_thin_routes_content_type(client):
    """Test that all thin routes return HTML content type."""
    routes = [
        "/api/runtime/thin/home/",
        "/api/runtime/thin/home/status",
        "/api/runtime/thin/media/",
        "/api/runtime/thin/media/play",
        "/api/runtime/thin/automation/",
        "/api/runtime/thin/automation/status",
    ]
    
    for route in routes:
        response = client.get(route)
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]


def test_thin_routes_navigation_links(client):
    """Test that thin routes contain proper navigation links."""
    response = client.get("/api/runtime/thin/home/")
    assert "/api/runtime/thin/home" in response.text
    assert "/api/runtime/thin/media" in response.text
    assert "/api/runtime/thin/automation" in response.text


def test_thin_routes_templates_exist():
    """Test that all required templates exist."""
    templates_dir = Path(__file__).parent.parent / "server" / "templates" / "thin"
    required_templates = [
        "home.html",
        "media.html", 
        "automation.html",
        "status.html"
    ]
    
    for template in required_templates:
        template_path = templates_dir / template
        assert template_path.exists(), f"Template {template} not found"
        assert template_path.is_file(), f"Template {template} is not a file"


def test_thin_routes_kiosk_features(client):
    """Test that thin routes include kiosk-specific features."""
    response = client.get("/api/runtime/thin/home/")
    
    # Check for kiosk-specific features
    assert "touch-target" in response.text  # Large touch targets
    assert "user-select: none" in response.text  # Disable text selection
    assert "contextmenu" in response.text  # Context menu handling
    assert "setTimeout" in response.text  # Auto-refresh


def test_thin_routes_responsive_design(client):
    """Test that thin routes include responsive design elements."""
    response = client.get("/api/runtime/thin/media/")
    
    # Check for responsive design classes
    assert "container mx-auto" in response.text
    assert "grid-cols" in response.text
    assert "md:grid-cols" in response.text
    assert "overflow-x-auto" in response.text


def test_thin_routes_icon_usage(client):
    """Test that thin routes use appropriate icons."""
    response = client.get("/api/runtime/thin/home/")
    
    # Check for icon usage
    assert "🏠" in response.text  # Home icon
    assert "🎬" in response.text  # Media icon
    assert "🤖" in response.text  # Automation icon
    assert "▶️" in response.text  # Play icon


def test_thin_routes_error_handling(client):
    """Test that thin routes handle errors gracefully."""
    # Test non-existent route
    response = client.get("/api/runtime/thin/nonexistent")
    assert response.status_code == 404
    
    # Test invalid navigation target
    response = client.get("/api/runtime/thin/home/navigate?target=invalid")
    assert response.status_code == 200  # Should show navigation page, not error


def test_job_queue_integration_in_automation(client, job_queue):
    """Test that automation views properly integrate with job queue."""
    # Clear any existing jobs
    job_queue.clear_completed_jobs()
    
    # Get initial status
    response = client.get("/api/runtime/thin/automation/")
    initial_content = response.text
    
    # Add a test job
    test_job = RecordingJob(
        job_id="integration_test_job",
        job_type=JobType.RECORDING,
        status=JobStatus.QUEUED,
        priority=1,
        created_at=datetime.now(),
        updated_at=datetime.now(),
        params={},
        rule_id="test_rule",
        channel_id="test_channel",
        start_time=datetime.now() + timedelta(minutes=10),
        end_time=datetime.now() + timedelta(minutes=40),
        quality_profile="hd"
    )
    job_queue.add_job(test_job)
    
    # Get updated status
    response = client.get("/api/runtime/thin/automation/")
    updated_content = response.text
    
    # Clean up
    job_queue.cancel_job("integration_test_job")
    
    # Verify content changed (job count updated)
    assert response.status_code == 200
    assert "Automation Center" in updated_content