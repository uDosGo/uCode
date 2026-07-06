// Shared type definitions extracted from gridsmith, gridcore, and viewport-renderer.
// These are the canonical interfaces used across the uCode monorepo.

export interface Coordinate {
  x: number
  y: number
  layer: number
}

export interface PathNode {
  x: number
  y: number
  layer: number
}

export interface PathResult {
  path: PathNode[]
  steps: number
  found: boolean
}

export interface GridCell {
  coord: string
  x: number
  y: number
  layer: number
  char?: string
  fg?: number
  bg?: number
}

export interface GridSpec {
  cols: number
  rows: number
  cellSize: number
}

export interface WorldManifest {
  id: string
  name: string
  type: 'earth' | 'dungeon' | 'vault' | 'library'
  seed?: number
  source?: 'generated' | 'basic' | 'amos'
}

export interface LayerSummary {
  z: number
  cellCount: number
}

export interface UvoxCell {
  x: number
  y: number
  layer: number
  char: string
  fg: number
  bg: number
  coord: string
}

export interface UvoxManifest {
  format: 'uvox/1.0'
  gridId: string
  cols: number
  rows: number
  createdAt: string
  cells: UvoxCell[]
}

export interface ToolParameter {
  type: 'string' | 'number' | 'array' | 'object'
  description: string
  default?: string | number | number[]
  items?: { type: 'number' }
}

export interface ToolDefinition {
  name: string
  description: string
  parameters: Record<string, ToolParameter>
}

export interface CellEditPayload {
  char?: string
  fg?: number
  bg?: number
  [key: string]: unknown
}

export interface CellEditResult {
  cell: Record<string, unknown>
  previous: Record<string, unknown> | null
}