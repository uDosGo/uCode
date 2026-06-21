---
title: "uHomeNest First Time Launch Guide"
status: draft
last_updated: 2026-04-22T23:26:13+10:00
category: guide
tags: [guide, ucode3]
description: "Welcome to uHomeNest! This guide will walk you through your first time launch experience, covering all the new featur..."
---
# uHomeNest First Time Launch Guide

**Version**: 1.0
**Date**: 2024-04-17
**Status**: Active

Welcome to uHomeNest! This guide will walk you through your first time launch experience, covering all the new features and capabilities available in the latest version.

## Overview

This guide is designed to help you:
1. **Launch uHomeNest for the first time**
2. **Explore the new features** introduced in recent updates
3. **Configure your household media system**
4. **Set up automation and DVR**
5. **Integrate with your home network**

## Prerequisites

Before starting, ensure you have:

- ✅ Completed the [Sonic-Home installation](installer/SONIC-HOME-INSTALLER-GUIDE.md)
- ✅ System with minimum requirements (4GB RAM, 2+ CPU cores)
- ✅ Network connection for initial setup
- ✅ Modern web browser (Chrome, Firefox, Safari, Edge)

## Launching uHomeNest

### Starting the Server

```bash
# Start all services
sudo systemctl start uhome-server
sudo systemctl start jellyfin
sudo systemctl start postgresql

# Check service status
sudo systemctl status uhome-server

# View logs (optional)
journalctl -u uhome-server -f
```

### Accessing the Web Interface

Open your browser and navigate to:

**Default URL**: `http://localhost:8000`
**LAN Access**: `http://[server-ip]:8000` (if configured)

You should see the uHomeNest welcome screen with setup options.

## First Time Setup Wizard

### Step 1: Welcome Screen

- **Language Selection**: Choose your preferred language
- **Time Zone**: Set your local time zone
- **Terms of Service**: Review and accept

### Step 2: Admin Account Setup

- **Email**: admin@uhome.local (or your email)
- **Username**: uhome-admin
- **Password**: Create a strong password (minimum 12 characters)
- **Security Question**: Set up account recovery

### Step 3: System Configuration

#### Media Library Setup

- **Library Paths**: `/media/library` (default)
- **Recording Path**: `/media/recordings`
- **Transcoding Cache**: `/var/uhome/transcode`
- **Metadata Storage**: `/var/uhome/metadata`

#### Network Configuration

- **Server Name**: uhome-server (or custom name)
- **Port**: 8000 (default)
- **LAN Access**: Enable/disable
- **UPnP**: Enable/disable automatic port forwarding

### Step 4: Feature Selection

**New Features Available**:

- [x] **DVR System** (Digital Video Recorder)
- [x] **Advanced Job Queue** (Media processing)
- [x] **Thin UI** (Lightweight interface)
- [x] **Jellyfin Integration** (Media server)
- [ ] **Home Assistant** (Optional)
- [ ] **Matter Bridge** (Optional)

### Step 5: Initial Setup Complete

- **Review Configuration**: Verify all settings
- **Start Services**: Initialize all components
- **Launch Dashboard**: Enter uHomeNest

## Exploring New Features

### 1. DVR System (Digital Video Recorder)

**What's New**:
- **5 Rule Types**: Time-based, Series, Movie, Keyword, Channel
- **Priority Scheduling**: 1-5 priority levels
- **Conflict Resolution**: Automatic handling of scheduling conflicts
- **Quality Profiles**: SD, HD, 4K recording options

**First Time Setup**:

1. **Navigate to DVR Section**: Click "DVR" in the main menu
2. **Create Your First Rule**:
   - Click "Add Rule"
   - Select rule type (e.g., "Time-Based")
   - Configure schedule and channel
   - Set quality profile (HD recommended)
   - Save rule

