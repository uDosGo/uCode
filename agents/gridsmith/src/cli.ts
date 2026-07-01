import { GRIDSMITH_TOOLS, convertLatLonToUCode, convertUCodeToLatLon, createGridWorld, importBasicProgram } from './index'

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
      '  grid create --cols 80 --rows 24',
      '  location latlon-to-ucode --lat -33.8688 --lon 151.2093 --level 340',
      '  location ucode-to-latlon --coord L340-0A0B-0000-0',
    ].join('\n') + '\n',
  )
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

  if (section === 'grid' && action === 'create') {
    const cols = Number(argValue(args, '--cols', '80'))
    const rows = Number(argValue(args, '--rows', '24'))
    printJson({ grid: createGridWorld(cols, rows) })
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

  printUsage()
  process.exitCode = 1
}

main()