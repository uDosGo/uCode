import { mkdir, writeFile } from 'node:fs/promises'
import path from 'node:path'
import { createGrid } from '@udos/gridcore'
import { editCell } from './cell'

export interface WorldManifest {
  id: string
  name: string
  type: 'earth' | 'dungeon' | 'vault' | 'library'
  seed?: number
  source?: 'generated' | 'basic' | 'amos'
}

export function createWorldManifest(
  id: string,
  name: string,
  type: WorldManifest['type'],
  seed?: number,
  source: WorldManifest['source'] = 'generated',
): WorldManifest {
  return { id, name, type, seed, source }
}

export interface WorldCreationOptions {
  name: string
  type: WorldManifest['type']
  cols?: number
  rows?: number
  seed?: number
  terrain?: Record<string, string>
}

export async function createWorld(options: WorldCreationOptions): Promise<{
  manifest: WorldManifest
  grid: { cols: number; rows: number; cellCount: number }
  files: Record<string, string>
}> {
  const cols = options.cols ?? 80
  const rows = options.rows ?? 24
  const slug = options.name.toLowerCase().replace(/[^a-z0-9]+/g, '-').slice(0, 80)
  const grid = createGrid(cols, rows)

  // Apply terrain if provided
  if (options.terrain) {
    for (const [coord, char] of Object.entries(options.terrain)) {
      const parts = coord.split(',')
      if (parts.length === 2) {
        const x = Number(parts[0])
        const y = Number(parts[1])
        if (!isNaN(x) && !isNaN(y)) {
          editCell(grid, x, y, 0, { char })
        }
      }
    }
  }

  const manifest = createWorldManifest(slug, options.name, options.type, options.seed)

  const workspaceRoot = path.resolve(process.cwd(), 'workspaces/gridcore')
  const worldDir = path.join(workspaceRoot, 'worlds', slug)
  const manifestPath = path.join(worldDir, 'manifest.json')
  const gridPath = path.join(worldDir, 'grid.json')

  await mkdir(worldDir, { recursive: true })

  const gridExport = {
    id: slug,
    cols: grid.cols,
    rows: grid.rows,
    cells: [...grid.cells.values()].map(c => ({
      x: c.x,
      y: c.y,
      layer: c.layer,
      char: c.char,
      fg: c.fg,
      bg: c.bg,
      coord: c.coord,
    })),
  }

  await writeFile(manifestPath, JSON.stringify(manifest, null, 2), 'utf-8')
  await writeFile(gridPath, JSON.stringify(gridExport, null, 2), 'utf-8')

  return {
    manifest,
    grid: { cols: grid.cols, rows: grid.rows, cellCount: grid.cells.size },
    files: {
      manifest: manifestPath,
      grid: gridPath,
    },
  }
}