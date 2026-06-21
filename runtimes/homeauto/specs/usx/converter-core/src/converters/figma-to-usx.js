/**
 * Figma → USX Converter
 * 
 * Converts Figma design exports (JSON) into USX bundles.
 * Phase 0: Basic structure extraction.
 * Phase 1+: Full Figma API integration with node traversal.
 */

import { createBundle, createWidget, createContainer, createText, createButton, generateId, timestamp } from '../index.js';

/**
 * Convert a Figma document JSON to a USX bundle.
 * @param {Object} figmaDoc - Figma document JSON (from Figma API or plugin export)
 * @param {Object} [options] - Conversion options
 * @param {string} [options.id] - Bundle ID (auto-generated if not provided)
 * @param {string} [options.name] - Bundle name (from document if not provided)
 * @returns {Object} USX bundle
 */
export function figmaToUsx(figmaDoc, options = {}) {
  const id = options.id || `figma-${generateId()}`;
  const name = options.name || figmaDoc.name || 'Untitled Figma Export';

  // Extract layout from Figma nodes
  const layout = extractLayout(figmaDoc);

  // Extract basic skin from Figma styles
  const skin = extractSkin(figmaDoc);

  // Extract variables from Figma variables
  const lens = extractLens(figmaDoc);

  return createBundle({
    id,
    name,
    description: `Converted from Figma: ${name}`,
    source: {
      tool: 'figma',
      version: figmaDoc.version || '1.0.0',
      exported_at: timestamp(),
      exported_by: options.exportedBy || 'unknown'
    },
    lens,
    skin,
    layout,
    meta: {
      tags: ['figma', 'converted'],
      categories: ['surface'],
      related_bundles: []
    }
  });
}

/**
 * Extract layout structure from Figma nodes.
 * @param {Object} figmaDoc - Figma document
 * @returns {Object} USX Layout object
 */
function extractLayout(figmaDoc) {
  const root = figmaDoc.document || figmaDoc;
  
  return {
    version: '1.0.0',
    type: 'surface',
    title: root.name || 'Surface',
    viewport: {
      width: root.absoluteBoundingBox?.width ? `${root.absoluteBoundingBox.width}px` : '100%',
      height: root.absoluteBoundingBox?.height ? `${root.absoluteBoundingBox.height}px` : '100%'
    },
    root: convertNode(root)
  };
}

/**
 * Recursively convert a Figma node to a USX widget.
 * @param {Object} node - Figma node
 * @returns {Object} USX widget
 */
function convertNode(node) {
  if (!node || !node.type) return null;

  const widgetType = figmaTypeToWidgetType(node.type);
  const widget = createWidget(
    node.id || generateId(),
    widgetType,
    {
      bounds: node.absoluteBoundingBox ? {
        x: node.absoluteBoundingBox.x,
        y: node.absoluteBoundingBox.y,
        width: node.absoluteBoundingBox.width,
        height: node.absoluteBoundingBox.height,
        unit: 'px'
      } : undefined,
      content: extractContent(node),
      props: extractProps(node)
    }
  );

  // Convert children
  if (node.children && node.children.length > 0) {
    widget.children = node.children
      .map(convertNode)
      .filter(Boolean);
  }

  return widget;
}

/**
 * Map Figma node types to USX widget types.
 * @param {string} figmaType - Figma node type
 * @returns {string} USX widget type
 */
function figmaTypeToWidgetType(figmaType) {
  const typeMap = {
    'FRAME': 'container',
    'GROUP': 'container',
    'TEXT': 'text',
    'RECTANGLE': 'container',
    'ELLIPSE': 'container',
    'LINE': 'divider',
    'VECTOR': 'image',
    'INSTANCE': 'custom',
    'COMPONENT': 'container',
    'COMPONENT_SET': 'container',
    'BOOLEAN_OPERATION': 'container',
    'STAR': 'container',
    'POLYGON': 'container',
    'SLICE': 'container',
    'SECTION': 'container',
    'TABLE': 'table',
    'TABLE_CELL': 'text',
    'WIDGET': 'custom',
    'EMBED': 'iframe',
    'LINK_UNFURL': 'card'
  };
  return typeMap[figmaType] || 'container';
}

