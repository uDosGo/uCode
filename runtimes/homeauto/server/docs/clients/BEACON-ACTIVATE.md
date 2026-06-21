# Beacon Activate

## Purpose

Describe the active v2 role of Beacon-facing local access in `uHomeNest`.

This document promotes the useful Beacon concept from the archive without
bringing forward the old repo ownership model unchanged.

## Current Ownership

`uHomeNest` owns:

- local-network access surfaces
- living-room or tablet-safe portal entry points
- Thin GUI and kiosk-safe presentation shells
- Vault Reader presentation on nearby devices
- curated offline-content surfaces presented behind Beacon Activate

`uDOS-wizard` owns:

- broader networking contracts
- online provider bridges
- wider control-plane transport rules
- the Beacon Activate Wi-Fi offer and local access handoff
- browser workflow and operator control surfaces

## Core Rule

Beacon is an access and handoff surface, not a data store.

`Beacon Activate` is the local Wi-Fi connection and portal experience offered
by Wizard. It introduces the user to `uHomeNest` surfaces that can:

- show approved vault content on a TV or tablet
- present a host-curated offline information library
- route nearby clients into safe household interfaces

The Beacon host user chooses what information is compiled and presented.

## Design Principles

- presence over storage
- local-first access
- replaceable entry hardware
- graceful degradation when richer services are offline
- no confusion between portal access and canonical vault ownership

## Recommended Surface Split

### Beacon Portal

Use for:

- announcing local `uHOME` presence
- offering a nearby Wi-Fi connection
- directing nearby users to a portal or local URL
- exposing a simple landing surface for household-safe clients
- introducing nearby users to curated offline content

### Vault Reader

Use for:

- TV-safe or tablet-safe reading of curated markdown content
- binder or document viewing that does not imply edit ownership
- room-oriented local presentation

## Shared Render Rule

Beacon Activate does not require a completely separate rendering stack.

Shared IO or render modules may serve:

- the Wizard web publishing contract
- the Beacon Activate local portal library contract

The difference is the delivery surface and runtime ownership, not necessarily
the renderer module itself.

## Failure Model

If the richer local runtime is degraded, the portal should still communicate:

- that the local node exists
- whether the requested surface is temporarily unavailable
- whether the user should retry locally later

Do not move canonical data into the portal layer just to survive failure.

## Relationship To Home Automation

These Beacon Activate surfaces are separate from:

- Home Assistant bridges
- Matter or device-control automation
- Wizard- or Ubuntu-hosted online surfaces that are outside the uHOME stream

Those systems may appear behind the portal, but they are not the same contract.

## Near-Term Documentation Goal

As `uHomeNest` implementation hardens, this doc should grow into:

- portal URL and Beacon Activate guidance
- approved client modes
- local access policy
- household-safe content projection rules
- host-curated offline library packaging guidance

Household networking policy for **regular LAN** operation is exposed through:

- `GET /api/runtime/contracts/uhome-network-policy`
- `GET /api/runtime/contracts/uhome-network-policy/schema`
- `POST /api/runtime/contracts/uhome-network-policy/validate`

`uHomeNest` ships the contract and schema; the default profile is **`lan`**.
Future work may link profiles to **uDOS-ubuntu** command-centre networking.
