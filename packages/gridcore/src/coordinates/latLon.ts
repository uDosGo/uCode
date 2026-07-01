const EARTH_CIRCUMFERENCE_M = 40075000

export function cellSizeAtLevel(level: number): number {
  return EARTH_CIRCUMFERENCE_M / Math.pow(2, (level - 300) / 10)
}

export function latLonToNormalized(lat: number, lon: number): { x: number; y: number } {
  const x = (lon + 180) / 360
  const y =
    (1 -
      Math.log(
        Math.tan((lat * Math.PI) / 180) +
          1 / Math.cos((lat * Math.PI) / 180),
      ) /
        Math.PI) /
    2
  return { x, y }
}

export function normalizedToLatLon(x: number, y: number): { lat: number; lon: number } {
  const lon = x * 360 - 180
  const lat = Math.atan(Math.sinh(Math.PI * (1 - 2 * y))) * (180 / Math.PI)
  return { lat, lon }
}

export function haversineDistanceMeters(
  a: { lat: number; lon: number },
  b: { lat: number; lon: number },
): number {
  const R = 6371000
  const dLat = ((b.lat - a.lat) * Math.PI) / 180
  const dLon = ((b.lon - a.lon) * Math.PI) / 180
  const aa =
    Math.sin(dLat / 2) * Math.sin(dLat / 2) +
    Math.cos((a.lat * Math.PI) / 180) *
      Math.cos((b.lat * Math.PI) / 180) *
      Math.sin(dLon / 2) *
      Math.sin(dLon / 2)
  const c = 2 * Math.atan2(Math.sqrt(aa), Math.sqrt(1 - aa))
  return R * c
}
