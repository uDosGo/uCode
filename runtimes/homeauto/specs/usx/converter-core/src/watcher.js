/**
 * USX File Watcher
 * 
 * Watches directories for changes to design tool exports and
 * automatically converts them to USX bundles.
 * 
 * Usage: node src/watcher.js <watch-dir> [output-dir]
 */

import { resolve } from 'path';
import { readFileSync, existsSync, mkdirSync } from 'fs';
import { figmaToUsx } from './converters/figma-to-usx.js';
import { saveBundle } from './index.js';

let chokidar;

/**
 * Start watching a directory for design file changes.
 * @param {string} watchDir - Directory to watch
 * @param {string} [outputDir] - Output directory for .usx files (defaults to watchDir)
 */
export async function startWatcher(watchDir, outputDir) {
  try {
    chokidar = await import('chokidar');
  } catch {
    console.error('❌ chokidar not installed. Run: npm install chokidar');
    process.exit(1);
  }

  const outDir = outputDir || watchDir;
  if (!existsSync(outDir)) {
    mkdirSync(outDir, { recursive: true });
  }

  console.log(`👀 Watching: ${watchDir}`);
  console.log(`📁 Output:   ${outDir}`);

  const watcher = chokidar.watch(watchDir, {
    ignored: /(^|[\/\\])\../, // ignore dotfiles
    persistent: true,
    ignoreInitial: true
  });

  watcher
    .on('add', (filePath) => handleFileChange(filePath, outDir, 'added'))
    .on('change', (filePath) => handleFileChange(filePath, outDir, 'changed'))
    .on('error', (error) => console.error(`❌ Watcher error: ${error}`));
}

/**
 * Handle a file change event.
 * @param {string} filePath - Path to changed file
 * @param {string} outputDir - Output directory
 * @param {string} event - Event type
 */
function handleFileChange(filePath, outputDir, event) {
  const ext = filePath.split('.').pop().toLowerCase();
  
  switch (ext) {
    case 'json':
      // Try Figma conversion
      try {
        const content = readFileSync(filePath, 'utf-8');
        const json = JSON.parse(content);
        
        // Detect Figma format by checking for typical Figma fields
        if (json.document || json.document?.type === 'DOCUMENT') {
          console.log(`🔄 ${event}: ${filePath} (Figma)`);
          const bundle = figmaToUsx(json);
          const outputPath = resolve(outputDir, `${bundle.id}.usx`);
          saveBundle(outputPath, bundle);
          console.log(`✅ Converted: ${outputPath}`);
        }
      } catch (err) {
        // Not a valid Figma export, skip silently
      }
      break;

    case 'xd':
    case 'sketch':
      console.log(`⏳ ${event}: ${filePath} (converter not yet implemented)`);
      break;

    default:
      // Unknown format, skip
      break;
  }
}

// CLI entry point
const watchDir = process.argv[2];
const outputDir = process.argv[3];

if (watchDir) {
  startWatcher(resolve(watchDir), outputDir ? resolve(outputDir) : undefined);
} else {
  console.log('Usage: node src/watcher.js <watch-dir> [output-dir]');
  console.log('Example: node src/watcher.js ./exports ./bundles');
}

export default { startWatcher };
