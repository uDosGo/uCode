import type { Cell } from './cell'

export interface Layer {
  z: number
  cells: Cell[]
}

export function createLayer(z: number, cells: Cell[] = []): Layer {
  return { z, cells }
}

export function composeLayers(layers: Layer[]): Cell[] {
  const byPosition = new Map<string, Cell>()
  const sorted = [...layers].sort((a, b) => a.z - b.z)

  for (const layer of sorted) {
    for (const cell of layer.cells) {
      byPosition.set(`${cell.x}:${cell.y}`, cell)
    }
  }

  return [...byPosition.values()]
}