/**
 * Extract text content from a Figma node.
 * @param {Object} node - Figma node
 * @returns {Object|null} Content object
 */
function extractContent(node) {
  if (node.type === 'TEXT' && node.characters) {
    return { text: node.characters };
  }
  if (node.type === 'INSTANCE' && node.componentProperties) {
    const props = {};
    for (const [key, value] of Object.entries(node.componentProperties)) {
      props[key] = value.value;
    }
    return props;
  }
  return null;
}

/**
 * Extract additional props from a Figma node.
 * @param {Object} node - Figma node
 * @returns {Object} Props object
 */
function extractProps(node) {
  const props = {};
  
  if (node.opacity !== undefined && node.opacity !== 1) {
    props.opacity = node.opacity;
  }
  if (node.visible === false) {
    props.visible = false;
  }
  if (node.locked) {
    props.locked = true;
  }
  if (node.cornerRadius) {
    props.borderRadius = node.cornerRadius;
  }
  if (node.effects && node.effects.length > 0) {
    props.effects = node.effects;
  }
  
  return Object.keys(props).length > 0 ? props : undefined;
}

/**
 * Extract skin from Figma styles.
 * @param {Object} figmaDoc - Figma document
 * @returns {Object} USX Skin object
 */
function extractSkin(figmaDoc) {
  const styles = figmaDoc.styles || {};
  const colors = {};
  const typography = {};

  for (const [key, style] of Object.entries(styles)) {
    if (style.styleType === 'FILL') {
      colors[key] = {
        light: style.color || '#000000',
        description: style.description || key
      };
    } else if (style.styleType === 'TEXT') {
      typography[key] = {
        font_family: style.fontFamily || 'Inter',
        font_size: style.fontSize ? `${style.fontSize}px` : '16px',
        font_weight: style.fontWeight || 400,
        line_height: style.lineHeightPx ? style.lineHeightPx / style.fontSize : 1.5
      };
    }
  }

  return {
    version: '1.0.0',
    id: `figma-${figmaDoc.name || 'export'}`,
    name: `Figma: ${figmaDoc.name || 'Export'}`,
    framework: 'tailwind',
    colors: Object.keys(colors).length > 0 ? colors : { primary: { light: '#0d6efd' } },
    typography: Object.keys(typography).length > 0 ? typography : undefined
  };
}

/**
 * Extract LENS from Figma variables.
 * @param {Object} figmaDoc - Figma document
 * @returns {Object} USX Lens object
 */
function extractLens(figmaDoc) {
  const variables = figmaDoc.variables || {};
  const lensVariables = {};

  for (const [key, variable] of Object.entries(variables)) {
    lensVariables[key] = {
      type: typeof variable.value === 'number' ? 'number' :
            typeof variable.value === 'boolean' ? 'boolean' : 'string',
      default: variable.value,
      description: variable.description || key
    };
  }

  return {
    version: '1.0.0',
    variables: lensVariables,
    components: {},
    runtime: {
      connection_status: 'connected',
      last_sync: timestamp(),
      unsaved_changes: false
    },
    features: {}
  };
}

// CLI entry point
const filePath = process.argv[2];
if (filePath) {
  import('fs').then(fs => {
    try {
      const figmaDoc = JSON.parse(fs.readFileSync(filePath, 'utf-8'));
      const bundle = figmaToUsx(figmaDoc);
      const outputPath = filePath.replace(/\.json$/, '.usx');
      import('../index.js').then(({ saveBundle }) => {
        saveBundle(outputPath, bundle);
        console.log(`✅ Converted: ${filePath} → ${outputPath}`);
      });
    } catch (err) {
      console.error(`❌ Conversion failed: ${err.message}`);
      process.exit(1);
    }
  });
}

export { figmaToUsx };
export default { figmaToUsx };
