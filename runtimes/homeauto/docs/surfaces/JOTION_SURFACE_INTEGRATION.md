---
title: "Jotion → uCode3 Surface Integration Plan"
status: draft
last_updated: 2026-05-17T00:14:16+10:00
category: documentation
tags: [integration, jotion, ucode3]
description: "**Status:** Planning — Reference implementation: `https://github.com/PerHac13/jotion`"
---
# Jotion → uCode3 Surface Integration Plan

## Notion-Style Document Workspace for uCode

**Status:** Planning — Reference implementation: `https://github.com/PerHac13/jotion`
**Surface ID:** `jotion-document-workspace`
**Skin ID:** `jotion-notion-skin`
**Router ID:** `jotion-router`
**Version:** 1.0.0
**Slot:** uCode3 Surface Layer (Console/Tablet/Layback)

---

## Part 1: Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        uCode3 Notion-Style Workspace                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────┐    ┌─────────────────────────────────────────────┐│
│  │   Jotion Core       │    │              USX Surface Layer              ││
│  │   (Next.js 13)      │    │                                             ││
│  │                     │    │  ┌─────────┐  ┌─────────┐  ┌─────────────┐  ││
│  │  ┌───────────────┐  │    │  │  LENS   │  │  SKIN   │  │  Notion     │  ││
│  │  │ Document      │──┼────┼─▶│ Document│──│ Tailwind │──│ Block       │  ││
│  │  │ Editor        │  │    │  │ State   │  │ Style   │  │ Renderer    │  ││
│  │  └───────────────┘  │    │  └─────────┘  └─────────┘  └─────────────┘  ││
│  │                     │    │                                             ││
│  │  ┌───────────────┐  │    │  ┌─────────────────────────────────────────┐││
│  │  │ Convex DB     │──┼────┼─▶│           USX Schema Router            │││
│  │  │ (Real-time)   │  │    │  │  (LENS variables → SKIN output)        │││
│  │  └───────────────┘  │    │  └─────────────────────────────────────────┘││
│  └─────────────────────┘    └─────────────────────────────────────────────┘│
│                                                                             │
│  Output: React Components    │    Runtime: uCode3 Browser Engine            │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Integration Rationale

Jotion provides a full-featured Notion-style document workspace built on Next.js 13, Convex DB, Clerk auth, and BlockNote editor. By wrapping Jotion as a uCode3 USX Surface, we gain:

- **Collaborative document editing** with real-time sync
- **Block-based editor** (headings, lists, to-do, code, callouts, etc.)
- **Infinite children** document hierarchy
- **Trash can** with recovery
- **File uploads** via Edge Store
- **Web publishing** per document
- **Dark/light theme** support

All surfaced through uCode3's LENS/SKIN/Router architecture — zero hardcoding, fully themeable.

---

## Part 2: Technology Stack Integration

### 2.1 Jotion Core Stack (as is)

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Framework** | Next.js 13 | React framework with App Router |
| **Database** | Convex | Real-time backend + state management |
| **Auth** | Clerk | User authentication |
| **Editor** | BlockNote | Notion-style block editor |
| **Styling** | Tailwind CSS | Utility classes |
| **File Storage** | Edge Store | File uploads |
| **Icons** | Lucide React | Icon library |

### 2.2 uCode3 Integration Layer

| Layer | Implementation | USX Role |
|-------|----------------|----------|
| **LENS** | Document state + user preferences | Variables |
| **SKIN** | Tailwind + Notion styling | Theme |
| **Router** | URL + document routing | Navigation |
| **Surface** | Jotion components wrapped | Renderer |

### 2.3 uCode3 Slot Mapping

| Slot | Jotion Component | uCode3 Surface |
|------|-----------------|----------------|
| 64 | Document Editor | `jotion:editor` |
| 65 | Navigation Sidebar | `jotion:sidebar` |
| 66 | Document List | `jotion:documents` |
| 67 | Trash Can | `jotion:trash` |
| 68 | Settings | `jotion:settings` |
| 69 | Cover Image | `jotion:cover` |
| 70 | Document Icon | `jotion:icon` |

---

## Part 3: LENS Variables Schema (Jotion)

