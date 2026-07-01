import type { Cell, Grid } from '@udos/gridcore'
import { CanvasViewport } from '../canvas/CanvasViewport'
import { DOMViewport } from '../dom/DOMViewport'
import { type CanvasViewportOptions, ViewportWidget } from './ViewportWidget'

export class TerminalWidget extends ViewportWidget {
  private viewport: DOMViewport

  constructor(options: CanvasViewportOptions) {
    super({ ...options, font: 'petme64' })
    this.viewport = new DOMViewport({ ...options, font: 'petme64' })
  }

  render(grid: Grid): void {
    this.viewport.render(grid)
  }

  update(grid: Grid): void {
    this.viewport.update(grid)
  }

  updateCell(x: number, y: number, cell: Cell): void {
    this.viewport.updateCell(x, y, cell)
  }

  destroy(): void {
    this.viewport.destroy()
  }
}

export class TeletextWidget extends ViewportWidget {
  private viewport: CanvasViewport

  constructor(options: CanvasViewportOptions) {
    super({
      ...options,
      font: 'teletext50',
      crtEffects: options.crtEffects ?? { scanlines: true, glow: true, vignette: true },
    })
    this.viewport = new CanvasViewport({
      ...options,
      font: 'teletext50',
      crtEffects: options.crtEffects ?? { scanlines: true, glow: true, vignette: true },
    })
  }

  render(grid: Grid): void {
    this.viewport.render(grid)
  }

  update(grid: Grid): void {
    this.viewport.update(grid)
  }

  updateCell(x: number, y: number, cell: Cell): void {
    this.viewport.updateCell(x, y, cell)
  }

  destroy(): void {
    this.viewport.destroy()
  }
}