3. **Test Recording**:
   ```bash
   # Manually trigger a test recording
   curl -X POST http://localhost:8000/api/dvr/test-recording \
     -H "Content-Type: application/json" \
     -d '{"channel": "test-channel", "duration": 60}'
   ```

### 2. Advanced Job Queue

**What's New**:
- **5 Job Types**: Recording, Post-Processing, Cleanup, Transcoding, Metadata
- **Priority-Based Processing**: Lower numbers = higher priority
- **Worker Pool**: Configurable concurrent workers
- **Job Persistence**: Survives server restarts

**Monitoring Jobs**:

1. **View Job Queue**: Navigate to "System" > "Job Queue"
2. **Check Status**: See active, completed, and failed jobs
3. **Manage Jobs**: Cancel or reprioritize jobs as needed

### 3. Thin UI System

**What's New**:
- **Server-Rendered Prose**: Fast, lightweight documentation viewing
- **Port Configuration**: Default port 8000, fully configurable
- **Embeddable Components**: Easy integration into dashboards
- **Mobile-Optimized**: Responsive design for all devices

**Using Thin UI**:

1. **Access Documentation**:
   ```
   http://localhost:8000/api/runtime/thin/browse?rel=QUICKSTART.md
   ```

2. **View Automation Status**:
   ```
   http://localhost:8000/api/runtime/thin/automation
   ```

3. **Embed in Dashboard**:
   ```html
   <iframe src="/api/runtime/thin/automation" style="width: 100%; height: 400px;"></iframe>
   ```

### 4. Enhanced Jellyfin Integration

**What's New**:
- **Automatic Library Sync**: Real-time synchronization
- **DVR Integration**: Recordings appear in Jellyfin
- **Metadata Enhancement**: Rich metadata for recordings
- **Playback Statistics**: Track viewing habits

**Setup Jellyfin**:

1. **Access Jellyfin**: `http://localhost:8096`
2. **Complete Setup Wizard**: Follow Jellyfin's initial setup
3. **Configure Libraries**: Add your media folders
4. **Enable uHomeNest Plugin**: Install the uHomeNest integration

## Configuring Your Media System

### Media Library Setup

1. **Add Library Folders**:
   - Navigate to "Media" > "Library"
   - Click "Add Folder"
   - Select folder type (Movies, TV Shows, Music, Photos)
   - Browse to folder location
   - Set scan schedule (Daily recommended)

2. **Configure Metadata**:
   - **Scrapers**: TheMovieDB, TVDB, MusicBrainz
   - **Language**: Set preferred metadata language
   - **Artwork**: Enable automatic poster/fanart download
   - **NFO Files**: Enable for Kodi compatibility

### DVR Configuration

1. **EPG Setup**:
   - Navigate to "DVR" > "EPG Sources"
   - Add EPG source (XMLTV recommended)
   - Configure update schedule (Daily at 3 AM)

2. **Tuner Configuration**:
   - Detect available tuners
   - Configure tuner priorities
   - Set maximum concurrent recordings

3. **Recording Profiles**:
   - **SD**: 720x480, 1.5 Mbps
   - **HD**: 1920x1080, 5 Mbps (Default)
   - **4K**: 3840x2160, 15 Mbps

### Automation Setup

1. **Home Assistant Integration** (if enabled):
   - Configure entities
   - Set up automation rules
   - Create dashboards

2. **Scheduled Tasks**:
   - Library scans
   - Metadata updates
   - System maintenance

## Setting Up Your First Recordings

### Creating DVR Rules

#### Time-Based Rule (Simple)

1. **Navigate**: DVR > Add Rule > Time-Based
2. **Configure**:
   - Rule Name: "Morning News"
   - Channel: News HD
   - Start Time: 7:00 AM
   - End Time: 8:00 AM
   - Days: Monday-Friday
   - Quality: HD
   - Priority: 1 (Highest)
3. **Save**: Rule is now active

#### Series Rule (Advanced)

