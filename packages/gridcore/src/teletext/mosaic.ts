import type { Cell } from '../geometry/cell'
import { createEmptyBlock2x3, type Block2x3 } from './block2x3'

export function calculateMosaicBlock(cell: Cell): Block2x3 {
  const block = createEmptyBlock2x3()
  const seed = `${cell.x},${cell.y},${cell.layer}`.split('').reduce((acc, c) => acc + c.charCodeAt(0), 0)

  block.topLeft = (seed & 1) === 1
  block.topRight = (seed & 2) === 2
  block.midLeft = (seed & 4) === 4
  block.midRight = (seed & 8) === 8
  block.bottomLeft = (seed & 16) === 16
  block.bottomRight = (seed & 32) === 32

  return block
}
