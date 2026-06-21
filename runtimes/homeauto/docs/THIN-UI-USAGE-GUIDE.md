---
title: "uHomeNest Thin UI Usage Guide"
status: draft
last_updated: 2026-04-22T23:26:13+10:00
category: guide
tags: [guide, ucode3]
description: "This guide provides comprehensive documentation for using the uHomeNest thin UI, including port information, API endp..."
---
# uHomeNest Thin UI Usage Guide

**Version**: 1.0
**Date**: 2024-04-17
**Status**: Active

This guide provides comprehensive documentation for using the uHomeNest thin UI, including port information, API endpoints, and usage examples.

## Overview

The uHomeNest thin UI provides a lightweight, server-rendered interface for accessing household media, automation status, and documentation through simple HTTP endpoints. The thin UI is designed to work on various devices including tablets, TVs, and desktop browsers.

## Base Configuration

### Default Port

**Primary Port**: `8000`
**Base URL**: `http://127.0.0.1:8000`

The default port for uHomeNest is **8000**, as specified in the quickstart guide and server configuration. All thin UI endpoints are relative to this base URL.

### Configuration Options

You can change the port by modifying the server startup command:

```bash
# Default port 8000
python -m uvicorn uhome_server.app:app --host 127.0.0.1 --port 8000 --reload

# Custom port (e.g., 7890)
python -m uvicorn uhome_server.app:app --host 127.0.0.1 --port 7890 --reload

# Production configuration
python -m uvicorn uhome_server.app:app --host 0.0.0.0 --port 8000
```

### Environment Variables

You can also configure the port using environment variables:

```bash
# Set port via environment variable
export UHOME_SERVER_PORT=8080
python -m uvicorn uhome_server.app:app --host 127.0.0.1 --port $UHOME_SERVER_PORT
```

## Thin UI Endpoints

### 1. Prose Reader (`GET /api/runtime/thin/read`)

**Purpose**: Render Markdown content as HTML with Tailwind Typography styling

**Parameters**:
- `path` (required): Path to Markdown file relative to repo root
- `rel` (optional): Relative path from `docs/` directory

**Examples**:

```http
GET /api/runtime/thin/read?path=docs/QUICKSTART.md
GET /api/runtime/thin/read?rel=QUICKSTART.md
```

**Response**: HTML-rendered content with Tailwind `prose` class

**Usage**:
```html
<!-- Embed in your UI -->
<iframe src="/api/runtime/thin/read?rel=QUICKSTART.md" width="100%" height="600"></iframe>
```

### 2. Documentation Browser (`GET /api/runtime/thin/browse`)

**Purpose**: Browse and navigate documentation files

**Parameters**:
- `rel` (required): Relative path from `docs/` directory
- `format` (optional): `html` (default) or `raw`

**Examples**:

```http
GET /api/runtime/thin/browse?rel=architecture/README.md
GET /api/runtime/thin/browse?rel=media/DVR-DESIGN.md&format=raw
```

**Response**: 
- `format=html`: HTML-rendered content
- `format=raw`: Raw Markdown content

**File Browser Example**:
```html
<ul>
  <li><a href="/api/runtime/thin/browse?rel=QUICKSTART.md">Quickstart</a></li>
  <li><a href="/api/runtime/thin/browse?rel=architecture/README.md">Architecture</a></li>
  <li><a href="/api/runtime/thin/browse?rel=media/DVR-DESIGN.md">DVR Design</a></li>
</ul>
```

### 3. Automation Status (`GET /api/runtime/thin/automation`)

**Purpose**: Display current automation status and home control information

**Parameters**: None

**Example**:
```http
GET /api/runtime/thin/automation
```

**Response**: HTML page showing:
- Current automation jobs
- Home Assistant entity states
- Recent automation events
- System health status

**Usage**:
```html
<!-- Full-page automation dashboard -->
<iframe src="/api/runtime/thin/automation" style="width: 100%; height: 100vh; border: none;"></iframe>
```

### 4. Media Status (`GET /api/runtime/thin/media`)

**Purpose**: Display current media playback and DVR status

**Parameters**: None

**Example**:
```http
GET /api/runtime/thin/media
```

**Response**: HTML page showing:
- Current playback sessions
- Upcoming recordings
- Recent recordings
- Media library statistics

## API Integration

### JavaScript Client Example