1. **Navigate**: DVR > Add Rule > Series
2. **Configure**:
   - Rule Name: "Favorite Show"
   - Series: Search for your show
   - Seasons: All (or specific seasons)
   - Quality: HD
   - Priority: 2
   - Keep Until: 30 days
   - Avoid Duplicates: Yes
3. **Save**: All episodes will be recorded

### Managing Recordings

1. **View Upcoming**: DVR > Schedule
2. **View Completed**: DVR > Recordings
3. **Play Recording**: Click play or add to playlist
4. **Delete Recording**: Select and confirm deletion
5. **Export Recording**: Download for external use

## Exploring the Dashboard

### Main Dashboard Sections

1. **Media Status**:
   - Current playback sessions
   - Library statistics
   - Recent additions

2. **DVR Status**:
   - Active recordings
   - Upcoming schedule
   - Disk usage

3. **System Health**:
   - CPU/Memory usage
   - Service status
   - Network activity

4. **Quick Actions**:
   - Add media folder
   - Create DVR rule
   - Run library scan
   - Restart services

### Customizing Your Dashboard

1. **Add Widgets**:
   - Click "Customize" > "Add Widget"
   - Choose from available widgets
   - Drag to desired position

2. **Remove Widgets**:
   - Click "Customize" > "Remove"
   - Confirm removal

3. **Rearrange Layout**:
   - Drag and drop widgets
   - Resize as needed
   - Save layout

## Advanced Configuration

### Job Queue Settings

```yaml
# In /etc/uhome/uhome-config.yaml
job_queue:
  max_workers: 4
  persistence: true
  persistence_path: /var/uhome/job_queue.json
  retry_failed: true
  max_retries: 3
  priority_levels: 5
```

### DVR Advanced Settings

```yaml
# In /etc/uhome/uhome-config.yaml
dvr:
  pre_roll: 30s      # Start recording 30s early
  post_roll: 120s    # End recording 2m late
  conflict_strategy: priority  # or 'first-come', 'manual'
  max_concurrent: 4  # Maximum simultaneous recordings
  epg_update: "0 3 * * *"  # Daily at 3 AM
  cleanup_old: 30    # Delete recordings after 30 days
```

### Performance Optimization

```yaml
# In /etc/uhome/uhome-config.yaml
performance:
  transcoding:
    hardware_accel: true
    vaapi_device: /dev/dri/renderD128
    max_concurrent: 2
  
  database:
    connection_pool: 10
    timeout: 30
  
  caching:
    enabled: true
    ttl: 3600
```

## Troubleshooting First Launch

### Common Issues

#### Server Won't Start

**Symptoms**: `systemctl status uhome-server` shows failed

**Solutions**:
```bash
# Check logs
journalctl -u uhome-server -n 50

# Test dependencies
python3 -c "import uhome_server"

# Reinstall
cd /opt/uhome
source venv/bin/activate
pip install -e . --force-reinstall
```

#### Web Interface Not Accessible

**Symptoms**: Browser shows "Connection Refused"

**Solutions**:
```bash
# Check port binding
ss -tulnp | grep 8000

# Test locally
curl http://localhost:8000/api/health

# Check firewall
sudo ufw status
sudo ufw allow 8000/tcp
```

#### DVR Not Working

**Symptoms**: Recordings don't start

**Solutions**:
```bash
# Check DVR service
sudo systemctl status uhome-dvr

# Test tuner
v4l2-ctl --list-devices

# Check permissions
ls -la /media/recordings
sudo chown uhome:uhome /media/recordings
```

#### Jellyfin Integration Failed

**Symptoms**: Media doesn't appear in Jellyfin

**Solutions**:
```bash
# Check Jellyfin status
sudo systemctl status jellyfin

# Test API
curl http://localhost:8096/System/Info

# Check integration
curl http://localhost:8000/api/jellyfin/status
```

## Security Setup

### Changing Default Passwords