```json
{
  "$schema": "https://usx.dev/schema/lens-v1",
  "version": "1.0.0",
  "lens": {
    "id": "jotion-document-workspace",
    "name": "Notion-Style Document Workspace",
    "description": "Collaborative document editing with block-based editor",
    "source": "jotion",
    "variables": {
      "snack_box": {
        "document": {
          "id": "string",
          "title": "string",
          "content": "object",
          "icon": "string",
          "cover_image": "string",
          "is_published": "boolean",
          "parent_document": "string | null"
        },
        "workspace": {
          "sidebar_open": "boolean",
          "current_view": "document | trash | settings",
          "search_query": "string",
          "theme": "light | dark"
        },
        "features": {
          "real_time_sync": "boolean",
          "infinite_children": "boolean",
          "file_upload": "boolean",
          "web_publishing": "boolean"
        }
      },
      "runtime": {
        "user": {
          "id": "string",
          "email": "string",
          "name": "string",
          "avatar": "string"
        },
        "connection_status": "connected | disconnected | reconnecting",
        "last_sync": "ISO-8601",
        "unsaved_changes": "boolean"
      }
    }
  }
}
```

### LENS Variable Reference

| Variable Path | Type | Default | Description |
|--------------|------|---------|-------------|
| `snack_box.document.id` | string | — | Unique document identifier |
| `snack_box.document.title` | string | "Untitled" | Document title |
| `snack_box.document.content` | object | `{type:"doc",content:[]}` | BlockNote document content |
| `snack_box.document.icon` | string | "📄" | Document emoji icon |
| `snack_box.document.cover_image` | string | null | Cover image URL |
| `snack_box.document.is_published` | boolean | false | Web publishing status |
| `snack_box.document.parent_document` | string\|null | null | Parent document ID for hierarchy |
| `snack_box.workspace.sidebar_open` | boolean | true | Sidebar visibility |
| `snack_box.workspace.current_view` | enum | "document" | Active workspace view |
| `snack_box.workspace.search_query` | string | "" | Document search query |
| `snack_box.workspace.theme` | enum | "light" | Color theme |
| `snack_box.features.real_time_sync` | boolean | true | Enable Convex real-time sync |
| `snack_box.features.infinite_children` | boolean | true | Enable nested documents |
| `snack_box.features.file_upload` | boolean | true | Enable file attachments |
| `snack_box.features.web_publishing` | boolean | true | Enable publish to web |
| `runtime.user.*` | object | — | Authenticated user info |
| `runtime.connection_status` | enum | "disconnected" | Convex connection state |
| `runtime.last_sync` | ISO-8601 | — | Last sync timestamp |
| `runtime.unsaved_changes` | boolean | false | Pending changes indicator |

---

## Part 4: SKIN Schema (Notion Style)

```json
{
  "$schema": "https://usx.dev/schema/skin-v1",
  "version": "1.0.0",
  "skin": {
    "id": "jotion-notion-skin",
    "name": "Notion-Style Document Skin",
    "inherits": "usx://themes/notion",
    "framework": "Tailwind CSS",
    "overrides": {
      "color": {
        "background": "#ffffff",
        "surface": "#f7f6f3",
        "text": "#37352f",
        "text_muted": "#6b6b6b",
        "border": "#e9e9e7",
        "primary": "#2e7d64",
        "accent": "#eb5757"
      },
      "typography": {
        "body_font": "Inter, -apple-system, BlinkMacSystemFont, sans-serif",
        "heading_font": "Inter, -apple-system, sans-serif",
        "mono_font": "'SF Mono', Monaco, monospace",
        "base_size": "16px",
        "line_height": "1.5"
      },
      "components": {
        "sidebar": "sidebar",
        "editor": "block-editor",
        "document_list": "document-tree",
        "toolbar": "floating-toolbar",
        "cover": "cover-image",
        "icon": "document-icon"
      },
      "effects": {
        "hover": "opacity-80 transition",
        "focus": "ring-2 ring-primary",
        "drag_handle": "grab-cursor",
        "selection": "bg-primary/10"
      }
    },
    "extended": {
      "notion": {
        "block_types": [
          "heading1", "heading2", "heading3",
          "paragraph", "bulleted_list", "numbered_list",
          "to_do", "toggle", "code", "quote",
          "callout", "divider", "image", "bookmark"
        ],
        "animations": true,
        "drag_drop": true,
        "inline_math": true,
        "inline_code": true
      }
    }
  }
}
```

