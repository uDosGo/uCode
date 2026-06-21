/**
 * USX uDosGo Loader
 * 
 * Loads and manages USX surfaces within the uDosGo engine.
 * Provides surface lifecycle management, event bridging,
 * and communication between uDosGo and USX renderer instances.
 * 
 * Usage:
 *   import { SurfaceLoader } from './src/index.js';
 *   const loader = new SurfaceLoader();
 *   await loader.init();
 *   const surface = await loader.loadSurface('./path/to/bundle.usx');
 *   surface.show();
 */

import { readFileSync, existsSync, watchFile } from 'fs';
import { resolve } from 'path';
import { createServer } from 'http';
import { spawn } from 'child_process';

// ─── Surface Loader ────────────────────────────────────────────────

export class SurfaceLoader {
  constructor(options = {}) {
    this.surfaces = new Map();
    this.registry = null;
    this.rendererServer = null;
    this.port = options.port || 3333;
    this.baseDir = options.baseDir || process.cwd();
    this.ready = false;
  }

  /**
   * Initialize the surface loader.
   * Starts the USX renderer server if not already running.
   */
  async init() {
    console.log('🚀 Initializing USX Surface Loader...');
    
    // Try to connect to existing renderer server
    try {
      const response = await fetch(`http://localhost:${this.port}/api/bundles`);
      if (response.ok) {
        console.log(`🔗 Connected to USX renderer on port ${this.port}`);
        this.ready = true;
        return this;
      }
    } catch {
      // Server not running, will start it
    }
    
    // Start renderer server
    await this._startRenderer();
    this.ready = true;
    return this;
  }

  /**
   * Start the USX renderer server as a child process.
   */
  async _startRenderer() {
    const rendererPath = resolve(this.baseDir, '../renderer/src/server.js');
    
    if (!existsSync(rendererPath)) {
      console.warn('⚠️  Renderer server not found, surfaces will be rendered inline');
      return;
    }
    
    return new Promise((resolve, reject) => {
      const proc = spawn('node', [rendererPath, this.baseDir, String(this.port)], {
        stdio: ['pipe', 'inherit', 'inherit'],
        detached: false
      });
      
      this.rendererServer = proc;
      
      // Wait for server to start
      const check = setInterval(async () => {
        try {
          const response = await fetch(`http://localhost:${this.port}/api/bundles`);
          if (response.ok) {
            clearInterval(check);
            console.log(`✅ USX renderer started on port ${this.port}`);
            resolve();
          }
        } catch {}
      }, 200);
      
      setTimeout(() => {
        clearInterval(check);
        reject(new Error('Renderer server failed to start'));
      }, 10000);
      
      proc.on('error', (err) => {
        clearInterval(check);
        reject(err);
      });
    });
  }

  // ─── Surface Lifecycle ───────────────────────────────────────────

  /**
   * Load a USX surface from a bundle file.
   * @param {string} filePath - Path to .usx file
   * @param {Object} [options] - Surface options
   * @returns {Surface} Surface instance
   */
  loadSurface(filePath, options = {}) {
    const resolvedPath = resolve(this.baseDir, filePath);
    
    if (!existsSync(resolvedPath)) {
      throw new Error(`Surface bundle not found: ${resolvedPath}`);
    }
    
    const content = readFileSync(resolvedPath, 'utf-8');
    const bundle = JSON.parse(content);
    
    const surface = new Surface(bundle, {
      ...options,
      loader: this,
      port: this.port
    });
    
    this.surfaces.set(bundle.id, surface);
    console.log(`📦 Surface loaded: ${bundle.name} (${bundle.id})`);
    
    return surface;
  }

  /**
   * Load a surface from a bundle object.
   * @param {Object} bundle - USX bundle object
   * @param {Object} [options] - Surface options
   * @returns {Surface} Surface instance
   */
  loadSurfaceFromBundle(bundle, options = {}) {
    const surface = new Surface(bundle, {
      ...options,
      loader: this,
      port: this.port
    });
    
    this.surfaces.set(bundle.id, surface);
    return surface;
  }

