export interface GlyphMap {
  unicode: string
  bitmap: number[][]
}

export class SVGFontMapper {
  private families = new Map<string, ArrayBuffer>()

  loadFont(family: string, fontData: ArrayBuffer): void {
    this.families.set(family, fontData)
  }

  parseSVG(svgString: string): { source: string } {
    return { source: svgString }
  }

  svgToBitmap(_svg: { source: string }, width: number, height: number): number[][] {
    return Array.from({ length: height }, () => Array.from({ length: width }, () => 0))
  }

  bitmapToGrid(bitmap: number[][]): number[][] {
    return bitmap.map(row => [...row])
  }

  extractGlyphs(_svgFont: { source: string }): GlyphMap[] {
    return []
  }

  mapGlyphToCell(glyph: GlyphMap): number[][] {
    return glyph.bitmap
  }
}
