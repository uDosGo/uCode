import {
  BORDER_MODE_CONFIGS,
  calculateViewportSize,
  getViewportCells,
  type Cell,
  type Grid,
  type Viewport,
} from '@udos/gridcore'
import { applyCRTEffectsFilter } from '../effects/crt'
import { getPalette } from '../palette/usx'
import { ViewportWidget, type CanvasViewportOptions } from '../core/ViewportWidget'

export class CanvasViewport extends ViewportWidget {
  private canvas: HTMLCanvasElement
  private context: CanvasRenderingContext2D
  private lastGrid: Grid | null = null

  constructor(options: CanvasViewportOptions) {
    super(options)
    this.canvas = document.createElement('canvas')
    this.canvas.width = options.width
    this.canvas.height = options.height
    this.context = this.canvas.getContext('2d') as CanvasRenderingContext2D
    if (options.target) options.target.appendChild(this.canvas)
  }

  render(grid: Grid): void {
    this.lastGrid = grid
    this.drawGrid(grid)
  }

  update(grid: Grid): void {
    this.lastGrid = grid
    this.drawGrid(grid)
  }

  updateCell(x: number, y: number, cell: Cell): void {
    if (!this.lastGrid) return
    this.lastGrid.cells.set(`${x}:${y}:${cell.layer}`, cell)
    this.drawGrid(this.lastGrid)
  }

  setZoom(zoom: number): void {
    this.options.zoom = zoom
    if (this.lastGrid) this.drawGrid(this.lastGrid)
  }

  toDataURL(format: 'image/png' = 'image/png'): string {
    return this.canvas.toDataURL(format)
  }

  toBlob(callback: (blob: Blob | null) => void): void {
    this.canvas.toBlob(callback)
  }

  destroy(): void {
    this.canvas.remove()
  }

  private drawGrid(grid: Grid): void {
    const viewport: Viewport = {
      cols: grid.cols,
      rows: grid.rows,
      zoom: typeof this.options.zoom === 'number' ? this.options.zoom : 1,
      borderMode: this.options.borderMode,
      displayMode: this.options.displayMode,
    }

    const visible = getViewportCells(grid, viewport)
    const metrics = calculateViewportSize(
      this.options.width,
      this.options.height,
      viewport,
      24,
      24,
    )
    const palette = getPalette(this.options.palette)

    this.context.clearRect(0, 0, this.canvas.width, this.canvas.height)
    this.context.save()
    this.context.translate(metrics.padX, metrics.padY)
    this.context.scale(metrics.scale, metrics.scale)

    for (const cell of visible) {
      const fg = palette[Math.max(0, Math.min(cell.fg ?? 7, palette.length - 1))]
      const bg = palette[Math.max(0, Math.min(cell.bg ?? 0, palette.length - 1))]
      const x = cell.x * 24
      const y = cell.y * 24

      this.context.fillStyle = bg
      this.context.fillRect(x, y, 24, 24)
      this.context.fillStyle = fg
      this.context.font = '18px monospace'
      this.context.textBaseline = 'middle'
      this.context.textAlign = 'center'
      this.context.fillText(cell.char ?? ' ', x + 12, y + 12)
    }

    this.context.restore()

    if (this.options.crtEffects) {
      this.canvas.style.filter = applyCRTEffectsFilter(this.options.crtEffects)
    }

    const border = BORDER_MODE_CONFIGS[this.options.borderMode]
    this.canvas.style.padding = `${((1 - border.fillFraction) / 2) * 100}%`
  }
}
