# Unit 01 — uHOME basics

A short orientation for the **uHOME-server** repo and how it sits next to the
uDOS family.

## What uHOME is

- Household **media**, **controller-first kiosk / thin UI**, and **LAN server**
- **Linux** is the uHOME orchestration host; optional **Windows + Steam** is a
  non-authoritative gaming/desktop side (see `docs/architecture.md`)
- **Install / recovery / dual-boot** bootstrap is **`sonic-screwdriver`**, not
  Wizard-first flows

## Where to read next

| Lane | Purpose |
| --- | --- |
| [`docs/`](../docs/README.md) | Stable reference: architecture, clients, ops |
| [`wiki/`](README.md) | Short units and quick starts (you are here) |
| [`learning/`](../learning/README.md) | Study order, courses pointers, uDOS Library links |

## Family docs

- **Stream boundaries and sequencing:** [`uDOS-dev` `docs/uhome-stream.md`](https://github.com/fredporter/uDOS-dev/blob/main/docs/uhome-stream.md)
- **Public library (GitHub Pages):** [uDOS Library — Learning hub](https://fredporter.github.io/uDOS-docs/learning.html) (when Pages is deployed)

## Checklist

- [ ] Read `docs/pathway/README.md` for repo positioning
- [ ] Read `docs/architecture.md` for topology and services
- [ ] Run `QUICKSTART.md` or `FIRST-TIME-INSTALL.md` for a local smoke path
