/**
 * USX Bundle Validator
 * 
 * Validates USX bundles against their JSON schemas.
 * Usage: node src/validate.js <path-to-bundle.usx>
 */

import { readFileSync } from 'fs';
import { resolve } from 'path';
import { fileURLToPath } from 'path';
import { dirname } from 'path';

const __dirname = dirname(fileURLToPath(import.meta.url));

// Inline minimal validation (avoids ajv dependency for Phase 0)
// Full ajv-based validation will be added in Phase 1

const REQUIRED_TOP_LEVEL = ['version', 'id', 'name', 'lens', 'skin', 'layout'];
const REQUIRED_LENS = ['version'];
const REQUIRED_SKIN = ['version', 'id', 'name', 'colors'];
const REQUIRED_LAYOUT = ['version'];

/**
 * Validate a USX bundle structure.
 * @param {Object} bundle - Parsed USX bundle
 * @returns {{ valid: boolean, errors: string[] }}
 */
export function validateBundle(bundle) {
  const errors = [];

  // Check top-level required fields
  for (const field of REQUIRED_TOP_LEVEL) {
    if (bundle[field] === undefined) {
      errors.push(`Missing required top-level field: '${field}'`);
    }
  }

  if (errors.length > 0) {
    return { valid: false, errors };
  }

  // Validate LENS
  if (bundle.lens) {
    for (const field of REQUIRED_LENS) {
      if (bundle.lens[field] === undefined) {
        errors.push(`Missing required LENS field: '${field}'`);
      }
    }
  }

  // Validate SKIN
  if (bundle.skin) {
    for (const field of REQUIRED_SKIN) {
      if (bundle.skin[field] === undefined) {
        errors.push(`Missing required SKIN field: '${field}'`);
      }
    }
  }

  // Validate Layout
  if (bundle.layout) {
    for (const field of REQUIRED_LAYOUT) {
      if (bundle.layout[field] === undefined) {
        errors.push(`Missing required Layout field: '${field}'`);
      }
    }

    // Check layout has either root or widgets
    if (!bundle.layout.root && !bundle.layout.widgets) {
      errors.push('Layout must have either "root" or "widgets"');
    }
  }

  // Validate widget IDs are unique
  const ids = new Set();
  function checkWidgetIds(widget) {
    if (!widget || !widget.id) return;
    if (ids.has(widget.id)) {
      errors.push(`Duplicate widget ID: '${widget.id}'`);
    }
    ids.add(widget.id);
    if (widget.children) {
      widget.children.forEach(checkWidgetIds);
    }
  }

  if (bundle.layout?.root) {
    checkWidgetIds(bundle.layout.root);
  }
  if (bundle.layout?.widgets) {
    bundle.layout.widgets.forEach(checkWidgetIds);
  }

  return {
    valid: errors.length === 0,
    errors
  };
}

// CLI entry point
const filePath = process.argv[2];
if (filePath) {
  try {
    const bundle = JSON.parse(readFileSync(resolve(filePath), 'utf-8'));
    const result = validateBundle(bundle);
    
    if (result.valid) {
      console.log(`✅ Bundle '${bundle.name || filePath}' is valid`);
      process.exit(0);
    } else {
      console.error(`❌ Bundle '${filePath}' is invalid:`);
      result.errors.forEach(err => console.error(`   • ${err}`));
      process.exit(1);
    }
  } catch (err) {
    console.error(`❌ Failed to load bundle: ${err.message}`);
    process.exit(1);
  }
}

export default { validateBundle };
