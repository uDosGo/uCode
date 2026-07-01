# uCode Student Pathway — Updated for uCode v2

## Overview

uCode is the BBC BASIC for SDL 2.0 runtime environment with Python orchestration, AMOS shim compatibility, and Snack container packaging. The student pathway guides learners from "Hello World" to publishing their own games and tools.

**Runtime:** BBCSDL engine + Python bridge + AMOS shim
**Tooling:** `ucode` CLI, Vault, Snack containers, LENS/SKIN
**Output:** Teletext (MODE 7), sprites (BOBs), story forms (Marp), grid worlds

---

## Part 1: Student Intake Funnel

```
DISCOVERY CHANNELS
├── GitHub Education (Learning Path, Student Pack)
├── freeCodeCamp (BBC BASIC tutorial series)
├── YouTube (Build-along videos)
├── Dev.to (Article series)
└── Discord / Word of mouth
                ▼
ORIENTATION (Course 00) — 15 min
├── "What is uCode?" (BBC BASIC, teletext, sprites, grids)
├── "Your First Vault" (hands-on: ~/Vault/)
├── "The BBC BASIC REPL" (run, print, mode 7)
└── Checkpoint: `ucode verify orientation`
                ▼
LEVEL 1: BBC BASIC Foundations (2-3 hours)
LEVEL 2: Teletext & Grids (4-5 hours)
LEVEL 3: Sprites, BOBs & Games (6-8 hours)
LEVEL 4: Snack Containers & Publishing (8-10 hours)
LEVEL 5: Grid Worlds & Spatial Algebra (10-12 hours)
                ▼
CONTRIBUTOR ON-RAMP
├── Earn "Vault Keeper", "Sprite Master", "Grid Cartographer" badges
├── First PR: docs fix, snack example, or spatial contribution
└── Invited to Dev Lane (#ucode-dev channel)
```

---

## Part 2: Skill Progression

| Level | Skills Acquired | Badge | Output |
|-------|----------------|-------|--------|
| **Orientation** | Vault structure, BBC BASIC REPL, MODE 7 basics | `orientation-complete` | First .ucode script |
| **Level 1** | Variables, loops, conditionals, PRINT, INPUT | `basic-coder` | Calculator, quiz game |
| **Level 2** | MODE 7 teletext, grid algebra, character sets | `teletext-operator` | Teletext page, menu screen |
| **Level 3** | Sprites, BOBs, collision, sound, animation | `sprite-master` | Platformer or shoot-em-up |
| **Level 4** | Snack containers, manifest, assets, LENS capture | `snack-publisher` | Published .snack |
| **Level 5** | Grid worlds, spatial algebra, voxel mapping, pathfinding | `grid-cartographer` | Game world with layers |

---

## Part 3: BBC BASIC Quick Reference (Levels 1-2)

### Your First Program
```bbcbasic
10 REM Hello uCode
20 MODE 7
30 COLOUR 2
40 PRINT TAB(10,12); "Hello, uCode!"
50 END
```

### Variables & Input
```bbcbasic
10 INPUT "What is your name? ", name$
20 PRINT "Hello, "; name$
30 age% = 42
40 PRINT "You are "; age%; " years old"
```

### Teletext Grid (MODE 7)
```bbcbasic
10 MODE 7
20 COLOUR 1  : REM Red text
30 PRINT TAB(5,5); "MENU"
40 COLOUR 3  : REM Cyan text
50 PRINT TAB(5,7); "1. Play"
60 PRINT TAB(5,8); "2. Options"
70 PRINT TAB(5,9); "3. Quit"
```

---

## Part 4: Sprite & Game Reference (Levels 3-4)

### Sprites (GFXLIB)
```bbcbasic
10 INSTALL @lib$ + "gfxlib"
20 PROC_gfx_init(640, 480, 32)
30 sprite% = FN_load_sprite("player.chr", 24, 24)
40 PROC_sprite_place(sprite%, 100, 200)
```

### BOBs (IMGLIB)
```bbcbasic
10 INSTALL @lib$ + "imglib"
20 bob% = FN_load_gif("explosion.gif")
30 PROC_bob_create(bob%, 200, 150)
40 PROC_bob_animate(bob%, 0, -1)  : REM Loop forever
```

