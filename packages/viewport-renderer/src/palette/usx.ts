export type PaletteName = 'usx' | 'c64' | 'teletext' | 'nes'

export const USX_PALETTE = ['#010409', '#E76F51', '#238636', '#d29922', '#58a6ff', '#bc8cff', '#39d2c0', '#e6edf3']
export const C64_PALETTE = ['#000000', '#FFFFFF', '#813338', '#75cec8', '#8e3c97', '#56ac4d', '#2e2c9b', '#edf171']
export const TELETEXT_PALETTE = ['#000000', '#ff0000', '#00ff00', '#ffff00', '#0000ff', '#ff00ff', '#00ffff', '#ffffff']
export const NES_PALETTE = ['#7c7c7c', '#0000fc', '#0000bc', '#4428bc', '#940084', '#a80020', '#a81000', '#881400']

export function getUSXPalette(): string[] {
  return [...USX_PALETTE]
}

export function getC64Palette(): string[] {
  return [...C64_PALETTE]
}

export function getTeletextPalette(): string[] {
  return [...TELETEXT_PALETTE]
}

export function getPalette(name: PaletteName): string[] {
  if (name === 'c64') return getC64Palette()
  if (name === 'teletext') return getTeletextPalette()
  if (name === 'nes') return [...NES_PALETTE]
  return getUSXPalette()
}
