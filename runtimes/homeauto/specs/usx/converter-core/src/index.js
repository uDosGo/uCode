/**
 * @usx/converter-core
 * 
 * Core module for creating, validating, and transforming USX bundles.
 * Provides the foundation for all design tool → USX converters.
 */

import { readFileSync, writeFileSync, existsSync, mkdirSync } from 'fs';
import { dirname, resolve } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));

// ─── Bundle Creation ───────────────────────────────────────────────

/**
 * Create a new USX bundle object.
 * @param {Object} options
 * @param {string} options.id - Unique bundle identifier
 * @param {string} options.name - Human-readable name
 * @param {string} [options.description] - Optional description
 * @param {Object} [options.source] - Source tool metadata
 * @param {Object} [options.lens] - LENS state/variables
 * @param {Object} [options.skin] - SKIN styling/theme
 * @param {Object} [options.layout] - Layout structure
 * @param {Object} [options.meta] - Additional metadata
 * @returns {Object} USX bundle
 */
export function createBundle({ id, name, description, source, lens, skin, layout, meta }) {
  return {
    $schema: 'https://usx.dev/schema/bundle-v1',
    version: '1.0.0',
    id,
    name,
    description: description || '',
    source: source || { tool: 'manual', version: '1.0.0', exported_at: new Date().toISOString() },
    lens: lens || { version: '1.0.0', variables: {}, components: {}, runtime: {}, features: {} },
    skin: skin || { version: '1.0.0', id: 'default', name: 'Default', colors: {} },
    layout: layout || { version: '1.0.0', type: 'surface', root: { id: 'root', type: 'container', children: [] } },
    meta: meta || {}
  };
}

// ─── Bundle I/O ────────────────────────────────────────────────────

/**
 * Load a USX bundle from a file.
 * @param {string} filePath - Path to .usx file
 * @returns {Object} Parsed USX bundle
 */
export function loadBundle(filePath) {
  const content = readFileSync(filePath, 'utf-8');
  return JSON.parse(content);
}

/**
 * Save a USX bundle to a file.
 * @param {string} filePath - Output path
 * @param {Object} bundle - USX bundle object
 * @param {boolean} [pretty=true] - Pretty-print JSON
 */
export function saveBundle(filePath, bundle, pretty = true) {
  const dir = dirname(filePath);
  if (!existsSync(dir)) {
    mkdirSync(dir, { recursive: true });
  }
  const json = pretty ? JSON.stringify(bundle, null, 2) : JSON.stringify(bundle);
  writeFileSync(filePath, json, 'utf-8');
}

// ─── Bundle Merging ────────────────────────────────────────────────

/**
 * Deep merge two USX bundles. Later bundle values override earlier ones.
 * @param {Object} base - Base bundle
 * @param {Object} override - Override bundle
 * @returns {Object} Merged bundle
 */
export function mergeBundles(base, override) {
  const merged = structuredClone(base);
  
  // Merge LENS
  if (override.lens) {
    merged.lens = deepMerge(merged.lens, override.lens);
  }
  
  // Merge SKIN
  if (override.skin) {
    merged.skin = deepMerge(merged.skin, override.skin);
  }
  
  // Merge Layout
  if (override.layout) {
    merged.layout = deepMerge(merged.layout, override.layout);
  }
  
  // Override metadata
  if (override.meta) {
    merged.meta = { ...merged.meta, ...override.meta };
  }
  
  return merged;
}

// ─── Template Resolution ───────────────────────────────────────────

/**
 * Resolve {{variable.path}} templates in a string against a LENS object.
 * @param {string} template - Template string with {{path}} syntax
 * @param {Object} lens - LENS object with variables
 * @param {Object} [context] - Additional context (e.g., loop variables)
 * @returns {string} Resolved string
 */
export function resolveTemplate(template, lens, context = {}) {
  return template.replace(/\{\{([^}]+)\}\}/g, (match, path) => {
    const trimmed = path.trim();
    
    // Check context first (loop variables)
    if (context[trimmed] !== undefined) {
      return String(context[trimmed]);
    }
    
    // Resolve against LENS
    const value = resolvePath(lens, trimmed);
    if (value !== undefined) {
      return String(value);
    }
    
    // Return original if not found
    return match;
  });
}

/**
 * Resolve a dot-notation path against an object.
 * @param {Object} obj - Source object
 * @param {string} path - Dot-notation path (e.g., 'variables.userName')
 * @returns {*} Resolved value or undefined
 */
export function resolvePath(obj, path) {
  return path.split('.').reduce((current, key) => {
    return current && current[key] !== undefined ? current[key] : undefined;
  }, obj);
}

// ─── Widget Helpers ────────────────────────────────────────────────

/**
 * Create a widget object.
 * @param {string} id - Widget ID
 * @param {string} type - Widget type
 * @param {Object} [options] - Additional widget properties
 * @returns {Object} Widget object
 */
export function createWidget(id, type, options = {}) {
  return {
    id,
    type,
    ...options
  };
}

/**
 * Create a text widget.
 * @param {string} id - Widget ID
 * @param {string} text - Text content
 * @param {Object} [options] - Additional properties
 * @returns {Object} Text widget
 */
export function createText(id, text, options = {}) {
  return createWidget(id, 'text', {
    content: { text },
    ...options
  });
}

/**
 * Create a button widget.
 * @param {string} id - Widget ID
 * @param {string} label - Button label
 * @param {Object} [options] - Additional properties
 * @returns {Object} Button widget
 */
export function createButton(id, label, options = {}) {
  return createWidget(id, 'button', {
    content: { label },
    ...options
  });
}

/**
 * Create a container widget.
 * @param {string} id - Widget ID
 * @param {Array} [children] - Child widgets
 * @param {Object} [options] - Additional properties
 * @returns {Object} Container widget
 */
export function createContainer(id, children = [], options = {}) {
  return createWidget(id, 'container', {
    children,
    ...options
  });
}

// ─── Utility Functions ─────────────────────────────────────────────

/**
 * Deep merge two objects (mutates target).
 * @param {Object} target - Target object
 * @param {Object} source - Source object
 * @returns {Object} Merged object
 */
function deepMerge(target, source) {
  for (const key of Object.keys(source)) {
    if (source[key] && typeof source[key] === 'object' && !Array.isArray(source[key])) {
      if (!target[key] || typeof target[key] !== 'object') {
        target[key] = {};
      }
      deepMerge(target[key], source[key]);
    } else {
      target[key] = source[key];
    }
  }
  return target;
}

/**
 * Generate a UUID v4.
 * @returns {string} UUID
 */
export function generateId() {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, (c) => {
    const r = Math.random() * 16 | 0;
    return (c === 'x' ? r : (r & 0x3 | 0x8)).toString(16);
  });
}

/**
 * Get current ISO timestamp.
 * @returns {string} ISO 8601 timestamp
 */
export function timestamp() {
  return new Date().toISOString();
}

export default {
  createBundle,
  loadBundle,
  saveBundle,
  mergeBundles,
  resolveTemplate,
  resolvePath,
  createWidget,
  createText,
  createButton,
  createContainer,
  generateId,
  timestamp
};
