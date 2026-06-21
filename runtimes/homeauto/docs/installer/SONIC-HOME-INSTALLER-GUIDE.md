---
title: "Sonic-Home Installer Guide for uHomeNest"
status: draft
last_updated: 2026-04-22T23:26:13+10:00
category: guide
tags: [cli, guide, sonic, ucode3]
description: "This guide provides comprehensive instructions for using the Sonic-Home installer to set up uHomeNest on your househo..."
---
# Sonic-Home Installer Guide for uHomeNest

**Version**: 1.0
**Date**: 2024-04-17
**Status**: Active

This guide provides comprehensive instructions for using the Sonic-Home installer to set up uHomeNest on your household media server.

## Overview

Sonic-Home is a specialized installer built on the `sonic-screwdriver` framework, designed to simplify the installation and configuration of uHomeNest for household media and automation purposes.

## Prerequisites

### Hardware Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| **CPU** | 2 cores @ 2.0GHz | 4+ cores @ 2.5GHz+ |
| **RAM** | 4GB | 8GB+ |
| **Storage** | 64GB SSD | 256GB+ SSD (500GB+ for media) |
| **Network** | 100Mbps Ethernet | Gigabit Ethernet |
| **GPU** | Integrated | Dedicated (for transcoding) |

### Supported Operating Systems

- **Ubuntu** 22.04 LTS (Recommended)
- **Debian** 11+ 
- **Fedora** 36+
- **CentOS** 8+

### Required Tools

- USB flash drive (8GB+)
- Ventoy (for multi-boot USB)
- Internet connection

## Installation Methods

### Method 1: Ventoy USB (Recommended)

#### Step 1: Prepare Ventoy USB

1. **Download Ventoy**:
   ```bash
   wget https://github.com/ventoy/Ventoy/releases/download/v1.0.96/ventoy-1.0.96-linux.tar.gz
   ```

2. **Install Ventoy**:
   ```bash
   tar -xvf ventoy-1.0.96-linux.tar.gz
   cd ventoy-1.0.96
   sudo ./Ventoy2Disk.sh -i /dev/sdX
   ```
   *Replace `/dev/sdX` with your USB device (e.g., `/dev/sdb`)*

#### Step 2: Add Sonic-Home Installer

1. **Download Sonic-Home ISO**:
   ```bash
   wget https://github.com/fredporter/sonic-screwdriver/releases/download/v3.2.1/sonic-home-v3.2.1.iso
   ```

2. **Copy to Ventoy USB**:
   ```bash
   cp sonic-home-v3.2.1.iso /path/to/ventoy-usb/
   ```

#### Step 3: Boot and Install

1. **Boot from USB**: Restart computer and select Ventoy USB
2. **Select Sonic-Home**: Choose the Sonic-Home ISO from Ventoy menu
3. **Follow installer**: Complete the graphical installation process

### Method 2: Direct ISO Installation

#### Step 1: Create Bootable USB

```bash
# On Linux
sudo dd if=sonic-home-v3.2.1.iso of=/dev/sdX bs=4M status=progress

# On macOS
sudo dd if=sonic-home-v3.2.1.iso of=/dev/rdiskX bs=1m
```

#### Step 2: Boot and Install

1. Boot from the USB drive
2. Select "Install Sonic-Home"
3. Follow the on-screen instructions

### Method 3: Network Installation (Advanced)

```bash
# Boot into live environment
wget https://github.com/fredporter/sonic-screwdriver/releases/download/v3.2.1/sonic-home-netboot.tar.gz

# Extract and run installer
tar -xzvf sonic-home-netboot.tar.gz
cd sonic-home
sudo ./install.sh
```

## Installation Process

### Step-by-Step Guide

#### 1. Language and Region

- Select your preferred language
- Choose time zone
- Configure keyboard layout

#### 2. Disk Partitioning

**Recommended Partition Scheme**:

| Mount Point | Size | Filesystem | Purpose |
|-------------|------|------------|---------|
| `/` | 50GB | ext4 | Root filesystem |
| `/home` | 100GB | ext4 | User home directories |
| `/var` | 200GB+ | ext4 | Media storage, logs |
| `swap` | RAM × 2 | swap | System swap |
| `/media` | Remaining | ext4 | Media library |

#### 3. User Setup

- Create admin user (e.g., `uhome-admin`)
- Set strong password
- Configure sudo access

#### 4. Network Configuration

- Set hostname (e.g., `uhome-server`)
- Configure static IP (recommended for servers)
- Set DNS servers (use local or public DNS)

