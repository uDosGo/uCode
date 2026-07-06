import { writeFileSync, mkdirSync, existsSync, readFileSync } from 'node:fs'
import { dirname, join, extname } from 'node:path'

// ---------------------------------------------------------------------------
// Types (aligned with SKILLS_FRAMEWORK.md §3)
// ---------------------------------------------------------------------------

export interface SkinWeaverInput {
  source_assets: Array<{
    path: string
    type: string
    format?: string
    transform?: {
      scale?: number
      rotation?: number
      center?: [number, number]
    }
  }>
  target: {
    locale: string
    resolution: { cols: number; rows: number }
    palette: string
  }
}

export interface CharacterMapping {
  source: string
  target_char: string
  target_fg: number
  target_bg: number
  description: string
}

export interface TeletextOverride {
  header_row?: { fg: number; bg: number; bold?: boolean }
  hud_row?: { fg: number; bg: number; bold?: boolean }
  alert_row?: { fg: number; bg: number; bold?: boolean }
}

export interface SkinManifest {
  name: string
  version: string
  palette: Record<string, string>
  character_mappings: CharacterMapping[]
  teletext_overrides: TeletextOverride
}

export interface ExportedAsset {
  source: string
  output: string
}

export interface SkinWeaverOutput {
  skill: 'SKIN-Weaver'
  version: '1.0'
  executed_at: string
  skin_name: string
  manifest: SkinManifest
  exported_assets: ExportedAsset[]
  manifest_written_to?: string
}

// ---------------------------------------------------------------------------
// Palette definitions
// ---------------------------------------------------------------------------

const PALETTES: Record<string, Record<string, string>> = {
  bbc_mode7: {
    '0': '#000000',
    '1': '#ff0000',
    '2': '#00ff00',
    '3': '#ffff00',
    '4': '#0000ff',
    '5': '#ff00ff',
    '6': '#00ffff',
    '7': '#ffffff',
  },
  teletext_classic: {
    '0': '#000000',
    '1': '#ff0000',
    '2': '#00cc00',
    '3': '#cccc00',
    '4': '#0000cc',
    '5': '#cc00cc',
    '6': '#00cccc',
    '7': '#cccccc',
  },
  dark_fantasy: {
    '0': '#0a0a0a',
    '1': '#8b0000',
    '2': '#2e8b57',
    '3': '#b8860b',
    '4': '#191970',
    '5': '#4b0082',
    '6': '#5f9ea0',
    '7': '#a9a9a9',
  },
  repton_classic: {
    '0': '#000000',
    '1': '#ff8800',
    '2': '#00cc00',
    '3': '#ffff00',
    '4': '#0044cc',
    '5': '#cc44cc',
    '6': '#00cccc',
    '7': '#cccccc',
  },
  elite_wireframe: {
    '0': '#000000',
    '1': '#00ff00',
    '2': '#00ff00',
    '3': '#ffff00',
    '4': '#0000ff',
    '5': '#ff00ff',
    '6': '#00ffff',
    '7': '#00ff00',
  },
}

// ---------------------------------------------------------------------------
// Character mapping heuristics
// ---------------------------------------------------------------------------

const CHAR_MAP: Record<string, { char: string; fg: number; bg: number; desc: string }> = {
  wireframe_model: { char: '@', fg: 2, bg: 0, desc: 'Wireframe ship model' },
  sprite_data: { char: '*', fg: 3, bg: 0, desc: 'Sprite character' },
  teletext_pages: { char: ' ', fg: 7, bg: 0, desc: 'Teletext page' },
  audio_data: { char: '~', fg: 5, bg: 0, desc: 'Audio asset' },
  map_data: { char: '#', fg: 6, bg: 0, desc: 'Map tile' },
  level_data: { char: '#', fg: 1, bg: 0, desc: 'Level layout' },
  game_data: { char: '?', fg: 7, bg: 0, desc: 'Game data file' },
  image_asset: { char: '&', fg: 4, bg: 0, desc: 'Image asset' },
  binary_asset: { char: '%', fg: 5, bg: 0, desc: 'Binary asset' },
  character_data: { char: 'C', fg: 2, bg: 0, desc: 'Character definition' },
}

function guessCharMapping(asset: SkinWeaverInput['source_assets'][0]): CharacterMapping {
  const type = asset.format || asset.type
  const mapping = CHAR_MAP[type] || { char: '?', fg: 7, bg: 0, desc: asset.type }
  return {
    source: asset.path,
    target_char: mapping.char,
    target_fg: mapping.fg,
    target_bg: mapping.bg,
    description: mapping.desc,
  }
}

