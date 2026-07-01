import type { Grid } from '../geometry/grid'
import type { Cell } from '../geometry/cell'

export type BorderMode = 1 | 2 | 3
export type DisplayMode = 'teletext' | 'mono' | 'wireframe'

export interface Viewport {
  cols: number
  rows: number
  zoom: number
  borderMode: BorderMode
  displayMode: DisplayMode
}

export const BORDER_MODE_CONFIGS: Record<BorderMode, { fillFraction: number }> = {
  1: { fillFraction: 0.8 },
  2: { fillFraction: 0.9 },
  3: { fillFraction: 0.98 },
}

export function getViewportCells(grid: Grid, viewport: Viewport): Cell[] {
  const rows = Math.min(viewport.rows, grid.rows)
  const cols = Math.min(viewport.cols, grid.cols)
  const visible: Cell[] = []

  for (let y = 0; y < rows; y++) {
    for (let x = 0; x < cols; x++) {
      const key = `${x}:${y}:0`
      const cell = grid.cells.get(key)
      if (cell) visible.push(cell)
    }
  }

  return visible
}

export function calculateViewportSize(
  containerWidth: number,
  containerHeight: number,
  viewport: Viewport,
  cellWidth: number,
  cellHeight: number,
): { width: number; height: number; scale: number; padX: number; padY: number } {
  const border = BORDER_MODE_CONFIGS[viewport.borderMode]
  const padFraction = (1 - border.fillFraction) / 2
  const availableWidth = containerWidth * (1 - padFraction * 2)
  const availableHeight = containerHeight * (1 - padFraction * 2)

  const contentWidth = viewport.cols * cellWidth
  const contentHeight = viewport.rows * cellHeight

  const scale = Math.min(availableWidth / contentWidth, availableHeight / contentHeight, 4) * viewport.zoom

  return {
    width: contentWidth * scale,
    height: contentHeight * scale,
    scale,
    padX: containerWidth * padFraction,
    padY: containerHeight * padFraction,
  }
}
