import { createGrid, listCells, latLonToUCode, uCodeToLatLon } from '@udos/gridcore'
import type { Grid } from '@udos/gridcore'
import { importBasicProgram } from './tools/basic'
import { importAmosProgram } from './tools/amos'
import { editCell } from './tools/cell'
import type { CellPayload } from './tools/cell'
import { composeGridLayers } from './tools/layers'
import { exportUvox } from './tools/uvox'
import { findPath } from './tools/pathfind'
import { createWorld, createWorldManifest } from './tools/world'
import type { WorldCreationOptions } from './tools/world'
import { sourceMiner } from './tools/source-miner'
import type {
  SourceMinerInput,
  SourceMinerOutput,
  MemoryMapEntry,
  FunctionEntry,
  DataStructure,
  AssetReference,
  Recommendation,
} from './tools/source-miner'

export interface GridSmithToolParameter {
  type: 'string' | 'number' | 'array' | 'object'
  description: string
  default?: string | number | number[]
  items?: { type: 'number' }
}

export interface GridSmithToolDefinition {
  name: string
  description: string
  parameters: Record<string, GridSmithToolParameter>
}

export const GRIDSMITH_TOOLS: GridSmithToolDefinition[] = [
  {
    name: 'create_world',
    description: 'Create a new world with optional terrain.',
    parameters: {
      name: { type: 'string', description: 'World name' },
      type: { type: 'string', description: 'World type: earth, dungeon, vault, or library' },
      cols: { type: 'number', description: 'Grid column count', default: 80 },
      rows: { type: 'number', description: 'Grid row count', default: 24 },
      seed: { type: 'number', description: 'Random seed', default: 0 },
      terrain: { type: 'object', description: 'Map of "x,y" -> character for terrain' },
    },
  },
  {
    name: 'import_basic_program',
    description: 'Import a BASIC program as a grid world.',
    parameters: {
      program: { type: 'string', description: 'BASIC program code or file path' },
      world_name: { type: 'string', description: 'Name for the generated world' },
    },
  },
  {
    name: 'import_amos_program',
    description: 'Import an AMOS program as a grid world.',
    parameters: {
      program: { type: 'string', description: 'AMOS program code or file path' },
      world_name: { type: 'string', description: 'Name for the generated world' },
    },
  },
  {
    name: 'create_grid',
    description: 'Create a new grid.',
    parameters: {
      cols: { type: 'number', description: 'Grid column count', default: 80 },
      rows: { type: 'number', description: 'Grid row count', default: 24 },
      cell_size: { type: 'number', description: 'Logical cell size', default: 24 },
    },
  },
  {
    name: 'edit_cell',
    description: 'Edit a specific cell.',
    parameters: {
      grid_id: { type: 'string', description: 'Grid identifier' },
      x: { type: 'number', description: 'X cell coordinate' },
      y: { type: 'number', description: 'Y cell coordinate' },
      layer: { type: 'number', description: 'Layer index', default: 0 },
      data: { type: 'object', description: 'Cell payload (char, fg, bg)' },
    },
  },
  {
    name: 'compose_layers',
    description: 'Compose layers into a single view.',
    parameters: {
      grid_id: { type: 'string', description: 'Grid identifier' },
      layers: {
        type: 'array',
        description: 'Ordered layer list',
        default: [0, 1, 2, 3, 4, 5],
        items: { type: 'number' },
      },
    },
  },
  {
    name: 'export_uvox',
    description: 'Export a grid as a .uvox artifact.',
    parameters: {
      grid_id: { type: 'string', description: 'Grid identifier' },
      output_path: { type: 'string', description: 'Output file path' },
    },
  },
  {
    name: 'pathfind',
    description: 'Find path between two points on a grid (A*).',
    parameters: {
      grid_id: { type: 'string', description: 'Grid identifier' },
      start_x: { type: 'number', description: 'Start X coordinate' },
      start_y: { type: 'number', description: 'Start Y coordinate' },
      end_x: { type: 'number', description: 'End X coordinate' },
      end_y: { type: 'number', description: 'End Y coordinate' },
      layer: { type: 'number', description: 'Layer index', default: 0 },
    },
  },
  {
    name: 'latlon_to_ucode',
    description: 'Convert lat/lon to uCode.',
    parameters: {
      lat: { type: 'number', description: 'Latitude' },
      lon: { type: 'number', description: 'Longitude' },
      level: { type: 'number', description: 'uCode level', default: 340 },
    },
  },
  {
    name: 'ucode_to_latlon',
    description: 'Convert uCode to lat/lon.',
    parameters: {
      coord: { type: 'string', description: 'uCode coordinate' },
    },
  },
  {
    name: 'source_miner',
    description: 'Scan 6502 assembly source code for LENS-extractable integration points.',
    parameters: {
      source_path: { type: 'string', description: 'Path to source directory or file' },
      language: { type: 'string', description: 'Source language(s) as CSV', default: '6502' },
      target_patterns: { type: 'string', description: 'File patterns as CSV (e.g. *.asm,*.s)', default: '' },
      exclude_patterns: { type: 'string', description: 'Exclude patterns as CSV (e.g. test_*,*.tmp)', default: '' },
    },
  },
]

export function createGridWorld(cols = 80, rows = 24): { grid: Grid; cols: number; rows: number; cellCount: number } {
  const grid = createGrid(cols, rows)
  return {
    grid,
    cols: grid.cols,
    rows: grid.rows,
    cellCount: listCells(grid).length,
  }
}

export function convertLatLonToUCode(lat: number, lon: number, level = 340): string {
  return latLonToUCode(lat, lon, level)
}

export function convertUCodeToLatLon(coord: string): { lat: number; lon: number } | null {
  return uCodeToLatLon(coord)
}

export {
  importBasicProgram,
  importAmosProgram,
  editCell,
  composeGridLayers,
  exportUvox,
  findPath,
  createWorld,
  createWorldManifest,
  sourceMiner,
}
export type {
  Grid,
  CellPayload,
  WorldCreationOptions,
  SourceMinerInput,
  SourceMinerOutput,
  MemoryMapEntry,
  FunctionEntry,
  DataStructure,
  AssetReference,
  Recommendation,
}
