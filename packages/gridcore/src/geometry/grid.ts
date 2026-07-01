import { createCell, type Cell } from './cell'

export interface Grid {
  cols: number
  rows: number
  cells: Map<string, Cell>
}

export function cellKey(x: number, y: number, layer: number): string {
  return `${x}:${y}:${layer}`
}

export function createGrid(cols: number, rows: number): Grid {
  const grid: Grid = {
    cols,
    rows,
    cells: new Map(),
  }

  for (let y = 0; y < rows; y++) {
    for (let x = 0; x < cols; x++) {
      const coord = `L340-${x.toString(36).toUpperCase().padStart(2, '0')}${y.toString(36).toUpperCase().padStart(2, '0')}-0000-0`
      grid.cells.set(cellKey(x, y, 0), createCell(coord, x, y, 0))
    }
  }

  return grid
}

export function getCell(grid: Grid, x: number, y: number, layer: number): Cell | undefined {
  return grid.cells.get(cellKey(x, y, layer))
}

export function setCell(grid: Grid, cell: Cell): void {
  grid.cells.set(cellKey(cell.x, cell.y, cell.layer), cell)
}

export function listCells(grid: Grid): Cell[] {
  return [...grid.cells.values()]
}
