---
title: "Jotion Surface Specification v1.0.0"
status: draft
last_updated: 2026-05-17T00:14:16+10:00
category: specification
tags: [integration, jotion, specification, ucode3]
description: "**Updated:** 2026-05-16"
---
# Jotion Surface Specification v1.0.0

**Status:** Draft
**Updated:** 2026-05-16
**Surface ID:** `jotion-document-workspace`
**Reference:** `https://github.com/PerHac13/jotion`

---

## 1. Purpose

This spec defines the Jotion Notion-style document workspace as a uCode3 USX Surface. Jotion provides collaborative document editing with a block-based editor (BlockNote), real-time database (Convex), and user authentication (Clerk).

## 2. Surface Contract

### 2.1 Identity

| Field | Value |
|-------|-------|
| `open_box.id` | `jotion-ucode3-surface` |
| `type` | `application/vnd.usx.surface` |
| `version` | `1.0.0` |
| `surface` | `ucode3` |
| `framework` | `next.js` |

### 2.2 Dependencies

| Dependency | Version | Purpose |
|------------|---------|---------|
| Next.js | 13.x | React framework |
| Convex | latest | Real-time database |
| Clerk | latest | Authentication |
| BlockNote | latest | Block editor |
| Tailwind CSS | 3.x | Styling |
| Edge Store | latest | File uploads |
| Lucide React | latest | Icons |

### 2.3 Slot Mapping (uCode3 Console)

| Slot | Command | Component |
|------|---------|-----------|
| 64 | `jotion:editor` | Document Editor |
| 65 | `jotion:sidebar` | Navigation Sidebar |
| 66 | `jotion:documents` | Document List |
| 67 | `jotion:trash` | Trash Can |
| 68 | `jotion:settings` | Settings |
| 69 | `jotion:cover` | Cover Image |
| 70 | `jotion:icon` | Document Icon |

## 3. LENS Variables

### 3.1 Document State

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `snack_box.document.id` | string | — | Document ID |
| `snack_box.document.title` | string | "Untitled" | Document title |
| `snack_box.document.content` | object | `{type:"doc",content:[]}` | BlockNote content |
| `snack_box.document.icon` | string | "📄" | Emoji icon |
| `snack_box.document.cover_image` | string\|null | null | Cover image URL |
| `snack_box.document.is_published` | boolean | false | Published status |
| `snack_box.document.parent_document` | string\|null | null | Parent document ID |

### 3.2 Workspace State

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `snack_box.workspace.sidebar_open` | boolean | true | Sidebar visibility |
| `snack_box.workspace.current_view` | enum | "document" | Active view |
| `snack_box.workspace.search_query` | string | "" | Search query |
| `snack_box.workspace.theme` | enum | "light" | Color theme |

### 3.3 Feature Flags

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `snack_box.features.real_time_sync` | boolean | true | Convex sync |
| `snack_box.features.infinite_children` | boolean | true | Nested docs |
| `snack_box.features.file_upload` | boolean | true | File attachments |
| `snack_box.features.web_publishing` | boolean | true | Publish to web |

### 3.4 Runtime State

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `runtime.user.id` | string | — | User ID |
| `runtime.user.email` | string | — | User email |
| `runtime.user.name` | string | — | User display name |
| `runtime.user.avatar` | string | — | Avatar URL |
| `runtime.connection_status` | enum | "disconnected" | Connection state |
| `runtime.last_sync` | ISO-8601 | — | Last sync timestamp |
| `runtime.unsaved_changes` | boolean | false | Pending changes |

## 4. SKIN Theme

### 4.1 Color Tokens

| Token | Light | Dark | CSS Variable |
|-------|-------|------|-------------|
| `background` | `#ffffff` | `#191919` | `--jotion-bg` |
| `surface` | `#f7f6f3` | `#2f2f2f` | `--jotion-surface` |
| `text` | `#37352f` | `#e9e9e7` | `--jotion-text` |
| `text_muted` | `#6b6b6b` | `#9b9b9b` | `--jotion-text-muted` |
| `border` | `#e9e9e7` | `#3d3d3d` | `--jotion-border` |
| `primary` | `#2e7d64` | `#4baa8a` | `--jotion-primary` |
| `accent` | `#eb5757` | `#eb5757` | `--jotion-accent` |

