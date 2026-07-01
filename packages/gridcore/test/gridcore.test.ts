import { describe, expect, it } from 'vitest'
import { createGrid, getCell } from '../src/geometry/grid'
import { latLonToUCode, parseUCode, uCodeToLatLon } from '../src/coordinates/uCode'
import { calculateViewportSize } from '../src/viewport/calculator'

describe('gridcore smoke tests', () => {
  it('creates a populated grid', () => {
    const grid = createGrid(4, 3)
    expect(grid.cells.size).toBe(12)
    expect(getCell(grid, 0, 0, 0)).toBeTruthy()
  })

  it('round-trips uCode to geographic point', () => {
    const code = latLonToUCode(35.6762, 139.6503, 340, 0)
    const parsed = parseUCode(code)
    expect(parsed).toBeTruthy()

    const back = uCodeToLatLon(code)
    expect(back).toBeTruthy()
    expect(Math.abs(back!.lat - 35.6762)).toBeLessThan(10)
    expect(Math.abs(back!.lon - 139.6503)).toBeLessThan(10)
  })

  it('calculates viewport size', () => {
    const result = calculateViewportSize(1600, 900, {
      cols: 80,
      rows: 24,
      zoom: 1,
      borderMode: 1,
      displayMode: 'teletext',
    }, 24, 24)

    expect(result.scale).toBeGreaterThan(0)
    expect(result.width).toBeGreaterThan(0)
    expect(result.height).toBeGreaterThan(0)
  })
})
