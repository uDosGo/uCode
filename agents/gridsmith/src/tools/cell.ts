import { setCell, getCell, createCell } from '@udos/gridcore'
import type { Grid } from '@udos/gridcore'

export interface CellPayload {
  char?: string
  fg?: number
  bg?: number
  [key: string]: unknown
}

export function editCell(
  grid: Grid,
  x: number,
  y: number,
  layer: number,
  data: CellPayload,
): { cell: Record<string, unknown>; previous: Record<string, unknown> | null } {
  const existing = getCell(grid, x, y, layer)

  const coord = existing?.coord ?? `L340-${x.toString(36).toUpperCase().padStart(2, '0')}${y.toString(36).toUpperCase().padStart(2, '0')}-0000-0`

  const cell = createCell(coord, x, y, layer)
  if (data.char !== undefined) cell.char = data.char
  if (data.fg !== undefined) cell.fg = data.fg
  if (data.bg !== undefined) cell.bg = data.bg

  setCell(grid, cell)

  return {
    cell: { x: cell.x, y: cell.y, layer: cell.layer, char: cell.char, fg: cell.fg, bg: cell.bg },
    previous: existing ? { x: existing.x, y: existing.y, layer: existing.layer, char: existing.char, fg: existing.fg, bg: existing.bg } : null,
  }
}