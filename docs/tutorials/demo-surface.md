# Demo Surface

A demonstration USXD surface showing the basic structure.

```usxd
SURFACE name="demo-surface" version="1.0.0"

STYLE
background: "#000000"
color: "#00FF00"
typography: "ui-monospace, monospace"

REGIONS
header: "Demo Surface Header"
content: "Main Content Area"
footer: "Status Footer"

CONTROLS
esc: quit
ctrl+r: refresh
ctrl+h: help
```

```grid size="12x6"
┌──────────────────┐
│ Demo Surface     │
├──────────────────┤
│                  │
│  Content Area    │
│                  │
├──────────────────┤
│ Status: Ready    │
└──────────────────┘
```