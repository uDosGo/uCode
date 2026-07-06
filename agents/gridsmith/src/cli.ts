import { createGrid } from '@udos/gridcore'
import {
  GRIDSMITH_TOOLS,
  createGridWorld,
  convertLatLonToUCode,
  convertUCodeToLatLon,
  importAmosProgram,
  importBasicProgram,
  editCell,
  composeGridLayers,
  exportUvox,
  findPath,
  createWorld,
  sourceMiner,
  lensCraft,
} from './index'

function argValue(args: string[], flag: string, fallback?: string): string | undefined {
  const index = args.indexOf(flag)
  if (index === -1 || index + 1 >= args.length) return fallback
  return args[index + 1]
}

function printJson(value: unknown): void {
  process.stdout.write(`${JSON.stringify(value, null, 2)}\n`)
}

function printUsage(): void {
  process.stdout.write(
    [
      'GridSmith CLI',
      '',
      'Commands:',
      '  tools list',
      '  world create --name "My World" --type dungeon [--cols 80 --rows 24 --seed 42]',
      '  world import-basic --program <file|code> --world-name "Name"',
      '  world import-amos --program <file|code> --world-name "Name"',
      '  grid create [--grid-id mygrid] [--cols 80 --rows 24]',
      '  cell edit --grid-id mygrid --x 0 --y 0 [--layer 0] --char X --fg 7 --bg 0',
      '  layers compose --grid-id mygrid [--layers 0,1,2]',
      '  uvox export --grid-id mygrid --output output.uvox',
      '  path find --grid-id mygrid --start-x 0 --start-y 0 --end-x 10 --end-y 10 [--layer 0]',
      '  location latlon-to-ucode --lat -33.8688 --lon 151.2093 --level 340',
      '  location ucode-to-latlon --coord L340-0A0B-0000-0',
    ].join('\n') + '\n',
  )
}

// Stateful grid registry for CLI
const gridRegistry = new Map<string, ReturnType<typeof createGrid>>()

function getOrCreateGrid(id: string, cols = 80, rows = 24) {
  let grid = gridRegistry.get(id)
  if (!grid) {
    grid = createGrid(cols, rows)
    gridRegistry.set(id, grid)
  }
  return grid
}

