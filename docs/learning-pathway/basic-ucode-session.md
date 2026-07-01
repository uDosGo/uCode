# Basic uCODE Session

Use this example to exercise the current `uDOS-shell` Go TUI.

## Start The Shell

```bash
go run ./cmd/ucode
```

Or build once and run:

```bash
go build -o ucode ./cmd/ucode && ./ucode
```

## Example Inputs

```text
#binder create shell-activation
#wizard assist topic:shell
? summarize the current workflow state
contract workflow-state
contract grid-place
grid seed places
workflow state demo-workflow
workflow action demo-workflow advance
automation queue runtime.command-registry
automation result <job-id>
session workflows
session jobs
session history
ls missing-directory
open workspace
exit
```

## Keybinding Quickstart

| Key | Effect |
|---|---|
| Enter | Submit command |
| Backspace | Delete previous character |
| Space | Insert a space (command token separator) |
| Left / Right | Move cursor in input |
| Home / End | Jump to start / end of line |
| Ctrl+A / Ctrl+E | Move cursor to start / end |
| Ctrl+U | Delete from start to cursor |
| Ctrl+K | Delete from cursor to end |
| Ctrl+W | Delete previous word |
| Ctrl+L | Redraw screen |
| ? | Toggle help overlay (when input is empty) |
| : | Open command menu |
| / | Enter filter mode (while menu is open) |
| Esc | Close overlay or clear filter |
| Ctrl+C | Exit |

### Command Menu (`:`)

- Press `:` to open the command menu.
- Press `/` to enter filter mode — type to narrow items in real time.
- Press `Esc` to clear the filter without closing the menu.
- On the **Workflow Ledger** selector: press `a` to advance, `p` to pause the highlighted workflow.
- On the **Automation Ledger** selector: press `r` to show the result for the highlighted job.
- Press `Esc` from the root menu to close.

## What To Expect

- namespace-prefixed commands are parsed into namespace, action, and args
- plain commands default to the `system` namespace
- `? <question>` targets the Core-owned local GPT4All assist lane
- `#wizard assist ...` remains the Wizard-owned assist and online API lane
- `#ok route ...` requests a provider-routing decision from Wizard `/ok/route`
- the session history tags assist events by lane so local vs Wizard handling stays visible
- plain CLI commands are attempted first; failed CLI execution falls through to the Core GPT4All lane
- the GPT4All fallback carries a version-locked knowledge stamp from checked-in Core artifacts
- contract-aware prompt commands can inspect Core workflow and automation artifacts
- contract-aware prompt commands can also inspect Grid place, layer, and artifact contracts
- `grid seed <layers|places|artifacts>` inspects starter spatial registries from `uDOS-grid`
- workflow and automation prompt actions keep in-memory session state for the current TUI run
- session ledger commands expose tracked workflows, jobs, and recent transitions
- the selector menu supports real-time filter narrowing via the `/` key
- focused operator actions (advance, pause, result) are available directly on ledger selectors

This keeps the repo boundary clear while the interactive surface matures.
