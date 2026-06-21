/**
 * USX Live Preview Server
 * 
 * HTTP + WebSocket server that serves rendered USX bundles
 * and supports live reload on file changes.
 * 
 * Usage: node src/server.js [bundle-dir] [port]
 *   --watch    Watch bundle directory for changes
 *   --port     Server port (default: 3333)
 */

import { createServer } from 'http';
import { readFileSync, existsSync, readdirSync } from 'fs';
import { resolve, extname } from 'path';
import { fileURLToPath } from 'url';
import { dirname } from 'path';

const __dirname = dirname(fileURLToPath(import.meta.url));

// ─── Configuration ─────────────────────────────────────────────────

const PORT = parseInt(process.env.USX_PORT || process.argv[3] || '3333', 10);
const BUNDLE_DIR = resolve(process.argv[2] || process.cwd());
const WATCH_MODE = process.argv.includes('--watch');

// ─── Bundle Cache ──────────────────────────────────────────────────

const bundleCache = new Map();
let currentBundleId = null;

/**
 * Load and cache a USX bundle.
 */
function loadBundle(filePath) {
  try {
    const content = readFileSync(filePath, 'utf-8');
    const bundle = JSON.parse(content);
    bundleCache.set(bundle.id, { bundle, filePath, mtime: Date.now() });
    currentBundleId = bundle.id;
    return bundle;
  } catch (err) {
    console.error(`❌ Failed to load bundle: ${err.message}`);
    return null;
  }
}

/**
 * Find and load the first .usx file in a directory.
 */
function findAndLoadBundle(dir) {
  try {
    const files = readdirSync(dir);
    const usxFile = files.find(f => f.endsWith('.usx') || f.endsWith('.usx.json'));
    if (usxFile) {
      return loadBundle(resolve(dir, usxFile));
    }
  } catch {}
  return null;
}

// ─── HTTP Server ───────────────────────────────────────────────────

const MIME_TYPES = {
  '.html': 'text/html',
  '.css': 'text/css',
  '.js': 'application/javascript',
  '.json': 'application/json',
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.svg': 'image/svg+xml',
  '.ico': 'image/x-icon'
};

const server = createServer(async (req, res) => {
  const url = new URL(req.url, `http://localhost:${PORT}`);
  const path = url.pathname;

  // API: List available bundles
  if (path === '/api/bundles') {
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({
      bundles: Array.from(bundleCache.entries()).map(([id, { bundle }]) => ({
        id: bundle.id,
        name: bundle.name,
        description: bundle.description,
        source: bundle.source?.tool
      })),
      current: currentBundleId
    }));
    return;
  }

  // API: Get bundle by ID
  if (path.startsWith('/api/bundle/')) {
    const bundleId = path.slice('/api/bundle/'.length);
    const cached = bundleCache.get(bundleId);
    if (cached) {
      res.writeHead(200, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify(cached.bundle));
    } else {
      res.writeHead(404, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ error: 'Bundle not found' }));
    }
    return;
  }

  // API: Reload bundles
  if (path === '/api/reload') {
    bundleCache.clear();
    findAndLoadBundle(BUNDLE_DIR);
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ status: 'reloaded', bundles: bundleCache.size }));
    return;
  }

  // API: Validate a bundle
  if (path === '/api/validate') {
    const bundleId = url.searchParams.get('bundle') || currentBundleId;
    const cached = bundleId ? bundleCache.get(bundleId) : null;
    
    if (cached) {
      try {
        const { validateBundle, formatValidationResult } = await import('../../converter-core/src/validate-schema.js');
        const result = await validateBundle(cached.bundle);
        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify(result, null, 2));
      } catch (err) {
        res.writeHead(500, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ error: `Validation error: ${err.message}` }));
      }
    } else {
      res.writeHead(404, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ error: 'No bundle loaded' }));
    }
    return;
  }

  // Serve rendered bundle
  if (path === '/' || path === '/index.html') {
    const bundleId = url.searchParams.get('bundle') || currentBundleId;
    const cached = bundleId ? bundleCache.get(bundleId) : null;
    
    if (cached) {
      const { renderBundle } = await import('./renderer.js');
      
      // Parse query params as LENS overrides
      const overrides = {};
      for (const [key, value] of url.searchParams) {
        if (key.startsWith('lens.')) {
          overrides[key.slice(5)] = value;
        } else if (key === '_darkMode') {
          overrides._darkMode = value === 'true' || value === '1';
        }
      }
      
      const html = renderBundle(cached.bundle, overrides);
      res.writeHead(200, { 'Content-Type': 'text/html' });
      res.end(html);
    } else {
      // Show bundle selector
      res.writeHead(200, { 'Content-Type': 'text/html' });
      res.end(generateIndexPage());
    }
    return;
  }

  // Serve static files from bundle directory
  const filePath = resolve(BUNDLE_DIR, path.slice(1));
  if (existsSync(filePath)) {
    const ext = extname(filePath);
    const contentType = MIME_TYPES[ext] || 'application/octet-stream';
    try {
      const content = readFileSync(filePath);
      res.writeHead(200, { 'Content-Type': contentType });
      res.end(content);
    } catch {
      res.writeHead(404);
      res.end('Not found');
    }
    return;
  }

  // 404
  res.writeHead(404, { 'Content-Type': 'text/html' });
  res.end('<h1>404 — Bundle not found</h1>');
});

// ─── WebSocket Server ──────────────────────────────────────────────

let wss;