#### 5. Package Selection

**Required Packages**:
- [x] uHomeNest Core
- [x] Jellyfin Media Server
- [x] FFmpeg (with hardware acceleration)
- [x] Python 3.11+
- [x] PostgreSQL 15+
- [ ] Home Assistant (optional)
- [ ] Matter Bridge (optional)

#### 6. Advanced Configuration

**DVR Settings**:
- Enable DVR service: `YES`
- Recording storage: `/media/recordings`
- Max concurrent recordings: `4`
- Quality profile: `HD (1080p)`

**Media Settings**:
- Library paths: `/media/library`
- Metadata storage: `/var/uhome/metadata`
- Transcoding cache: `/var/uhome/transcode`

#### 7. Installation

- Review configuration
- Confirm installation
- Wait for completion (~15-30 minutes)

## Post-Installation Setup

### First Boot Configuration

```bash
# Log in as admin user
ssh uhome-admin@uhome-server

# Update system
sudo apt update && sudo apt upgrade -y

# Start uHomeNest services
sudo systemctl start uhome-server
sudo systemctl enable uhome-server

# Check status
sudo systemctl status uhome-server
```

### Network Configuration

```bash
# Set static IP (example)
sudo nano /etc/netplan/01-netcfg.yaml

network:
  version: 2
  renderer: networkd
  ethernets:
    eth0:
      dhcp4: no
      addresses: [192.168.1.100/24]
      gateway4: 192.168.1.1
      nameservers:
        addresses: [8.8.8.8, 8.8.4.4]

# Apply network changes
sudo netplan apply
```

### Firewall Setup

```bash
# Install and configure UFW
sudo apt install ufw
sudo ufw allow 22/tcp       # SSH
sudo ufw allow 8096/tcp     # Jellyfin
sudo ufw allow 8000/tcp     # uHomeNest API
sudo ufw allow 8080/tcp     # uHomeNest Web
sudo ufw enable
```

## Configuration Files

### Main Configuration

**Location**: `/etc/uhome/uhome-config.yaml`

```yaml
# Server Configuration
server:
  host: 0.0.0.0
  port: 8000
  debug: false
  workers: 4

# Media Configuration
media:
  library_path: /media/library
  recordings_path: /media/recordings
  transcoding_path: /var/uhome/transcode
  max_concurrent_recordings: 4
  quality_profiles:
    sd: {width: 720, height: 480, bitrate: 1500}
    hd: {width: 1920, height: 1080, bitrate: 5000}
    uhd: {width: 3840, height: 2160, bitrate: 15000}

# DVR Configuration
dvr:
  enabled: true
  epg_update_interval: 24h
  pre_roll: 30s
  post_roll: 120s
  conflict_resolution: priority

# Jellyfin Integration
jellyfin:
  url: http://localhost:8096
  api_key: "your-api-key-here"
  username: "uhome-admin"
  password: "secure-password"

# Database Configuration
database:
  host: localhost
  port: 5432
  name: uhome
  user: uhome
  password: "db-password"
```

### Service Configuration

**Systemd Service**: `/etc/systemd/system/uhome-server.service`

```ini
[Unit]
Description=uHomeNest Server
After=network.target postgresql.service

[Service]
User=uhome
Group=uhome
WorkingDirectory=/opt/uhome
Environment="PATH=/opt/uhome/venv/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
ExecStart=/opt/uhome/venv/bin/python -m uvicorn uhome_server.app:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

## First Time Launch

### Starting Services

```bash
# Start all uHomeNest services
sudo systemctl start uhome-server
sudo systemctl start jellyfin
sudo systemctl start postgresql

# Enable auto-start
sudo systemctl enable uhome-server
sudo systemctl enable jellyfin
sudo systemctl enable postgresql
```

### Initial Setup Wizard

1. **Access Web Interface**: `http://uhome-server:8000`
2. **Complete Setup Wizard**:
   - Set admin password
   - Configure media library paths
   - Set up DVR rules
   - Configure automation preferences

3. **Test Connections**:
   ```bash
   # Test API
   curl http://localhost:8000/api/health
   
   # Test Jellyfin
   curl http://localhost:8096/System/Info
   
   # Test DVR status
   curl http://localhost:8000/api/dvr/status
   ```

### Creating First DVR Rule