function main(): void {
  const args = process.argv.slice(2)
  const [section, action] = args

  if (!section) {
    printUsage()
    process.exitCode = 1
    return
  }

  if (section === 'tools' && action === 'list') {
    printJson({ tools: GRIDSMITH_TOOLS })
    return
  }

  if (section === 'world' && action === 'create') {
    const name = argValue(args, '--name', 'New World') || 'New World'
    const type = argValue(args, '--type', 'earth') as 'earth' | 'dungeon' | 'vault' | 'library'
    const cols = Number(argValue(args, '--cols', '80'))
    const rows = Number(argValue(args, '--rows', '24'))
    const seed = Number(argValue(args, '--seed', '0')) || undefined
    createWorld({ name, type, cols, rows, seed })
      .then(result => printJson(result))
      .catch(error => {
        process.stderr.write(`${String(error)}\n`)
        process.exitCode = 1
      })
    return
  }

  if (section === 'world' && action === 'import-basic') {
    const program = argValue(args, '--program', '') || ''
    const worldName = argValue(args, '--world-name', 'Imported BASIC World') || 'Imported BASIC World'
    importBasicProgram(program, worldName)
      .then(result => printJson(result))
      .catch(error => {
        process.stderr.write(`${String(error)}\n`)
        process.exitCode = 1
      })
    return
  }

  if (section === 'world' && action === 'import-amos') {
    const program = argValue(args, '--program', '') || ''
    const worldName = argValue(args, '--world-name', 'Imported AMOS World') || 'Imported AMOS World'
    importAmosProgram(program, worldName)
      .then(result => printJson(result))
      .catch(error => {
        process.stderr.write(`${String(error)}\n`)
        process.exitCode = 1
      })
    return
  }

  if (section === 'grid' && action === 'create') {
    const gridId = argValue(args, '--grid-id', `grid-${Date.now()}`) || `grid-${Date.now()}`
    const cols = Number(argValue(args, '--cols', '80'))
    const rows = Number(argValue(args, '--rows', '24'))
    const world = createGridWorld(cols, rows)
    gridRegistry.set(gridId, world.grid)
    printJson({ gridId, cols: world.cols, rows: world.rows, cellCount: world.cellCount })
    return
  }

  if (section === 'cell' && action === 'edit') {
    const gridId = argValue(args, '--grid-id', 'default') || 'default'
    const grid = getOrCreateGrid(gridId)
    const x = Number(argValue(args, '--x', '0'))
    const y = Number(argValue(args, '--y', '0'))
    const layer = Number(argValue(args, '--layer', '0'))
    const char = argValue(args, '--char')
    const fg = argValue(args, '--fg')
    const bg = argValue(args, '--bg')
    const data: Record<string, unknown> = {}
    if (char !== undefined) data.char = char
    if (fg !== undefined) data.fg = Number(fg)
    if (bg !== undefined) data.bg = Number(bg)
    printJson(editCell(grid, x, y, layer, data))
    return
  }

  if (section === 'layers' && action === 'compose') {
    const gridId = argValue(args, '--grid-id', 'default') || 'default'
    const grid = getOrCreateGrid(gridId)
    const layersStr = argValue(args, '--layers', '0,1,2,3,4,5')
    const layers = (layersStr || '0,1,2,3,4,5').split(',').map(Number)
    const result = composeGridLayers(grid, layers)
    printJson({ cellCount: result.cellCount, layerCount: result.layers.length })
    return
  }

  if (section === 'uvox' && action === 'export') {
    const gridId = argValue(args, '--grid-id', 'default') || 'default'
    const grid = getOrCreateGrid(gridId)
    const output = argValue(args, '--output', 'output.uvox') || 'output.uvox'
    exportUvox(grid, gridId, output)
      .then(result => printJson(result))
      .catch(error => {
        process.stderr.write(`${String(error)}\n`)
        process.exitCode = 1
      })
    return
  }

  if (section === 'path' && action === 'find') {
    const gridId = argValue(args, '--grid-id', 'default') || 'default'
    const grid = getOrCreateGrid(gridId)
    const startX = Number(argValue(args, '--start-x', '0'))
    const startY = Number(argValue(args, '--start-y', '0'))
    const endX = Number(argValue(args, '--end-x', '0'))
    const endY = Number(argValue(args, '--end-y', '0'))
    const layer = Number(argValue(args, '--layer', '0'))
    printJson(findPath(grid, startX, startY, endX, endY, layer))
    return
  }

  if (section === 'location' && action === 'latlon-to-ucode') {
    const lat = Number(argValue(args, '--lat'))
    const lon = Number(argValue(args, '--lon'))
    const level = Number(argValue(args, '--level', '340'))
    printJson({ coord: convertLatLonToUCode(lat, lon, level) })
    return
  }

  if (section === 'location' && action === 'ucode-to-latlon') {
    const coord = argValue(args, '--coord', '') || ''
    printJson({ location: convertUCodeToLatLon(coord) })
    return
  }

  if (section === 'skill' && action === 'source-miner') {
    const sourcePath = argValue(args, '--source', process.cwd()) || process.cwd()
    const langStr = argValue(args, '--language', '6502') || '6502'
    const lang = langStr.split(',').map(s => s.trim())
    const targetPatterns = (argValue(args, '--patterns', '') || '').split(',').filter(Boolean)
    const excludePatterns = (argValue(args, '--exclude', '') || '').split(',').filter(Boolean)

    const result = sourceMiner({
      source: { type: 'local_path', url: sourcePath, language: lang },
      options: {
        scan_depth: 'full',
        target_patterns: targetPatterns.length > 0 ? targetPatterns : undefined,
        exclude_patterns: excludePatterns.length > 0 ? excludePatterns : undefined,
      },
    })
    printJson(result)
    return
  }

  if (section === 'skill' && action === 'lens-craft') {
    const minerJson = argValue(args, '--miner-report', '') || ''
    const moduleName = argValue(args, '--module', 'lens_extractor') || 'lens_extractor'
    const outputPath = argValue(args, '--output', '') || ''

    if (!minerJson) {
      process.stderr.write('Error: --miner-report required (Source-Miner JSON output)\n')
      process.exitCode = 1
      return
    }

    const report = JSON.parse(minerJson)
    const result = lensCraft({
      source_miner_report: report,
      emulator: { type: '6502', endianness: 'little' },
      output: {
        language: 'python',
        module_name: moduleName,
        path: outputPath || undefined,
      },
    })
    printJson(result)
    return
  }

  printUsage()
  process.exitCode = 1
}

main()