async function setupWebSocket() {
  const { WebSocketServer } = await import('ws');
  wss = new WebSocketServer({ server });
  
  wss.on('connection', (ws) => {
    console.log('🔌 WebSocket client connected');
    
    // Send current bundle info on connect
    ws.send(JSON.stringify({
      type: 'connected',
      bundles: Array.from(bundleCache.keys()),
      current: currentBundleId
    }));
    
    ws.on('close', () => {
      console.log('🔌 WebSocket client disconnected');
    });
  });
}

/**
 * Broadcast a message to all WebSocket clients.
 */
function broadcast(message) {
  if (!wss) return;
  const data = JSON.stringify(message);
  wss.clients.forEach(client => {
    if (client.readyState === 1) { // WebSocket.OPEN
      client.send(data);
    }
  });
}

// ─── File Watching ─────────────────────────────────────────────────

async function setupFileWatcher() {
  if (!WATCH_MODE) return;
  
  const { watch } = await import('chokidar');
  
  const watcher = watch(BUNDLE_DIR, {
    ignored: /(^|[\/\\])\../,
    persistent: true,
    ignoreInitial: true
  });
  
  watcher.on('change', (filePath) => {
    if (filePath.endsWith('.usx') || filePath.endsWith('.usx.json')) {
      console.log(`🔄 Bundle changed: ${filePath}`);
      const bundle = loadBundle(filePath);
      if (bundle) {
        broadcast({
          type: 'bundle_updated',
          bundleId: bundle.id,
          name: bundle.name,
          timestamp: Date.now()
        });
        console.log(`✅ Reloaded: ${bundle.name}`);
      }
    }
  });
  
  console.log(`👀 Watching: ${BUNDLE_DIR}`);
}

// ─── Index Page ────────────────────────────────────────────────────

function generateIndexPage() {
  const bundleList = Array.from(bundleCache.entries()).map(([id, { bundle }]) => `
    <div class="bundle-card" onclick="window.location='/?bundle=${id}'">
      <h3>${bundle.name || id}</h3>
      <p>${bundle.description || 'No description'}</p>
      <span class="source">${bundle.source?.tool || 'manual'} · v${bundle.version}</span>
    </div>
  `).join('');

  return `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>USX Preview Server</title>
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body { font-family: system-ui, sans-serif; background: #f5f5f5; color: #333; padding: 2rem; }
    h1 { margin-bottom: 0.5rem; }
    .subtitle { color: #666; margin-bottom: 2rem; }
    .bundles { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 1rem; }
    .bundle-card { background: white; border: 1px solid #ddd; border-radius: 8px; padding: 1.5rem; cursor: pointer; transition: all 0.2s; }
    .bundle-card:hover { border-color: #0066ff; box-shadow: 0 2px 8px rgba(0,102,255,0.15); transform: translateY(-2px); }
    .bundle-card h3 { margin-bottom: 0.5rem; }
    .bundle-card p { color: #666; font-size: 0.9rem; margin-bottom: 0.5rem; }
    .bundle-card .source { font-size: 0.8rem; color: #999; }
    .empty { text-align: center; padding: 4rem; color: #999; }
    .empty h2 { margin-bottom: 1rem; }
    .status { position: fixed; bottom: 1rem; right: 1rem; background: #333; color: white; padding: 0.5rem 1rem; border-radius: 20px; font-size: 0.8rem; }
  </style>
</head>
<body>
  <h1>🎨 USX Preview Server</h1>
  <p class="subtitle">Port ${PORT} · ${bundleCache.size} bundle(s) loaded</p>
  
  ${bundleCache.size > 0 
    ? `<div class="bundles">${bundleList}</div>`
    : `<div class="empty">
        <h2>No bundles loaded</h2>
        <p>Place .usx files in: <code>${BUNDLE_DIR}</code></p>
        <p>Or run: <code>node src/server.js /path/to/bundles</code></p>
       </div>`
  }
  
  <div class="status" id="status">Connected</div>
  
  <script>
    const ws = new WebSocket('ws://localhost:${PORT}');
    ws.onmessage = (event) => {
      const msg = JSON.parse(event.data);
      if (msg.type === 'bundle_updated') {
        document.getElementById('status').textContent = '🔄 Reloading...';
        setTimeout(() => window.location.reload(), 500);
      }
    };
    ws.onclose = () => {
      document.getElementById('status').textContent = '⚠️ Disconnected';
    };
  </script>
</body>
</html>`;
}

// ─── Startup ───────────────────────────────────────────────────────

async function start() {
  // Load initial bundles
  const initialBundle = findAndLoadBundle(BUNDLE_DIR);
  if (initialBundle) {
    console.log(`📦 Loaded: ${initialBundle.name} (${initialBundle.id})`);
  } else {
    console.log(`📂 No .usx files found in: ${BUNDLE_DIR}`);
  }

  // Setup WebSocket
  await setupWebSocket();

  // Setup file watcher
  if (WATCH_MODE) {
    await setupFileWatcher();
  }

  // Start server
  server.listen(PORT, () => {
    console.log(`\n🚀 USX Preview Server`);
    console.log(`   http://localhost:${PORT}`);
    console.log(`   WebSocket: ws://localhost:${PORT}`);
    if (WATCH_MODE) console.log(`   Watch mode: enabled`);
    console.log(`   Bundle dir: ${BUNDLE_DIR}\n`);
  });
}

start().catch(err => {
  console.error('❌ Failed to start server:', err);
  process.exit(1);
});
