import { describe, expect, it } from 'vitest'
import {
  GRIDSMITH_TOOLS,
  createGridWorld,
  convertLatLonToUCode,
  convertUCodeToLatLon,
  editCell,
  composeGridLayers,
  findPath,
} from '../src/index'
import { importBasicProgram } from '../src/tools/basic'
import { importAmosProgram } from '../src/tools/amos'
import { createWorldManifest } from '../src/tools/world'

describe('GridSmith tool definitions', () => {
  it('has 16 registered tools', () => {
    expect(GRIDSMITH_TOOLS).toHaveLength(16)
  })

  it.each([
    'create_world',
    'import_basic_program',
    'import_amos_program',
    'create_grid',
    'edit_cell',
    'compose_layers',
    'export_uvox',
    'pathfind',
    'latlon_to_ucode',
    'ucode_to_latlon',
  ])('defines tool: %s', (name) => {
    const tool = GRIDSMITH_TOOLS.find(t => t.name === name)
    expect(tool).toBeDefined()
    expect(tool!.description.length).toBeGreaterThan(0)
    expect(tool!.parameters).toBeTruthy()
  })
})

describe('GridSmith core class', () => {
  it('creates a grid world', () => {
    const world = createGridWorld(10, 5)
    expect(world.cols).toBe(10)
    expect(world.rows).toBe(5)
    expect(world.cellCount).toBe(50)
  })

  it('creates default grid', () => {
    const world = createGridWorld()
    expect(world.cols).toBe(80)
    expect(world.rows).toBe(24)
    expect(world.cellCount).toBe(1920)
  })

  it('returns grid object', () => {
    const world = createGridWorld(4, 3)
    expect(world.grid).toBeDefined()
    expect(world.grid.cols).toBe(4)
    expect(world.grid.rows).toBe(3)
  })
})

describe('Cell editing', () => {
  it('edits a cell and returns previous state', () => {
    const { grid } = createGridWorld(10, 5)
    const result = editCell(grid, 3, 2, 0, { char: '@', fg: 2 })
    expect(result.cell.char).toBe('@')
    expect(result.cell.fg).toBe(2)
    expect(result.previous).toBeDefined()
  })

  it('returns null previous for unset cells', () => {
    const { grid } = createGridWorld(10, 5)
    // A cell not yet populated outside layer 0
    const result = editCell(grid, 0, 0, 99, { char: '!' })
    expect(result.cell.char).toBe('!')
  })
})

describe('Layer composition', () => {
  it('composes layers', () => {
    const { grid } = createGridWorld(10, 5)
    const result = composeGridLayers(grid, [0, 1])
    expect(result.cellCount).toBeGreaterThan(0)
    expect(result.layers.length).toBe(2)
  })
})

describe('Pathfinding', () => {
  it('finds a clear path across empty grid', () => {
    const { grid } = createGridWorld(80, 24)
    const result = findPath(grid, 0, 0, 10, 10, 0)
    expect(result.found).toBe(true)
    expect(result.steps).toBeGreaterThan(0)
  })

  it('returns not found for blocked paths', () => {
    const { grid } = createGridWorld(10, 5)
    // Block the only path with walls
    for (let y = 0; y < 5; y++) {
      editCell(grid, 5, y, 0, { char: '#' })
    }
    const result = findPath(grid, 0, 2, 9, 2, 0)
    expect(result.found).toBe(false)
  })
})

describe('Coordinate conversions', () => {
  it('converts lat/lon to uCode', () => {
    const coord = convertLatLonToUCode(35.6762, 139.6503, 340)
    expect(coord).toMatch(/^L340/)
  })

  it('round-trips uCode', () => {
    const coord = convertLatLonToUCode(-33.8688, 151.2093, 340)
    const location = convertUCodeToLatLon(coord)
    expect(location).toBeTruthy()
    expect(location!.lat).toBeDefined()
    expect(location!.lon).toBeDefined()
  })

  it('returns null for invalid uCode', () => {
    expect(convertUCodeToLatLon('')).toBeNull()
  })
})

describe('BASIC importer', () => {
  it('imports inline BASIC program', async () => {
    const program = '10 PRINT "Hello"\n20 GOTO 10'
    const result = await importBasicProgram(program, 'Test World')
    expect(result.world).toBeTruthy()
    expect(result.files.manifest).toBeDefined()
    expect(result.summary.sourceType).toBe('inline')
  })
})

describe('AMOS importer', () => {
  it('imports inline AMOS program', async () => {
    const program = 'SPRITE 1, 100, 50, 1\nBOB 1, 200, 100, "image.gif"\nSOUND 1, 100, 200, 50\nMOVE 1, 300, 200, 10'
    const result = await importAmosProgram(program, 'AMOS World')
    expect(result.world).toBeTruthy()
    expect(result.files.manifest).toBeDefined()
    expect(result.summary.sourceType).toBe('inline')
    expect(result.summary.sprites).toBe(1)
    expect(result.summary.bobs).toBe(1)
    expect(result.summary.sounds).toBe(1)
    expect(result.summary.moves).toBe(1)
  })

  it('parses comments in AMOS programs', async () => {
    const program = 'REM This is a comment\nSPRITE 1, 10, 20, 1'
    const result = await importAmosProgram(program, 'Comment World')
    const worldAssets = result.world.assets as Record<string, unknown>
    expect(worldAssets.commentCount).toBe(1)
  })
})

describe('World manifest', () => {
  it('creates a world manifest', () => {
    const manifest = createWorldManifest('test-world', 'Test Dungeon', 'dungeon', 42, 'amos')
    expect(manifest.id).toBe('test-world')
    expect(manifest.name).toBe('Test Dungeon')
    expect(manifest.type).toBe('dungeon')
    expect(manifest.seed).toBe(42)
    expect(manifest.source).toBe('amos')
  })

  it('defaults to generated source', () => {
    const manifest = createWorldManifest('map-1', 'Map One', 'earth')
    expect(manifest.source).toBe('generated')
    expect(manifest.seed).toBeUndefined()
  })
})