### SKIN Color Tokens

| Token | Light | Dark | CSS Variable |
|-------|-------|------|-------------|
| `background` | `#ffffff` | `#191919` | `--jotion-bg` |
| `surface` | `#f7f6f3` | `#2f2f2f` | `--jotion-surface` |
| `text` | `#37352f` | `#e9e9e7` | `--jotion-text` |
| `text_muted` | `#6b6b6b` | `#9b9b9b` | `--jotion-text-muted` |
| `border` | `#e9e9e7` | `#3d3d3d` | `--jotion-border` |
| `primary` | `#2e7d64` | `#4baa8a` | `--jotion-primary` |
| `accent` | `#eb5757` | `#eb5757` | `--jotion-accent` |

### SKIN Typography Scale

| Level | Size | Weight | Line Height |
|-------|------|--------|-------------|
| `heading1` | 40px | 700 | 1.2 |
| `heading2` | 28px | 600 | 1.3 |
| `heading3` | 22px | 600 | 1.3 |
| `body` | 16px | 400 | 1.5 |
| `caption` | 14px | 400 | 1.4 |
| `code` | 14px | 400 | 1.5 |

---

## Part 5: USX Router Schema (Jotion)

```json
{
  "$schema": "https://usx.dev/schema/router-v1",
  "version": "1.0.0",
  "router": {
    "id": "jotion-router",
    "source": "lens://jotion-document-workspace/variables",
    "target": "skin://jotion-notion-skin/output",
    "mappings": [
      {
        "lens_var": "snack_box.document",
        "skin_output": "document_view",
        "transform": "document_to_editor",
        "fields": ["id", "title", "content", "icon", "cover_image"]
      },
      {
        "lens_var": "snack_box.workspace.theme",
        "skin_output": "color_mode",
        "transform": "theme_to_tailwind",
        "values": {
          "light": "light",
          "dark": "dark"
        }
      },
      {
        "lens_var": "snack_box.workspace.sidebar_open",
        "skin_output": "sidebar_visible",
        "transform": "boolean_to_class",
        "true": "sidebar-expanded",
        "false": "sidebar-collapsed"
      },
      {
        "lens_var": "runtime.user",
        "skin_output": "user_context",
        "transform": "user_to_profile"
      },
      {
        "lens_var": "snack_box.features",
        "skin_output": "feature_flags",
        "transform": "features_to_toggles"
      }
    ],
    "render": {
      "engine": "next.js",
      "components": {
        "document": "DocumentPage",
        "sidebar": "NavigationSidebar",
        "editor": "BlockEditor"
      },
      "output": "web"
    }
  }
}
```

### Router Transform Functions

| Transform | Input | Output | Description |
|-----------|-------|--------|-------------|
| `document_to_editor` | LENS document object | SKIN editor props | Maps document state to editor component props |
| `theme_to_tailwind` | "light" \| "dark" | CSS class | Applies Tailwind dark mode class |
| `boolean_to_class` | boolean | CSS class string | Maps boolean to sidebar visibility class |
| `user_to_profile` | user object | profile component props | Maps user data to profile display |
| `features_to_toggles` | feature flags object | feature toggle array | Maps feature flags to UI toggles |

---

## Part 6: uCode3 Surface Component

