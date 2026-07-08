import { describe, expect, it } from 'vitest'
import { inspireEngine } from '../src/tools/inspire-engine'
import { ucodeWeaver } from '../src/tools/ucode-weaver'

describe('uCode-Weaver', () => {
  it('generates BBC BASIC skeleton for Apple Panic from GDD', () => {
    const gddResult = inspireEngine({
      target_game: 'Apple Panic',
      approach: 'rewrite_inspired_by',
      research_sources: [],
      design_constraints: {
        target_runtime: 'bbc_basic_sdl',
        display_mode: 'teletext',
      },
    })

    const result = ucodeWeaver({
      gdd: gddResult.game_design_document,
      program_name: 'Apple Panic',
      runtime: 'bbc_basic_sdl',
      display_mode: 'teletext',
    })

    expect(result.skill).toBe('uCode-Weaver')
    expect(result.version).toBe('1.0')
    expect(result.program_name).toBe('Apple Panic')
    expect(result.generated_code).toBeTruthy()
    expect(result.generated_code).toMatch(/uCode-Weaver/)
    expect(result.generated_code).toMatch(/platformer/)
    expect(result.generated_code).toMatch(/arcade/)
    expect(result.generated_code).toMatch(/CLS/)
    expect(result.generated_code).toMatch(/ENDPROC/)
    expect(result.generated_code).toMatch(/INKEY/)
  })

  it('generates BBC BASIC skeleton for Knight Orc from GDD', () => {
    const gddResult = inspireEngine({
      target_game: 'Knight Orc',
      approach: 'rewrite_inspired_by',
      research_sources: [],
      design_constraints: {
        target_runtime: 'bbc_basic_sdl',
        display_mode: 'teletext',
      },
    })

    const result = ucodeWeaver({
      gdd: gddResult.game_design_document,
      program_name: 'Knight Orc',
      runtime: 'bbc_basic_sdl',
      display_mode: 'teletext',
    })

    expect(result.skill).toBe('uCode-Weaver')
    expect(result.program_name).toBe('Knight Orc')
    expect(result.generated_code).toMatch(/text_adventure/)
    expect(result.generated_code).toMatch(/fantasy/)
    expect(result.generated_code).toMatch(/INPUT/)
  })

  it('generates BBC BASIC skeleton for uConstruct from GDD', () => {
    const gddResult = inspireEngine({
      target_game: 'uConstruct',
      approach: 'rewrite_inspired_by',
      research_sources: [],
      design_constraints: {
        target_runtime: 'bbc_basic_sdl',
        display_mode: 'teletext',
      },
    })

    const result = ucodeWeaver({
      gdd: gddResult.game_design_document,
      program_name: 'uConstruct',
      runtime: 'bbc_basic_sdl',
      display_mode: 'teletext',
    })

    expect(result.skill).toBe('uCode-Weaver')
    expect(result.generated_code).toMatch(/construction/)
    expect(result.generated_code).toMatch(/simulation/)
  })

  it('includes LENS-extractable variables in generated code', () => {
    const gddResult = inspireEngine({
      target_game: 'Knight Orc',
      approach: 'rewrite_inspired_by',
      research_sources: [],
      design_constraints: {
        target_runtime: 'bbc_basic_sdl',
        display_mode: 'teletext',
      },
    })

    const result = ucodeWeaver({
      gdd: gddResult.game_design_document,
      program_name: 'Knight Orc',
      runtime: 'bbc_basic_sdl',
      display_mode: 'teletext',
    })

    // Should include LENS-extractable variables from integration spec
    expect(result.generated_code).toMatch(/player_location/)
    expect(result.generated_code).toMatch(/player_inventory/)
    expect(result.generated_code).toMatch(/game_time/)
    expect(result.generated_code).toMatch(/npc_statuses/)
  })

  it('returns list of procedures', () => {
    const gddResult = inspireEngine({
      target_game: 'Apple Panic',
      approach: 'rewrite_inspired_by',
      research_sources: [],
      design_constraints: {
        target_runtime: 'bbc_basic_sdl',
        display_mode: 'teletext',
      },
    })

    const result = ucodeWeaver({
      gdd: gddResult.game_design_document,
      program_name: 'Apple Panic',
      runtime: 'bbc_basic_sdl',
      display_mode: 'teletext',
    })

    expect(result.procedures.length).toBeGreaterThan(0)
    const procNames = result.procedures.map((p) => p.name)
    expect(procNames).toContain('PROCinit')
    expect(procNames).toContain('PROCinput')
    expect(procNames).toContain('PROCupdate')
    expect(procNames).toContain('PROCrender')
    expect(procNames).toContain('FNgame_over')
    expect(procNames).toContain('PROCgame_over')
  })
})