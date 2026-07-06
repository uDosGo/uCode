# BBCSDL Engine Package

Bundled BBCSDL interpreter and core libraries for the uCode BASIC runtime.

## Layout

```
bbcsdl/
  bbcsdl          -- BBCSDL executable binary
  lib/            -- Core libraries (gfxlib, imglib, audiolib, etc.)
  examples/       -- Sample .bbc programs
```

## Assembly

The `assemble.mjs` script collects the BBCSDL binary and its companion libraries
into a single distributable directory for the `@udos/bbcsdl-engine` package.

```bash
npm run assemble