```javascript
// Thin UI Client Class
class ThinUIClient {
    constructor(baseUrl = 'http://127.0.0.1:8000') {
        this.baseUrl = baseUrl;
    }

    async getProse(path) {
        const response = await fetch(`${this.baseUrl}/api/runtime/thin/read?path=${encodeURIComponent(path)}`);
        return await response.text();
    }

    async browseDocs(relPath, format = 'html') {
        const response = await fetch(`${this.baseUrl}/api/runtime/thin/browse?rel=${encodeURIComponent(relPath)}&format=${format}`);
        return await response.text();
    }

    async getAutomationStatus() {
        const response = await fetch(`${this.baseUrl}/api/runtime/thin/automation`);
        return await response.text();
    }

    async getMediaStatus() {
        const response = await fetch(`${this.baseUrl}/api/runtime/thin/media`);
        return await response.text();
    }
}

// Usage
const client = new ThinUIClient();

// Load quickstart guide
client.getProse('docs/QUICKSTART.md').then(html => {
    document.getElementById('docs-container').innerHTML = html;
});
```

### Python Client Example

```python
import requests
from typing import Optional

class ThinUIClient:
    def __init__(self, base_url: str = "http://127.0.0.1:8000"):
        self.base_url = base_url.rstrip("/")
    
    def get_prose(self, path: str) -> str:
        """Get rendered prose content."""
        url = f"{self.base_url}/api/runtime/thin/read"
        params = {"path": path}
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.text
    
    def browse_docs(self, rel_path: str, format: str = "html") -> str:
        """Browse documentation."""
        url = f"{self.base_url}/api/runtime/thin/browse"
        params = {"rel": rel_path, "format": format}
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.text
    
    def get_automation_status(self) -> str:
        """Get automation status page."""
        url = f"{self.base_url}/api/runtime/thin/automation"
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    
    def get_media_status(self) -> str:
        """Get media status page."""
        url = f"{self.base_url}/api/runtime/thin/media"
        response = requests.get(url)
        response.raise_for_status()
        return response.text

# Usage
client = ThinUIClient()

# Get quickstart guide
quickstart_html = client.get_prose("docs/QUICKSTART.md")
print(quickstart_html[:500])  # Print first 500 characters
```

## Port Configuration Guide

### Development vs Production Ports

| Environment | Recommended Port | Binding | Purpose |
|-------------|------------------|---------|---------|
| Development | 8000 | 127.0.0.1 | Local development with hot reload |
| Development | 7890 | 127.0.0.1 | Alternative dev port |
| Production | 8000 | 0.0.0.0 | LAN-accessible server |
| Production | 8080 | 0.0.0.0 | Alternative production port |

### Changing Ports

**Temporary Change**:
```bash
# Run on port 8080
python -m uvicorn uhome_server.app:app --host 127.0.0.1 --port 8080 --reload
```

**Permanent Change**:
Edit `src/uhome_server/config.py` and set the default port:

```python
# Default server configuration
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8080  # Changed from 8000
```

### Port Forwarding

For remote access, you may need to set up port forwarding on your router:

```bash
# Example: Forward external port 8080 to internal port 8000
# Router configuration varies by manufacturer
# Internal IP: 192.168.1.100 (your server IP)
# External Port: 8080
# Internal Port: 8000
```

## Security Considerations

### LAN-Only Access

By default, uHomeNest binds to `127.0.0.1` (localhost only). For LAN access:

```bash
# Allow LAN access (behind firewall)
python -m uvicorn uhome_server.app:app --host 0.0.0.0 --port 8000
```

### Authentication

Thin UI endpoints are currently unauthenticated. For production use:

1. **Use a reverse proxy** (Nginx, Apache) with authentication
2. **Enable HTTPS** with Let's Encrypt
3. **Restrict access** by IP range
4. **Consider VPN** for remote access

### Reverse Proxy Example (Nginx)

```nginx
server {
    listen 80;
    server_name uhome.example.com;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        
        # Authentication
        auth_basic "Restricted Access";
        auth_basic_user_file /etc/nginx/.htpasswd;
    }
}
```

## Common Port Issues

### Port Already in Use

```bash
# Check what's using the port
lsof -i :8000

# Kill process on port 8000
kill $(lsof -t -i :8000)

# Use a different port
python -m uvicorn uhome_server.app:app --host 127.0.0.1 --port 8080
```

### Firewall Blocking