### 4.2 Typography

| Level | Font | Size | Weight | Line Height |
|-------|------|------|--------|-------------|
| Body | Inter | 16px | 400 | 1.5 |
| Heading 1 | Inter | 40px | 700 | 1.2 |
| Heading 2 | Inter | 28px | 600 | 1.3 |
| Heading 3 | Inter | 22px | 600 | 1.3 |
| Code | SF Mono | 14px | 400 | 1.5 |
| Caption | Inter | 14px | 400 | 1.4 |

### 4.3 Component Classes

| Component | CSS Class | Description |
|-----------|-----------|-------------|
| Sidebar | `.navigation-sidebar` | Fixed left sidebar |
| Editor | `.block-editor` | Main editor container |
| Document List | `.document-tree` | Hierarchical document tree |
| Toolbar | `.floating-toolbar` | Floating format toolbar |
| Cover | `.cover-image` | Document cover image |
| Icon | `.document-icon` | Document emoji icon |

## 5. Router Mappings

| LENS Variable | SKIN Output | Transform | Description |
|---------------|-------------|-----------|-------------|
| `snack_box.document` | `document_view` | `document_to_editor` | Document → editor props |
| `snack_box.workspace.theme` | `color_mode` | `theme_to_tailwind` | Theme → CSS class |
| `snack_box.workspace.sidebar_open` | `sidebar_visible` | `boolean_to_class` | Boolean → CSS class |
| `runtime.user` | `user_context` | `user_to_profile` | User → profile props |
| `snack_box.features` | `feature_flags` | `features_to_toggles` | Flags → toggles |

## 6. Deployment

### 6.1 Docker Compose

```yaml
# surfaces/jotion/docker-compose.jotion.yml
services:
  jotion:
    image: ucode3-jotion:latest
    ports: ["3002:3000"]
    environment:
      - CONVEX_DEPLOYMENT=${CONVEX_DEPLOYMENT}
      - NEXT_PUBLIC_CONVEX_URL=${NEXT_PUBLIC_CONVEX_URL}
      - NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=${NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY}
      - CLERK_SECRET_KEY=${CLERK_SECRET_KEY}
      - EDGE_STORE_ACCESS_KEY=${EDGE_STORE_ACCESS_KEY}
      - EDGE_STORE_SECRET_KEY=${EDGE_STORE_SECRET_KEY}
```

### 6.2 Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `CONVEX_DEPLOYMENT` | Yes | Convex deployment ID |
| `NEXT_PUBLIC_CONVEX_URL` | Yes | Convex URL |
| `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` | Yes | Clerk publishable key |
| `CLERK_SECRET_KEY` | Yes | Clerk secret key |
| `EDGE_STORE_ACCESS_KEY` | Yes | Edge Store access key |
| `EDGE_STORE_SECRET_KEY` | Yes | Edge Store secret key |

## 7. Acceptance Criteria

- [ ] Document creation and editing works via BlockNote
- [ ] Real-time sync via Convex is operational
- [ ] User authentication via Clerk is functional
- [ ] File uploads via Edge Store work
- [ ] Dark/light theme switching functions
- [ ] Sidebar toggle works
- [ ] Document hierarchy (infinite children) works
- [ ] Trash can with recovery works
- [ ] Web publishing per document works
- [ ] Mobile responsive layout functions
- [ ] LENS variables update correctly
- [ ] SKIN theme applies correctly
- [ ] Router mappings transform correctly
- [ ] Docker Compose deployment works
- [ ] Health check endpoint responds

## 8. Related Documents

- `docs/surfaces/JOTION_SURFACE_INTEGRATION.md` — Full integration plan
- `surfaces/jotion/lens/jotion-schema.json` — LENS schema
- `surfaces/jotion/skin/jotion-skin.json` — SKIN schema
- `surfaces/jotion/router/jotion-router.json` — Router schema
- `surfaces/jotion/surface-definition.json` — Surface definition
