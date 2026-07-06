import { createLayer, composeLayers, getCell, listCells } from '@udos/gridcore'
import type { Grid, Layer, Cell } from '@udos/gridcore'

export interface LayerSummary { z: number; cellCount: number }

export function composeGridLayers(grid: Grid, layerIndices: number[]): { layers: LayerSummary[]; composed: Cell[]; cellCount: number } {
  const layers: Layer[] = []

  for (const z of layerIndices) {
    const cells: Cell[] = []
    for (let y = 0; y < grid.rows; y++) {
      for (let x = 0; x < grid.cols; x++) {
        const cell = getCell(grid, x, y, z)
        if (cell) {
          cells.push(cell)
        }
      }
    }
    layers.push(createLayer(z, cells))
  }

  const composed = composeLayers(layers)

  return {
    layers: layers.map(l => ({ z: l.z, cellCount: l.cells.length })),
    composed,
    cellCount: composed.length,
  }
}