---
title: "uHomeNest Deployment Guide"
status: draft
last_updated: 2026-05-26T19:20:27+10:00
category: guide
tags: [deployment, homenest, ucode3, uhome]
description: "Comprehensive deployment guide for uHomeNest v1.0.1, covering installation, configuration, and management of the home..."
---
# uHomeNest Deployment Guide

## 🚀 Overview

Comprehensive deployment guide for uHomeNest v1.0.1, covering installation, configuration, and management of the home stream server with Jellyfin orchestration.

## 📋 Prerequisites

### System Requirements
- **Operating System**: Ubuntu 22.04 LTS or 24.04 LTS
- **CPU**: 4 cores minimum (8+ recommended for transcoding)
- **RAM**: 8GB minimum (16GB+ recommended)
- **Storage**: 50GB+ for system, additional for media vault
- **Network**: Gigabit Ethernet recommended

### Software Dependencies
- Docker 20.10+
- Docker Compose v2+
- Node.js 18+
- Python 3.10+
- FFmpeg 4.4+
- Git

### Installation

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y docker.io docker-compose nodejs python3 ffmpeg git

# Add user to docker group
sudo usermod -aG docker $USER
newgrp docker

# Verify installation
docker --version
docker-compose --version
node --version
python3 --version
ffmpeg -version
```

## 📦 Installation Methods

### Method 1: Automatic Installation

```bash
# Clone repository
git clone https://github.com/fredporter/uHomeNest.git
cd uHomeNest

# Run installation script
./scripts/install.sh

# Start services
./scripts/start.sh
```

### Method 2: Manual Installation

```bash
# Clone repository
git clone https://github.com/fredporter/uHomeNest.git
cd uHomeNest

# Install Node.js dependencies
npm install

# Build UI assets
npm run build

# Setup Docker network
docker network create uhomenest-network

# Start Jellyfin
docker-compose -f docker/jellyfin.yml up -d

# Start API server
npm run start:api

# Start UI server
npm run start:ui
```

### Method 3: Docker Compose (Recommended)

```bash
# Clone repository
git clone https://github.com/fredporter/uHomeNest.git
cd uHomeNest

# Start all services
docker-compose up -d

# Verify services
docker-compose ps
```

## 🎛️ Configuration

### Environment Variables

Create `.env` file in project root:

```env
# Server Configuration
PORT=7890
HOST=0.0.0.0
ENVIRONMENT=production

# Jellyfin Configuration
JELLYFIN_HOST=jellyfin
JELLYFIN_PORT=8096
JELLYFIN_API_KEY=your-api-key

# Media Vault
MEDIA_VAULT_PATH=/home/user/media
MEDIA_SCAN_INTERVAL=3600

# Database
DB_HOST=localhost
DB_PORT=5432
DB_NAME=uhomenest
DB_USER=uhomenest
DB_PASSWORD=secure-password

# Home Assistant
HA_URL=http://homeassistant:8123
HA_TOKEN=your-long-lived-token
```

### Configuration Files

#### `config/server.json`

```json
{
  "port": 7890,
  "host": "0.0.0.0",
  "environment": "production",
  "logLevel": "info",
  "maxUploadSize": "50mb",
  "rateLimit": {
    "windowMs": 15 * 60 * 1000,
    "max": 100
  },
  "jellyfin": {
    "host": "jellyfin",
    "port": 8096,
    "apiKey": "your-api-key",
    "timeout": 30000
  },
  "mediaVault": {
    "path": "/home/user/media",
    "scanInterval": 3600,
    "supportedTypes": ["mp4", "mkv", "avi", "mp3", "flac"]
  }
}
```

#### `config/ui.json`

```json
{
  "theme": "dark",
  "defaultView": "launcher",
  "kioskMode": false,
  "refreshRate": 60,
  "usxd": {
    "launcher": "ui/usxd/launcher.json",
    "mediaBrowser": "ui/usxd/media-browser.json",
    "nowPlaying": "ui/usxd/now-playing.json"
  }
}
```

## 🚀 Starting Services

### Start All Services

```bash
# Using start script
./scripts/start.sh

# Manual start
docker-compose up -d
npm run start:api
npm run start:ui
```

### Start Individual Components

```bash
# Start Jellyfin
docker-compose -f docker/jellyfin.yml up -d

# Start API server
npm run start:api

# Start UI server
npm run start:ui

