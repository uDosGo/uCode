import { describe, expect, it } from 'vitest'
import { getPalette, getUSXPalette } from '../src/palette/usx'

describe('palette exports', () => {
  it('returns USX palette by default', () => {
    const palette = getUSXPalette()
    expect(palette.length).toBeGreaterThan(0)
  })

  it('returns named palette', () => {
    const palette = getPalette('teletext')
    expect(palette[1]).toBe('#ff0000')
  })
})
