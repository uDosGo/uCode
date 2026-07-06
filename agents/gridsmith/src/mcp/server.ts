#!/usr/bin/env node

import { createServer } from 'node:http'
import type { Grid } from '@udos/gridcore'
import {
  GRIDSMITH_TOOLS,
  createGridWorld,
  convertLatLonToUCode,
  convertUCodeToLatLon,
  importBasicProgram,
  importAmosProgram,
  editCell,
  composeGridLayers,
  exportUvox,
  findPath,
  createWorld,
  sourceMiner,
  lensCraft,
  skinWeaver,
  writeSkinManifest,
  mcpScribe,
} from '../index'

const PORT = process.env.GRIDSMITH_MCP_PORT || '8670'
const HOST = process.env.GRIDSMITH_MCP_HOST || '127.0.0.1'

// Stateful grid registry — maps grid_id -> Grid
const gridRegistry = new Map<string, Grid>()

interface McpRequest {
  jsonrpc: '2.0'
  id: number | string
  method: string
  params?: Record<string, unknown>
}

interface McpResponse {
  jsonrpc: '2.0'
  id: number | string | null
  result?: unknown
  error?: { code: number; message: string; data?: unknown }
}

function mcpResponse(id: number | string | null, result: unknown): McpResponse {
  return { jsonrpc: '2.0', id, result }
}

function mcpError(id: number | string | null, code: number, message: string, data?: unknown): McpResponse {
  return { jsonrpc: '2.0', id, error: { code, message, data } }
}

function getOrCreateGrid(id: string, cols = 80, rows = 24): Grid {
  let grid = gridRegistry.get(id)
  if (!grid) {
    const created = createGridWorld(cols, rows)
    grid = created.grid
    gridRegistry.set(id, grid)
  }
  return grid
}

async function invokeTool(name: string, params: Record<string, unknown>): Promise<unknown> {
  switch (name) {
    case 'tools/list':
      return { tools: GRIDSMITH_TOOLS }

    case 'create_world':
      return createWorld({
        name: String(params.name || 'New World'),
        type: (params.type as 'earth' | 'dungeon' | 'vault' | 'library') || 'earth',
        cols: Number(params.cols) || 80,
        rows: Number(params.rows) || 24,
        seed: Number(params.seed) || undefined,
        terrain: (params.terrain as Record<string, string>) || undefined,
      })

    case 'create_grid': {
      const cols = Number(params.cols) || 80
      const rows = Number(params.rows) || 24
      const world = createGridWorld(cols, rows)
      const gridId = String(params.grid_id || `grid-${Date.now()}`)
      gridRegistry.set(gridId, world.grid)
      return { gridId, cols: world.cols, rows: world.rows, cellCount: world.cellCount }
    }

    case 'edit_cell': {
      const gridId = String(params.grid_id || 'default')
      const grid = getOrCreateGrid(gridId)
      return editCell(
        grid,
        Number(params.x),
        Number(params.y),
        Number(params.layer) || 0,
        (params.data as Record<string, unknown>) || {},
      )
    }

    case 'compose_layers': {
      const gridId = String(params.grid_id || 'default')
      const grid = getOrCreateGrid(gridId)
      const layers = (params.layers as number[]) || [0, 1, 2, 3, 4, 5]
      const result = composeGridLayers(grid, layers)
      return { cellCount: result.cellCount, layerCount: result.layers.length }
    }

    case 'export_uvox': {
      const gridId = String(params.grid_id || 'default')
      const grid = getOrCreateGrid(gridId)
      const outputPath = String(params.output_path || 'output.uvox')
      return exportUvox(grid, gridId, outputPath)
    }

    case 'pathfind': {
      const gridId = String(params.grid_id || 'default')
      const grid = getOrCreateGrid(gridId)
      return findPath(
        grid,
        Number(params.start_x),
        Number(params.start_y),
        Number(params.end_x),
        Number(params.end_y),
        Number(params.layer) || 0,
      )
    }

    case 'import_basic_program':
      return importBasicProgram(
        String(params.program || ''),
        String(params.world_name || 'BASIC World'),
      )

    case 'import_amos_program':
      return importAmosProgram(
        String(params.program || ''),
        String(params.world_name || 'AMOS World'),
      )

    case 'latlon_to_ucode':
      return {
        coord: convertLatLonToUCode(
          Number(params.lat),
          Number(params.lon),
          Number(params.level) || 340,
        ),
      }

    case 'ucode_to_latlon':
      return {
        location: convertUCodeToLatLon(String(params.coord || '')),
      }

    case 'source_miner': {
      const sourcePath = String(params.source_path || process.cwd())
      const langStr = String(params.language || '6502')
      const language = langStr.split(',').map((s: string) => s.trim())
      const targetStr = String(params.target_patterns || '')
      const excludeStr = String(params.exclude_patterns || '')
      const targetPatterns = targetStr ? targetStr.split(',').filter(Boolean) : []
      const excludePatterns = excludeStr ? excludeStr.split(',').filter(Boolean) : []

      return sourceMiner({
        source: { type: 'local_path', url: sourcePath, language },
        options: {
          scan_depth: 'full',
          target_patterns: targetPatterns.length > 0 ? targetPatterns : undefined,
          exclude_patterns: excludePatterns.length > 0 ? excludePatterns : undefined,
        },
      })
    }

    case 'lens_craft': {
      const minerJson = String(params.source_miner_json || '{}')
      const moduleName = String(params.module_name || 'lens_extractor')
      const outputPath = String(params.output_path || '')

      const report = JSON.parse(minerJson)
      return lensCraft({
        source_miner_report: report,
        emulator: { type: '6502', endianness: 'little' },
        output: {
          language: 'python',
          module_name: moduleName,
          path: outputPath || undefined,
        },
      })
    }

    case 'skin_weaver': {
      const assetsJson = String(params.assets_json || '[]')
      const palette = String(params.palette || 'bbc_mode7')
      const outputDir = String(params.output_dir || '')

      const assets = JSON.parse(assetsJson)
      const result = skinWeaver({
        source_assets: assets,
        target: {
          locale: 'teletext_grid',
          resolution: { cols: 40, rows: 25 },
          palette,
        },
      })

      if (outputDir) {
        const writtenTo = writeSkinManifest(result, outputDir, 'yaml')
        return { ...result, manifest_written_to: writtenTo }
      }
      return result
    }

    case 'mcp_scribe': {
      const minerJson = String(params.source_miner_json || '{}')
      const programName = String(params.program_name || 'Unknown')
      const programType = (params.program_type as string) || 'adapt-source'

      const report = JSON.parse(minerJson)
      return mcpScribe({
        program_name: programName,
        program_type: programType as 'adapt-source' | 'rewrite' | 'port-c-to-basic' | 'rewrite_inspired_by',
        game_mechanics: { genre: [] },
        source_miner_report: report,
      })
    }

    default:
      throw new Error(`Unknown tool: ${name}`)
  }
}

