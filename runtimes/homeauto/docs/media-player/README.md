---
title: "uHome Media Player — Universal Local Media Hub"
status: draft
last_updated: 2026-05-20T22:32:12+10:00
category: readme
tags: [ucode3]
description: "**Document ID:** UDN-MEDIA-001"
---
# uHome Media Player — Universal Local Media Hub

**Document ID:** UDN-MEDIA-001  
**Status:** Active  
**Version:** 1.0.0  
**Date:** 2026-04-21  
**Priority:** HIGH  
**Related:** [uHomeNest v1.0.0 Dev Brief](./UHOMENEST-V1-DEV-BRIEF.md), [HA Deep Integration](./UDN-HA-EMBED-001.md), [Matter+HA Integration](./UDN-INTEGRATION-001.md)

***

## Executive Summary

uHome Media Player is a **subscription-free, local-first media hub** combining multiple open-source engines into a single controller-friendly interface. Rather than choosing one engine, uHome **embeds them all** and provides a **unified catalog, universal TV guide, and manual metadata confirmation system** — giving users the "iTunes store browsing experience" without the store, and full ownership of their content.

**Core Principle:** You own the media. You confirm what you own. The system enhances it with metadata from public sources. No automated matching without consent.

***

## Media Engine Selection

### Chosen Engines

| Engine       | Role                                    | Why Chosen                                                              |
| ------------ | --------------------------------------- | ----------------------------------------------------------------------- |
| **Jellyfin** | Primary media server & transcoding      | Mature, open-source, no subscriptions, hardware transcoding, multi-user |
| **Kodi**     | Direct playback & advanced UI rendering | Best-in-class codec support, skinning engine, works offline             |
| **mpv**      | Lightweight playback engine             | Ultra-fast, minimal resources, excellent format support                 |
| **yt-dlp**   | YouTube/streaming extraction            | Downloads/streams from 1000+ sites, replaces "apps"                     |
| **FFmpeg**   | Transcoding & format conversion         | Industry standard, handles anything                                     |

### Why Not Just One?

| Use Case                     | Best Engine                   |
| ---------------------------- | ----------------------------- |
| 4K HDR movie with Atmos      | Kodi (direct play)            |
| Remote streaming to tablet   | Jellyfin (transcode)          |
| Old SD video on Raspberry Pi | mpv (lightweight)             |
| YouTube playlist             | yt-dlp + mpv                  |
| Music library                | Jellyfin (with Finamp client) |

**Strategy:** uHome provides a **playback router** — automatically selects the best engine for the content and target device.

***

## Unified Media Catalog

### Architecture

````
┌─────────────────────────────────────────────────────────────────────┐
│                    uHome Media Catalog                              │
│                    (SQLite + JSON)                                  │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                 │
│  │ ~/media/    │  │ Jellyfin    │  │ User Added  │                 │
│  │ Vault       │──│ Library     │──│ Manual      │                 │
│  │ Scanner     │  │ API         │  │ Entries     │                 │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘                 │
│         │                │                │                         │
│         └────────────────┼────────────────┘                         │
│                          ▼                                          │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │                    Unified Catalog                            │  │
│  │  ┌─────────────────────────────────────────────────────────┐  │  │
│  │  │ Movies | TV Shows | Music | YouTube | Live TV | Games   │  │  │
│  │  └─────────────────────────────────────────────────────────┘  │  │
│  │                                                                │  │
│  │  "Browse like iTunes Store"                                   │  │
│  │  - Posters, backdrops, metadata from TMDB/OMDb/MusicBrainz   │  │
│  │  - User confirms ownership before metadata applied           │  │
│  │  - Everything is catalogued, playable only if owned          │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
````

### Catalog Data Model

