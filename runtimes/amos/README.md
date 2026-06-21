# uCode2 — ProseUI

**Beautiful GFM markdown learning environment.**

uCode2 is a thin shim that provides the **ProseUI** surface — a full-featured markdown editor, document viewer, and learning environment. The canonical source lives in [uConnect](https://github.com/uDosGo/uConnect).

## What This Repo Provides

- `bin/ucode2-binder` — CLI entry point that launches ProseUI
- *(AMOS shim moved to uCode1 `core_py/bbc/amos_shim.bbc`)*

## Architecture

uCode2 is intentionally thin — it's a **pointer repo** that delegates to uConnect's ProseUI surface:

```
uCode2 (this repo)
  └── thin shim → uConnect/ui/src/surfaces/proseui/
```

## Quick Start

```bash
# Install
pip install ucode2

# Launch ProseUI
ucode2
```

## License

MIT — see [LICENSE](LICENSE).

## Part of uDos Ecosystem

uCode2 is part of the [uDosGo](https://github.com/uDosGo) open-source ecosystem:

- **uCode1** — Grid/Cell foundation, BBC BASIC, Teletext
- **uCode2** — ProseUI markdown learning (you are here)
- **uServer** — Always-on local hosting (intranet)
- **uConnect** — UI Hub, Snackbar, surfaces, USX design system

All uCode1 + uCode2 remain **open source forever** — no cloud, no payment, no tracking.