  /**
   * Get a loaded surface by ID.
   */
  getSurface(id) {
    return this.surfaces.get(id);
  }

  /**
   * List all loaded surfaces.
   */
  listSurfaces() {
    return Array.from(this.surfaces.values()).map(s => ({
      id: s.id,
      name: s.name,
      version: s.version,
      visible: s.visible,
      type: s.bundle.layout?.type || 'surface'
    }));
  }

  /**
   * Unload a surface.
   */
  unloadSurface(id) {
    const surface = this.surfaces.get(id);
    if (surface) {
      surface.destroy();
      this.surfaces.delete(id);
      console.log(`🗑️  Surface unloaded: ${id}`);
      return true;
    }
    return false;
  }

  /**
   * Bridge an event from uDosGo to a USX surface.
   */
  bridgeEvent(surfaceId, eventType, payload) {
    const surface = this.surfaces.get(surfaceId);
    if (!surface) {
      console.warn(`⚠️  Surface not found: ${surfaceId}`);
      return;
    }
    
    surface.handleExternalEvent(eventType, payload);
  }

  /**
   * Shutdown the loader and all surfaces.
   */
  async shutdown() {
    console.log('🛑 Shutting down USX Surface Loader...');
    
    // Destroy all surfaces
    for (const [id, surface] of this.surfaces) {
      surface.destroy();
    }
    this.surfaces.clear();
    
    // Kill renderer server
    if (this.rendererServer) {
      this.rendererServer.kill();
      this.rendererServer = null;
    }
    
    this.ready = false;
    console.log('✅ Surface Loader shut down');
  }
}

// ─── Surface Class ─────────────────────────────────────────────────

export class Surface {
  constructor(bundle, options = {}) {
    this.bundle = bundle;
    this.id = bundle.id;
    this.name = bundle.name;
    this.version = bundle.version;
    this.loader = options.loader;
    this.port = options.port || 3333;
    this.container = options.container || null;
    this.visible = false;
    this.eventListeners = new Map();
    this._ws = null;
    this._iframe = null;
    this._onMessage = this._handleMessage.bind(this);
  }

  /**
   * Show the surface in the specified container.
   * @param {HTMLElement|string} [container] - DOM element or selector
   */
  show(container) {
    if (container) {
      this.container = typeof container === 'string'
        ? document.querySelector(container)
        : container;
    }
    
    if (!this.container) {
      console.warn('⚠️  No container specified for surface');
      return;
    }
    
    this.visible = true;
    
    // Create iframe for the surface
    this._iframe = document.createElement('iframe');
    this._iframe.src = `http://localhost:${this.port}/?bundle=${this.id}`;
    this._iframe.style.cssText = `
      width: 100%; height: 100%; border: none;
      background: var(--usx-bg, #fff);
    `;
    this._iframe.setAttribute('data-usx-surface', this.id);
    
    this.container.innerHTML = '';
    this.container.appendChild(this._iframe);
    
    // Connect to WebSocket for live updates
    this._connectWebSocket();
    
    // Listen for messages from the iframe
    window.addEventListener('message', this._onMessage);
    
    console.log(`🖥️  Surface shown: ${this.name}`);
    
    // Dispatch event
    this._dispatchEvent('surface:show', { surfaceId: this.id });
  }

  /**
   * Hide the surface.
   */
  hide() {
    if (!this.visible) return;
    
    this.visible = false;
    
    if (this._iframe && this.container) {
      this.container.removeChild(this._iframe);
    }
    
    this._disconnectWebSocket();
    window.removeEventListener('message', this._onMessage);
    
    this._dispatchEvent('surface:hide', { surfaceId: this.id });
  }

