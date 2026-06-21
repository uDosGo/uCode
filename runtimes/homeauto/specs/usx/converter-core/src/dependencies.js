/**
 * USX Bundle Dependencies
 * 
 * Manages dependencies between USX bundles.
 * Supports importing bundles, resolving dependency trees,
 * and merging dependent bundles into a single composite bundle.
 * 
 * Usage:
 *   import { DependencyResolver } from './dependencies.js';
 *   const resolver = new DependencyResolver();
 *   resolver.addBundle('dashboard', dashboardBundle);
 *   resolver.addBundle('chart', chartBundle);
 *   const tree = resolver.resolveDependencies('dashboard');
 *   const merged = resolver.mergeBundles('dashboard');
 */

import { readFileSync, readdirSync, existsSync } from 'fs';
import { resolve, extname, join } from 'path';

// ─── Dependency Resolver ───────────────────────────────────────────

export class DependencyResolver {
  constructor(options = {}) {
    this.bundles = new Map();
    this.registry = options.registry || null;
    this.baseDir = options.baseDir || process.cwd();
  }

  /**
   * Add a bundle to the resolver.
   * @param {string} id - Bundle ID
   * @param {Object} bundle - USX bundle object
   */
  addBundle(id, bundle) {
    this.bundles.set(id, bundle);
  }

  /**
   * Load a bundle from a file and add it.
   * @param {string} filePath - Path to .usx file
   * @returns {Object} Loaded bundle
   */
  loadBundle(filePath) {
    const resolvedPath = resolve(this.baseDir, filePath);
    
    if (!existsSync(resolvedPath)) {
      throw new Error(`Bundle file not found: ${resolvedPath}`);
    }
    
    const content = readFileSync(resolvedPath, 'utf-8');
    const bundle = JSON.parse(content);
    
    if (!bundle.id) {
      throw new Error(`Bundle at ${filePath} has no "id" field`);
    }
    
    this.addBundle(bundle.id, bundle);
    return bundle;
  }

  /**
   * Load all bundles from a directory.
   * @param {string} dirPath - Directory path
   * @returns {number} Number of bundles loaded
   */
  loadBundleDirectory(dirPath) {
    const resolvedPath = resolve(this.baseDir, dirPath);
    let count = 0;
    
    try {
      const files = readdirSync(resolvedPath);
      for (const file of files) {
        if (file.endsWith('.usx') || file.endsWith('.usx.json')) {
          try {
            this.loadBundle(join(dirPath, file));
            count++;
          } catch (err) {
            console.warn(`⚠️  Failed to load ${file}: ${err.message}`);
          }
        }
      }
    } catch (err) {
      console.warn(`⚠️  Failed to read directory ${resolvedPath}: ${err.message}`);
    }
    
    return count;
  }

  /**
   * Get a bundle by ID.
   */
  getBundle(id) {
    return this.bundles.get(id);
  }

  /**
   * Check if a bundle has dependencies.
   */
  hasDependencies(id) {
    const bundle = this.bundles.get(id);
    if (!bundle) return false;
    return !!(bundle.dependencies || bundle.imports);
  }

  /**
   * Get the dependency IDs for a bundle.
   */
  getDependencyIds(id) {
    const bundle = this.bundles.get(id);
    if (!bundle) return [];
    
    const deps = [];
    
    // Check dependencies field
    if (bundle.dependencies) {
      if (Array.isArray(bundle.dependencies)) {
        deps.push(...bundle.dependencies);
      } else if (typeof bundle.dependencies === 'object') {
        deps.push(...Object.keys(bundle.dependencies));
      }
    }
    
    // Check imports field
    if (bundle.imports) {
      if (Array.isArray(bundle.imports)) {
        deps.push(...bundle.imports);
      } else if (typeof bundle.imports === 'object') {
        deps.push(...Object.keys(bundle.imports));
      }
    }
    
    return [...new Set(deps)];
  }

  // ─── Dependency Resolution ───────────────────────────────────────