```sql
-- Core catalog table
CREATE TABLE catalog_items (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    type TEXT NOT NULL, -- movie, tv_show, episode, music, youtube, live_tv
    year INTEGER,
    runtime INTEGER,
    synopsis TEXT,
    
    -- Ownership confirmation
    ownership_confirmed BOOLEAN DEFAULT 0,
    ownership_date DATE,
    ownership_proof TEXT, -- path to digital file or scan of physical
    
    -- Metadata sources
    tmdb_id INTEGER,
    imdb_id TEXT,
    musicbrainz_id TEXT,
    
    -- Local paths
    media_path TEXT, -- where file lives
    poster_path TEXT,
    backdrop_path TEXT,
    
    -- User tags/collections
    tags TEXT, -- JSON array
    user_rating INTEGER,
    
    created_at DATETIME,
    updated_at DATETIME
);

-- YouTube playlist table
CREATE TABLE youtube_playlists (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    obf_sheet TEXT, -- OBF format sheet for generation
    last_synced DATETIME
);

CREATE TABLE youtube_items (
    id TEXT PRIMARY KEY,
    playlist_id TEXT,
    video_id TEXT,
    title TEXT,
    duration INTEGER,
    thumbnail TEXT,
    order_index INTEGER
);
```

***

## Metadata Confirmation Workflow

### User-Confirmed Enhancement

**Principle:** No automated matching. User confirms each title.

````
┌─────────────────────────────────────────────────────────────────────┐
│                    Metadata Confirmation Flow                       │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  1. Scanner finds: /media/movies/unknown_file.mkv                   │
│                                                                     │
│  2. System extracts hash, guesses title from filename              │
│                                                                     │
│  3. Console shows: "New media detected"                            │
│     ┌─────────────────────────────────────────────────────────┐    │
│     │  [?] Unknown Movie                                       │    │
│     │  Filename: unknown_file.mkv                              │    │
│     │  Size: 4.2 GB                                            │    │
│     │                                                          │    │
│     │  Search: [    ] (A button to search)                     │    │
│     │                                                          │    │
│     │  Suggestions from TMDB:                                  │    │
│     │  ┌─────────┐ ┌─────────┐ ┌─────────┐                    │    │
│     │  │Matrix   │ │Matrix   │ │Dark     │                    │    │
│     │  │(1999)   │ │Reloaded │ │Knight   │                    │    │
│     │  │4.2★     │ │(2003)   │ │(2008)   │                    │    │
│     │  │         │ │3.8★     │ │4.5★     │                    │    │
│     │  └─────────┘ └─────────┘ └─────────┘                    │    │
│     │                                                          │    │
│     │  [B: Skip] [A: Select] [X: Manual Entry]                │    │
│     └─────────────────────────────────────────────────────────┘    │
│                                                                     │
│  4. User selects "The Matrix (1999)"                               │
│                                                                     │
│  5. System prompts: "Do you own this digital copy?"                │
│     [Yes, I own it] [No, just browsing] [I own physical]           │
│                                                                     │
│  6. If Yes:                                                         │
│     - Downloads poster, backdrop, metadata from TMDB               │
│     - Marks as "owned" in catalog                                  │
│     - Makes playable                                               │
│                                                                     │
│  7. If No:                                                          │
│     - Still shows in catalog (browsable)                           │
│     - Shows "Not in library" badge                                 │
│     - No playback option                                           │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
````

### Catalog Browsing Experience

**"iTunes Store" style browsing:**

````
┌─────────────────────────────────────────────────────────────────────┐
│  uHome Catalog                                          [Search]    │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ▼ Movies                                                          │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐      │
│  │┌───────┐│ │┌───────┐│ │┌───────┐│ │┌───────┐│ │┌───────┐│      │
│  ││Matrix ││ ││Incep- ││ ││Mad    ││ ││Pulp   ││ ││God-   ││      │
│  ││  ✓    ││ ││tion   ││ ││Max    ││ ││Fiction││ ││father ││      │
│  │└───────┘│ ││  ✓    ││ ││  ✓    ││ ││  ✗    ││ ││  ✓    ││      │
│  │ The     │ │└───────┘│ │└───────┘│ │└───────┘│ │└───────┘│      │
│  │ Matrix  │ │Inception│ │Fury Road│ │Pulp    │ │The      │      │
│  │ 1999    │ │2010     │ │2015     │ │Fiction │ │Godfather│      │
│  │ ★4.2    │ │ ★4.1    │ │ ★4.6    │ │1994    │ │1972     │      │
│  │[OWNED]  │ │[OWNED]  │ │[OWNED]  │ │        │ │[OWNED]  │      │
│  └─────────┘ └─────────┘ └─────────┘ └─────────┘ └─────────┘      │
│                                                                     │
│  ▼ Recently Added                                                   │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐                               │
│  │Dune 2   │ │Poor     │ │Oppen-   │                               │
│  │  ✓      │ │Things   │ │heimer   │                               │
│  │ 2024    │ │  ✓      │ │  ✓      │                               │
│  │ ★4.5    │ │2023     │ │2023     │                               │
│  └─────────┘ └─────────┘ └─────────┘                               │
│                                                                     │
│  ▼ Trending on TMDB (Not in Library)                               │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐                               │
│  │Dune 2   │ │Barbie   │ │Saltburn │                               │
│  │  ✗      │ │  ✗      │ │  ✗      │                               │
│  │ 2024    │ │2023     │ │2023     │                               │
│  │ ★4.5    │ │ ★3.9    │ │ ★4.0    │                               │
│  └─────────┘ └─────────┘ └─────────┘                               │
│                                                                     │
│  [D-pad: Navigate] [A: View Details] [Y: Add to Wishlist]          │
└─────────────────────────────────────────────────────────────────────┘