```bash
# Check firewall status
sudo ufw status

# Allow port 8000
sudo ufw allow 8000

# Reload firewall
sudo ufw reload
```

### Connection Refused

```bash
# Check if server is running
ps aux | grep uvicorn

# Check server logs
tail -f ~/.udos/logs/uhome-server.log

# Restart server
bash scripts/restart-uhome-server.sh
```

## Thin UI Best Practices

### Performance Optimization

1. **Use caching** for frequently accessed documentation
2. **Limit concurrent requests** to prevent overload
3. **Use compression** in reverse proxy
4. **Optimize images** in documentation

### Responsive Design

```html
<!-- Responsive thin UI container -->
<div class="container mx-auto px-4 py-8">
    <div class="prose max-w-none">
        <!-- Thin UI content will be rendered here -->
    </div>
</div>
```

### Accessibility

1. **Use semantic HTML** in thin UI templates
2. **Ensure proper contrast** for readability
3. **Support keyboard navigation**
4. **Provide text alternatives** for media

## Troubleshooting

### Thin UI Not Loading

1. **Check server status**: `curl http://127.0.0.1:8000/api/health`
2. **Verify port**: `netstat -tuln | grep 8000`
3. **Check logs**: `tail -f ~/.udos/logs/uhome-server.log`
4. **Test direct access**: Open `http://127.0.0.1:8000/api/runtime/thin/read?rel=QUICKSTART.md`

### Slow Response Times

1. **Check server load**: `top` or `htop`
2. **Monitor memory usage**: `free -h`
3. **Check disk I/O**: `iotop`
4. **Review job queue**: `GET /api/dvr/jobs`

### Styling Issues

1. **Verify CSS loading**: Check `/static/thin/prose.css`
2. **Inspect elements**: Use browser dev tools
3. **Clear cache**: `Ctrl+F5` or clear browser cache
4. **Rebuild CSS**: `cd thin-prose-build && npm run build`

## Integration with uHomeNest Ecosystem

### Dashboard Integration

```html
<!-- Example dashboard with thin UI components -->
<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
    <div class="bg-white p-4 rounded-lg shadow">
        <h2 class="text-xl font-bold mb-4">Automation Status</h2>
        <iframe src="/api/runtime/thin/automation" class="w-full h-64 border-none"></iframe>
    </div>
    <div class="bg-white p-4 rounded-lg shadow">
        <h2 class="text-xl font-bold mb-4">Media Status</h2>
        <iframe src="/api/runtime/thin/media" class="w-full h-64 border-none"></iframe>
    </div>
</div>
```

### Mobile Optimization

```html
<!-- Mobile-optimized thin UI -->
<div class="md:hidden">
    <!-- Mobile-specific layout -->
    <div class="space-y-4">
        <a href="/api/runtime/thin/browse?rel=QUICKSTART.md" class="block p-4 bg-blue-100 rounded">
            Quickstart Guide
        </a>
        <a href="/api/runtime/thin/automation" class="block p-4 bg-green-100 rounded">
            Automation Status
        </a>
    </div>
</div>
```

## Future Enhancements

### Planned Thin UI Features

1. **Search functionality** for documentation
2. **Table of contents** generation
3. **Dark mode** support
4. **Print-friendly** views
5. **Offline caching** for documentation

### Roadmap Alignment

These enhancements align with the uHomeNest v4 roadmap:
- **Q2 2024**: Documentation enhancements
- **Q3 2024**: Client integration improvements
- **Q4 2024**: Operational maturity features

## Conclusion

This guide provides comprehensive documentation for using the uHomeNest thin UI, including:

- **Port configuration** and management
- **Endpoint documentation** with examples
- **Client integration** examples (JavaScript, Python)
- **Security considerations** for production use
- **Troubleshooting** common issues
- **Best practices** for optimal performance

The thin UI is designed to be simple, lightweight, and accessible while providing essential functionality for household media and automation management.

**Next Steps**:
1. Review the [Quickstart Guide](QUICKSTART.md) for initial setup
2. Explore the [Architecture Documentation](architecture/README.md)
3. Check the [DVR System Design](architecture/media/DVR-DESIGN.md)
4. Refer to the [CI/CD Setup Guide](CI-CD-SETUP-GUIDE.md) for deployment

**Support**: For issues or questions, consult the [Troubleshooting](#troubleshooting) section or check the project documentation.