```tsx
// surfaces/jotion/components/JotionSurface.tsx
'use client';

import React, { useState, useEffect } from 'react';
import { useConvex } from 'convex/react';
import { useUser } from '@clerk/nextjs';
import { api } from '@/convex/_generated/api';
import { Id } from '@/convex/_generated/dataModel';

// USX imports
import { useLENS } from '@usx/lens';
import { useSKIN } from '@usx/skin';
import { DocumentEditor } from './DocumentEditor';
import { NavigationSidebar } from './NavigationSidebar';
import { DocumentList } from './DocumentList';
import { CoverImage } from './CoverImage';
import { DocumentIcon } from './DocumentIcon';

interface JotionSurfaceProps {
  documentId?: Id<"documents">;
  surfaceConfig?: any;
}

export const JotionSurface: React.FC<JotionSurfaceProps> = ({ 
  documentId,
  surfaceConfig 
}) => {
  // USX Lens state
  const { lens, updateLens } = useLENS('jotion-document-workspace');
  const { skin, applySkin } = useSKIN('jotion-notion-skin');
  
  // Jotion core hooks
  const { user } = useUser();
  const convex = useConvex();
  
  // Local state
  const [document, setDocument] = useState<any>(null);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [isLoading, setIsLoading] = useState(true);
  
  // Load document from Convex
  useEffect(() => {
    if (documentId) {
      const loadDocument = async () => {
        try {
          const doc = await convex.query(api.documents.getById, { id: documentId });
          setDocument(doc);
          
          // Update LENS with document state
          updateLens({
            snack_box: {
              document: {
                id: doc._id,
                title: doc.title,
                content: doc.content,
                icon: doc.icon,
                cover_image: doc.coverImage,
                is_published: doc.isPublished,
                parent_document: doc.parentDocument
              }
            }
          });
        } catch (error) {
          console.error('Failed to load document:', error);
        } finally {
          setIsLoading(false);
        }
      };
      
      loadDocument();
    }
  }, [documentId, convex, updateLens]);
  
  // Apply SKIN on mount
  useEffect(() => {
    if (skin) {
      applySkin(skin);
    }
  }, [skin, applySkin]);
  
  // Handle document updates
  const handleDocumentUpdate = (updates: any) => {
    setDocument((prev: any) => ({ ...prev, ...updates }));
    updateLens({
      snack_box: {
        document: {
          ...lens.snack_box.document,
          ...updates
        }
      }
    });
  };
  
  // Handle sidebar toggle
  const handleSidebarToggle = () => {
    const newState = !sidebarOpen;
    setSidebarOpen(newState);
    updateLens({
      snack_box: {
        workspace: {
          ...lens.snack_box.workspace,
          sidebar_open: newState
        }
      }
    });
  };
  
  if (isLoading) {
    return (
      <div className="jotion-loading">
        <div className="loading-spinner"></div>
        <div className="loading-text">LOADING DOCUMENT...</div>
      </div>
    );
  }
  
  return (
    <div className={`jotion-surface ${skin?.color_mode === 'dark' ? 'dark' : ''}`}>
      {/* Navigation Sidebar */}
      <NavigationSidebar 
        isOpen={sidebarOpen}
        onToggle={handleSidebarToggle}
        currentDocumentId={documentId}
      />
      
      {/* Main Content Area */}
      <div className={`main-content ${sidebarOpen ? 'sidebar-open' : 'sidebar-closed'}`}>
        {/* Document Cover */}
        {document?.coverImage && (
          <CoverImage 
            url={document.coverImage}
            onChange={(url) => handleDocumentUpdate({ coverImage: url })}
          />
        )}
        
        {/* Document Icon */}
        <div className="document-header">
          <DocumentIcon 
            icon={document?.icon} 
            onChange={(icon) => handleDocumentUpdate({ icon })}
          />
          <h1 className="document-title">
            {document?.title || 'Untitled'}
          </h1>
        </div>
        
        {/* Block Editor */}
        <DocumentEditor 
          documentId={documentId}
          initialContent={document?.content}
          onChange={(content) => handleDocumentUpdate({ content })}
        />
        
        {/* Document Footer */}
        <div className="document-footer">
          <div className="footer-info">
            <span>Last edited: {new Date(document?.updatedAt).toLocaleString()}</span>
            {document?.isPublished && (
              <span className="published-badge">
                <i className="icon-globe"></i> Published
              </span>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
```

---

## Part 7: Jotion Surface CSS (Tailwind + USX Variables)

