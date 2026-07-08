import { writeFileSync, mkdirSync, existsSync } from 'node:fs'
import { dirname, join } from 'node:path'

// ---------------------------------------------------------------------------
// Types (aligned with SKILLS_FRAMEWORK.md §2)
// ---------------------------------------------------------------------------

export interface LensCraftInput {
  source_miner_report: {
    findings: {
      memory_map: Array<{
        label: string
        address: string
        type: string
        description: string
        confidence: number
        length?: number
      }>
      functions: Array<{
        name: string
        address: string
        description: string
      }>
    }
    source: string
  }
  emulator: {
    type: string
    memory_size?: number
    memory_base?: string
    endianness: 'little' | 'big'
  }
  output: {
    language: string
    module_name: string
    path?: string
  }
}

export interface ExtractorDefinition {
  name: string
  type: 'bitmask' | 'struct' | 'array' | 'uint8' | 'uint16' | 'uint32' | 'int16' | 'int32'
  address: string
  size: number
  labels?: Record<string, string>
  fields?: Array<{ name: string; offset: number; type: string; description: string }>
  element_type?: string
  description: string
}

export interface LensCraftOutput {
  skill: 'LENS-Craft'
  version: '1.0'
  executed_at: string
  module_path: string
  extractors: ExtractorDefinition[]
  generated_code?: string
  written_to?: string
}

// ---------------------------------------------------------------------------
// Python code generation
// ---------------------------------------------------------------------------

function pascalCase(name: string): string {
  return name
    .replace(/[^a-zA-Z0-9]/g, ' ')
    .split(/[\s_]+/)
    .map((w) => w.charAt(0).toUpperCase() + w.slice(1).toLowerCase())
    .join('')
}

function snakeCase(name: string): string {
  return name
    .replace(/[^a-zA-Z0-9]/g, '_')
    .replace(/([a-z])([A-Z])/g, '$1_$2')
    .toLowerCase()
}

function pythonType(ext: ExtractorDefinition): string {
  switch (ext.type) {
    case 'bitmask':
    case 'uint8':
      return 'int'
    case 'uint16':
    case 'int16':
      return 'int'
    case 'uint32':
    case 'int32':
      return 'int'
    case 'array':
      return 'dict'
    case 'struct':
      return 'dict'
    default:
      return 'int'
  }
}

function pythonDocstring(description: string): string {
  return `"""${description}"""`
}

function generateBitmaskGetter(ext: ExtractorDefinition, addr: number): string {
  const cases = ext.labels
    ? Object.entries(ext.labels)
        .map(([val, label]) => `        ${val}: "${label}"`)
        .join(',\n')
    : ''
  const classLabel = ext.labels ? `        labels = {${cases ? '\n' + cases + '\n' : ''}        }\n        return labels.get(val, "unknown")` : 'return val'
  return [
    `    @property`,
    `    def ${snakeCase(ext.name)}(self) -> str:`,
    `        ${pythonDocstring(ext.description)}`,
    `        val = self._emu.read_byte(0x${addr.toString(16)})`,
    classLabel,
  ].join('\n')
}

function generateSimpleGetter(ext: ExtractorDefinition, addr: number): string {
  const method = ext.type === 'uint32' || ext.type === 'int32'
    ? `read_uint32(0x${addr.toString(16)})`
    : ext.type === 'uint16' || ext.type === 'int16'
      ? `read_uint16(0x${addr.toString(16)})`
      : `read_byte(0x${addr.toString(16)})`
  return [
    `    @property`,
    `    def ${snakeCase(ext.name)}(self) -> ${pythonType(ext)}:`,
    `        ${pythonDocstring(ext.description)}`,
    `        return self._emu.${method}`,
  ].join('\n')
}

function generateStructGetter(ext: ExtractorDefinition, addr: number): string {
  const fieldLines = ext.fields?.map((f) => {
    const readMethod = f.type === 'uint32'
      ? `read_uint32(0x${(addr + f.offset).toString(16)})`
      : f.type === 'uint16'
        ? `read_uint16(0x${(addr + f.offset).toString(16)})`
        : `read_byte(0x${(addr + f.offset).toString(16)})`
    return `            "${f.name}": self._emu.${readMethod}`
  }) || []
  return [
    `    @property`,
    `    def ${snakeCase(ext.name)}(self) -> dict:`,
    `        ${pythonDocstring(ext.description)}`,
    '        return {',
    ...fieldLines,
    '        }',
  ].join('\n')
}

function generateArrayGetter(ext: ExtractorDefinition, addr: number): string {
  const size = ext.size || 1
  const labels = ext.labels
    ? Object.entries(ext.labels).map(([idx, label]) => `        items = ${JSON.stringify(Object.values(ext.labels!))}`).join('\n')
    : ''
  const labelBlock = labels
    ? `\n${labels}\n        result = {}\n        for i, label in enumerate(items):\n            result[label] = self._emu.read_byte(0x${addr.toString(16)} + i)\n        return result`
    : `        result = {}\n        for i in range(${size}):\n            result[i] = self._emu.read_byte(0x${addr.toString(16)} + i)\n        return result`
  return [
    `    @property`,
    `    def ${snakeCase(ext.name)}(self) -> dict:`,
    `        ${pythonDocstring(ext.description)}`,
    labelBlock,
  ].join('\n')
}