# Start media scanner
npm run start:scanner
```

## 🔍 Health Checks

### Service Health

```bash
# Check all services
./scripts/healthcheck.sh

# Check specific service
curl -sS http://localhost:7890/api/health

# Expected response
{"status":"ok","services":{"api":"healthy","ui":"healthy","jellyfin":"healthy","scanner":"healthy"}}
```

### Container Health

```bash
# Check Docker containers
docker ps

# Check container logs
docker logs uhomenest-api
docker logs uhomenest-ui
docker logs jellyfin

# Check resource usage
docker stats
```

## 📊 Monitoring

### Logs

```bash
# API server logs
journalctl -u uhomenest-api -f

# UI server logs
journalctl -u uhomenest-ui -f

# Jellyfin logs
docker logs jellyfin -f

# Media scanner logs
journalctl -u uhomenest-scanner -f
```

### Metrics

```bash
# System metrics
htop
vmstat 1
iostat -x 1

# Docker metrics
docker stats --no-stream

# API metrics
curl http://localhost:7890/api/metrics
```

## 🔄 Updates

### Update uHomeNest

```bash
# Pull latest changes
cd uHomeNest
git pull origin main

# Update dependencies
npm install

# Rebuild UI
npm run build

# Restart services
./scripts/restart.sh
```

### Update Jellyfin

```bash
# Pull latest Jellyfin image
docker-compose -f docker/jellyfin.yml pull

# Recreate container
docker-compose -f docker/jellyfin.yml up -d --force-recreate
```

## ⚠️ Troubleshooting

### Common Issues

**Port Conflict**
```bash
# Check port usage
sudo netstat -tulnp | grep 7890

# Kill conflicting process
sudo kill -9 <PID>

# Restart service
./scripts/restart.sh
```

**Permission Issues**
```bash
# Check media vault permissions
ls -la ~/media

# Fix permissions
chmod -R 755 ~/media
chown -R $USER:$USER ~/media

# Restart services
./scripts/restart.sh
```

**Jellyfin Connection**
```bash
# Check Jellyfin status
curl http://localhost:8096/health

# Restart Jellyfin
docker restart jellyfin

# Check logs
docker logs jellyfin
```

**Database Issues**
```bash
# Check database connection
psql -h localhost -U uhomenest -d uhomenest

# Reset database
npm run db:reset

# Re-run migrations
npm run db:migrate
```

## 🛡️ Security

### Security Best Practices

```bash
# Change default passwords
./scripts/change-passwords.sh

# Enable firewall
sudo ufw enable
sudo ufw allow 7890
sudo ufw allow 8096

# Setup SSL
sudo apt install certbot
sudo certbot certonly --standalone -d yourdomain.com

# Configure HTTPS
./scripts/configure-https.sh
```

### Backup

```bash
# Backup configuration
./scripts/backup-config.sh

# Backup database
./scripts/backup-db.sh

# Backup media metadata
./scripts/backup-media.sh

# Full backup
./scripts/backup-full.sh
```

### Restore

```bash
# Restore configuration
./scripts/restore-config.sh <backup-file>

# Restore database
./scripts/restore-db.sh <backup-file>

# Restore media metadata
./scripts/restore-media.sh <backup-file>

# Full restore
./scripts/restore-full.sh <backup-file>
```

## 📈 Performance Optimization

### Jellyfin Optimization

```bash
# Configure transcoding
# Edit: config/jellyfin/transcoding.json

# Hardware acceleration
sudo apt install intel-media-va-driver-non-free
sudo usermod -aG video,render $USER

# Restart Jellyfin
docker restart jellyfin
```

### Media Scanning

```bash
# Optimize scan schedule
# Edit: config/scanner.json

# Manual scan
npm run scan:media

# Force re-index
npm run scan:media -- --force
```

### Caching

```bash
# Configure cache
# Edit: config/cache.json

# Clear cache
npm run cache:clear

# Warm cache
npm run cache:warm
```

## 🔧 Maintenance

### Regular Tasks

```bash
# Daily
./scripts/daily-maintenance.sh

# Weekly
./scripts/weekly-maintenance.sh

# Monthly
./scripts/monthly-maintenance.sh
```

### Cleanup

```bash
# Clear logs
./scripts/clear-logs.sh

# Clean temporary files
./scripts/clean-temp.sh

# Optimize database
./scripts/optimize-db.sh
```

## 📚 Advanced Configuration

### Custom USXD Layouts

```bash
# Create custom layout
cp ui/usxd/launcher.json ui/usxd/custom.json

