# Grid Algebra Release Collation (v2.0 -> v2.1)

Date: 2026-06-22  
Status: Locked architecture translated to package scaffolds

## Scope

This collates the live Grid Algebra implementation points from uCore and maps them to the new uCode packages:

- @udos/gridcore
- @udos/viewport-renderer

## Source Index (uCore)

1. frontend/src/surfaces/gridui/grid-algebra/GridCell.ts
- Cell shape and GridBuffer creation
- Buffer dimension utilities

2. frontend/src/surfaces/gridui/grid-algebra/GridTransform.ts
- Pure transforms: resize, overlay, scroll, crop, merge, fill, writeString

3. frontend/src/surfaces/gridui/grid-algebra/SpatialCodec.ts
- uCode <-> lat/lon conversion (Web Mercator)
- zoom-level cell size and navigation helpers

4. frontend/src/surfaces/gridui/grid-algebra/TeletextPage.ts
- Teletext page store and page construction patterns

5. frontend/src/surfaces/gridui/panels/GridBufferRenderer.tsx
- DOM grid rendering path and font/color application

6. frontend/src/surfaces/gridui/GridUIStore.ts
- Viewport settings and border mode behavior

7. docs/DOCLANG_BRIDGE_EXPORT_SPEC.md
- Spatial fields alignment: ucode, layer, zoom_level

## Legacy Archive Scan Status

The following requested archive roots were not found on this machine during implementation:

- /Users/fredbook/Code/uCode1
- /Users/fredbook/Code/UniversalSketchSVG
- /Users/fredbook/Code/ThinUI

To avoid blocking the release track, collation used live uCore implementations and existing in-repo specs as source-of-truth inputs.

## Package Mapping

### @udos/gridcore

Implemented in uCode/packages/gridcore:

- src/geometry/cell.ts
- src/geometry/grid.ts
- src/geometry/layer.ts
- src/geometry/cube.ts
- src/coordinates/uCode.ts
- src/coordinates/latLon.ts
- src/viewport/calculator.ts
- src/teletext/mosaic.ts
- src/teletext/block2x3.ts

Current state:
- Pure TypeScript math/data package scaffold
- No rendering dependency
- Includes smoke tests for grid creation, uCode conversions, and viewport sizing

### @udos/viewport-renderer

Implemented in uCode/packages/viewport-renderer:

- src/core/ViewportWidget.ts
- src/core/widgets.ts (TerminalWidget, TeletextWidget)
- src/canvas/CanvasViewport.ts
- src/dom/DOMViewport.ts
- src/fonts/petme64.ts
- src/fonts/teletext50.ts
- src/palette/usx.ts
- src/effects/crt.ts
- src/animation/sprite.ts
- src/animation/bob.ts

Current state:
- Embeddable renderer scaffold wired to @udos/gridcore
- DOM and Canvas rendering classes in place
- Widget wrappers for wrapper-only GridUI migration path

## Locked Decisions Preserved

1. Separation of concerns
- Algebra and coordinate logic isolated in gridcore.
- Rendering concerns isolated in viewport-renderer.

2. Wrapper-only GridUI direction
- Terminal and Teletext represented as widget instances.
- Border modes remain surface-level controls.

3. Packaging
- Both packages scaffolded for ESM + CJS via tsup.
- npm workspace created at uCode/package.json with packages/*.

## Known Gaps Before Publish

1. gridcore parity gaps
- Existing uCore transform helpers (resize/overlay/scroll/etc.) are not yet fully ported into the new package namespace.

2. renderer hardening gaps
- Canvas code currently browser-canvas-first; node-canvas server rendering path should be finalized.
- Font loading pipeline and glyph metrics calibration still pending.

3. compatibility/migration gaps
- uCore GridUI is not yet switched to consume published @udos packages.
- Migration guide and integration tests still required.

## Next Release Actions

1. Port remaining transforms from GridTransform.ts into @udos/gridcore.
2. Add viewport snapshot tests (Terminal and Teletext fixture grids).
3. Add node-canvas rendering path and PNG baseline tests.
4. Wire uCore GridUI to import package builds rather than local grid-algebra files.
5. Publish @udos/gridcore and @udos/viewport-renderer at 1.0.0.
