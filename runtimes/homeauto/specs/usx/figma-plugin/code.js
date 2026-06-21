/**
 * USX Figma Plugin — Code
 * 
 * Exports Figma frames and components to the USX Bundle Format.
 * Runs in the Figma plugin sandbox.
 * 
 * Features:
 * - Export selected frame(s) as USX bundles
 * - Convert Figma nodes to USX widgets
 * - Extract colors, typography, and effects to SKIN
 * - Extract text content and variables to LENS
 * - Export entire page as a multi-widget layout
 */

// ─── Main Export Function ──────────────────────────────────────────

/**
 * Export selected Figma nodes to a USX bundle.
 */
function exportSelectionToUSX() {
  const selection = figma.currentPage.selection;
  
  if (selection.length === 0) {
    figma.notify('⚠️ Select a frame or component to export');
    return;
  }
  
  const bundles = selection.map(node => convertNodeToBundle(node));
  
  if (bundles.length === 1) {
    // Single selection — send bundle directly
    const bundle = bundles[0];
    figma.ui.postMessage({
      type: 'export-bundle',
      bundle: bundle,
      fileName: `${bundle.id}.usx`
    });
    figma.notify(`✅ Exported: ${bundle.name}`);
  } else {
    // Multiple selections — send as a collection
    figma.ui.postMessage({
      type: 'export-bundles',
      bundles: bundles,
      count: bundles.length
    });
    figma.notify(`✅ Exported ${bundles.length} bundles`);
  }
}

/**
 * Export the entire current page as a USX bundle.
 */
function exportPageToUSX() {
  const page = figma.currentPage;
  const frames = page.children.filter(n => n.type === 'FRAME' || n.type === 'COMPONENT' || n.type === 'GROUP');
  
  if (frames.length === 0) {
    figma.notify('⚠️ No frames found on this page');
    return;
  }
  
  const bundle = {
    $schema: 'https://usx.dev/schema/bundle-v1',
    version: '1.0.0',
    id: `page-${page.id}`,
    name: page.name,
    description: `Exported from Figma page: ${page.name}`,
    source: {
      tool: 'figma',
      version: '1.0.0',
      exported_at: new Date().toISOString(),
      exported_by: 'USX Figma Plugin'
    },
    lens: {
      version: '1.0.0',
      variables: {},
      components: {},
      runtime: {},
      features: {}
    },
    skin: extractPageSkin(page),
    layout: {
      version: '1.0.0',
      type: 'surface',
      title: page.name,
      viewport: {
        width: '100%',
        height: '100%'
      },
      root: {
        id: 'page-root',
        type: 'container',
        children: frames.map(frame => convertFigmaNode(frame))
      }
    },
    meta: {
      tags: ['figma', 'exported'],
      categories: ['surface'],
      preview_image: ''
    }
  };
  
  figma.ui.postMessage({
    type: 'export-bundle',
    bundle: bundle,
    fileName: `${bundle.id}.usx`
  });
  figma.notify(`✅ Exported page: ${page.name}`);
}

// ─── Node Conversion ───────────────────────────────────────────────

/**
 * Convert a single Figma node to a USX bundle.
 */
function convertNodeToBundle(node) {
  const bundle = {
    $schema: 'https://usx.dev/schema/bundle-v1',
    version: '1.0.0',
    id: `figma-${node.id.replace(/[^a-zA-Z0-9_-]/g, '-')}`,
    name: node.name,
    description: `Exported from Figma: ${node.name}`,
    source: {
      tool: 'figma',
      version: '1.0.0',
      exported_at: new Date().toISOString(),
      exported_by: 'USX Figma Plugin'
    },
    lens: {
      version: '1.0.0',
      variables: extractVariables(node),
      components: {},
      runtime: {},
      features: {}
    },
    skin: extractSkin(node),
    layout: {
      version: '1.0.0',
      type: 'surface',
      title: node.name,
      viewport: {
        width: `${node.width}px`,
        height: `${node.height}px`
      },
      root: convertFigmaNode(node)
    },
    meta: {
      tags: ['figma', 'exported'],
      categories: ['surface'],
      preview_image: ''
    }
  };
  
  return bundle;
}

/**
 * Convert a Figma node to a USX widget.
 */