Legend: ✓ = Owned (playable) | ✗ = Not owned (browsable only)
````

***

## Universal TV Guide

### Live TV & EPG Integration

**Sources for free, subscription-free TV guide:**

| Source              | Type           | Coverage       | Region      |
| ------------------- | -------------- | -------------- | ----------- |
| **HDHomeRun**       | OTA tuner      | Local channels | Worldwide   |
| **Pluto TV**        | Free streaming | 250+ channels  | US/UK/EU    |
| **Tubi**            | Free streaming | 200+ channels  | US/CA/UK/AU |
| **Plex Free**       | Free streaming | 200+ channels  | Worldwide   |
| **Samsung TV Plus** | Free streaming | 200+ channels  | Worldwide   |
| **Xumo**            | Free streaming | 200+ channels  | US/CA/UK    |
| **Local EPG XML**   | User-provided  | Any            | Any         |

### EPG Data Sources

```yaml
# config/epg_sources.yaml
sources:
  - name: hdhomerun
    type: tuner
    url: http://hdhomerun.local
    scan_interval: 3600
    
  - name: pluto
    type: web
    url: https://i.mjh.nz/PlutoTV/
    format: xmltv
    scan_interval: 86400
    
  - name: local_xml
    type: file
    path: /media/config/epg.xml
    format: xmltv
    
  - name: schedules_direct
    type: subscription
    enabled: false  # Paid option, not default
```

### TV Guide UI

````
┌─────────────────────────────────────────────────────────────────────┐
│  Live TV                                              Now: 7:42 PM  │
├─────────────────────────────────────────────────────────────────────┤
│  Channels │ 7:00p     7:30p     8:00p     8:30p     9:00p          │
│  ─────────┼────────────────────────────────────────────────────────┤
│  ▶ NBC    │ News     │[Wheel of│ The Voice │ The Voice │ Local     │
│  WNBC     │ (7:00p)  │ Fortune]│ (8:00p)   │ (8:30p)   │ News      │
│           │          │ (7:30p) │           │           │ (9:00p)   │
│  ─────────┼──────────┼─────────┼───────────┼───────────┼───────────┤
│  CBS      │ Evening  │ Young   │ FBI       │ FBI:      │ Local     │
│  WCBS     │ News     │ Sheldon │ (8:00p)   │ Internatl │ News      │
│           │ (7:00p)  │ (7:30p) │           │ (9:00p)   │ (10:00p)  │
│  ─────────┼──────────┼─────────┼───────────┼───────────┼───────────┤
│  Pluto    │ MST3K    │ MST3K   │ Rifftrax  │ Rifftrax  │ Mystery   │
│  Classic  │ (7:00p)  │ (7:30p) │ (8:00p)   │ (8:30p)   │ Science   │
│  ─────────┼──────────┼─────────┼───────────┼───────────┼───────────┤
│  Tubi     │ Hell's   │ Hell's  │ Kitchen   │ Kitchen   │ Bar       │
│  Reality  │ Kitchen   │ Kitchen │ (8:00p)   │ (8:30p)   │ Rescue    │
│                                                                     │
│  [D-pad: Navigate] [A: Watch] [X: Record] [Y: Guide Options]       │
└─────────────────────────────────────────────────────────────────────┘
````

