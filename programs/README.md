# uCode Programs — Classic Game Adaptations

5 classic programs adapted for the uCode platform (BBC BASIC for SDL 2.0 + AMOS Runtime add-on).

## Program Catalog

| Program | Approach | Effort | Est. Weeks | Status |
|---------|----------|--------|------------|--------|
| [Elite](elite/) | Adapt 6502 source (BeebAsm) | Medium | 3 | 🏗 Scaffold |
| [NetHack](nethack/) | Adapt C source → BBC BASIC | Medium | 3 | 🏗 Scaffold |
| [Repton](repton/) | Adapt 6502 source + clones | Small | 2 | 🏗 Scaffold |
| [Knight Orc](knight-orc/) | Rewrite (inspired by KAOS engine) | Large | 10 | 🏗 Scaffold |
| [Apple Panic](apple-panic/) | Rewrite (inspired by Space Panic) | Small | 2 | 🏗 Scaffold |

## Program Structure

Each program follows the canonical layout:

```
programs/<name>/
├── program.yaml          # Manifest (required)
├── src/                  # Source code (BBC BASIC, 6502 ASM, etc.)
├── assets/
│   ├── sprites/          # Character/sprite assets
│   └── sounds/           # WAV audio files
├── lens/                 # LENS extractor modules
├── skin/                 # SKIN theme definitions
├── mcp/                  # MCP command specifications
└── test/                 # Integration tests
```

## Build Order

1. **Repton** (smallest, fastest win — validates 6502 pipeline)
2. **Apple Panic** (small rewrite — validates BBC BASIC game loop)
3. **Elite** (medium adaptation — validates BeebAsm + LENS/MCP)
4. **NetHack** (medium adaptation — validates C→BBC BASIC port)
5. **Knight Orc** (large rewrite — validates full game design pipeline)

## Skills Required

| Skill | Used By | Status |
|-------|---------|--------|
| Source-Miner | Elite, Repton | Spec defined |
| LENS-Craft | All 5 | Spec defined |
| MCP-Scribe | All 5 | Spec defined |
| SKIN-Weaver | All 5 | Spec defined |
| Inspire-Engine | Knight Orc, Apple Panic | Spec defined |