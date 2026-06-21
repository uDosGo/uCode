---
title: "uHomeNest monorepo migration"
status: draft
last_updated: 2026-04-22T23:26:13+10:00
category: documentation
tags: [ucode3]
description: "| **uHomeNest** | This **Git repository** and monorepo (**v3.9.x** in root [`VERSION`](../VERSION)). |"
---
# uHomeNest monorepo migration

## Canonical names (uHomeNest **v3.9**)

| Name | Meaning |
| --- | --- |
| **uHomeNest** | This **Git repository** and monorepo (**v3.9.x** in root [`VERSION`](../VERSION)). |
| **uHOME** | **Product** name (household media + LAN server + thin UX). |
| **`uhome-server`** | **Python distribution** / CLI package ([`pyproject.toml`](../pyproject.toml)); installable name stays hyphenated for tooling. |
| **`uHOME-server` (string)** | **Legacy wire / contract** identifiers in some JSON payloads (e.g. `policy_owner`); do not rename without a contract version bump. |
| **Contributor / education briefs** | Canonical files: [`contributor-dev-brief.md`](contributor-dev-brief.md), [`education-dev-brief.md`](education-dev-brief.md). Stubs at `uHOME-server-*-dev-brief.md` redirect for old links. |

## Name and structure (assessment)

**Name:** **uHomeNest** clearly signals a single **nest** for uHOME packages (`server/`, `matter/`, `host/`) without overloading the **uHOME** product trademark in the repo id.

**Structure:** One clone replaces the old **`uHOME-family/`** three-repo layout. Legacy paths (`src/uhome_server/`, `apps/`, `docs/` at repo root) remain alongside **`server/`**, **`matter/`**, and **`host/`** so operators can migrate gradually; boundaries are documented in **`docs/base-runtime-boundary.md`**.

**Thin UX handoff:** Author kiosk-oriented **surface JSON** in sibling **UniversalSurfaceXD** (`interchange/examples/surface-uhome-thin-kiosk.json`, composer **`?sample=uhomeThin`**); implement API-backed UIs in this repo per **`docs/ui/UHOME-DASHBOARD.md`**.

## Engineering (UDN)

Tracked workflow lives under **`dev/`** (`WORKFLOW.md`, `TASK_FORGE.md`, **`UNIVERSAL-DEV.md`**), with **`DEV.md`** and **`TASKS.md`** at repo root. Open **`uHomeNest.code-workspace`** to pair this monorepo with sibling **UniversalSurfaceXD** (USXD).

## Mapping (standalone → monorepo path)

| Old repo (GitHub) | New path | Notes |
| --- | --- | --- |
| `fredporter/uHOME-server` | `server/` | Default path for server docs and Python package |
| `fredporter/uHOME-matter` | `matter/` | Bridge contracts and Matter-facing assets |
| `fredporter/uHOME-client` | `host/` | Renamed folder only; still the **client** runtime in prose |

## Local layout change

Previously, many setups used a parent folder (e.g. `uHOME-family/`) with **three sibling git clones**. That layout is replaced by **one clone** of **uHomeNest** with three subtrees.

A backup of the old sibling folder may exist as `uHOME-family.pre-uHomeNest-monorepo` under `~/Code/` after migration.

## Git history

The first **uHomeNest** commit imports file trees without preserving per-package `git` history in the monorepo. To inspect old line-by-line history, use the archived standalone repositories on GitHub until they are retired.

## Next steps (operator)

1. Create **`https://github.com/fredporter/uHomeNest`** (empty), add `origin`, push this repo.
2. When satisfied, **archive** `uHOME-server`, `uHOME-matter`, and `uHOME-client` on GitHub with a pointer to **uHomeNest**.
3. Update any CI, bookmarks, or docs that still reference the old repo URLs.
