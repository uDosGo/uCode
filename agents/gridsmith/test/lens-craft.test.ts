import { describe, expect, it } from 'vitest'
import { mkdtempSync, rmSync, readFileSync } from 'node:fs'
import { join } from 'node:path'
import { tmpdir } from 'node:os'
import { lensCraft } from '../src/tools/lens-craft'

const TEST_DIR = mkdtempSync(join(tmpdir(), 'gridsmith-lens-craft-'))

describe('LENS-Craft', () => {
  const minerReport = {
    skill: 'Source-Miner' as const,
    version: '1.0',
    executed_at: new Date().toISOString(),
    source: '/tmp/test/repton',
    findings: {
      memory_map: [
        {
          label: 'SHIP_STATUS',
          address: '0x0222',
          type: 'byte',
          description: 'Ship status: 0=docked, 1=in flight',
          confidence: 0.95,
        },
        {
          label: 'SCORE_LOW',
          address: '0x1100',
          type: 'byte',
          description: 'Score low byte',
          confidence: 0.85,
        },
        {
          label: 'SCORE_HIGH',
          address: '0x1101',
          type: 'byte',
          description: 'Score high byte',
          confidence: 0.8,
        },
        {
          label: 'LIVES',
          address: '0x1102',
          type: 'byte',
          description: 'Number of lives remaining',
          confidence: 0.85,
        },
        {
          label: 'EnemyData',
          address: '0x2000',
          type: 'struct',
          description: 'Enemy data structure',
          confidence: 0.6,
          length: 64,
        },
      ],
      functions: [
        { name: 'MainLoop', address: '0x0400', description: 'Main game loop' },
        { name: 'InitDisplay', address: '0x0500', description: 'Initialize display' },
      ],
    },
    recommendations: [],
  }

  it('generates Python extractor code from Source-Miner report', () => {
    const result = lensCraft({
      source_miner_report: minerReport,
      emulator: { type: '6502', endianness: 'little' },
      output: {
        language: 'python',
        module_name: 'repton_lens',
      },
    })

    expect(result.skill).toBe('LENS-Craft')
    expect(result.version).toBe('1.0')
    expect(result.extractors.length).toBeGreaterThan(0)
    expect(result.generated_code).toBeTruthy()

    // Should generate a Python class
    expect(result.generated_code).toMatch(/class ReptonLensExtractor:/)
    expect(result.generated_code).toMatch(/def __init__\(self, emu\):/)
    expect(result.generated_code).toMatch(/def capture_all\(self\) -> dict:/)
  })

  it('generates bitmask extractor for status/flag entries', () => {
    const result = lensCraft({
      source_miner_report: minerReport,
      emulator: { type: '6502', endianness: 'little' },
      output: { language: 'python', module_name: 'repton_lens' },
    })

    const shipStatus = result.extractors.find((e) => e.name.includes('ship_status'))
    expect(shipStatus).toBeDefined()
    expect(shipStatus?.type).toBe('bitmask')
    expect(shipStatus?.labels).toBeDefined()
    expect(shipStatus?.labels?.['0']).toBe('docked')

    // Should have bitmask code in generated output
    expect(result.generated_code).toMatch(/docked/)
    expect(result.generated_code).toMatch(/in_flight/)
  })

  it('generates simple byte getters for score/lives', () => {
    const result = lensCraft({
      source_miner_report: minerReport,
      emulator: { type: '6502', endianness: 'little' },
      output: { language: 'python', module_name: 'repton_lens' },
    })

    const scoreLow = result.extractors.find((e) => e.name.includes('score_low'))
    expect(scoreLow).toBeDefined()
    expect(scoreLow?.type).toBe('uint8')

    const lives = result.extractors.find((e) => e.name.includes('lives'))
    expect(lives).toBeDefined()
    expect(lives?.type).toBe('uint8')

    // Should use read_byte for single byte entries
    expect(result.generated_code).toMatch(/read_byte\(0x1100\)/)
    expect(result.generated_code).toMatch(/read_byte\(0x1102\)/)
  })

  it('generates struct extractor for EnemyData', () => {
    const result = lensCraft({
      source_miner_report: minerReport,
      emulator: { type: '6502', endianness: 'little' },
      output: { language: 'python', module_name: 'repton_lens' },
    })

    const enemyData = result.extractors.find((e) => e.name.includes('enemy_data'))
    expect(enemyData).toBeDefined()
    expect(enemyData?.type).toBe('struct')
    expect(enemyData?.size).toBe(64)
  })

  it('generates capture_all method with all extractors', () => {
    const result = lensCraft({
      source_miner_report: minerReport,
      emulator: { type: '6502', endianness: 'little' },
      output: { language: 'python', module_name: 'repton_lens' },
    })

    // capture_all should contain all extractor property names
    for (const ext of result.extractors) {
      const snakeName = ext.name.replace(/[^a-zA-Z0-9]/g, '_').replace(/([a-z])([A-Z])/g, '$1_$2').toLowerCase()
      expect(result.generated_code).toMatch(new RegExp(`"${snakeName}"`))
    }
  })

  it('writes file to disk when output path is provided', () => {
    const outDir = join(TEST_DIR, 'lens_output')
    const result = lensCraft({
      source_miner_report: minerReport,
      emulator: { type: '6502', endianness: 'little' },
      output: {
        language: 'python',
        module_name: 'test_lens',
        path: outDir,
      },
    })

    expect(result.written_to).toBeTruthy()
    expect(result.written_to).toMatch(/\.py$/)

    const fileContent = readFileSync(result.written_to!, 'utf-8')
    expect(fileContent).toMatch(/class TestLensExtractor:/)
    expect(fileContent).toMatch(/# Auto-generated by LENS-Craft/)
  })

  it('skips low-confidence entries', () => {
    const lowConfReport = {
      ...minerReport,
      findings: {
        ...minerReport.findings,
        memory_map: [
          {
            label: 'LOW_CONF',
            address: '0x5000',
            type: 'byte',
            description: 'Very uncertain',
            confidence: 0.3,
          },
          ...minerReport.findings.memory_map,
        ],
      },
    }

    const result = lensCraft({
      source_miner_report: lowConfReport,
      emulator: { type: '6502', endianness: 'little' },
      output: { language: 'python', module_name: 'test_lens' },
    })

    const lowConf = result.extractors.find((e) => e.name.includes('low_conf'))
    expect(lowConf).toBeUndefined()
  })

  it('cleans up test directory', () => {
    try { rmSync(TEST_DIR, { recursive: true, force: true }) } catch { /* ok */ }
    expect(true).toBe(true)
  })
})