import { cellSizeAtLevel, latLonToNormalized, normalizedToLatLon } from './latLon'

const EARTH_CIRCUMFERENCE_M = 40075000

export interface ParsedUCode {
  level: number
  gridX: number
  gridY: number
  cellX: number
  cellY: number
  layer: number
}

function encodeBase36(num: number): string {
  return num.toString(36).toUpperCase().padStart(2, '0')
}

function decodeBase36(code: string): number {
  return Number.parseInt(code, 36)
}

export function latLonToUCode(lat: number, lon: number, level = 340, layer = 0): string {
  const { x, y } = latLonToNormalized(lat, lon)
  const cellSizeM = cellSizeAtLevel(level)
  const gridSizeM = cellSizeM * 24
  const totalGrids = EARTH_CIRCUMFERENCE_M / gridSizeM

  const gridX = Math.floor(x * totalGrids)
  const gridY = Math.floor(y * totalGrids)
  const cellX = Math.floor((x * totalGrids * 24) % 24)
  const cellY = Math.floor((y * totalGrids * 24) % 24)

  return `L${level}-${encodeBase36(gridX)}${encodeBase36(gridY)}-${encodeBase36(cellX)}${encodeBase36(cellY)}-${layer}`
}

export function parseUCode(code: string): ParsedUCode | null {
  const match = code.match(/^L(\d+)-([A-Z0-9]{2})([A-Z0-9]{2})-([A-Z0-9]{2})([A-Z0-9]{2})-(\d)$/)
  if (!match) return null

  const [, level, gx, gy, cx, cy, layer] = match
  return {
    level: Number.parseInt(level, 10),
    gridX: decodeBase36(gx),
    gridY: decodeBase36(gy),
    cellX: decodeBase36(cx),
    cellY: decodeBase36(cy),
    layer: Number.parseInt(layer, 10),
  }
}

export function uCodeToLatLon(code: string): { lat: number; lon: number } | null {
  const parsed = parseUCode(code)
  if (!parsed) return null

  const cellSizeM = cellSizeAtLevel(parsed.level)
  const gridSizeM = cellSizeM * 24
  const totalGrids = EARTH_CIRCUMFERENCE_M / gridSizeM

  const x = (parsed.gridX * 24 + parsed.cellX + 0.5) / (totalGrids * 24)
  const y = (parsed.gridY * 24 + parsed.cellY + 0.5) / (totalGrids * 24)

  return normalizedToLatLon(x, y)
}
