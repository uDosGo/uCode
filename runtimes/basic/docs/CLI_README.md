---
title: "uCode1 CLI — User Guide"
status: active
last_updated: 2026-06-13
category: readme
tags: [ucode1]
description: "uCode1 CLI user guide — the Grid/Cell foundation layer of the uDos ecosystem"
---

# uCode1 CLI — User Guide

## Introduction

Welcome to uCode1 — the **Grid/Cell foundation layer** of the uDos ecosystem. uCode1 provides a BBC BASIC-inspired scripting runtime with a spatial grid/cell system, teletext graphics, and feed operations.

**CLI Command:** `ucode1`

### Layer Boundaries

| Layer | Component | Purpose | CLI |
|-------|-----------|---------|-----|
| **uCode1** | Grid/Cell Foundation | BBC BASIC runtime, grid/cell system, teletext | `ucode1` |
| **uCode2** | ProseUI | GFM markdown learning environment | `ucode2` |
| **uCode3** | Productivity Suite | WYSIWYG editor, collaboration | (commercial) |
| **uCode4** | Spatial/3D | 3D worlds, spatial computing | (commercial) |

## Installation

### Prerequisites

- Python 3.8+
- pip

### Install from source

```bash
git clone https://github.com/uDosGo/uCode1.git
cd uCode1
pip install -e .
```

## Usage

```bash
ucode1 [OPTIONS] [FILE]
ucode1 run <file>          # Run a .bas program
ucode1 snack <command>     # Snack management
ucode1 --repl              # Start interactive REPL
ucode1 --help              # Show help
ucode1 --version           # Show version
```

## Examples

```bash
# Run a BASIC program
ucode1 run examples/01_hello.bas

# Start the REPL
ucode1 --repl

# List snacks
ucode1 snack list
```