  /**
   * Reload the surface with optional variable overrides.
   * @param {Object} [overrides] - LENS variable overrides
   */
  reload(overrides = {}) {
    if (!this._iframe) return;
    
    const params = new URLSearchParams();
    for (const [key, value] of Object.entries(overrides)) {
      params.set(`lens.${key}`, String(value));
    }
    
    this._iframe.src = `http://localhost:${this.port}/?bundle=${this.id}&${params.toString()}`;
    
    this._dispatchEvent('surface:reload', { surfaceId: this.id, overrides });
  }

  /**
   * Update a LENS variable on the surface.
   */
  setVariable(path, value) {
    this._postMessage({
      type: 'set-variable',
      path,
      value
    });
  }

  /**
   * Get the current HTML content of the surface.
   */
  async getContent() {
    try {
      const response = await fetch(`http://localhost:${this.port}/api/bundle/${this.id}`);
      if (response.ok) {
        return await response.json();
      }
    } catch {}
    return this.bundle;
  }

  /**
   * Handle an external event from uDosGo.
   */
  handleExternalEvent(eventType, payload) {
    this._postMessage({
      type: 'external-event',
      eventType,
      payload
    });
    
    this._dispatchEvent('surface:event', { eventType, payload });
  }

  /**
   * Add an event listener for surface events.
   */
  on(eventType, callback) {
    if (!this.eventListeners.has(eventType)) {
      this.eventListeners.set(eventType, []);
    }
    this.eventListeners.get(eventType).push(callback);
  }

  /**
   * Remove an event listener.
   */
  off(eventType, callback) {
    const listeners = this.eventListeners.get(eventType);
    if (listeners) {
      const index = listeners.indexOf(callback);
      if (index !== -1) listeners.splice(index, 1);
    }
  }

  /**
   * Destroy the surface and clean up.
   */
  destroy() {
    this.hide();
    this.eventListeners.clear();
    this.bundle = null;
  }

  // ─── Internal ────────────────────────────────────────────────────

  /**
   * Post a message to the surface iframe.
   */
  _postMessage(data) {
    if (this._iframe && this._iframe.contentWindow) {
      this._iframe.contentWindow.postMessage(data, '*');
    }
  }

  /**
   * Handle messages from the surface iframe.
   */
  _handleMessage(event) {
    // Only accept messages from our iframe
    if (event.source !== this._iframe?.contentWindow) return;
    
    const data = event.data;
    if (!data || !data.type) return;
    
    switch (data.type) {
      case 'usx:event':
        this._dispatchEvent('widget:event', data.detail);
        break;
      case 'usx:update':
        this._dispatchEvent('variable:update', data.detail);
        break;
      case 'usx:darkmode':
        this._dispatchEvent('darkmode:toggle', data.detail);
        break;
      default:
        this._dispatchEvent('message', data);
    }
  }

  /**
   * Connect to the renderer WebSocket.
   */
  _connectWebSocket() {
    try {
      this._ws = new WebSocket(`ws://localhost:${this.port}`);
      
      this._ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (data.type === 'bundle_updated' && data.bundleId === this.id) {
          this._dispatchEvent('surface:updated', data);
          // Auto-reload
          if (this.visible) {
            this._iframe.src = this._iframe.src;
          }
        }
      };
      
      this._ws.onclose = () => {
        console.log('🔌 Surface WebSocket disconnected');
      };
    } catch (err) {
      console.warn('⚠️  WebSocket connection failed:', err.message);
    }
  }

  /**
   * Disconnect from WebSocket.
   */
  _disconnectWebSocket() {
    if (this._ws) {
      this._ws.close();
      this._ws = null;
    }
  }

  /**
   * Dispatch a surface event to registered listeners.
   */
  _dispatchEvent(eventType, data) {
    const listeners = this.eventListeners.get(eventType);
    if (listeners) {
      for (const callback of listeners) {
        try {
          callback(data);
        } catch (err) {
          console.error(`⚠️  Surface event handler error:`, err);
        }
      }
    }
  }
}

// ─── Default Export ────────────────────────────────────────────────

export default SurfaceLoader;
