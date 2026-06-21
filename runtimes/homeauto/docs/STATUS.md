---
title: "uHOME Server Status"
status: draft
last_updated: 2026-04-22T23:26:13+10:00
category: documentation
tags: [ucode3]
description: "Status: active standalone runtime"
---
# uHOME Server Status

Status: active standalone runtime
Updated: 2026-03-09

## Summary

The standalone `uHOME Server` repository now has its own repo structure,
installer boundary, and decentralized LAN-model contract in place.

## Current Focus

- extend the home-media runtime beyond scaffolded DVR and playback behavior
- keep the standalone server package reliable and locally bootable
- preserve clear repo boundaries between `uHomeNest`, `uDOS`, and
  companion repos

## Next Steps

- add dependency lockfiles for the standalone package
- replace file-backed scheduling behavior with a durable backend
- broaden storage identity and recovery rules beyond current registry records
- document deployment, packaging, and release flows for standalone installs