```bash
# Change admin password
curl -X POST http://localhost:8000/api/auth/change-password \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"current_password": "old", "new_password": "new-strong-password"}'

# Change database password
sudo -u postgres psql -c "ALTER USER uhome WITH PASSWORD 'new-db-password';"
```

### Enabling SSL

```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx

# Obtain certificate
sudo certbot certonly --standalone -d uhome.example.com

# Configure uHomeNest
sudo nano /etc/uhome/uhome-config.yaml

server:
  ssl: true
  cert_file: /etc/letsencrypt/live/uhome.example.com/fullchain.pem
  key_file: /etc/letsencrypt/live/uhome.example.com/privkey.pem

# Restart service
sudo systemctl restart uhome-server
```

### Firewall Configuration

```bash
# Basic firewall setup
sudo ufw allow 22/tcp       # SSH
sudo ufw allow 80/tcp       # HTTP
sudo ufw allow 443/tcp      # HTTPS
sudo ufw allow 8000/tcp     # uHomeNest API
sudo ufw allow 8096/tcp     # Jellyfin
sudo ufw enable

# Advanced rules
sudo ufw allow from 192.168.1.0/24 to any port 8000
sudo ufw deny from any to any port 8000 proto tcp
```

## Backup and Restore

### First Time Backup

```bash
# Create backup directory
sudo mkdir -p /backups/uhome
sudo chown uhome:uhome /backups/uhome

# Database backup
sudo -u postgres pg_dump uhome > /backups/uhome/uhome-db-$(date +%Y-%m-%d).sql

# Configuration backup
sudo tar -czvf /backups/uhome/uhome-config-$(date +%Y-%m-%d).tar.gz /etc/uhome

# Media backup (optional)
rsync -av --progress /media/recordings /backups/uhome/recordings/
```

### Scheduled Backups

```bash
# Daily database backup
sudo nano /etc/cron.daily/uhome-db-backup

#!/bin/bash
sudo -u postgres pg_dump uhome > /backups/uhome/uhome-db-$(date +%Y-%m-%d).sql
find /backups/uhome -name "uhome-db-*.sql" -mtime +7 -delete

# Weekly config backup
sudo nano /etc/cron.weekly/uhome-config-backup

#!/bin/bash
sudo tar -czvf /backups/uhome/uhome-config-$(date +%Y-%m-%d).tar.gz /etc/uhome
find /backups/uhome -name "uhome-config-*.tar.gz" -mtime +4 -delete
```

## Integrating with Your Home Network

### LAN Configuration

1. **Static IP Setup**:
   ```bash
   sudo nano /etc/netplan/01-netcfg.yaml
   
   network:
     version: 2
     ethernets:
       eth0:
         addresses: [192.168.1.100/24]
         gateway4: 192.168.1.1
         nameservers:
           addresses: [192.168.1.1, 8.8.8.8]
   ```

2. **DNS Configuration**:
   - Add to your router's DNS or hosts file:
   ```
   192.168.1.100 uhome-server.local uhome.local
   ```

### Client Device Setup

#### Android TV
1. Install **Jellyfin for Android TV**
2. Add uHomeNest server: `http://uhome-server:8000`
3. Log in with your credentials
4. Enjoy your media!

#### iOS Devices
1. Install **Jellyfin Mobile** from App Store
2. Add server: `http://uhome-server.local:8000`
3. Configure playback settings
4. Access your media library

#### Web Browsers
1. Navigate to `http://uhome-server:8000`
2. Bookmark for easy access
3. Use thin UI for lightweight access

## Example Workflows

### Recording Your Favorite Show

1. **Find Show**: Browse EPG or search
2. **Create Rule**: Set up series recording
3. **Watch Later**: Access from "Recordings" section
4. **Manage**: Delete or keep permanently

### Setting Up Family Profiles