### DVR Scheduling

```bash
# CLI commands for DVR
uhome dvr schedule --channel "NBC" --time "8:00p" --duration 60
uhome dvr list
uhome dvr cancel --id 1234
uhome dvr recordings --path /media/recordings
```

***

## YouTube Integration (No Subscriptions)

### Embedded YouTube "Apps"

Using **yt-dlp** + **mpv** to replace subscription-based YouTube apps:

| Feature              | Implementation                                           |
| -------------------- | -------------------------------------------------------- |
| Watch video          | `yt-dlp -f best -g "URL" \| mpv --no-video`               |
| Playlist playback    | `yt-dlp -f best -g -J "playlist URL" \| mpv --playlist=-` |
| Search               | `yt-dlp "ytsearch10:query" --flat-playlist`              |
| Channel subscription | OBF sheet + periodic check                               |
| Ad-free              | Built-in (yt-dlp skips sponsor segments)                 |

### OBF Sheet Format for YouTube Playlists

**OBF (Organized Bundle Format)** — a simple Markdown-based sheet for defining playlists:

```markdown
# OBF: YouTube Playlist Sheet
# @playlist: uHome Morning Mix
# @update: daily
# @max_items: 20

## Segment: News (5 items)
- https://youtube.com/watch?v=ABC123  # BBC World News
- https://youtube.com/watch?v=DEF456  # PBS Newshour
- https://youtube.com/watch?v=GHI789  # DW News
- https://youtube.com/watch?v=JKL012  # France 24
- https://youtube.com/watch?v=MNO345  # Al Jazeera

## Segment: Tech (3 items)
- https://youtube.com/@LinusTechTips/latest  # Latest LTT video
- https://youtube.com/watch?v=PQR678  # MKBHD
- https://youtube.com/watch?v=STU901  # Gamers Nexus

## Segment: Music (2 items)
- https://youtube.com/playlist?list=PL123456789  # Morning Jazz
- https://youtube.com/watch?v=VWX234  # Lo-Fi Beats

## Segment: Automation (via @ha)
- @ha:scene.morning_news  # Triggers HA scene before playlist
- @ha:climate.set_temperature?temperature=70  # Set thermostat
- @ha:light.turn_on?brightness=128  # Dim lights
```

### OBF Parser & Player

```bash
# CLI commands for OBF sheets
uhome obf parse ~/playlists/morning-mix.obf --output playlist.json
uhome obf play ~/playlists/morning-mix.obf
uhome obf watch ~/playlists/ --auto-update

# Example output
uhome obf parse morning-mix.obf
# Parsed 5 news, 3 tech, 2 music items
# @ha triggers: scene.morning_news, climate.set_temperature, light.turn_on
# Playlist saved to: /tmp/morning-mix.json
```

### OBF for HA Functions/Settings/Config

```markdown
# OBF: Home Assistant Morning Routine
# @target: uhome-console
# @triggers: daily 7:00am, voice "good morning"

## Section: Environment
- @ha:climate.set_temperature?entity_id=climate.living_room&temperature=72
- @ha:light.turn_on?entity_id=light.kitchen&brightness=255
- @ha:light.turn_on?entity_id=light.living_room&brightness=128

## Section: Media
- @media:playlist?name=Morning News  # YouTube playlist
- @media:volume?level=30
- @media:source?input=TV

## Section: Notifications
- @ha:notify.mobile_phone?message="Good morning! News playing in living room"
- @ha:tts.say?entity_id=media_player.kitchen&message="Time to wake up"

## Section: Delayed Actions (30 min)
- @delay:1800
- @ha:media_player.media_stop?entity_id=media_player.living_room
- @ha:automation.trigger?entity_id=automation.after_news

## Section: Status Reporting
- @status:echo "Morning routine complete at {{now}}"
- @log:write "Morning routine executed"
```

### OBF Sheet Examples Directory