function generateProperty(ext: ExtractorDefinition): string {
  const addr = parseInt(ext.address, 16)

  switch (ext.type) {
    case 'bitmask':
      return generateBitmaskGetter(ext, addr)
    case 'struct':
      return generateStructGetter(ext, addr)
    case 'array':
      return generateArrayGetter(ext, addr)
    case 'uint8':
    case 'uint16':
    case 'uint32':
    case 'int16':
    case 'int32':
      return generateSimpleGetter(ext, addr)
    default:
      return generateSimpleGetter(ext, addr)
  }
}

function extractorToProvider(
  mem: Array<{
    label: string
    address: string
    type: string
    description: string
    confidence: number
    length?: number
  }>,
  programName: string,
): ExtractorDefinition[] {
  const providers: ExtractorDefinition[] = []

  for (const entry of mem) {
    // Skip low-confidence entries
    if (entry.confidence < 0.6) continue

    const snaked = snakeCase(entry.label)
    const name = `${programName}_${snaked}`.replace(/^[^a-z_]+/, '')

    switch (entry.type) {
      case 'byte':
        // Check if it looks like a bitmask from description or label
        if ((entry.description && /stat(e|us)|flag|mode|bit/i.test(entry.description)) ||
            /status|flag|mode/i.test(entry.label)) {
          providers.push({
            name,
            type: 'bitmask',
            address: entry.address,
            size: 1,
            labels: guessBitmaskLabels(entry.label, entry.description),
            description: entry.description,
          })
        } else if (entry.length && entry.length > 1) {
          providers.push({
            name,
            type: 'array',
            address: entry.address,
            size: entry.length,
            description: entry.description,
          })
        } else {
          providers.push({
            name,
            type: 'uint8',
            address: entry.address,
            size: 1,
            description: entry.description,
          })
        }
        break

      case 'struct':
        providers.push({
          name,
          type: 'struct',
          address: entry.address,
          size: entry.length || 4,
          fields: [],
          description: entry.description,
        })
        break

      default:
        providers.push({
          name,
          type: 'uint8',
          address: entry.address,
          size: 1,
          description: entry.description,
        })
    }
  }

  return providers
}

function guessBitmaskLabels(
  label: string,
  description: string,
): Record<string, string> {
  const lower = description.toLowerCase()

  // Common bitmask patterns
  if (/docked|docking|flight|land/.test(lower)) {
    return { '0': 'docked', '1': 'in_flight', '2': 'docking', '3': 'jumping' }
  }
  if (/paused|running|stopped|title/i.test(lower)) {
    return { '0': 'title_screen', '1': 'running', '2': 'paused', '3': 'game_over' }
  }
  if (/alive|dead|hurt|invincible/i.test(lower)) {
    return { '0': 'alive', '1': 'dead', '2': 'hurt', '3': 'invincible' }
  }

  return { '0': 'off', '1': 'on' }
}

function generatePythonCode(
  extractors: ExtractorDefinition[],
  moduleName: string,
  sourcePath: string,
): string {
  const className = pascalCase(moduleName) + 'Extractor'

  const propertyBlocks = extractors.map(generateProperty).join('\n\n')

  const captureItems = extractors
    .map((e) => `            "${snakeCase(e.name)}": self.${snakeCase(e.name)}`)
    .join(',\n')

  const header = [
    '# Auto-generated by LENS-Craft v1.0',
    `# Source: ${sourcePath}`,
    `# ${extractors.length} extractors generated`,
    '',
    '',
    `class ${className}:`,
  ].join('\n')

  const init = [
    '    def __init__(self, emu):',
    '        """Initialize with a 6502 emulator instance.',
    '',
    '        Args:',
    '            emu: Emulator providing read_byte(addr), read_uint16(addr),',
    '                 read_uint32(addr) in little-endian byte order.',
    '        """',
    '        self._emu = emu',
  ].join('\n')

  const captureAll = [
    '',
    '    def capture_all(self) -> dict:',
    '        """Capture all known state in a single snapshot."""',
    '        return {',
    captureItems,
    '        }',
  ].join('\n')

  return [header, init, propertyBlocks, captureAll, ''].join('\n\n')
}

// ---------------------------------------------------------------------------
// Main LENS-Craft entry point
// ---------------------------------------------------------------------------

export function lensCraft(input: LensCraftInput): LensCraftOutput {
  const memoryMap = input.source_miner_report.findings.memory_map || []
  const sourcePath = input.source_miner_report.source || 'unknown'

  // Derive program name from source path
  const pathSegments = sourcePath.replace(/\/$/, '').split('/')
  const programName = pathSegments[pathSegments.length - 1] || 'unknown'

  const extractors = extractorToProvider(memoryMap, programName)

  const moduleName = input.output.module_name
  const generatedCode = generatePythonCode(extractors, moduleName, sourcePath)

  // Write to disk if output path is provided
  let writtenTo: string | undefined
  if (input.output.path) {
    const outPath = input.output.path.endsWith('.py')
      ? input.output.path
      : join(input.output.path, `${moduleName}.py`)

    const dir = dirname(outPath)
    if (!existsSync(dir)) {
      mkdirSync(dir, { recursive: true })
    }
    writeFileSync(outPath, generatedCode, 'utf-8')
    writtenTo = outPath
  }

  return {
    skill: 'LENS-Craft',
    version: '1.0',
    executed_at: new Date().toISOString(),
    module_path: input.output.path || `${moduleName}.py`,
    extractors,
    generated_code: generatedCode,
    written_to: writtenTo,
  }
}