```bash
# Create a time-based recording rule
curl -X POST http://localhost:8000/api/dvr/rules \
  -H "Content-Type: application/json" \
  -d '{
    "rule_name": "Nightly News",
    "rule_type": "time-based",
    "channel_id": "news-hd",
    "start_time": "2024-04-18T18:30:00",
    "end_time": "2024-04-18T19:00:00",
    "quality_profile": "hd",
    "priority": 1
  }'
```

## Troubleshooting

### Common Issues

#### Installation Fails

**Symptoms**: Installer hangs or crashes

**Solutions**:
1. Check USB integrity: `badblocks -v /dev/sdX`
2. Verify ISO checksum
3. Try different USB port
4. Use different installation method

#### Services Won't Start

**Symptoms**: `systemctl status` shows failed services

**Solutions**:
```bash
# Check logs
journalctl -u uhome-server -f

# Test dependencies
python3 --version
psql --version
ffmpeg -version

# Reinstall dependencies
sudo apt install --reinstall python3-pip postgresql ffmpeg
```

#### Network Connectivity Issues

**Symptoms**: Can't access web interface

**Solutions**:
```bash
# Check firewall
sudo ufw status

# Test network
ping uhome-server
nc -zv uhome-server 8000

# Check service binding
ss -tulnp | grep 8000
```

#### DVR Not Recording

**Symptoms**: Scheduled recordings don't start

**Solutions**:
```bash
# Check DVR service
sudo systemctl status uhome-dvr

# Test tuner
v4l2-ctl --list-devices

# Check disk space
df -h /media/recordings

# Review logs
tail -f /var/log/uhome/dvr.log
```

## Upgrading uHomeNest

### Minor Version Upgrade

```bash
# Stop services
sudo systemctl stop uhome-server

# Update code
cd /opt/uhome
git pull origin main

# Update dependencies
source venv/bin/activate
pip install -r requirements.txt

# Restart services
sudo systemctl start uhome-server
```

### Major Version Upgrade

```bash
# Backup configuration
sudo cp /etc/uhome/uhome-config.yaml /etc/uhome/uhome-config.yaml.bak
sudo pg_dump uhome > uhome-db-backup.sql

# Download new installer
wget https://github.com/fredporter/sonic-screwdriver/releases/latest/download/sonic-home-latest.iso

# Reinstall using Ventoy
# (Follow installation steps above)

# Restore configuration
sudo cp /etc/uhome/uhome-config.yaml.bak /etc/uhome/uhome-config.yaml
sudo psql uhome < uhome-db-backup.sql
```

## Backup and Restore

### Backup Procedure

```bash
# Database backup
sudo pg_dump uhome > /backups/uhome-db-$(date +%Y-%m-%d).sql

# Configuration backup
sudo tar -czvf /backups/uhome-config-$(date +%Y-%m-%d).tar.gz /etc/uhome

# Media backup (optional)
rsync -av /media/recordings /backups/recordings/
```

### Restore Procedure

```bash
# Restore database
sudo psql uhome < /backups/uhome-db-latest.sql

# Restore configuration
sudo tar -xzvf /backups/uhome-config-latest.tar.gz -C /

# Restore media
rsync -av /backups/recordings/ /media/recordings/

# Restart services
sudo systemctl restart uhome-server
```

## Security Hardening

### User Management

```bash
# Create dedicated service user
sudo adduser --system --group uhome

# Set proper permissions
sudo chown -R uhome:uhome /opt/uhome
sudo chown -R uhome:uhome /media/recordings
sudo chmod 750 /etc/uhome
```

### SSL Configuration

```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d uhome.example.com

# Configure uHomeNest for SSL
sudo nano /etc/uhome/uhome-config.yaml

server:
  ssl: true
  cert_file: /etc/letsencrypt/live/uhome.example.com/fullchain.pem
  key_file: /etc/letsencrypt/live/uhome.example.com/privkey.pem
```

### Automatic Updates

```bash
# Set up automatic security updates
sudo apt install unattended-upgrades
sudo dpkg-reconfigure unattended-upgrades

# Configure automatic uHomeNest updates
sudo nano /etc/cron.weekly/uhome-update

#!/bin/bash
cd /opt/uhome
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart uhome-server
```

## Performance Optimization

### Hardware Acceleration

```bash
# Install VA-API for Intel GPUs
sudo apt install i965-va-driver libva-drm2 libva-x11-2

# Install VDPAU for NVIDIA
sudo apt install nvidia-driver libvdpau1

# Test hardware acceleration
vainfo
vdpauinfo
```

### Transcoding Optimization