async function handleRequest(body: string): Promise<McpResponse> {
  let req: McpRequest

  try {
    req = JSON.parse(body) as McpRequest
  } catch {
    return mcpError(null, -32700, 'Parse error')
  }

  if (req.jsonrpc !== '2.0') {
    return mcpError(req.id, -32600, 'Invalid Request')
  }

  try {
    switch (req.method) {
      case 'initialize':
        return mcpResponse(req.id, {
          protocolVersion: '2024-11-05',
          capabilities: { tools: {} },
          serverInfo: { name: 'gridsmith-mcp', version: '0.2.0' },
        })

      case 'tools/list':
        return mcpResponse(req.id, { tools: GRIDSMITH_TOOLS })

      case 'tools/call': {
        const params = req.params as { name?: string; arguments?: Record<string, unknown> }
        if (!params?.name) {
          return mcpError(req.id, -32602, 'Missing tool name')
        }
        const result = await invokeTool(params.name, params.arguments || {})
        return mcpResponse(req.id, { content: [{ type: 'text', text: JSON.stringify(result) }] })
      }

      case 'ping':
        return mcpResponse(req.id, {})

      default:
        return mcpError(req.id, -32601, `Method not found: ${req.method}`)
    }
  } catch (err) {
    return mcpError(req.id, -32000, String(err))
  }
}

function main(): void {
  const server = createServer(async (req, res) => {
    if (req.method !== 'POST') {
      res.writeHead(405, { 'Content-Type': 'application/json' })
      res.end(JSON.stringify(mcpError(null, -32000, 'Method not allowed')))
      return
    }

    const chunks: Buffer[] = []
    for await (const chunk of req) {
      chunks.push(chunk)
    }
    const body = Buffer.concat(chunks).toString('utf-8')

    const response = await handleRequest(body)

    res.writeHead(200, {
      'Content-Type': 'application/json',
      'Access-Control-Allow-Origin': '*',
    })
    res.end(JSON.stringify(response))
  })

  server.listen(Number(PORT), HOST, () => {
    process.stderr.write(`GridSmith MCP server listening on ${HOST}:${PORT}\n`)
  })
}

main()