function convertFigmaNode(node) {
  const widget = {
    id: node.id.replace(/[^a-zA-Z0-9_-]/g, '-'),
    type: mapNodeType(node),
    bounds: {
      x: node.x,
      y: node.y,
      width: node.width,
      height: node.height,
      unit: 'px'
    },
    props: extractProps(node),
    content: extractContent(node)
  };
  
  // Add fills as skin reference
  if (node.fills && node.fills.length > 0) {
    const fill = node.fills[0];
    if (fill.type === 'SOLID') {
      widget.skin_ref = `colors.${colorToName(fill.color)}`;
    }
  }
  
  // Add effects
  if (node.effects && node.effects.length > 0) {
    widget.props.effects = node.effects.map(e => ({
      type: e.type,
      visible: e.visible,
      radius: e.radius,
      offset: e.offset,
      color: e.color
    }));
  }
  
  // Add corner radius
  if (node.cornerRadius) {
    widget.props.borderRadius = node.cornerRadius;
  }
  
  // Add opacity
  if (node.opacity !== undefined && node.opacity < 1) {
    widget.props.opacity = node.opacity;
  }
  
  // Convert children
  if ('children' in node && node.children.length > 0) {
    widget.children = node.children.map(child => convertFigmaNode(child));
  }
  
  return widget;
}

/**
 * Map Figma node types to USX widget types.
 */
function mapNodeType(node) {
  switch (node.type) {
    case 'FRAME':
    case 'GROUP':
      return 'container';
    case 'TEXT':
      return 'text';
    case 'RECTANGLE':
    case 'ELLIPSE':
    case 'POLYGON':
    case 'STAR':
      return 'container';
    case 'LINE':
      return 'divider';
    case 'VECTOR':
    case 'BOOLEAN_OPERATION':
      return 'icon';
    case 'INSTANCE':
    case 'COMPONENT':
      return 'container';
    case 'SECTION':
      return 'card';
    default:
      return 'container';
  }
}

/**
 * Extract widget props from a Figma node.
 */
function extractProps(node) {
  const props = {};
  
  // Layout props
  if (node.layoutMode) {
    props.display = node.layoutMode === 'HORIZONTAL' ? 'flex' : 'flex';
    props.flexDirection = node.layoutMode === 'HORIZONTAL' ? 'row' : 'column';
    if (node.primaryAxisAlignItems) props.justifyContent = node.primaryAxisAlignItems.toLowerCase();
    if (node.counterAxisAlignItems) props.alignItems = node.counterAxisAlignItems.toLowerCase();
    if (node.itemSpacing) props.gap = `${node.itemSpacing}px`;
    if (node.paddingTop) props.paddingTop = `${node.paddingTop}px`;
    if (node.paddingRight) props.paddingRight = `${node.paddingRight}px`;
    if (node.paddingBottom) props.paddingBottom = `${node.paddingBottom}px`;
    if (node.paddingLeft) props.paddingLeft = `${node.paddingLeft}px`;
  }
  
  // Auto layout
  if (node.layoutGrow) props.flexGrow = node.layoutGrow;
  if (node.layoutAlign) props.alignSelf = node.layoutAlign.toLowerCase();
  
  // Clips content
  if (node.clipsContent) props.overflow = 'hidden';
  
  return props;
}

/**
 * Extract text content from a Figma node.
 */
function extractContent(node) {
  if (node.type === 'TEXT') {
    return { text: node.characters };
  }
  
  if (node.type === 'INSTANCE' || node.type === 'COMPONENT') {
    // Try to find text children for button labels
    const textChildren = node.children.filter(c => c.type === 'TEXT');
    if (textChildren.length > 0) {
      return { label: textChildren[0].characters };
    }
  }
  
  return {};
}

/**
 * Extract LENS variables from a Figma node.
 */
function extractVariables(node) {
  const variables = {};
  
  // Extract text content as potential variables
  if (node.type === 'TEXT') {
    const varName = node.name.replace(/[^a-zA-Z0-9_]/g, '_').toLowerCase();
    if (varName) {
      variables[varName] = {
        type: 'string',
        default: node.characters,
        description: `From Figma text: ${node.name}`
      };
    }
  }
  
  // Recurse into children
  if ('children' in node) {
    for (const child of node.children) {
      Object.assign(variables, extractVariables(child));
    }
  }
  
  return variables;
}

/**
 * Extract SKIN data from a Figma node.
 */