```yaml
# In uhome-config.yaml
transcoding:
  hardware_acceleration: true
  vaapi_device: /dev/dri/renderD128
  max_concurrent: 4
  presets:
    fast: {crf: 23, preset: veryfast}
    balanced: {crf: 20, preset: fast}
    quality: {crf: 18, preset: medium}
```

### Database Optimization

```sql
-- Optimize PostgreSQL for uHomeNest
ALTER SYSTEM SET shared_buffers = '2GB';
ALTER SYSTEM SET effective_cache_size = '4GB';
ALTER SYSTEM SET maintenance_work_mem = '512MB';
ALTER SYSTEM SET work_mem = '16MB';
ALTER SYSTEM SET random_page_cost = 1.1;

-- Create indexes for DVR tables
CREATE INDEX idx_recordings_start_time ON recordings(start_time);
CREATE INDEX idx_job_queue_priority ON job_queue(priority);
```

## Monitoring and Maintenance

### System Monitoring

```bash
# Install monitoring tools
sudo apt install htop iotop iftop nmon

# Check system resources
htop

# Monitor disk I/O
iotop -o

# Monitor network
iftop -i eth0
```

### Log Management

```bash
# View uHomeNest logs
journalctl -u uhome-server -f

# Rotate logs
sudo logrotate /etc/logrotate.d/uhome

# Log configuration
sudo nano /etc/logrotate.d/uhome

/var/log/uhome/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    create 640 uhome uhome
}
```

### Scheduled Maintenance

```bash
# Cleanup old recordings
sudo nano /etc/cron.daily/uhome-cleanup

#!/bin/bash
find /media/recordings -type f -mtime +30 -delete
/opt/uhome/venv/bin/python -m uhome_server.cli cleanup --days 30

# Database maintenance
sudo nano /etc/cron.weekly/uhome-db-maintenance

#!/bin/bash
sudo -u postgres vacuumdb --analyze uhome
sudo -u postgres reindex database uhome
```

## Integration with Home Automation

### Home Assistant Configuration

```yaml
# configuration.yaml
media_player:
  - platform: jellyfin
    host: localhost
    port: 8096
    ssl: false

sensor:
  - platform: rest
    name: uHome DVR Status
    resource: http://localhost:8000/api/dvr/status
    value_template: "{{ value_json.active_recordings }}"
    scan_interval: 60

automation:
  - alias: "Notify when recording starts"
    trigger:
      platform: state
      entity_id: sensor.uhome_dvr_status
    action:
      service: notify.mobile_app
      data:
        message: "DVR recording started"
```

### Matter Bridge Configuration

```yaml
# matter-config.yaml
devices:
  - type: media_player
    name: Living Room TV
    uhome_entity: media_player.living_room
    matter_device_type: television
    features:
      - power
      - volume
      - playback_control
      - input_selection
```

## Uninstallation

### Clean Removal

```bash
# Stop services
sudo systemctl stop uhome-server jellyfin postgresql

# Remove packages
sudo apt remove uhome-server jellyfin postgresql

# Remove configuration
sudo rm -rf /etc/uhome /opt/uhome /var/uhome

# Remove data (optional)
sudo rm -rf /media/recordings /media/library

# Remove users
sudo deluser uhome
sudo delgroup uhome
```

## Support Resources

### Documentation

- [uHomeNest Official Docs](https://github.com/fredporter/uHomeNest/docs)
- [Jellyfin Documentation](https://jellyfin.org/docs)
- [Sonic-Screwdriver Docs](https://github.com/fredporter/sonic-screwdriver)

### Community

- GitHub Issues: https://github.com/fredporter/uHomeNest/issues
- Discussion Forum: https://github.com/fredporter/uHomeNest/discussions
- Matrix Chat: #uhome:matrix.org

### Troubleshooting Guides

- [Common Installation Issues](docs/TROUBLESHOOTING.md)
- [DVR Troubleshooting](docs/architecture/media/DVR-TROUBLESHOOTING.md)
- [Network Configuration](docs/NETWORK-GUIDE.md)

## Conclusion

This guide provides comprehensive instructions for installing, configuring, and maintaining uHomeNest using the Sonic-Home installer. The installation process is designed to be straightforward while providing flexibility for advanced configurations.

**Next Steps**:
1. Prepare installation media using Ventoy
2. Follow the step-by-step installation guide
3. Complete post-installation setup
4. Configure DVR rules and media library
5. Set up monitoring and maintenance

For additional help, refer to the [official documentation](https://github.com/fredporter/uHomeNest/docs) or the [community support resources](#support-resources).