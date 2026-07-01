import type { Cell, Grid, Viewport } from '@udos/gridcore'

export interface CanvasViewportOptions {
  width: number
  height: number
  zoom: 'auto' | number
  borderMode: 1 | 2 | 3
  displayMode: 'teletext' | 'mono' | 'wireframe'
  palette: 'usx' | 'c64' | 'teletext' | 'nes'
  font: 'petme64' | 'teletext50' | 'custom'
  flashInterval?: number
  crtEffects?: {
    scanlines: boolean
    glow: boolean
    vignette: boolean
  }
  target?: HTMLElement
}

export abstract class ViewportWidget {
  protected options: CanvasViewportOptions

  constructor(options: CanvasViewportOptions) {
    this.options = options
  }

  abstract render(grid: Grid): void
  abstract update(grid: Grid): void
  abstract updateCell(x: number, y: number, cell: Cell): void
  abstract destroy(): void

  setBorderMode(mode: 1 | 2 | 3): void {
    this.options.borderMode = mode
  }

  setDisplayMode(mode: 'teletext' | 'mono' | 'wireframe'): void {
    this.options.displayMode = mode
  }

  setPalette(palette: 'usx' | 'c64' | 'teletext' | 'nes'): void {
    this.options.palette = palette
  }
}

export interface ViewportWidgetOptions extends CanvasViewportOptions {}
