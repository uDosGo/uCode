# Embedding uCode

uCode provides its core functionality as standalone browser-embeddable bundles. This allows host applications (like uCore) to consume the grid algebra and viewport rendering without needing to manage the full uCode monorepo or internal dependencies.

## Available Embeddables

| Package | Bundle Path | Global Name | Purpose |
|---------|-------------|-------------|---------|
| `@udos/gridcore` | `gridcore.js` | `uDosGridCore` | Grid algebra, coordinates, and cell models. |
| `@udos/viewport-renderer` | `viewport-renderer.js` | `uDosViewportRenderer` | Canvas/DOM rendering, widgets. |

## How to Serve

From the root of the `uCode` repository, run:

```bash
npm run serve:embed
```

This will:
1. Build all packages.
2. Collect the `.global.js` bundles into `dist-embed/`.
3. Start a local server at `http://localhost:8000`.

## How to Consume

### 1. Script Tag (Legacy/Simple)

```html
<script src="http://localhost:8000/gridcore.js"></script>
<script src="http://localhost:8000/viewport-renderer.js"></script>
<script>
  const { Grid } = uDosGridCore;
  const { TerminalWidget } = uDosViewportRenderer;
  
  // Initialize grid and renderer...
</script>
```

### 2. ESM Import (Modern)

The bundles are also available as ESM modules in each package's `dist/index.js`. Host applications using modern bundlers (Vite, Webpack) should ideally consume `@udos/gridcore` and `@udos/viewport-renderer` as npm packages or via local file references in their `package.json`:

```json
"dependencies": {
  "@udos/gridcore": "file:../uCode/packages/gridcore",
  "@udos/viewport-renderer": "file:../uCode/packages/viewport-renderer"
}
```

## Development Flow

When working on uCode:
1. Keep the `uCode` repo independent.
2. Run `npm run build` or `npm run dev` in the packages to update the bundles.
3. If `uCore` is running and consuming the served files, it will receive the updates on refresh.