```css
/* surfaces/jotion/skin/jotion-surface.css */
/* Complete Jotion styling with USX variables */

:root {
  /* USX color tokens */
  --jotion-bg: var(--usx-color-background, #ffffff);
  --jotion-surface: var(--usx-color-surface, #f7f6f3);
  --jotion-text: var(--usx-color-text, #37352f);
  --jotion-text-muted: var(--usx-color-text-muted, #6b6b6b);
  --jotion-border: var(--usx-color-border, #e9e9e7);
  --jotion-primary: var(--usx-color-primary, #2e7d64);
  --jotion-accent: var(--usx-color-accent, #eb5757);
  
  /* Notion-specific spacing */
  --jotion-sidebar-width: 280px;
  --jotion-sidebar-collapsed: 48px;
  --jotion-header-height: 56px;
}

/* Surface layout */
.jotion-surface {
  display: flex;
  min-height: 100vh;
  background: var(--jotion-bg);
  color: var(--jotion-text);
  font-family: var(--usx-font-body, Inter, sans-serif);
}

/* Sidebar styling */
.navigation-sidebar {
  width: var(--jotion-sidebar-width);
  background: var(--jotion-surface);
  border-right: 1px solid var(--jotion-border);
  transition: width 0.2s ease;
  overflow: hidden;
  position: fixed;
  left: 0;
  top: 0;
  bottom: 0;
  z-index: 10;
}

.navigation-sidebar.collapsed {
  width: var(--jotion-sidebar-collapsed);
}

.sidebar-toggle {
  position: absolute;
  right: -12px;
  top: 20px;
  width: 24px;
  height: 24px;
  background: var(--jotion-surface);
  border: 1px solid var(--jotion-border);
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 20;
}

/* Main content area */
.main-content {
  flex: 1;
  margin-left: var(--jotion-sidebar-width);
  transition: margin-left 0.2s ease;
  min-height: 100vh;
  background: var(--jotion-bg);
}

.main-content.sidebar-closed {
  margin-left: var(--jotion-sidebar-collapsed);
}

/* Document header */
.document-header {
  max-width: 900px;
  margin: 0 auto;
  padding: 32px 24px 16px;
  display: flex;
  align-items: center;
  gap: 12px;
}

.document-title {
  font-size: 32px;
  font-weight: 700;
  margin: 0;
  border: none;
  background: transparent;
  width: 100%;
  padding: 4px 0;
  color: var(--jotion-text);
}

.document-title:focus {
  outline: none;
}

/* Block editor container */
.block-editor {
  max-width: 900px;
  margin: 0 auto;
  padding: 0 24px 64px;
  min-height: 400px;
}

/* Editor content styling */
.block-editor .bn-editor {
  background: transparent;
  padding: 0;
}

.block-editor .bn-block {
  margin: 8px 0;
}

/* Notion-style blocks */
.heading1 {
  font-size: 40px;
  font-weight: 700;
  margin: 28px 0 8px;
}

.heading2 {
  font-size: 28px;
  font-weight: 600;
  margin: 24px 0 8px;
}

.heading3 {
  font-size: 22px;
  font-weight: 600;
  margin: 20px 0 8px;
}

.to-do {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  margin: 8px 0;
}

.to-do input[type="checkbox"] {
  margin-top: 4px;
  width: 16px;
  height: 16px;
  cursor: pointer;
}

.to-do .checked {
  text-decoration: line-through;
  opacity: 0.6;
}

/* Callout block */
.callout {
  background: var(--jotion-surface);
  border-radius: 8px;
  padding: 16px;
  margin: 16px 0;
  display: flex;
  gap: 12px;
  border-left: 4px solid var(--jotion-primary);
}

/* Code block */
.code-block {
  background: #1e1e1e;
  border-radius: 8px;
  padding: 16px;
  font-family: var(--usx-font-mono, monospace);
  font-size: 14px;
  overflow-x: auto;
  margin: 16px 0;
}

/* Document footer */
.document-footer {
  max-width: 900px;
  margin: 0 auto;
  padding: 32px 24px 64px;
  border-top: 1px solid var(--jotion-border);
  color: var(--jotion-text-muted);
  font-size: 14px;
}

.footer-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.published-badge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 4px 8px;
  background: var(--jotion-primary);
  color: white;
  border-radius: 16px;
  font-size: 12px;
}

/* Loading state */
.jotion-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100vh;
  background: var(--jotion-bg);
  color: var(--jotion-text);
  font-family: var(--usx-font-mono, monospace);
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 3px solid var(--jotion-border);
  border-top-color: var(--jotion-primary);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin-bottom: 16px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Dark mode overrides */
.dark {
  --jotion-bg: #191919;
  --jotion-surface: #2f2f2f;
  --jotion-text: #e9e9e7;
  --jotion-border: #3d3d3d;
}

/* Responsive design */
@media (max-width: 768px) {
  .navigation-sidebar {
    position: fixed;
    transform: translateX(-100%);
    transition: transform 0.2s ease;
  }
  
  .navigation-sidebar.mobile-open {
    transform: translateX(0);
  }
  
  .main-content {
    margin-left: 0;
  }
  
  .document-header,
  .block-editor,
  .document-footer {
    padding-left: 16px;
    padding-right: 16px;
  }
  
  .document-title {
    font-size: 24px;
  }
}
```

