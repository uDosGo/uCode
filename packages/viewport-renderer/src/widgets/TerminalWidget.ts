import type { Cell, Grid } from '@udos/gridcore'
import {
  TerminalSurface,
  RuntimeBridge,
  TeletextPageProvider,
  type OutputLine,
} from '@udos/gridcore'
import { DOMViewport } from '../dom/DOMViewport'
import { ViewportWidget, type CanvasViewportOptions } from '../core/ViewportWidget'

export interface TerminalWidgetOptions extends CanvasViewportOptions {
  surface?: TerminalSurface
  bridge?: RuntimeBridge
  onTeletextNavigate?: (page: number) => void
}

export class TerminalWidget extends ViewportWidget {
  private viewport: DOMViewport
  private surface: TerminalSurface
  private bridge: RuntimeBridge
  private inputElement: HTMLTextAreaElement | null = null
  private onTeletextNavigate?: (page: number) => void

  constructor(options: TerminalWidgetOptions) {
    super({ ...options, font: 'petme64' })

    this.surface = options.surface ?? new TerminalSurface({
      cols: options.width ? Math.floor(options.width / 24) : 80,
      rows: options.height ? Math.floor(options.height / 24) : 24,
    })

    this.bridge = options.bridge ?? new RuntimeBridge()
    this.onTeletextNavigate = options.onTeletextNavigate

    this.viewport = new DOMViewport({ ...options, font: 'petme64' })

    // Wire surface changes to viewport re-render
    this.surface.onDisplayChange(() => {
      this.viewport.render(this.surface.getGrid())
    })

    // Wire bridge command output → terminal output
    this.bridge.on('command-output', (output: unknown) => {
      if (typeof output === 'string') {
        this.surface.writeLine(output, 'output')
      } else if (Array.isArray(output)) {
        for (const line of output) {
          if (typeof line === 'string') {
            this.surface.writeLine(line, 'output')
          } else if (line && typeof line === 'object' && 'text' in (line as Record<string, unknown>)) {
            const ol = line as { text: string; role: 'output' | 'error' | 'prompt' | 'echo' }
            this.surface.writeLine(ol.text, ol.role)
          }
        }
      }
    })

    // Wire teletext navigation from bridge → external callback
    this.bridge.on('teletext-navigate', (page: unknown) => {
      const pageNum = typeof page === 'number' ? page : parseInt(String(page), 10)
      if (!isNaN(pageNum)) {
        this.onTeletextNavigate?.(pageNum)
      }
    })
  }

  /** Create a hidden textarea for keyboard input capture */
  attachKeyboardInput(container: HTMLElement): void {
    if (this.inputElement) return

    const input = document.createElement('textarea')
    input.style.position = 'absolute'
    input.style.left = '-9999px'
    input.style.width = '1px'
    input.style.height = '1px'
    input.style.opacity = '0'
    input.setAttribute('aria-label', 'Terminal input')

    input.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') {
        e.preventDefault()
        const cmd = this.surface.getInput()
        this.surface.submit()
        // Also send through bridge
        if (cmd) {
          this.bridge.sendCommand(cmd).catch(() => {})
        }
        input.value = ''
      } else if (e.key === 'Backspace') {
        e.preventDefault()
        this.surface.typeBackspace()
      } else if (e.key === 'ArrowUp') {
        e.preventDefault()
        this.surface.navigateHistory(-1)
      } else if (e.key === 'ArrowDown') {
        e.preventDefault()
        this.surface.navigateHistory(1)
      } else if (e.key.length === 1 && e.key.charCodeAt(0) >= 32 && e.key.charCodeAt(0) <= 126) {
        e.preventDefault()
        this.surface.typeChar(e.key)
      }
    })

    // Focus the input on click anywhere in the container
    container.addEventListener('click', () => {
      input.focus()
    })

    container.style.position = 'relative'
    container.appendChild(input)
    this.inputElement = input
  }

  /** Get the underlying terminal surface (for direct programmatic access) */
  getSurface(): TerminalSurface {
    return this.surface
  }

  /** Get the bridge (for wiring to teletext, etc.) */
  getBridge(): RuntimeBridge {
    return this.bridge
  }

  /** Get the DOM element for external attachment */
  getElement(): HTMLDivElement | undefined {
    return (this.viewport as DOMViewport).getElement?.()
  }

  render(grid?: Grid): void {
    this.viewport.render(grid ?? this.surface.getGrid())
  }

  update(grid?: Grid): void {
    this.viewport.update(grid ?? this.surface.getGrid())
  }

  updateCell(x: number, y: number, cell: Cell): void {
    this.viewport.updateCell(x, y, cell)
  }

  destroy(): void {
    this.inputElement?.remove()
    this.inputElement = null
    this.viewport.destroy()
  }
}