  /**
   * Resolve the full dependency tree for a bundle.
   * Returns a topologically sorted array of bundle IDs.
   * @param {string} id - Root bundle ID
   * @returns {string[]} Ordered dependency IDs (root last)
   */
  resolveDependencies(id) {
    const visited = new Set();
    const order = [];
    
    const visit = (nodeId, path = []) => {
      if (path.includes(nodeId)) {
        throw new Error(`Circular dependency detected: ${path.join(' -> ')} -> ${nodeId}`);
      }
      
      if (visited.has(nodeId)) return;
      visited.add(nodeId);
      
      const deps = this.getDependencyIds(nodeId);
      for (const depId of deps) {
        if (!this.bundles.has(depId)) {
          console.warn(`⚠️  Missing dependency: ${depId} (required by ${nodeId})`);
          continue;
        }
        visit(depId, [...path, nodeId]);
      }
      
      order.push(nodeId);
    };
    
    visit(id);
    return order;
  }

  /**
   * Get the dependency tree as a nested structure.
   * @param {string} id - Root bundle ID
   * @returns {Object} Dependency tree
   */
  getDependencyTree(id) {
    const bundle = this.bundles.get(id);
    if (!bundle) return null;
    
    const deps = this.getDependencyIds(id);
    
    return {
      id,
      name: bundle.name || id,
      version: bundle.version,
      dependencies: deps.map(depId => this.getDependencyTree(depId)).filter(Boolean)
    };
  }

  /**
   * Check if a dependency is satisfied (exists and version-compatible).
   * @param {string} id - Bundle ID
   * @param {string} [version] - Required version (semver range)
   * @returns {boolean}
   */
  isDependencySatisfied(id, version) {
    const bundle = this.bundles.get(id);
    if (!bundle) return false;
    
    if (!version) return true;
    
    // Simple version check (exact match or major.minor match)
    const required = version.replace(/[^0-9.]/g, '');
    const actual = (bundle.version || '').replace(/[^0-9.]/g, '');
    
    if (!actual) return false;
    
    const reqParts = required.split('.');
    const actParts = actual.split('.');
    
    // Check major version
    if (reqParts[0] && actParts[0] && reqParts[0] !== actParts[0]) {
      return false;
    }
    
    // Check minor version if specified
    if (reqParts[1] && actParts[1] && reqParts[1] !== actParts[1]) {
      return false;
    }
    
    return true;
  }

  // ─── Bundle Merging ──────────────────────────────────────────────

  /**
   * Merge a bundle with all its dependencies into a single composite bundle.
   * @param {string} id - Root bundle ID
   * @param {Object} [options] - Merge options
   * @param {boolean} [options.deepMerge=true] - Deep merge LENS and SKIN
   * @param {boolean} [options.prefixWidgets=true] - Prefix widget IDs to avoid conflicts
   * @returns {Object} Merged bundle
   */
  mergeBundles(id, options = {}) {
    const { deepMerge = true, prefixWidgets = true } = options;
    
    const root = this.bundles.get(id);
    if (!root) {
      throw new Error(`Bundle not found: ${id}`);
    }
    
    const order = this.resolveDependencies(id);
    
    // Start with the root bundle
    const merged = JSON.parse(JSON.stringify(root));
    
    // Merge dependencies in order (dependencies first, root last)
    for (const depId of order) {
      if (depId === id) continue;
      
      const dep = this.bundles.get(depId);
      if (!dep) continue;
      
      merged._dependencies = merged._dependencies || {};
      merged._dependencies[depId] = {
        name: dep.name,
        version: dep.version,
        merged: true
      };
      
      // Merge LENS variables
      if (deepMerge && dep.lens) {
        merged.lens = this._deepMerge(merged.lens || {}, dep.lens);
      }
      
      // Merge SKIN definitions
      if (deepMerge && dep.skin) {
        merged.skin = this._deepMerge(merged.skin || {}, dep.skin);
      }
      
      // Merge Layout widgets
      if (dep.layout) {
        merged.layout = merged.layout || {};
        
        // Merge widgets array
        if (dep.layout.widgets) {
          merged.layout.widgets = merged.layout.widgets || [];
          
          for (const widget of dep.layout.widgets) {
            const prefixed = prefixWidgets
              ? this._prefixWidgetIds(widget, depId)
              : widget;
            merged.layout.widgets.push(prefixed);
          }
        }
        
        // Merge root widget
        if (dep.layout.root && !merged.layout.root) {
          merged.layout.root = prefixWidgets
            ? this._prefixWidgetIds(dep.layout.root, depId)
            : dep.layout.root;
        }
      }
    }
    
    // Add metadata about merged dependencies
    merged._mergedFrom = order.filter(d => d !== id);
    merged._mergeTimestamp = new Date().toISOString();
    
    return merged;
  }

