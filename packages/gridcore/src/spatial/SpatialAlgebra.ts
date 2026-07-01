import { haversineDistanceMeters } from '../coordinates/latLon'
import { latLonToUCode, parseUCode, uCodeToLatLon } from '../coordinates/uCode'

export type Direction = 'N' | 'S' | 'E' | 'W' | 'NE' | 'NW' | 'SE' | 'SW'

export class SpatialAlgebra {
  latLonToUCode(lat: number, lon: number, level: number): string {
    return latLonToUCode(lat, lon, level)
  }

  uCodeToLatLon(coord: string): { lat: number; lon: number } | null {
    return uCodeToLatLon(coord)
  }

  getZoomLevel(coord: string): number | null {
    return parseUCode(coord)?.level ?? null
  }

  getNeighbour(coord: string, direction: Direction): string | null {
    const parsed = parseUCode(coord)
    if (!parsed) return null

    const vectors: Record<Direction, [number, number]> = {
      N: [0, -1],
      S: [0, 1],
      E: [1, 0],
      W: [-1, 0],
      NE: [1, -1],
      NW: [-1, -1],
      SE: [1, 1],
      SW: [-1, 1],
    }

    const [dx, dy] = vectors[direction]
    let cellX = parsed.cellX + dx
    let cellY = parsed.cellY + dy
    let gridX = parsed.gridX
    let gridY = parsed.gridY

    while (cellX < 0) {
      cellX += 24
      gridX -= 1
    }
    while (cellX >= 24) {
      cellX -= 24
      gridX += 1
    }
    while (cellY < 0) {
      cellY += 24
      gridY -= 1
    }
    while (cellY >= 24) {
      cellY -= 24
      gridY += 1
    }

    const to36 = (n: number) => n.toString(36).toUpperCase().padStart(2, '0')
    return `L${parsed.level}-${to36(gridX)}${to36(gridY)}-${to36(cellX)}${to36(cellY)}-${parsed.layer}`
  }

  getBoundingBox(coord1: string, coord2: string): { minLat: number; minLon: number; maxLat: number; maxLon: number } | null {
    const a = uCodeToLatLon(coord1)
    const b = uCodeToLatLon(coord2)
    if (!a || !b) return null

    return {
      minLat: Math.min(a.lat, b.lat),
      minLon: Math.min(a.lon, b.lon),
      maxLat: Math.max(a.lat, b.lat),
      maxLon: Math.max(a.lon, b.lon),
    }
  }

  distanceBetween(coord1: string, coord2: string): number | null {
    const a = uCodeToLatLon(coord1)
    const b = uCodeToLatLon(coord2)
    if (!a || !b) return null
    return haversineDistanceMeters(a, b)
  }

  pathFind(from: string, to: string): string[] {
    if (from === to) return [from]
    return [from, to]
  }

  clusterRegion(coord: string, radius: number): string[] {
    if (radius <= 0) return [coord]
    return [coord]
  }
}
