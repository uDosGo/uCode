import { mkdir, readFile, writeFile } from 'node:fs/promises'
import path from 'node:path'

interface ParsedBasicLine {
  lineNumber: number | null
  statement: string
}

function slugify(value: string): string {
  return value
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '')
    .slice(0, 80)
}

function parseBasicLines(program: string): ParsedBasicLine[] {
  return program
    .split(/\r?\n/)
    .map(line => line.trimEnd())
    .filter(Boolean)
    .map(line => {
      const match = line.match(/^(\d+)\s*(.*)$/)
      if (!match) {
        return { lineNumber: null, statement: line.trim() }
      }
      return {
        lineNumber: Number(match[1]),
        statement: match[2].trim(),
      }
    })
}

function classifyStatements(lines: ParsedBasicLine[]): Record<string, number> {
  const counts = {
    print: 0,
    data: 0,
    goto: 0,
    gosub: 0,
    rem: 0,
    other: 0,
  }

  for (const line of lines) {
    const statement = line.statement.toUpperCase()
    if (statement.startsWith('PRINT')) counts.print += 1
    else if (statement.startsWith('DATA')) counts.data += 1
    else if (statement.startsWith('GOTO')) counts.goto += 1
    else if (statement.startsWith('GOSUB')) counts.gosub += 1
    else if (statement.startsWith('REM')) counts.rem += 1
    else counts.other += 1
  }

  return counts
}

export async function importBasicProgram(programOrPath: string, worldName: string): Promise<{
  world: Record<string, unknown>
  files: Record<string, string>
  summary: Record<string, unknown>
}> {
  const maybeFile = path.resolve(programOrPath)
  let source = programOrPath
  let sourceType: 'inline' | 'file' = 'inline'

  try {
    source = await readFile(maybeFile, 'utf-8')
    sourceType = 'file'
  } catch {
    sourceType = 'inline'
  }

  const parsed = parseBasicLines(source)
  const stats = classifyStatements(parsed)
  const slug = slugify(worldName || 'basic-world') || 'basic-world'
  const workspaceRoot = path.resolve(process.cwd(), 'workspaces/gridcore')
  const scriptsDir = path.join(workspaceRoot, 'scripts/basic')
  const worldsDir = path.join(workspaceRoot, 'worlds/libraries')
  const importsDir = path.join(workspaceRoot, 'grids/imports')

  await mkdir(scriptsDir, { recursive: true })
  await mkdir(worldsDir, { recursive: true })
  await mkdir(importsDir, { recursive: true })

  const scriptPath = path.join(scriptsDir, `${slug}.bas`)
  const worldPath = path.join(worldsDir, `${slug}.json`)
  const importPath = path.join(importsDir, `${slug}.json`)

  const world = {
    id: slug,
    name: worldName,
    type: 'library',
    source: 'basic',
    sourceType,
    grid: {
      cols: 80,
      rows: Math.max(parsed.length, 1),
      cellSize: 24,
    },
    layers: ['terrain', 'details', 'entities'],
    metrics: {
      lineCount: parsed.length,
      maxLineLength: parsed.reduce((max, line) => Math.max(max, line.statement.length), 0),
      statements: stats,
    },
  }

  const importArtifact = {
    worldId: slug,
    preview: parsed.slice(0, 24).map((line, index) => ({
      row: index,
      lineNumber: line.lineNumber,
      text: line.statement,
    })),
  }

  await writeFile(scriptPath, source, 'utf-8')
  await writeFile(worldPath, JSON.stringify(world, null, 2), 'utf-8')
  await writeFile(importPath, JSON.stringify(importArtifact, null, 2), 'utf-8')

  return {
    world,
    files: {
      script: scriptPath,
      manifest: worldPath,
      importArtifact: importPath,
    },
    summary: {
      sourceType,
      lineCount: parsed.length,
      statements: stats,
    },
  }
}