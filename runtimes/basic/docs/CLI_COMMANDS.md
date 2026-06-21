---
title: "uCode1 CLI Command Reference"
status: active
last_updated: 2026-06-13
category: reference
tags: [ucode1]
description: "Complete CLI command reference for uCode1"
---

# uCode1 CLI Command Reference

## Overview

The `ucode1` command is the **runtime and educational interface** for the uCode1 layer of the uDos ecosystem. It provides BBC BASIC scripting, grid/cell management, teletext rendering, and feed operations.

**Layer:** uCode1 — Grid/Cell Foundation

## Usage

```bash
ucode1 <command> [arguments] [flags]
```

## Core Commands

### Program Execution

```bash
ucode1 run <file.bas>
```

Runs a BBC BASIC program file through the Liquid template engine.

### Interactive REPL

```bash
ucode1 --repl
```

Starts an interactive REPL with UDORuntime commands:
- `list_skills` — List available skills
- `list_tasks` — List active tasks
- `list_variables` — List runtime variables
- `run_skill <id>` — Execute a skill by ID

### Snack Management

```bash
ucode1 snack list          # List available snacks
ucode1 snack show <id>     # Show snack details
ucode1 snack create        # Create a new snack
ucode1 snack validate      # Validate a snack file
ucode1 snack run <file>    # Run a snack
ucode1 snack test          # Test snack functionality
```

## Options

| Flag | Description |
|------|-------------|
| `--help` | Show help message |
| `--version` | Show version |
| `--repl` | Start interactive REPL |
| `--debug` | Enable debug output |