---

## Part 8: Integration Configuration

### 8.1 Next.js Configuration for uCode3

```typescript
// surfaces/jotion/next.config.js
/** @type {import('next').NextConfig} */
const nextConfig = {
  experimental: {
    appDir: true,
  },
  images: {
    domains: ['files.edgestore.dev'],
  },
  // USX integration
  env: {
    USX_SURFACE_ID: 'jotion-document-workspace',
    USX_SKIN_ID: 'jotion-notion-skin',
    USX_ROUTER_ENDPOINT: '/api/usx/router',
  },
  // Webpack aliases for USX
  webpack: (config) => {
    config.resolve.alias['@usx'] = path.resolve(__dirname, 'usx');
    config.resolve.alias['@lens'] = path.resolve(__dirname, 'lens');
    config.resolve.alias['@skin'] = path.resolve(__dirname, 'skin');
    return config;
  },
};

module.exports = nextConfig;
```

### 8.2 USX API Route

```typescript
// surfaces/jotion/router/api/route.ts
import { NextRequest, NextResponse } from 'next/server';
import { getLensState } from '@usx/lens';
import { transformRouter } from '@usx/router';

export async function POST(req: NextRequest) {
  const body = await req.json();
  const { action, surface, lens_update } = body;
  
  switch (action) {
    case 'sync_lens':
      const currentLens = await getLensState('jotion-document-workspace');
      const routedSkin = await transformRouter(currentLens, 'jotion-router');
      return NextResponse.json({
        success: true,
        lens: currentLens,
        skin: routedSkin
      });
      
    case 'update_document':
      // Update Convex document
      const { documentId, updates } = lens_update;
      // ... Convex mutation
      return NextResponse.json({ success: true });
      
    default:
      return NextResponse.json({ error: 'Unknown action' }, { status: 400 });
  }
}
```

### 8.3 Docker Compose for uCode3 Jotion Surface

```yaml
# surfaces/jotion/docker-compose.jotion.yml
version: '3.8'

services:
  jotion:
    build:
      context: .
      dockerfile: Dockerfile.jotion
    image: ucode3-jotion:latest
    container_name: ucode3-jotion
    ports:
      - "3002:3000"
    volumes:
      - ./jotion:/app
      - ./usx:/app/usx
    environment:
      - NODE_ENV=production
      - CONVEX_DEPLOYMENT=${CONVEX_DEPLOYMENT}
      - NEXT_PUBLIC_CONVEX_URL=${NEXT_PUBLIC_CONVEX_URL}
      - NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=${NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY}
      - CLERK_SECRET_KEY=${CLERK_SECRET_KEY}
      - EDGE_STORE_ACCESS_KEY=${EDGE_STORE_ACCESS_KEY}
      - EDGE_STORE_SECRET_KEY=${EDGE_STORE_SECRET_KEY}
      - USX_SURFACE_API=http://ucode-usx-router:3001
    depends_on:
      - convex
      - usx-router
    restart: unless-stopped
    networks:
      - ucode-network

  convex:
    image: getconvex/convex:latest
    container_name: ucode3-convex
    ports:
      - "3210:3210"
    volumes:
      - ./convex:/app
    environment:
      - CONVEX_DEPLOYMENT=${CONVEX_DEPLOYMENT}
    networks:
      - ucode-network

  usx-router:
    image: node:18-alpine
    container_name: ucode-usx-router
    ports:
      - "3001:3001"
    volumes:
      - ./usx-router:/app
    working_dir: /app
    command: node server.js
    networks:
      - ucode-network
    environment:
      - PORT=3001
      - JOTION_ENDPOINT=http://jotion:3000

networks:
  ucode-network:
    driver: bridge
```