````
~/media/obf-sheets/
├── playlists/
│   ├── morning-news.obf
│   ├── workout-mix.obf
│   ├── chill-evening.obf
│   └── weekend-marathon.obf
├── ha-scenes/
│   ├── good-morning.obf
│   ├── movie-time.obf
│   ├── good-night.obf
│   └── away-mode.obf
├── automations/
│   ├── welcome-home.obf
│   ├── leak-detected.obf
│   └── door-opened.obf
└── examples/
    ├── iwantmymtv.obf      # MTV-style music video playlist
    ├── 90s-cartoons.obf    # Nostalgia block
    └── news-briefing.obf   # Custom news briefing
````

***

## uhome CLI — Media Commands

### Command Structure

```bash
uhome media <subcommand> [options]
```

### Core Subcommands

| Command                | Description             | Example                                                |
| ---------------------- | ----------------------- | ------------------------------------------------------ |
| `uhome media scan`     | Scan ~/media/ vault     | `uhome media scan --deep`                              |
| `uhome media catalog`  | Browse/manage catalog   | `uhome media catalog list --type movie`                |
| `uhome media confirm`  | Confirm media ownership | `uhome media confirm --id abc123 --title "The Matrix"` |
| `uhome media metadata` | Fetch/update metadata   | `uhome media metadata fetch --id abc123`               |
| `uhome media play`     | Play media              | `uhome media play --id abc123 --engine auto`           |
| `uhome media now`      | Show now playing        | `uhome media now`                                      |
| `uhome media queue`    | Manage playback queue   | `uhome media queue add --id def456`                    |
| `uhome media tv-guide` | Live TV guide           | `uhome media tv-guide --channel NBC`                   |
| `uhome media record`   | DVR recording           | `uhome media record --channel CBS --time "8:00p"`      |
| `uhome media youtube`  | YouTube operations      | `uhome media youtube search "cats"`                    |
| `uhome media obf`      | OBF sheet operations    | `uhome media obf parse sheet.obf`                      |

### Detailed Command Specs

#### `uhome media scan`

```bash
uhome media scan [--path <path>] [--deep] [--watch]

# Scan default ~/media/
uhome media scan

# Deep scan (checksums, duration extraction)
uhome media scan --deep

# Watch mode (auto-scan on changes)
uhome media scan --watch

# Output
Scanning /media...
Found 47 files
  - 23 movies (14 new)
  - 15 TV episodes (8 new)
  - 9 music files (9 new)
Waiting for metadata confirmation: 14 items
```

#### `uhome media catalog`

```bash
# List catalog with filters
uhome media catalog list --type movie --owned --sort year

# Show single item
uhome media catalog show --id abc123

# Search catalog
uhome media catalog search "matrix"

# Add to wishlist (browsable, not owned)
uhome media catalog wishlist add --title "Dune 2" --tmdb-id 123456

# Output format
uhome media catalog list --format json | jq '.[].title'
```

#### `uhome media confirm`

```bash
# Interactive confirmation for new media
uhome media confirm

# Non-interactive (for scripting)
uhome media confirm --id abc123 --title "The Matrix" --year 1999 --owned

# Batch confirm from file
uhome media confirm --batch confirmations.json
```

#### `uhome media obf`

```bash
# Parse OBF sheet to JSON
uhome media obf parse ~/playlists/morning.obf --output playlist.json

# Execute OBF sheet (play + HA actions)
uhome media obf run ~/playlists/morning.obf

# Validate OBF syntax
uhome media obf validate ~/playlists/morning.obf

# Watch directory for OBF changes
uhome media obf watch ~/playlists/ --auto-execute

# List available OBF sheets
uhome media obf list --type playlist
```

#### `uhome media tv-guide`

```bash
# Show current guide
uhome media tv-guide --now

# Show specific channel
uhome media tv-guide --channel NBC --time "8:00p"

# Search guide
uhome media tv-guide --search "movie"

# Update EPG data
uhome media tv-guide --update

# Output
Now Playing (7:42 PM):
NBC: Wheel of Fortune (until 8:00p)
CBS: Young Sheldon (until 8:00p)
Pluto: MST3K (until 8:00p)
```

***

## Playback Engine Router

### Auto-Engine Selection Logic

