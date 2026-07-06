#!/usr/bin/env node
import {
  GRIDSMITH_TOOLS,
  composeGridLayers,
  convertLatLonToUCode,
  convertUCodeToLatLon,
  createGridWorld,
  createWorld,
  editCell,
  exportUvox,
  findPath,
  importAmosProgram,
  importBasicProgram
} from "../chunk-X2UHOTOK.js";

// src/mcp/server.ts
import { createServer } from "http";
var PORT = process.env.GRIDSMITH_MCP_PORT || "8670";
var HOST = process.env.GRIDSMITH_MCP_HOST || "127.0.0.1";
var gridRegistry = /* @__PURE__ */ new Map();
function mcpResponse(id, result) {
  return { jsonrpc: "2.0", id, result };
}
function mcpError(id, code, message, data) {
  return { jsonrpc: "2.0", id, error: { code, message, data } };
}
function getOrCreateGrid(id, cols = 80, rows = 24) {
  let grid = gridRegistry.get(id);
  if (!grid) {
    const created = createGridWorld(cols, rows);
    grid = created.grid;
    gridRegistry.set(id, grid);
  }
  return grid;
}
async function invokeTool(name, params) {
  switch (name) {
    case "tools/list":
      return { tools: GRIDSMITH_TOOLS };
    case "create_world":
      return createWorld({
        name: String(params.name || "New World"),
        type: params.type || "earth",
        cols: Number(params.cols) || 80,
        rows: Number(params.rows) || 24,
        seed: Number(params.seed) || void 0,
        terrain: params.terrain || void 0
      });
    case "create_grid": {
      const cols = Number(params.cols) || 80;
      const rows = Number(params.rows) || 24;
      const world = createGridWorld(cols, rows);
      const gridId = String(params.grid_id || `grid-${Date.now()}`);
      gridRegistry.set(gridId, world.grid);
      return { gridId, cols: world.cols, rows: world.rows, cellCount: world.cellCount };
    }
    case "edit_cell": {
      const gridId = String(params.grid_id || "default");
      const grid = getOrCreateGrid(gridId);
      return editCell(
        grid,
        Number(params.x),
        Number(params.y),
        Number(params.layer) || 0,
        params.data || {}
      );
    }
    case "compose_layers": {
      const gridId = String(params.grid_id || "default");
      const grid = getOrCreateGrid(gridId);
      const layers = params.layers || [0, 1, 2, 3, 4, 5];
      const result = composeGridLayers(grid, layers);
      return { cellCount: result.cellCount, layerCount: result.layers.length };
    }
    case "export_uvox": {
      const gridId = String(params.grid_id || "default");
      const grid = getOrCreateGrid(gridId);
      const outputPath = String(params.output_path || "output.uvox");
      return exportUvox(grid, gridId, outputPath);
    }
    case "pathfind": {
      const gridId = String(params.grid_id || "default");
      const grid = getOrCreateGrid(gridId);
      return findPath(
        grid,
        Number(params.start_x),
        Number(params.start_y),
        Number(params.end_x),
        Number(params.end_y),
        Number(params.layer) || 0
      );
    }
    case "import_basic_program":
      return importBasicProgram(
        String(params.program || ""),
        String(params.world_name || "BASIC World")
      );
    case "import_amos_program":
      return importAmosProgram(
        String(params.program || ""),
        String(params.world_name || "AMOS World")
      );
    case "latlon_to_ucode":
      return {
        coord: convertLatLonToUCode(
          Number(params.lat),
          Number(params.lon),
          Number(params.level) || 340
        )
      };
    case "ucode_to_latlon":
      return {
        location: convertUCodeToLatLon(String(params.coord || ""))
      };
    default:
      throw new Error(`Unknown tool: ${name}`);
  }
}
async function handleRequest(body) {
  let req;
  try {
    req = JSON.parse(body);
  } catch {
    return mcpError(null, -32700, "Parse error");
  }
  if (req.jsonrpc !== "2.0") {
    return mcpError(req.id, -32600, "Invalid Request");
  }
  try {
    switch (req.method) {
      case "initialize":
        return mcpResponse(req.id, {
          protocolVersion: "2024-11-05",
          capabilities: { tools: {} },
          serverInfo: { name: "gridsmith-mcp", version: "0.2.0" }
        });
      case "tools/list":
        return mcpResponse(req.id, { tools: GRIDSMITH_TOOLS });
      case "tools/call": {
        const params = req.params;
        if (!params?.name) {
          return mcpError(req.id, -32602, "Missing tool name");
        }
        const result = await invokeTool(params.name, params.arguments || {});
        return mcpResponse(req.id, { content: [{ type: "text", text: JSON.stringify(result) }] });
      }
      case "ping":
        return mcpResponse(req.id, {});
      default:
        return mcpError(req.id, -32601, `Method not found: ${req.method}`);
    }
  } catch (err) {
    return mcpError(req.id, -32e3, String(err));
  }
}
function main() {
  const server = createServer(async (req, res) => {
    if (req.method !== "POST") {
      res.writeHead(405, { "Content-Type": "application/json" });
      res.end(JSON.stringify(mcpError(null, -32e3, "Method not allowed")));
      return;
    }
    const chunks = [];
    for await (const chunk of req) {
      chunks.push(chunk);
    }
    const body = Buffer.concat(chunks).toString("utf-8");
    const response = await handleRequest(body);
    res.writeHead(200, {
      "Content-Type": "application/json",
      "Access-Control-Allow-Origin": "*"
    });
    res.end(JSON.stringify(response));
  });
  server.listen(Number(PORT), HOST, () => {
    process.stderr.write(`GridSmith MCP server listening on ${HOST}:${PORT}
`);
  });
}
main();