---

## Part 9: USX Surface Registration

```typescript
// surfaces/jotion/register.ts
import { registerSurface } from '@usx/core';

export const jotionSurface = registerSurface({
  id: 'jotion',
  name: 'Notion-Style Workspace',
  description: 'Collaborative document editing with block-based editor',
  version: '1.0.0',
  
  // LENS configuration
  lens: {
    schema: './lens/jotion-schema.json',
    defaults: {
      snack_box: {
        workspace: { sidebar_open: true, theme: 'light' },
        features: { real_time_sync: true, infinite_children: true }
      }
    }
  },
  
  // SKIN configuration
  skin: {
    schema: './skin/jotion-skin.json',
    themes: ['light', 'dark'],
    fonts: ['Inter', 'SF Mono']
  },
  
  // Router configuration
  router: {
    endpoint: '/api/usx/router',
    transforms: './router/jotion-transforms.ts'
  },
  
  // Component mapping
  components: {
    main: './components/JotionSurface',
    sidebar: './components/NavigationSidebar',
    editor: './components/DocumentEditor'
  },
  
  // Routes
  routes: {
    '/': { component: 'DocumentList' },
    '/document/:id': { component: 'DocumentEditor', props: { fullPage: true } },
    '/trash': { component: 'TrashCan' },
    '/settings': { component: 'Settings' }
  }
});
```

---

## Part 10: Complete USX Surface Definition

```json
{
  "open_box": {
    "id": "jotion-ucode3-surface",
    "type": "application/vnd.usx.surface",
    "version": "1.0.0",
    "surface": "ucode3",
    "framework": "next.js"
  },
  "meta": {
    "title": "Jotion Notion Clone",
    "description": "Full-featured document workspace for uCode3",
    "author": "PerHac13 + uCode Team",
    "repository": "https://github.com/PerHac13/jotion"
  },
  "lens": {
    "ref": "lens://jotion-document-workspace/variables",
    "snack_box": {
      "document": {
        "title": "Welcome to uCode3",
        "content": { "type": "doc", "content": [] },
        "icon": "📄",
        "is_published": false
      },
      "workspace": {
        "sidebar_open": true,
        "theme": "light"
      }
    }
  },
  "skin": {
    "ref": "skin://jotion-notion-skin/output",
    "colors": {
      "primary": "#2e7d64",
      "background": "#ffffff",
      "text": "#37352f"
    },
    "typography": {
      "body": "Inter",
      "mono": "SF Mono"
    }
  },
  "features": [
    "real-time-database",
    "infinite-children",
    "trash-can",
    "file-management",
    "live-icons",
    "expandable-sidebar",
    "mobile-responsive",
    "web-publishing",
    "cover-images",
    "recover-deleted"
  ],
  "deployment": {
    "type": "docker-compose",
    "file": "docker-compose.jotion.yml",
    "port": 3002,
    "health_check": "/api/health"
  }
}
```

---

## Part 11: Implementation Roadmap

### Phase 1: Foundation (Week 1)
- [ ] Clone Jotion repository into `surfaces/jotion/`
- [ ] Set up Convex deployment and environment variables
- [ ] Configure Clerk authentication
- [ ] Verify local development environment

### Phase 2: USX Wrapper (Week 2)
- [ ] Create LENS schema and variable bindings
- [ ] Create SKIN schema with Notion theme tokens
- [ ] Implement Router transforms
- [ ] Build JotionSurface wrapper component

### Phase 3: Integration (Week 3)
- [ ] Wire USX API routes
- [ ] Implement Docker Compose configuration
- [ ] Set up uCode3 slot mappings (64-70)
- [ ] Test surface registration

### Phase 4: Polish (Week 4)
- [ ] Responsive design verification
- [ ] Dark mode testing
- [ ] Performance optimization
- [ ] Documentation completion

---

## Part 12: Feature Matrix

| Feature | Jotion Core | USX LENS | USX SKIN | USX Router |
|---------|-------------|----------|----------|------------|
| Document Editing | ✅ BlockNote | ✅ Content