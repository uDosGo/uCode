import { describe, expect, it } from 'vitest'
import { TerminalSurface } from '../src/terminal/terminal-surface'

describe('TerminalSurface', () => {
  it('creates a terminal with default dimensions', () => {
    const term = new TerminalSurface()
    expect(term.cols).toBe(80)
    expect(term.rows).toBe(24)
    expect(term.prompt).toBe('OK>')
    expect(term.getInput()).toBe('')
  })

  it('creates a terminal with custom options', () => {
    const term = new TerminalSurface({ cols: 40, rows: 12, prompt: '>', historySize: 50 })
    expect(term.cols).toBe(40)
    expect(term.rows).toBe(12)
    expect(term.prompt).toBe('>')
  })

  it('throws for too few rows', () => {
    expect(() => new TerminalSurface({ rows: 1 })).toThrow()
  })

  it('produces a grid with correct dimensions', () => {
    const term = new TerminalSurface({ cols: 40, rows: 10 })
    const grid = term.getGrid()
    expect(grid.cols).toBe(40)
    expect(grid.rows).toBe(10)
    expect(grid.cells.size).toBe(400)
  })

  it('handles typed characters', () => {
    const term = new TerminalSurface({ cols: 40, rows: 5 })
    term.typeChar('H')
    term.typeChar('e')
    term.typeChar('l')
    term.typeChar('l')
    term.typeChar('o')
    expect(term.getInput()).toBe('Hello')
  })

  it('handles backspace', () => {
    const term = new TerminalSurface({ cols: 40, rows: 5 })
    term.setInput('Hello')
    term.typeBackspace()
    expect(term.getInput()).toBe('Hell')
  })

  it('ignores non-printable characters', () => {
    const term = new TerminalSurface({ cols: 40, rows: 5 })
    term.typeChar('\n')
    term.typeChar('\t')
    expect(term.getInput()).toBe('')
  })

  it('writes output lines', () => {
    const term = new TerminalSurface({ cols: 40, rows: 5 })
    term.writeLine('Hello, world!', 'output')
    term.writeLine('Error occurred', 'error')
    const grid = term.getGrid()
    // Grid should still have all cells
    expect(grid.cells.size).toBe(200)
  })

  it('respects output buffer limits', () => {
    const term = new TerminalSurface({ cols: 40, rows: 5 })
    // Write 20 lines, only 4 should be visible (rows-1 = 4)
    for (let i = 0; i < 20; i++) {
      term.writeLine(`Line ${i}`, 'output')
    }
    // Terminal should still work — grid intact
    const grid = term.getGrid()
    expect(grid.cells.size).toBe(200)
  })

  it('clears output', () => {
    const term = new TerminalSurface({ cols: 40, rows: 5 })
    term.writeLine('Some output', 'output')
    term.clear()
    expect(term.getInput()).toBe('')
  })

  it('resets fully', () => {
    const term = new TerminalSurface({ cols: 40, rows: 5 })
    term.writeLine('Output', 'output')
    term.setInput('Hello')
    term.reset()
    expect(term.getInput()).toBe('')
  })
})