  /**
   * Deep merge two objects.
   */
  _deepMerge(target, source) {
    const result = JSON.parse(JSON.stringify(target));
    
    for (const [key, value] of Object.entries(source)) {
      if (value && typeof value === 'object' && !Array.isArray(value)) {
        result[key] = this._deepMerge(result[key] || {}, value);
      } else if (Array.isArray(value)) {
        result[key] = [...(result[key] || []), ...value];
      } else {
        result[key] = value;
      }
    }
    
    return result;
  }

  /**
   * Prefix widget IDs to avoid conflicts when merging.
   */
  _prefixWidgetIds(widget, prefix) {
    if (!widget || typeof widget !== 'object') return widget;
    
    const result = JSON.parse(JSON.stringify(widget));
    
    if (result.id) {
      result.id = `${prefix}__${result.id}`;
    }
    
    if (result.children) {
      result.children = result.children.map(c => this._prefixWidgetIds(c, prefix));
    }
    
    return result;
  }

  // ─── Validation ──────────────────────────────────────────────────

  /**
   * Validate all dependencies for a bundle.
   * @param {string} id - Bundle ID
   * @returns {Object} Validation result
   */
  validateDependencies(id) {
    const bundle = this.bundles.get(id);
    if (!bundle) {
      return { valid: false, errors: [`Bundle not found: ${id}`], warnings: [] };
    }
    
    const errors = [];
    const warnings = [];
    const deps = this.getDependencyIds(id);
    
    for (const depId of deps) {
      const dep = this.bundles.get(depId);
      
      if (!dep) {
        errors.push(`Missing dependency: ${depId}`);
        continue;
      }
      
      // Check version compatibility
      const version = bundle.dependencies?.[depId] || bundle.imports?.[depId];
      if (version && !this.isDependencySatisfied(depId, version)) {
        warnings.push(`Version mismatch for ${depId}: required ${version}, found ${dep.version || 'unknown'}`);
      }
    }
    
    // Check for circular dependencies
    try {
      this.resolveDependencies(id);
    } catch (err) {
      errors.push(err.message);
    }
    
    return {
      valid: errors.length === 0,
      errors,
      warnings,
      total_dependencies: deps.length,
      resolved: deps.filter(d => this.bundles.has(d)).length,
      missing: deps.filter(d => !this.bundles.has(d)).length
    };
  }

  /**
   * List all bundles and their dependency status.
   * @returns {Array} Bundle dependency report
   */
  listDependencyReport() {
    const report = [];
    
    for (const [id, bundle] of this.bundles) {
      const deps = this.getDependencyIds(id);
      report.push({
        id,
        name: bundle.name || id,
        version: bundle.version,
        dependencies: deps,
        hasMissing: deps.some(d => !this.bundles.has(d)),
        missing: deps.filter(d => !this.bundles.has(d))
      });
    }
    
    return report;
  }

  /**
   * Clear all loaded bundles.
   */
  clear() {
    this.bundles.clear();
  }
}

// ─── Default Export ────────────────────────────────────────────────

export default DependencyResolver;