```go
// Determine best engine for playback
func SelectEngine(media Media, target Target) Engine {
    // Remote streaming
    if target.IsRemote {
        return JellyfinEngine  // Transcode for bandwidth
    }
    
    // 4K HDR content
    if media.Codec == "hevc" && media.HDR && target.Is4K {
        return KodiEngine  // Direct play, best quality
    }
    
    // Low-powered device (RPi, old laptop)
    if target.CPU < 2.0 {
        return MPVEngine  // Lightweight
    }
    
    // Music
    if media.Type == "music" {
        return JellyfinEngine  // Multi-room sync
    }
    
    // YouTube/Streaming
    if media.Source == "youtube" {
        return YTDLEngine + MPVEngine
    }
    
    // Default
    return MPVEngine
}
```

### Manual Engine Override

```bash
# Force specific engine
uhome media play --id abc123 --engine kodi
uhome media play --id def456 --engine jellyfin
uhome media play --url "https://youtu.be/..." --engine mpv
```

***

## Music Library

### Music Organization

````
~/media/music/
├── Artist Name/
│   ├── Album Name (Year)/
│   │   ├── 01 - Track Name.flac
│   │   ├── 01 - Track Name.md    # Lyrics, credits, notes
│   │   ├── cover.jpg
│   │   └── album.md              # Album review, metadata
│   └── artist.md                 # Biography, discography
├── playlists/
│   ├── morning-jazz.m3u
│   ├── workout.json              # OBF format
│   └── chill-obf.obf
└── index.md                      # Music catalog
````

### Music Features

- **Local library only** — No streaming subscriptions
- **FLAC/MP3/OGG** support
- **MusicBrainz** metadata (user-confirmed)
- **Multi-room sync** via Jellyfin
- **Gapless playback** (mpv)
- **ReplayGain** normalization

***

## uhome CLI — Music Commands

```bash
# Scan music library
uhome music scan

# Play album
uhome music play --album "Dark Side of the Moon"

# Play playlist
uhome music playlist play --name morning-jazz

# Now playing with visualizer
uhome music now --visualizer

# Sync to multiple rooms
uhome music sync --rooms kitchen,living_room --playlist chill
```

***

## Universal Media DB Integration

### Metadata Sources (User-Triggered Only)

| Source          | Content                      | API Required  |
| --------------- | ---------------------------- | ------------- |
| **TMDB**        | Movies, TV posters/backdrops | Free API key  |
| **OMDb**        | Movie ratings, IMDB links    | Free API key  |
| **MusicBrainz** | Music metadata               | Free (no key) |
| **Fanart.tv**   | High-res artwork             | Free API key  |
| **TheTVDB**     | Episode guides               | Free API key  |

### Metadata Fetch Flow

```bash
# User selects a title in catalog
uhome media metadata fetch --title "The Matrix" --type movie

# System prompts:
# "Found 3 matches:"
# 1. The Matrix (1999) ★4.2
# 2. The Matrix Reloaded (2003) ★3.8
# 3. The Matrix Revolutions (2003) ★3.5
# 
# Select match: 1

# "Download poster, backdrop, cast info? (y/n)" y

# Metadata saved to catalog
# Posters saved to ~/media/.metadata/posters/
```

***

## Example OBF Sheets

### "IWantMyMTV" — 80s Music Video Playlist

```markdown
# OBF: IWantMyMTV - 80s Music Videos
# @playlist: 80s MTV Classics
# @update: weekly
# @max_duration: 3600

## Segment: 1983
- https://youtube.com/watch?v=MgHrU  # Michael Jackson - Thriller
- https://youtube.com/watch?v=A7ry4  # David Bowie - Let's Dance
- https://youtube.com/watch?v=2Y6Ne  # Eurythmics - Sweet Dreams

## Segment: 1984
- https://youtube.com/watch?v=z9OGf  # Van Halen - Jump
- https://youtube.com/watch?v=6pYrS  # Prince - When Doves Cry
- https://youtube.com/watch?v=4B_UY  # Madonna - Like a Virgin

## Segment: 1985
- https://youtube.com/watch?v=oFRbZ  # Tears for Fears - Everybody Wants To Rule The World
- https://youtube.com/watch?v=WBRNW  # Dire Straits - Money for Nothing
- https://youtube.com/watch?v=8WEtx  # Whitney Houston - How Will I Know

## Segment: Interstitial (MTV-style VJs)
- @media:play ~/media/interstitials/mtv-vj-1.mp4
- @delay:30
- @media:play ~/media/interstitials/mtv-vj-2.mp4

## Segment: @ha integration for "MTV Party Mode"
- @ha:scene.mtv_party  # Color lights, disco ball
- @ha:light.living_room.effect?effect=colorloop
```

