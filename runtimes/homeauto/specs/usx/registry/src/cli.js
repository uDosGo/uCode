#!/usr/bin/env node

/**
 * USX Registry CLI
 * 
 * Manage the local USX bundle registry from the command line.
 * 
 * Usage:
 *   node src/cli.js init [db-path]              Initialize registry
 *   node src/cli.js import <file|dir> [db-path]  Import bundle(s)
 *   node src/cli.js list [db-path]               List all bundles
 *   node src/cli.js search <query> [db-path]     Search bundles
 *   node src/cli.js get <id> [db-path]           Get bundle details
 *   node src/cli.js delete <id> [db-path]        Delete a bundle
 *   node src/cli.js tags [db-path]               List all tags
 *   node src/cli.js stats [db-path]              Show registry stats
 *   node src/cli.js versions <id> [db-path]      Show version history
 */

import { Registry } from './index.js';

const [,, command, ...args] = process.argv;

async function main() {
  const registry = new Registry();
  
  switch (command) {
    case 'init':
      await initCommand(registry, args);
      break;
    case 'import':
      await importCommand(registry, args);
      break;
    case 'list':
      await listCommand(registry, args);
      break;
    case 'search':
      await searchCommand(registry, args);
      break;
    case 'get':
      await getCommand(registry, args);
      break;
    case 'delete':
      await deleteCommand(registry, args);
      break;
    case 'tags':
      await tagsCommand(registry, args);
      break;
    case 'stats':
      await statsCommand(registry, args);
      break;
    case 'versions':
      await versionsCommand(registry, args);
      break;
    default:
      showHelp();
  }
}

async function initCommand(registry, args) {
  const [dbPath] = args;
  if (dbPath) registry.dbPath = dbPath;
  await registry.init();
  console.log(`✅ Registry ready at: ${registry.dbPath}`);
  registry.close();
}

async function importCommand(registry, args) {
  const [target, dbPath] = args;
  if (!target) {
    console.error('❌ Usage: node src/cli.js import <file|dir> [db-path]');
    process.exit(1);
  }
  
  if (dbPath) registry.dbPath = dbPath;
  await registry.init();
  
  const { existsSync, statSync } = await import('fs');
  const { resolve } = await import('path');
  
  const resolved = resolve(target);
  if (!existsSync(resolved)) {
    console.error(`❌ Not found: ${resolved}`);
    process.exit(1);
  }
  
  const stat = statSync(resolved);
  let results;
  
  if (stat.isDirectory()) {
    results = registry.importDirectory(resolved);
  } else {
    results = [registry.importBundle(resolved)];
  }
  
  console.log(`\n📦 Imported ${results.length} bundle(s):\n`);
  for (const r of results) {
    console.log(`   ${r.name} (${r.id}) v${r.version}`);
    console.log(`   📊 ${r.lens_variables} vars · ${r.skin_colors} colors · ${r.widgets} widgets`);
    if (r.tags.length > 0) console.log(`   🏷️  ${r.tags.join(', ')}`);
    console.log();
  }
  
  registry.close();
}

async function listCommand(registry, args) {
  const [dbPath] = args;
  if (dbPath) registry.dbPath = dbPath;
  await registry.init();
  
  const bundles = registry.listBundles();
  
  if (bundles.length === 0) {
    console.log('📭 No bundles in registry');
  } else {
    console.log(`\n📦 ${bundles.length} bundle(s) in registry:\n`);
    for (const b of bundles) {
      console.log(`   ${b.name}`);
      console.log(`   ID: ${b.id} · v${b.version} · ${b.source}`);
      console.log(`   🏷️  ${b.tags.join(', ') || '(no tags)'}`);
      console.log(`   📅 ${b.updated_at}`);
      console.log();
    }
  }
  
  registry.close();
}

async function searchCommand(registry, args) {
  const [query, dbPath] = args;
  if (!query) {
    console.error('❌ Usage: node src/cli.js search <query> [db-path]');
    process.exit(1);
  }
  
  if (dbPath) registry.dbPath = dbPath;
  await registry.init();
  
  const results = registry.search(query);
  
  if (results.length === 0) {
    console.log(`🔍 No results for "${query}"`);
  } else {
    console.log(`\n🔍 ${results.length} result(s) for "${query}":\n`);
    for (const r of results) {
      console.log(`   ${r.name} (${r.id})`);
      console.log(`   ${r.description || '(no description)'}`);
      console.log(`   🏷️  ${r.tags.join(', ') || '(no tags)'}`);
      console.log();
    }
  }
  
  registry.close();
}