# Edit layout
nano ui/usxd/custom.json

# Apply layout
./scripts/apply-layout.sh custom
```

### API Extensions

```bash
# Create custom endpoint
# Add to: server/routes/custom.js

# Register route
# Add to: server/routes/index.js

# Restart API
npm run restart:api
```

### Plugin System

```bash
# Install plugin
npm run plugin:install <plugin-name>

# Configure plugin
nano config/plugins/<plugin-name>.json

# Enable plugin
npm run plugin:enable <plugin-name>

# Restart services
./scripts/restart.sh
```

## 🌐 Network Configuration

### Local Network

```bash
# Configure static IP
sudo nano /etc/netplan/01-netcfg.yaml

# Apply changes
sudo netplan apply

# Restart networking
sudo systemctl restart networking
```

### Remote Access

```bash
# Configure remote access
./scripts/configure-remote.sh

# Setup port forwarding
# Router-specific configuration

# Test remote access
curl http://your-public-ip:7890/api/health
```

### VPN Setup

```bash
# Install WireGuard
sudo apt install wireguard

# Configure VPN
./scripts/configure-vpn.sh

# Start VPN
sudo wg-quick up wg0
```

## 📱 Mobile Access

### iOS Setup

```bash
# Install companion app
# App Store: uHomeNest Companion

# Configure connection
# Enter server IP and credentials

# Test connection
# Should show home dashboard
```

### Android Setup

```bash
# Install companion app
# Play Store: uHomeNest Companion

# Configure connection
# Enter server IP and credentials

# Test connection
# Should show home dashboard
```

## 🎮 Controller Setup

### USXD Controller

```bash
# Pair controller
./scripts/pair-controller.sh

# Configure bindings
nano config/controller.json

# Test controller
npm run test:controller
```

### Gamepad Support

```bash
# Install drivers
sudo apt install xboxdrv

# Configure gamepad
./scripts/configure-gamepad.sh

# Test gamepad
jstest /dev/input/js0
```

## 📺 Display Configuration

### Kiosk Mode

```bash
# Enable kiosk mode
./scripts/enable-kiosk.sh

# Configure auto-start
sudo nano /etc/xdg/autostart/uhomenest.desktop

# Test kiosk mode
startx
```

### Multi-Display

```bash
# Configure displays
sudo nvidia-settings
# or
sudo arandr

# Save configuration
xrandr --output HDMI-1 --mode 1920x1080 --right-of eDP-1

# Make persistent
nano ~/.config/autostart/display.sh
```

## 🔊 Audio Configuration

### Audio Output

```bash
# List audio devices
aplay -l

# Set default device
# Edit: /etc/asound.conf

# Test audio
speaker-test -c 2
```

### Multi-Zone Audio

```bash
# Configure zones
nano config/audio.json

# Start audio service
npm run start:audio

# Test zones
npm run test:audio
```

## 📊 Usage Examples

### Basic Usage

```bash
# Start system
./scripts/start.sh

# Check status
./scripts/status.sh

# Play media
curl -X POST http://localhost:7890/api/playback/start -d '{"itemId":"123"}'

# Stop playback
curl -X POST http://localhost:7890/api/playback/stop
```

### Advanced Usage

```bash
# Custom API call
curl -X POST http://localhost:7890/api/custom -d '{"action":"scan","path":"/media/movies"}'

# Scheduled task
./scripts/schedule-task.sh "scan-media" "0 3 * * *"

# Backup before update
./scripts/backup-before-update.sh
```

## 📈 Deployment Checklist

### Pre-Deployment
- [ ] Review system requirements
- [ ] Install all dependencies
- [ ] Configure firewall
- [ ] Setup backup system
- [ ] Test network connectivity

### Deployment
- [ ] Clone repository
- [ ] Configure environment
- [ ] Run installation script
- [ ] Start services
- [ ] Verify health checks

### Post-Deployment
- [ ] Test all features
- [ ] Configure backups
- [ ] Setup monitoring
- [ ] Document configuration
- [ ] Train users

## 🔮 Future Enhancements

### Planned Features
- Advanced automation rules
- Voice control integration
- Multi-room audio sync
- Cloud backup integration
- Mobile app improvements

### Architecture Improvements
- Microservices migration
- Enhanced API layer
- Better plugin system
- Improved performance

---

*Last Updated: 2026-04-29*
*uHomeNest v1.0.1*
*Deployment Guide: Comprehensive*