### "Home Assistant Morning Briefing" OBF

```markdown
# OBF: Home Assistant Morning Briefing
# @target: uhome-console
# @triggers: daily 7:00am, voice "good morning"

## Section: Environment Preparation (T-5 min)
- @schedule:-300
- @ha:climate.set_temperature?entity_id=climate.living_room&temperature=71
- @ha:light.kitchen.turn_on?brightness=192&color_temp=3500

## Section: Good Morning (T=0)
- @ha:media_player.living_room.volume_set?volume_level=0.3
- @ha:tts.say?message="Good morning! Today is {{date('%A, %B %d')}}"
- @ha:notify.mobile?message="Morning briefing starting in living room"

## Section: Weather & Calendar
- @ha:weather.get_forecast?entity_id=weather.home
- @ha:calendar.get_events?days=1
- @ha:tts.say?message="Today's weather is {{weather}}. You have {{calendar.count}} events."

## Section: News Playlist
- @media:playlist?name=Morning News Briefing
- @media:volume?level=0.25

## Section: After News (30 min)
- @delay:1800
- @ha:media_player.living_room.media_stop
- @ha:light.living_room.turn_on?brightness=255
- @ha:automation.trigger?entity_id=automation.after_news

## Section: Status Report
- @status:display "Morning routine complete at {{now}}"
- @log:write "morning_briefing" "success" "{{now}}"
- @ha:notify.mobile?message="Morning routine complete. Have a great day!"
```

### "Movie Night" OBF with HA Scene

```markdown
# OBF: Movie Night
# @target: uhome-console
# @triggers: voice "movie night", ha scene selection

## Section: Environment
- @ha:scene.movie_time  # Dim lights, close blinds
- @ha:climate.set_temperature?entity_id=climate.living_room&temperature=68
- @ha:light.living_room_accent.turn_on?brightness=64

## Section: Media Selection (interactive)
- @prompt:select_movie
- @media:movie_list?filter=owned,recently_added
- @on_select:media_play

## Section: Intermission (45 min into movie)
- @schedule:2700
- @ha:light.living_room.turn_on?brightness=128&transition=30
- @ha:tts.say?message="Intermission! Bathroom break?"

## Section: After Movie
- @on_complete:
- @ha:light.living_room.turn_on?brightness=255&transition=60
- @ha:notify.mobile?message="Movie finished! Rate it? {{rating_prompt}}"
- @ha:scene.after_movie  # Return to normal
```

***

## Success Criteria

- [ ] `uhome media scan` detects media in `~/media/`
- [ ] Catalog shows both owned and unowned content
- [ ] Metadata confirmation workflow works (no auto-matching)
- [ ] Posters/backdrops download from TMDB on user confirmation
- [ ] TV guide shows OTA + free streaming channels
- [ ] DVR records scheduled shows
- [ ] YouTube plays via yt-dlp + mpv (no subscription)
- [ ] OBF parser generates playlists and executes HA actions
- [ ] Example OBF sheets work (IWantMyMTV, HA Morning)
- [ ] Playback router selects correct engine per content/target

***

## Related Documents

- [HA Deep Integration](./UDN-HA-EMBED-001.md)
- [uHomeNest v1.0.0 Dev Brief](./UHOMENEST-V1-DEV-BRIEF.md)
- [Alexa/Google/HomeKit Guide](./UDN-VOICE-INTEGRATION-001.md)
- [Vibe CLI Project Reset](./UDN-RESET-001.md)

***

## Version History

| Version | Date       | Changes                              |
| ------- | ---------- | ------------------------------------ |
| 1.0.0   | 2026-04-21 | Initial universal media player brief |