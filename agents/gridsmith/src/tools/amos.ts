import { mkdir, readFile, writeFile } from 'node:fs/promises'
import path from 'node:path'

interface AmosSpriteRef {
  number: number
  x: number
  y: number
  image: number | string
}

interface AmosBobRef {
  number: number
  x: number
  y: number
  image: string
}

interface AmosSoundRef {
  channel: number
  freq: number
  duration: number
  volume: number
}

interface AmosMoveCommand {
  spriteNumber: number
  targetX: number
  targetY: number
  steps: number
}

interface ParsedAmosProgram {
  sprites: AmosSpriteRef[]
  bobs: AmosBobRef[]
  sounds: AmosSoundRef[]
  moves: AmosMoveCommand[]
  rems: string[]
  otherLines: string[]
}

function slugify(value: string): string {
  return value
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '')
    .slice(0, 80)
}

function parseAmosLine(line: string): ParsedAmosProgram {
  const result: ParsedAmosProgram = {
    sprites: [],
    bobs: [],
    sounds: [],
    moves: [],
    rems: [],
    otherLines: [],
  }

  const trimmed = line.trim()
  const upper = trimmed.toUpperCase()

  // SPRITE number, x, y, img
  const spriteMatch = upper.match(/^\s*SPRITE\s+(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*$/)
  if (spriteMatch) {
    result.sprites.push({
      number: Number(spriteMatch[1]),
      x: Number(spriteMatch[2]),
      y: Number(spriteMatch[3]),
      image: Number(spriteMatch[4]),
    })
    return result
  }

  // BOB number, x, y, "image"
  const bobMatch = trimmed.match(/^\s*BOB\s+(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*,\s*"([^"]*)"\s*$/i)
  if (bobMatch) {
    result.bobs.push({
      number: Number(bobMatch[1]),
      x: Number(bobMatch[2]),
      y: Number(bobMatch[3]),
      image: bobMatch[4],
    })
    return result
  }

  // SOUND channel, freq, duration, volume
  const soundMatch = upper.match(/^\s*SOUND\s+(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*$/)
  if (soundMatch) {
    result.sounds.push({
      channel: Number(soundMatch[1]),
      freq: Number(soundMatch[2]),
      duration: Number(soundMatch[3]),
      volume: Number(soundMatch[4]),
    })
    return result
  }

  // MOVE sprite, x, y, steps
  const moveMatch = upper.match(/^\s*MOVE\s+(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*$/)
  if (moveMatch) {
    result.moves.push({
      spriteNumber: Number(moveMatch[1]),
      targetX: Number(moveMatch[2]),
      targetY: Number(moveMatch[3]),
      steps: Number(moveMatch[4]),
    })
    return result
  }

  // REM or ' (comment)
  if (upper.startsWith('REM') || trimmed.startsWith("'")) {
    result.rems.push(trimmed)
    return result
  }

  result.otherLines.push(trimmed)
  return result
}

function parseAmosProgram(program: string): ParsedAmosProgram {
  const lines = program.split(/\r?\n/).map(l => l.trimEnd()).filter(Boolean)
  const merged: ParsedAmosProgram = {
    sprites: [],
    bobs: [],
    sounds: [],
    moves: [],
    rems: [],
    otherLines: [],
  }

  for (const line of lines) {
    const parsed = parseAmosLine(line)
    merged.sprites.push(...parsed.sprites)
    merged.bobs.push(...parsed.bobs)
    merged.sounds.push(...parsed.sounds)
    merged.moves.push(...parsed.moves)
    merged.rems.push(...parsed.rems)
    merged.otherLines.push(...parsed.otherLines)
  }

  return merged
}

export interface AmosImportResult {
  world: Record<string, unknown>
  files: Record<string, string>
  summary: Record<string, unknown>
}

export async function importAmosProgram(
  programOrPath: string,
  worldName: string,
): Promise<AmosImportResult> {
  const maybeFile = path.resolve(programOrPath)
  let source = programOrPath
  let sourceType: 'inline' | 'file' = 'inline'

  try {
    source = await readFile(maybeFile, 'utf-8')
    sourceType = 'file'
  } catch {
    sourceType = 'inline'
  }

  const parsed = parseAmosProgram(source)
  const totalAssets =
    parsed.sprites.length + parsed.bobs.length + parsed.sounds.length + parsed.moves.length

  const slug = slugify(worldName || 'amos-world') || 'amos-world'
  const workspaceRoot = path.resolve(process.cwd(), 'workspaces/gridcore')
  const scriptsDir = path.join(workspaceRoot, 'scripts/amos')
  const worldsDir = path.join(workspaceRoot, 'worlds/libraries')
  const importsDir = path.join(workspaceRoot, 'grids/imports')

  await mkdir(scriptsDir, { recursive: true })
  await mkdir(worldsDir, { recursive: true })
  await mkdir(importsDir, { recursive: true })

  const scriptPath = path.join(scriptsDir, `${slug}.amos`)
  const worldPath = path.join(worldsDir, `${slug}.json`)
  const importPath = path.join(importsDir, `${slug}.json`)

  const world = {
    id: slug,
    name: worldName,
    type: 'dungeon',
    source: 'amos',
    sourceType,
    grid: {
      cols: 80,
      rows: Math.max(totalAssets, 1),
      cellSize: 24,
    },
    layers: ['terrain', 'details', 'entities'],
    assets: {
      sprites: parsed.sprites,
      bobs: parsed.bobs,
      sounds: parsed.sounds,
      moves: parsed.moves,
      commentCount: parsed.rems.length,
    },
    metrics: {
      totalLines: parsed.sprites.length + parsed.bobs.length + parsed.sounds.length + parsed.moves.length + parsed.rems.length + parsed.otherLines.length,
      spriteCount: parsed.sprites.length,
      bobCount: parsed.bobs.length,
      soundCount: parsed.sounds.length,
      moveCount: parsed.moves.length,
      commentCount: parsed.rems.length,
    },
  }

  const importArtifact = {
    worldId: slug,
    spriteTable: parsed.sprites,
    bobTable: parsed.bobs,
    soundTable: parsed.sounds,
    moveTable: parsed.moves,
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
      totalAssets,
      sprites: parsed.sprites.length,
      bobs: parsed.bobs.length,
      sounds: parsed.sounds.length,
      moves: parsed.moves.length,
    },
  }
}