function buildManifest(
  assets: SkinWeaverInput['source_assets'],
  skinName: string,
  paletteName: string,
  resolution: { cols: number; rows: number },
): SkinManifest {
  const palette = PALETTES[paletteName] || PALETTES.bbc_mode7

  const mappings: CharacterMapping[] = assets.map((a) => guessCharMapping(a))
  // Dedupe by target_char
  const seen = new Set<string>()
  const unique = mappings.filter((m) => {
    const key = `${m.target_char}-${m.target_fg}`
    if (seen.has(key)) return false
    seen.add(key)
    return true
  })

  const overrides: TeletextOverride = {
    header_row: { fg: 2, bg: 0, bold: true },
    hud_row: { fg: 3, bg: 0, bold: false },
    alert_row: { fg: 1, bg: 0, bold: true },
  }

  return {
    name: skinName,
    version: '1.0',
    palette,
    character_mappings: unique,
    teletext_overrides: overrides,
  }
}

// ---------------------------------------------------------------------------
// YAML manifest generation
// ---------------------------------------------------------------------------

function generateYamlManifest(manifest: SkinManifest): string {
  const lines: string[] = [
    `# Auto-generated by SKIN-Weaver v1.0`,
    `skin:`,
    `  name: "${manifest.name}"`,
    `  version: "${manifest.version}"`,
    ``,
    `palette:`,
  ]

  for (const [idx, color] of Object.entries(manifest.palette)) {
    lines.push(`  '${idx}': '${color}'`)
  }

  lines.push('')
  lines.push('character_mappings:')
  for (const m of manifest.character_mappings) {
    lines.push(`  - source: "${m.source}"`)
    lines.push(`    target_char: "${m.target_char}"`)
    lines.push(`    target_fg: ${m.target_fg}`)
    lines.push(`    target_bg: ${m.target_bg}`)
    lines.push(`    description: "${m.description}"`)
  }

  lines.push('')
  lines.push('teletext_overrides:')
  if (manifest.teletext_overrides.header_row) {
    const h = manifest.teletext_overrides.header_row
    lines.push(`  header_row:`)
    lines.push(`    fg: ${h.fg}`)
    lines.push(`    bg: ${h.bg}`)
    lines.push(`    bold: ${h.bold || false}`)
  }
  if (manifest.teletext_overrides.hud_row) {
    const h = manifest.teletext_overrides.hud_row
    lines.push(`  hud_row:`)
    lines.push(`    fg: ${h.fg}`)
    lines.push(`    bg: ${h.bg}`)
    lines.push(`    bold: ${h.bold || false}`)
  }
  if (manifest.teletext_overrides.alert_row) {
    const h = manifest.teletext_overrides.alert_row
    lines.push(`  alert_row:`)
    lines.push(`    fg: ${h.fg}`)
    lines.push(`    bg: ${h.bg}`)
    lines.push(`    bold: ${h.bold || false}`)
  }

  return lines.join('\n') + '\n'
}

// ---------------------------------------------------------------------------
// JSON manifest generation
// ---------------------------------------------------------------------------

function generateJsonManifest(manifest: SkinManifest): string {
  return JSON.stringify(
    {
      generated_by: 'SKIN-Weaver v1.0',
      skin: {
        name: manifest.name,
        version: manifest.version,
      },
      palette: manifest.palette,
      character_mappings: manifest.character_mappings,
      teletext_overrides: manifest.teletext_overrides,
    },
    null,
    2,
  )
}

// ---------------------------------------------------------------------------
// Main SKIN-Weaver entry point
// ---------------------------------------------------------------------------

export function skinWeaver(input: SkinWeaverInput): SkinWeaverOutput {
  const skinName = input.source_assets[0]?.path
    ? input.source_assets[0].path
        .split('/')
        .filter((s) => !s.startsWith('.'))
        .join('_')
        .replace(/[_/]/g, '_')
        .replace(/\.[^.]+$/, '')
        .slice(0, 30) || 'default_skin'
    : 'default_skin'

  if (!/^[a-z]/i.test(skinName)) {
    // prepend if starts with non-alpha
    const idx = skinName.search(/[a-z]/i)
    if (idx > 0) {
      // Just strip prefix non-alpha
    }
  }

  const manifest = buildManifest(
    input.source_assets,
    `${skinName} (${input.target.locale})`,
    input.target.palette,
    input.target.resolution,
  )

  const exportedAssets: ExportedAsset[] = input.source_assets.map((a) => ({
    source: a.path,
    output: `skins/${skinName}/chars/${a.path.split('/').pop() || 'asset'}.json`,
  }))

  return {
    skill: 'SKIN-Weaver',
    version: '1.0',
    executed_at: new Date().toISOString(),
    skin_name: skinName,
    manifest,
    exported_assets: exportedAssets,
  }
}

// ---------------------------------------------------------------------------
// File writing helper
// ---------------------------------------------------------------------------

export function writeSkinManifest(
  output: SkinWeaverOutput,
  outputDir: string,
  format: 'yaml' | 'json' = 'yaml',
): string {
  if (!existsSync(outputDir)) {
    mkdirSync(outputDir, { recursive: true })
  }

  const ext = format === 'yaml' ? '.yaml' : '.json'
  const outPath = join(outputDir, `${output.skin_name}.skin${ext}`)

  const content =
    format === 'yaml'
      ? generateYamlManifest(output.manifest)
      : generateJsonManifest(output.manifest)

  writeFileSync(outPath, content, 'utf-8')
  return outPath
}