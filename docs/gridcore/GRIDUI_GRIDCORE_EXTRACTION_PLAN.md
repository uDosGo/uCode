# GridUI -> GridCore Extraction Plan

Date: 2026-06-22  
Status: In progress

## Objective

Refactor GridUI into a thin wrapper surface while moving reusable algebra and viewport rendering into uCode packages:

- @udos/gridcore
- @udos/viewport-renderer

## Current Implementation Pivots

1. Algebra and coordinate logic lives under:
- frontend/src/surfaces/gridui/grid-algebra/

2. Rendering path currently lives under:
- frontend/src/surfaces/gridui/panels/GridBufferRenderer.tsx
- frontend/src/surfaces/gridui/panels/TerminalPanel.tsx
- frontend/src/surfaces/gridui/panels/TeletextGrid.tsx

3. Surface-level viewport and border behavior lives under:
- frontend/src/surfaces/gridui/GridUIStore.ts

## Archive Source Availability

Requested legacy paths were audited in the local development machine context:

- /Users/fredbook/Code/uCode1
- /Users/fredbook/Code/UniversalSketchSVG
- /Users/fredbook/Code/ThinUI

Result: these paths were not present in the current environment, so the collation baseline for this release was built from live uCore sources plus the locked architecture briefs.

## Border Modes

Current in-code values:
- mode 1: fillFraction 0.90
- mode 2: fillFraction 0.95
- mode 3: fillFraction 0.99

Locked release target values:
- mode 1: fillFraction 0.80
- mode 2: fillFraction 0.90
- mode 3: fillFraction 0.98

Action: align at integration cutover so all widgets share one behavior contract.

## Migration Steps

1. Extract
- Move and normalize algebra primitives into @udos/gridcore.
- Move and normalize rendering primitives into @udos/viewport-renderer.

2. Adapt
- Introduce wrapper widget contracts in GridUI surface.
- Replace panel-local layout/renderer logic with widget calls.

3. Validate
- Teletext page render parity (color, flash, mosaic blocks).
- Terminal render parity (font, sizing, crispness, scrolling).

4. Publish
- Pin frontend to @udos package versions.
- Remove duplicated local grid-algebra render loops.

## Release Artifacts

- uCode/docs/GRID_ALGEBRA_RELEASE_COLLATION.md
- uCode/packages/gridcore/*
- uCode/packages/viewport-renderer/*
