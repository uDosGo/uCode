import type { Layer } from './layer'

export interface Cube {
  layers: Map<number, Layer>
}

export function createCube(): Cube {
  return { layers: new Map() }
}

export function setCubeLayer(cube: Cube, layer: Layer): void {
  cube.layers.set(layer.z, layer)
}

export function getCubeLayer(cube: Cube, z: number): Layer | undefined {
  return cube.layers.get(z)
}

export function listCubeLayers(cube: Cube): Layer[] {
  return [...cube.layers.values()].sort((a, b) => a.z - b.z)
}
