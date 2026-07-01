import type { Grid } from '@udos/gridcore'
import { CanvasViewport } from '../canvas/CanvasViewport'
import { DOMViewport } from '../dom/DOMViewport'

export type RendererType = 'canvas' | 'dom'

export interface MapRendererOptions {
  rendererType: RendererType
  width: number
  height: number
  target?: HTMLElement
}

export class MapRenderer {
  private options: MapRendererOptions
  private canvasRenderer: CanvasViewport | null = null
  private domRenderer: DOMViewport | null = null

  constructor(options: MapRendererOptions) {
    this.options = options
    if (options.rendererType === 'canvas') {
      this.canvasRenderer = new CanvasViewport({
        width: options.width,
        height: options.height,
        zoom: 1,
        borderMode: 1,
        displayMode: 'teletext',
        palette: 'usx',
        font: 'teletext50',
        target: options.target,
      })
    } else {
      this.domRenderer = new DOMViewport({
        width: options.width,
        height: options.height,
        zoom: 1,
        borderMode: 1,
        displayMode: 'teletext',
        palette: 'usx',
        font: 'teletext50',
        target: options.target,
      })
    }
  }

  render(grid: Grid): void {
    if (this.canvasRenderer) this.canvasRenderer.render(grid)
    if (this.domRenderer) this.domRenderer.render(grid)
  }

  renderTile(grid: Grid, _x: number, _y: number, _zoom: number): void {
    this.render(grid)
  }

  renderLayer(grid: Grid, _layerId: string): void {
    this.render(grid)
  }

  exportToPNG(): string | null {
    if (!this.canvasRenderer) return null
    return this.canvasRenderer.toDataURL('image/png')
  }
}

export function renderMap(grid: Grid, renderer: MapRenderer): void {
  renderer.render(grid)
}
