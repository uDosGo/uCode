import type { GridBuffer } from '../buffer/cell'
import { cloneBuffer } from '../buffer/cell'

type EditorCommand = {
  do: (state: GridBuffer) => GridBuffer
  undo: (state: GridBuffer) => GridBuffer
}

export class GridEditor {
  private state: GridBuffer
  private undoStack: EditorCommand[] = []
  private redoStack: EditorCommand[] = []

  constructor(initial: GridBuffer) {
    this.state = cloneBuffer(initial)
  }

  get buffer(): GridBuffer {
    return cloneBuffer(this.state)
  }

  private execute(command: EditorCommand): void {
    this.state = command.do(this.state)
    this.undoStack.push(command)
    this.redoStack = []
  }

  placeCharacter(x: number, y: number, char: string): void {
    this.execute({
      do: state => {
        const next = cloneBuffer(state)
        if (next[y]?.[x]) next[y][x].char = char.slice(0, 1) || ' '
        return next
      },
      undo: state => {
        const next = cloneBuffer(state)
        if (next[y]?.[x]) next[y][x].char = ' '
        return next
      },
    })
  }

  setPixel(x: number, y: number, color: number): void {
    this.execute({
      do: state => {
        const next = cloneBuffer(state)
        if (next[y]?.[x]) next[y][x].fg = color
        return next
      },
      undo: state => {
        const next = cloneBuffer(state)
        if (next[y]?.[x]) next[y][x].fg = 7
        return next
      },
    })
  }

  clearCell(x: number, y: number): void {
    this.execute({
      do: state => {
        const next = cloneBuffer(state)
        if (next[y]?.[x]) {
          next[y][x].char = ' '
          next[y][x].fg = 7
          next[y][x].bg = 0
        }
        return next
      },
      undo: state => state,
    })
  }

  undo(): void {
    const cmd = this.undoStack.pop()
    if (!cmd) return
    this.state = cmd.undo(this.state)
    this.redoStack.push(cmd)
  }

  redo(): void {
    const cmd = this.redoStack.pop()
    if (!cmd) return
    this.state = cmd.do(this.state)
    this.undoStack.push(cmd)
  }
}