1. **Create Users**: Settings > Users > Add User
2. **Set Permissions**: Configure access levels
3. **Parental Controls**: Set content restrictions
4. **Personalize**: Customize dashboards per user

### Automating Media Management

1. **Library Scan**: Schedule daily scans
2. **Metadata Update**: Weekly metadata refresh
3. **Cleanup**: Automatic deletion of old recordings
4. **Notifications**: Email alerts for new content

## Getting Help

### Built-in Resources

- **Documentation**: `http://uhome-server:8000/docs`
- **API Reference**: `http://uhome-server:8000/api/docs`
- **Status Page**: `http://uhome-server:8000/status`

### Community Support

- **GitHub Issues**: https://github.com/fredporter/uHomeNest/issues
- **Discussions**: https://github.com/fredporter/uHomeNest/discussions
- **Matrix Chat**: #uhome:matrix.org

### Professional Support

- **Consulting**: Available for complex setups
- **Training**: Customized training sessions
- **Enterprise**: Commercial support packages

## Next Steps

Now that you've completed the first time launch:

1. ✅ **Explore the Dashboard**: Familiarize yourself with all sections
2. ✅ **Set Up Media Library**: Add your movies, shows, and music
3. ✅ **Configure DVR Rules**: Schedule your favorite programs
4. ✅ **Test Playback**: Verify everything works on your devices
5. ✅ **Set Up Backups**: Configure automatic backups
6. ✅ **Customize**: Personalize your uHomeNest experience

## Advanced Topics

### Customizing the Thin UI

```html
<!-- Custom thin UI template -->
<div class="custom-thin-ui">
    <header class="bg-blue-600 text-white p-4">
        <h1 class="text-2xl font-bold">My uHomeNest</h1>
    </header>
    <main class="p-4">
        <iframe src="/api/runtime/thin/automation" class="w-full h-screen"></iframe>
    </main>
</div>
```

### Creating Custom DVR Rules

```python
# Custom rule example
from uhome_server.services.dvr import create_custom_rule

def my_custom_rule():
    rule = create_custom_rule(
        name="Weekend Movies",
        rule_type="keyword",
        keywords=["movie", "film", "cinema"],
        time_ranges=[
            {"start": "18:00", "end": "23:59"},
            {"start": "00:00", "end": "02:00"}
        ],
        days=["sat", "sun"],
        quality="hd",
        priority=2
    )
    return rule
```

### Extending with Plugins

```yaml
# Plugin configuration
plugins:
  - name: weather-integration
    enabled: true
    config:
      api_key: "your-weather-api-key"
      location: "San Francisco, CA"
      update_interval: 60
  
  - name: news-aggregator
    enabled: true
    config:
      sources: ["bbc", "reuters", "ap"]
      categories: ["technology", "science"]
```

## Conclusion

Congratulations! You've successfully completed the first time launch of uHomeNest. This guide has walked you through:

- **Initial setup** and configuration
- **Exploring new features** like DVR and job queue
- **Configuring your media system**
- **Setting up recordings** and automation
- **Security and backup** best practices
- **Integrating with your network**

Your uHomeNest system is now ready to serve as the central hub for your household media and automation needs. As you become more familiar with the system, explore the advanced features and customization options to tailor uHomeNest to your specific requirements.

**Remember**:
- Check for updates regularly
- Review the [documentation](docs/README.md) for advanced features
- Join the [community](https://github.com/fredporter/uHomeNest/discussions) for tips and support
- Provide [feedback](https://github.com/fredporter/uHomeNest/issues) to help improve uHomeNest

Enjoy your new household media system! 🎬🎵📺

**Next Steps**:
1. [Explore the DVR System](architecture/media/DVR-DESIGN.md)
2. [Learn About Job Queue](src/uhome_server/services/job_queue.py)
3. [Set Up Home Automation](docs/architecture/AUTOMATION-GUIDE.md)
4. [Configure Advanced Features](docs/ADVANCED-CONFIGURATION.md)