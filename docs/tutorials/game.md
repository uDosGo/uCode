# Game Console

A surface designed for game interfaces with interactive controls.

```usxd
SURFACE name="game" version="1.0.0"

STYLE
background: "#000000"
color: "#FF5722"
typography: "ui-monospace, Press Start 2P, monospace"
font-size: "16px"
letter-spacing: "1px"

REGIONS
header: "Game Console - Level 1"
map: "Game Map Area"
stats: "Player Stats"
inventory: "Inventory"
controls: "Control Instructions"
footer: "Score: 0 | Lives: 3"

CONTROLS
w: move-up
s: move-down
a: move-left
d: move-right
space: jump
enter: select
esc: pause
ctrl+q: quit
up: menu-up
down: menu-down
```

```grid size="20x12" mode="game"
┌──────────────────────┐
│ Game Console - Lvl 1 │
├──────────────────────┤
│                      │
│   [GAME MAP AREA]    │
│                      │
├──────┬───────────────┤
│ Stats│ Inventory     │
├──────┴───────────────┤
│ W=↑ A=← D=→ S=↓       │
│ Space=Jump Enter=OK  │
└──────────────────────┘
```