function extractSkin(node) {
  const skin = {
    version: '1.0.0',
    id: `skin-${node.id.replace(/[^a-zA-Z0-9_-]/g, '-')}`,
    name: `${node.name} Theme`,
    framework: 'tailwind',
    colors: {},
    typography: {},
    spacing: {},
    effects: {},
    components: {}
  };
  
  // Extract colors from fills
  if (node.fills && node.fills.length > 0) {
    for (const fill of node.fills) {
      if (fill.type === 'SOLID' && fill.visible !== false) {
        const colorName = colorToName(fill.color);
        skin.colors[colorName] = {
          light: rgbToHex(fill.color),
          dark: rgbToHex(fill.color),
          css_variable: `--usx-${colorName}`
        };
      }
    }
  }
  
  // Extract typography from text nodes
  if (node.type === 'TEXT') {
    const fontName = node.fontName;
    if (fontName) {
      const typeName = node.name.replace(/[^a-zA-Z0-9_]/g, '_').toLowerCase() || 'body';
      skin.typography[typeName] = {
        font_family: `${fontName.family}, system-ui`,
        font_size: `${node.fontSize}px`,
        font_weight: node.fontWeight || 400,
        line_height: node.lineHeight?.value || 1.5
      };
    }
  }
  
  // Extract effects
  if (node.effects && node.effects.length > 0) {
    for (const effect of node.effects) {
      if (effect.visible !== false) {
        const effectName = effect.type.toLowerCase();
        skin.effects[effectName] = {
          type: effect.type.toLowerCase(),
          value: `${effect.radius}px`,
          css: `box-shadow: ${effect.offset?.x || 0}px ${effect.offset?.y || 0}px ${effect.radius}px rgba(0,0,0,0.1);`
        };
      }
    }
  }
  
  // Recurse into children
  if ('children' in node) {
    for (const child of node.children) {
      const childSkin = extractSkin(child);
      Object.assign(skin.colors, childSkin.colors);
      Object.assign(skin.typography, childSkin.typography);
      Object.assign(skin.effects, childSkin.effects);
    }
  }
  
  return skin;
}

/**
 * Extract page-level SKIN from all frames.
 */
function extractPageSkin(page) {
  const skin = {
    version: '1.0.0',
    id: `page-skin-${page.id}`,
    name: `${page.name} Theme`,
    framework: 'tailwind',
    colors: {},
    typography: {},
    spacing: {},
    effects: {},
    components: {}
  };
  
  for (const frame of page.children) {
    const frameSkin = extractSkin(frame);
    Object.assign(skin.colors, frameSkin.colors);
    Object.assign(skin.typography, frameSkin.typography);
    Object.assign(skin.effects, frameSkin.effects);
  }
  
  return skin;
}

// ─── Utilities ─────────────────────────────────────────────────────

/**
 * Convert RGB color object to hex string.
 */
function rgbToHex(color) {
  const r = Math.round(color.r * 255);
  const g = Math.round(color.g * 255);
  const b = Math.round(color.b * 255);
  return `#${r.toString(16).padStart(2, '0')}${g.toString(16).padStart(2, '0')}${b.toString(16).padStart(2, '0')}`;
}

/**
 * Generate a color name from RGB values.
 */
function colorToName(color) {
  const r = Math.round(color.r * 255);
  const g = Math.round(color.g * 255);
  const b = Math.round(color.b * 255);
  
  // Simple color name mapping
  if (r > 200 && g > 200 && b > 200) return 'background';
  if (r < 50 && g < 50 && b < 50) return 'text';
  if (r > 200 && g < 100 && b < 100) return 'error';
  if (r < 100 && g > 200 && b < 100) return 'success';
  if (r < 100 && g < 100 && b > 200) return 'primary';
  if (r > 200 && g > 200 && b < 100) return 'warning';
  
  return `color_${r}_${g}_${b}`;
}

// ─── Plugin UI Communication ───────────────────────────────────────

figma.ui.onmessage = (msg) => {
  switch (msg.type) {
    case 'export-selection':
      exportSelectionToUSX();
      break;
    case 'export-page':
      exportPageToUSX();
      break;
    case 'resize':
      figma.ui.resize(msg.width, msg.height);
      break;
    case 'notify':
      figma.notify(msg.text);
      break;
    case 'cancel':
      figma.closePlugin();
      break;
  }
};

// ─── Plugin Setup ──────────────────────────────────────────────────

// Show the plugin UI
figma.showUI(__html__, { width: 360, height: 480, title: 'USX Export' });

console.log('🎨 USX Figma Plugin loaded');
