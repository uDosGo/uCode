#!/usr/bin/env node

/**
 * USX CLI — Render and preview USX bundles from the command line.
 * 
 * Usage:
 *   node src/cli.js render <bundle.usx> [output.html]    # Render to HTML file
 *   node src/cli.js serve [bundle-dir] [port]             # Start preview server
 *   node src/cli.js watch [bundle-dir] [port]             # Start with file watching
 *   node src/cli.js validate <bundle.usx>                 # Validate a bundle
 *   node src/cli.js info <bundle.usx>                     # Show bundle info
 */

import { readFileSync, writeFileSync, existsSync } from 'fs';
import { resolve } from 'path';

const [,, command, ...args] = process.argv;

async function main() {
  switch (command) {
    case 'render':
      await renderCommand(args);
      break;
    case 'serve':
      await serveCommand(args, false);
      break;
    case 'watch':
      await serveCommand(args, true);
      break;
    case 'validate':
      await validateCommand(args);
      break;
    case 'info':
      await infoCommand(args);
      break;
    default:
      showHelp();
  }
}

/**
 * Render a USX bundle to an HTML file.
 */
async function renderCommand(args) {
  const [bundlePath, outputPath] = args;
  
  if (!bundlePath) {
    console.error('❌ Usage: node src/cli.js render <bundle.usx> [output.html]');
    process.exit(1);
  }
  
  const resolvedPath = resolve(bundlePath);
  if (!existsSync(resolvedPath)) {
    console.error(`❌ Bundle not found: ${resolvedPath}`);
    process.exit(1);
  }
  
  try {
    const bundle = JSON.parse(readFileSync(resolvedPath, 'utf-8'));
    const { renderBundle } = await import('./renderer.js');
    const html = renderBundle(bundle);
    
    const outPath = outputPath ? resolve(outputPath) : resolvedPath.replace(/\.usx(\.json)?$/, '.html');
    writeFileSync(outPath, html, 'utf-8');
    
    console.log(`✅ Rendered: ${resolvedPath} → ${outPath}`);
    console.log(`   Bundle: ${bundle.name} (${bundle.id})`);
    console.log(`   Size: ${(html.length / 1024).toFixed(1)} KB`);
  } catch (err) {
    console.error(`❌ Render failed: ${err.message}`);
    process.exit(1);
  }
}

/**
 * Start the preview server.
 */
async function serveCommand(args, watchMode) {
  const [bundleDir, port] = args;
  
  // Set env vars for server
  if (bundleDir) process.env.USX_BUNDLE_DIR = resolve(bundleDir);
  if (port) process.env.USX_PORT = port;
  if (watchMode) process.argv.push('--watch');
  
  // Import and start server
  await import('./server.js');
}

/**
 * Validate a USX bundle.
 */
async function validateCommand(args) {
  const [bundlePath] = args;
  
  if (!bundlePath) {
    console.error('❌ Usage: node src/cli.js validate <bundle.usx>');
    process.exit(1);
  }
  
  const resolvedPath = resolve(bundlePath);
  if (!existsSync(resolvedPath)) {
    console.error(`❌ Bundle not found: ${resolvedPath}`);
    process.exit(1);
  }
  
  try {
    const bundle = JSON.parse(readFileSync(resolvedPath, 'utf-8'));
    const { validateBundle } = await import('../../converter-core/src/validate.js');
    const result = validateBundle(bundle);
    
    if (result.valid) {
      console.log(`✅ Bundle '${bundle.name}' is valid`);
    } else {
      console.error(`❌ Bundle '${bundle.name}' is invalid:`);
      result.errors.forEach(err => console.error(`   • ${err}`));
      process.exit(1);
    }
  } catch (err) {
    console.error(`❌ Validation failed: ${err.message}`);
    process.exit(1);
  }
}

/**
 * Show bundle info.
 */
async function infoCommand(args) {
  const [bundlePath] = args;
  
  if (!bundlePath) {
    console.error('❌ Usage: node src/cli.js info <bundle.usx>');
    process.exit(1);
  }
  
  const resolvedPath = resolve(bundlePath);
  if (!existsSync(resolvedPath)) {
    console.error(`❌ Bundle not found: ${resolvedPath}`);
    process.exit(1);
  }
  
  try {
    const bundle = JSON.parse(readFileSync(resolvedPath, 'utf-8'));
    
    console.log(`\n📦 USX Bundle Info`);
    console.log(`   Name:        ${bundle.name}`);
    console.log(`   ID:          ${bundle.id}`);
    console.log(`   Version:     ${bundle.version}`);
    console.log(`   Description: ${bundle.description || '(none)'}`);
    console.log(`   Source:      ${bundle.source?.tool || 'manual'} (${bundle.source?.version || '?'})`);
    console.log(`   Exported:    ${bundle.source?.exported_at || 'unknown'}`);
    console.log(`   `);
    console.log(`   LENS:`);
    console.log(`     Variables:    ${Object.keys(bundle.lens?.variables || {}).length}`);
    console.log(`     Components:   ${Object.keys(bundle.lens?.components || {}).length}`);
    console.log(`     Features:     ${Object.keys(bundle.lens?.features || {}).length}`);
    console.log(`   SKIN:`);
    console.log(`     Colors:       ${Object.keys(bundle.skin?.colors || {}).length}`);
    console.log(`     Typography:   ${Object.keys(bundle.skin?.typography || {}).length}`);
    console.log(`     Components:   ${Object.keys(bundle.skin?.components || {}).length}`);
    console.log(`   Layout:`);
    console.log(`     Type:         ${bundle.layout?.type || '?'}`);
    console.log(`     Title:        ${bundle.layout?.title || '(none)'}`);
    console.log(`     Grid:         ${bundle.layout?.grid ? 'yes' : 'no'}`);
    console.log(`   `);
    console.log(`   Meta tags: ${(bundle.meta?.tags || []).join(', ') || '(none)'}`);
    console.log(`   File size: ${(readFileSync(resolvedPath).length / 1024).toFixed(1)} KB\n`);
  } catch (err) {
    console.error(`❌ Failed to read bundle: ${err.message}`);
    process.exit(1);
  }
}

function showHelp() {
  console.log(`
🎨 USX CLI — Render and preview USX bundles

Usage:
  node src/cli.js render <bundle.usx> [output.html]    Render to HTML file
  node src/cli.js serve [bundle-dir] [port]             Start preview server
  node src/cli.js watch [bundle-dir] [port]             Start with file watching
  node src/cli.js validate <bundle.usx>                 Validate a bundle
  node src/cli.js info <bundle.usx>                     Show bundle info

Examples:
  node src/cli.js render examples/hello-world.usx
  node src/cli.js serve ./examples 3333
  node src/cli.js watch ./examples 3333
  node src/cli.js validate examples/hello-world.usx
  node src/cli.js info examples/hello-world.usx
`);
}

main().catch(err => {
  console.error('❌ CLI error:', err.message);
  process.exit(1);
});
