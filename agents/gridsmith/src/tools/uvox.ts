import { writeFile, mkdir } from 'node:fs/promises'
import path from 'node:path'
import type { Grid } from '@udos/gridcore'
import { listCells } from '@udos/gridcore'

export interface UvoxManifest {
  format: 'uvox/1.0'
  gridId: string
  cols: number
  rows: number
  createdAt: string
  cells: UvoxCell[]
}

export interface UvoxCell {
  x: number
  y: number
  layer: number
  char: string
  fg: number
  bg: number
  coord: string
}

export async function exportUvox(
  grid: Grid,
  gridId: string,
  outputPath: string,
): Promise<{ path: string; bytes: number; cellCount: number }> {
  const resolved = path.resolve(outputPath)
  await mkdir(path.dirname(resolved), { recursive: true })

  const cells: UvoxCell[] = listCells(grid).map(cell => ({
    x: cell.x,
    y: cell.y,
    layer: cell.layer,
    char: cell.char ?? ' ',
    fg: cell.fg ?? 7,
    bg: cell.bg ?? 0,
    coord: cell.coord,
  }))

  const manifest: UvoxManifest = {
    format: 'uvox/1.0',
    gridId,
    cols: grid.cols,
    rows: grid.rows,
    createdAt: new Date().toISOString(),
    cells,
  }

  const json = JSON.stringify(manifest, null, 2)
  await writeFile(resolved, json, 'utf-8')

  return {
    path: resolved,
    bytes: Buffer.byteLength(json, 'utf-8'),
    cellCount: cells.length,
  }
}