### Collision Detection
```bbcbasic
100 IF FN_sprite_bob_collide(sprite%, bob%) THEN
110   PRINT "HIT!"
120   SOUND 1, 15, 200, 10
130 ENDIF
```

---

## Part 5: AMOS Shim Reference (Level 4)

```bbcbasic
10 INSTALL "amos_shim.bbc"
20 SPRITE 1, 100, 100, 1
30 BOB 1, 200, 150, 2
40 SOUND 1, 10, 100, 50
50 REPEAT
60   MOVE 1, 300, 200, 20
70   IF COLL(1,1) THEN PRINT "COLLISION!"
80   WAIT VBL
90 UNTIL 0
```

---

## Part 6: Snack Publishing (Level 4-5)

### Snack Container Structure
```
my-game.snack/
├── main.ucode
├── manifest.yaml
├── sprites/player.chr
├── bobs/explosion.gif
├── sounds/coin.wav
└── maps/level1.json
```

### Publishing Command
```bash
ucode snack create my-game --template game
ucode snack build my-game
ucode snack publish my-game.snack
```

### LENS Capture (Game State)
```bash
ucode lens capture my-game.snack --output state.json
```

### SKIN Transformation
```bash
ucode skin apply my-game.snack dark_mode
```

---

## Part 7: Grid World Building (Level 5)

```bash
# Create a dungeon world
gridsmith world create --name "Lost Caverns" --type dungeon --seed 42

# Create a grid
gridsmith grid create --cols 80 --rows 24

# Import a BASIC program as a world
gridsmith world import --program examples/adventure.bas --world "Adventure"

# Convert real-world coordinates to uCode spatial algebra
gridsmith location latlon-to-ucode --lat -33.8688 --lon 151.2093
```

---

## Part 8: Checkpoint System

Each checkpoint is verified via `ucode checkpoint verify <id>`:

```yaml
# checkpoints/01-hello-world.yaml
id: hello-world
name: "Hello World Checkpoint"
commands:
  - cmd: "test -f ~/Vault/programs/hello.ucode"
    pass: "hello.ucode exists"
  - cmd: "grep -q 'MODE 7' ~/Vault/programs/hello.ucode"
    pass: "Uses MODE 7 teletext"
badge: "basic-coder"
```

---

## Part 9: Course 101-301 (Benchoff Curriculum)

### Course 101: Foundations of Modern Retrocomputing
- **Module 1:** Quarter-Scale BeBox — 3D printing, GPIO, Python scripting
- **Module 2:** $15 Linux Handheld — BOM, Buildroot, PCB design, embedded Linux
- **Module 3:** Portable VT100 Dumb Terminal — firmware, ANSI parser, RS-232, product design

### Course 201: Advanced Interfaces & Useless Machines
- **Module 1:** 15-Drive Zip Tower — reverse engineering, PCB cloning, power distribution
- **Module 2:** CNCPong — game logic, real-time control, digital→physical mapping
- **Module 3:** Finite Atari Machine — CUDA, heuristic algorithms, emulator automation

### Course 301: Protocols, Security & Pure Fun
- **Module 1:** TerminalPython — serial protocols, Python/PySerial, vintage SBCs
- **Module 2:** MacSSL — TLS on 68K, retrocomputing, entropy collection
- **Module 3:** Nedry ("Ah, ah, ah!") — cross-platform concept, polished execution

---

## Part 10: Quick Reference Card

```bash
# For students
ucode run hello.ucode
ucode snack run my-game.snack
ucode checkpoint verify hello-world
ucode dashboard update

# For teachers
ucode badge grant basic-coder --to student-alice
ucode course validate courses/01-basic-foundations/

# For contributors
git clone https://github.com/uDosGo/uCode
ucode docs validate --file docs/tutorials/hello-world.md
gh pr create --title "docs: add hello world tutorial"
```

---

*Pathway adapted for uCode v2 — BBC BASIC for SDL 2.0. Benchoff curriculum preserved as Courses 101-301.*