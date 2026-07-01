export interface CRTEffects {
  scanlines: boolean
  glow: boolean
  vignette: boolean
}

export function applyCRTEffectsFilter(effects: CRTEffects): string {
  const filters: string[] = []
  if (effects.glow) filters.push('drop-shadow(0 0 6px rgba(120, 255, 210, 0.35))')
  if (effects.scanlines) filters.push('contrast(1.06)')
  if (effects.vignette) filters.push('brightness(0.95)')
  return filters.join(' ') || 'none'
}