async function getCommand(registry, args) {
  const [id, dbPath] = args;
  if (!id) {
    console.error('❌ Usage: node src/cli.js get <id> [db-path]');
    process.exit(1);
  }
  
  if (dbPath) registry.dbPath = dbPath;
  await registry.init();
  
  const bundle = registry.getBundle(id);
  if (!bundle) {
    console.error(`❌ Bundle not found: ${id}`);
    process.exit(1);
  }
  
  console.log(`\n📦 ${bundle.name}`);
  console.log(`   ID:          ${bundle.id}`);
  console.log(`   Version:     ${bundle.version}`);
  console.log(`   Description: ${bundle.description || '(none)'}`);
  console.log(`   Source:      ${bundle.source.tool} (${bundle.source.version})`);
  console.log(`   File:        ${bundle.file_path || '(memory)'}`);
  console.log(`   Size:        ${(bundle.file_size / 1024).toFixed(1)} KB`);
  console.log(`   Imported:    ${bundle.imported_at}`);
  console.log(`   Updated:     ${bundle.updated_at}`);
  console.log(`   `);
  console.log(`   Stats:`);
  console.log(`     LENS variables: ${bundle.stats.lens_variables}`);
  console.log(`     SKIN colors:    ${bundle.stats.skin_colors}`);
  console.log(`     Layout widgets: ${bundle.stats.widgets}`);
  console.log(`   `);
  console.log(`   Tags:       ${bundle.tags.join(', ') || '(none)'}`);
  console.log(`   Categories: ${bundle.categories.join(', ') || '(none)'}`);
  console.log();
  
  registry.close();
}

async function deleteCommand(registry, args) {
  const [id, dbPath] = args;
  if (!id) {
    console.error('❌ Usage: node src/cli.js delete <id> [db-path]');
    process.exit(1);
  }
  
  if (dbPath) registry.dbPath = dbPath;
  await registry.init();
  
  const deleted = registry.deleteBundle(id);
  if (deleted) {
    console.log(`✅ Deleted bundle: ${id}`);
  } else {
    console.error(`❌ Bundle not found: ${id}`);
  }
  
  registry.close();
}

async function tagsCommand(registry, args) {
  const [dbPath] = args;
  if (dbPath) registry.dbPath = dbPath;
  await registry.init();
  
  const tags = registry.getAllTags();
  
  if (tags.length === 0) {
    console.log('🏷️  No tags found');
  } else {
    console.log(`\n🏷️  ${tags.length} tag(s):\n`);
    for (const t of tags) {
      console.log(`   ${t.tag} (${t.count} bundle(s))`);
    }
    console.log();
  }
  
  registry.close();
}

async function statsCommand(registry, args) {
  const [dbPath] = args;
  if (dbPath) registry.dbPath = dbPath;
  await registry.init();
  
  const stats = registry.getStats();
  
  console.log(`\n📊 Registry Statistics\n`);
  console.log(`   Total bundles: ${stats.total_bundles}`);
  console.log(`   Total tags:    ${stats.total_tags}`);
  console.log(`   `);
  console.log(`   By source:`);
  for (const s of stats.by_source) {
    console.log(`     ${s.source_tool}: ${s.count}`);
  }
  console.log(`   `);
  console.log(`   Recent imports:`);
  for (const r of stats.recent_imports) {
    console.log(`     ${r.name} (${r.id}) — ${r.imported_at}`);
  }
  console.log();
  
  registry.close();
}

async function versionsCommand(registry, args) {
  const [id, dbPath] = args;
  if (!id) {
    console.error('❌ Usage: node src/cli.js versions <id> [db-path]');
    process.exit(1);
  }
  
  if (dbPath) registry.dbPath = dbPath;
  await registry.init();
  
  const versions = registry.getVersionHistory(id);
  
  if (versions.length === 0) {
    console.error(`❌ No versions found for: ${id}`);
  } else {
    console.log(`\n📜 Version history for ${id}:\n`);
    for (const v of versions) {
      console.log(`   v${v.version} — ${v.imported_at}`);
      if (v.file_path) console.log(`     ${v.file_path}`);
    }
    console.log();
  }
  
  registry.close();
}

function showHelp() {
  console.log(`
📦 USX Registry CLI — Manage the local bundle registry

Usage:
  node src/cli.js init [db-path]              Initialize registry
  node src/cli.js import <file|dir> [db-path]  Import bundle(s)
  node src/cli.js list [db-path]               List all bundles
  node src/cli.js search <query> [db-path]     Search bundles
  node src/cli.js get <id> [db-path]           Get bundle details
  node src/cli.js delete <id> [db-path]        Delete a bundle
  node src/cli.js tags [db-path]               List all tags
  node src/cli.js stats [db-path]              Show registry stats
  node src/cli.js versions <id> [db-path]      Show version history

Examples:
  node src/cli.js init ./usx-registry.db
  node src/cli.js import ../examples ./usx-registry.db
  node src/cli.js search dashboard
  node src/cli.js stats
`);
}

main().catch(err => {
  console.error('❌ Registry CLI error:', err.message);
  process.exit(1);
});
