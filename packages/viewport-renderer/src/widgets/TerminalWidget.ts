import type { Cell, Grid } from "@udos/gridcore";
import {
  ViewportWidget,
  type CanvasViewportOptions,
} from "../core/ViewportWidget";
import { DOMViewport } from "../dom/DOMViewport";

export class TerminalWidget extends ViewportWidget {
  private viewport: DOMViewport;

  constructor(options: CanvasViewportOptions) {
    super({ ...options, font: "petme64" });
    this.viewport = new DOMViewport({ ...options, font: "petme64" });
  }

  render(grid: Grid): void {
    this.viewport.render(grid);
  }

  update(grid: Grid): void {
    this.viewport.update(grid);
  }

  updateCell(x: number, y: number, cell: Cell): void {
    this.viewport.updateCell(x, y, cell);
  }

  destroy(): void {
    this.viewport.destroy();
  }
}
