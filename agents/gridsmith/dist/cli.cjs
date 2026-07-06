"use strict";
var __create = Object.create;
var __defProp = Object.defineProperty;
var __getOwnPropDesc = Object.getOwnPropertyDescriptor;
var __getOwnPropNames = Object.getOwnPropertyNames;
var __getProtoOf = Object.getPrototypeOf;
var __hasOwnProp = Object.prototype.hasOwnProperty;
var __copyProps = (to, from, except, desc) => {
  if (from && typeof from === "object" || typeof from === "function") {
    for (let key of __getOwnPropNames(from))
      if (!__hasOwnProp.call(to, key) && key !== except)
        __defProp(to, key, { get: () => from[key], enumerable: !(desc = __getOwnPropDesc(from, key)) || desc.enumerable });
  }
  return to;
};
var __toESM = (mod, isNodeMode, target) => (target = mod != null ? __create(__getProtoOf(mod)) : {}, __copyProps(
  // If the importer is in node compatibility mode or this is not an ESM
  // file that has been converted to a CommonJS file using a Babel-
  // compatible transform (i.e. "__esModule" has not been set), then set
  // "default" to the CommonJS "module.exports" for node compatibility.
  isNodeMode || !mod || !mod.__esModule ? __defProp(target, "default", { value: mod, enumerable: true }) : target,
  mod
));

// src/cli.ts
var import_gridcore7 = require("@udos/gridcore");

// src/index.ts
var import_gridcore6 = require("@udos/gridcore");

// src/tools/basic.ts
var import_promises = require("fs/promises");
var import_node_path = __toESM(require("path"), 1);
function slugify(value) {
  return value.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-+|-+$/g, "").slice(0, 80);
}
function parseBasicLines(program) {
  return program.split(/\r?\n/).map((line) => line.trimEnd()).filter(Boolean).map((line) => {
    const match = line.match(/^(\d+)\s*(.*)$/);
    if (!match) {
      return { lineNumber: null, statement: line.trim() };
    }
    return {
      lineNumber: Number(match[1]),
      statement: match[2].trim()
    };
  });
}
function classifyStatements(lines) {
  const counts = {
    print: 0,
    data: 0,
    goto: 0,
    gosub: 0,
    rem: 0,
    other: 0
  };
  for (const line of lines) {
    const statement = line.statement.toUpperCase();
    if (statement.startsWith("PRINT")) counts.print += 1;
    else if (statement.startsWith("DATA")) counts.data += 1;
    else if (statement.startsWith("GOTO")) counts.goto += 1;
    else if (statement.startsWith("GOSUB")) counts.gosub += 1;
    else if (statement.startsWith("REM")) counts.rem += 1;
    else counts.other += 1;
  }
  return counts;
}
async function importBasicProgram(programOrPath, worldName) {
  const maybeFile = import_node_path.default.resolve(programOrPath);
  let source = programOrPath;
  let sourceType = "inline";
  try {
    source = await (0, import_promises.readFile)(maybeFile, "utf-8");
    sourceType = "file";
  } catch {
    sourceType = "inline";
  }
  const parsed = parseBasicLines(source);
  const stats = classifyStatements(parsed);
  const slug = slugify(worldName || "basic-world") || "basic-world";
  const workspaceRoot = import_node_path.default.resolve(process.cwd(), "workspaces/gridcore");
  const scriptsDir = import_node_path.default.join(workspaceRoot, "scripts/basic");
  const worldsDir = import_node_path.default.join(workspaceRoot, "worlds/libraries");
  const importsDir = import_node_path.default.join(workspaceRoot, "grids/imports");
  await (0, import_promises.mkdir)(scriptsDir, { recursive: true });
  await (0, import_promises.mkdir)(worldsDir, { recursive: true });
  await (0, import_promises.mkdir)(importsDir, { recursive: true });
  const scriptPath = import_node_path.default.join(scriptsDir, `${slug}.bas`);
  const worldPath = import_node_path.default.join(worldsDir, `${slug}.json`);
  const importPath = import_node_path.default.join(importsDir, `${slug}.json`);
  const world = {
    id: slug,
    name: worldName,
    type: "library",
    source: "basic",
    sourceType,
    grid: {
      cols: 80,
      rows: Math.max(parsed.length, 1),
      cellSize: 24
    },
    layers: ["terrain", "details", "entities"],
    metrics: {
      lineCount: parsed.length,
      maxLineLength: parsed.reduce((max, line) => Math.max(max, line.statement.length), 0),
      statements: stats
    }
  };
  const importArtifact = {
    worldId: slug,
    preview: parsed.slice(0, 24).map((line, index) => ({
      row: index,
      lineNumber: line.lineNumber,
      text: line.statement
    }))
  };
  await (0, import_promises.writeFile)(scriptPath, source, "utf-8");
  await (0, import_promises.writeFile)(worldPath, JSON.stringify(world, null, 2), "utf-8");
  await (0, import_promises.writeFile)(importPath, JSON.stringify(importArtifact, null, 2), "utf-8");
  return {
    world,
    files: {
      script: scriptPath,
      manifest: worldPath,
      importArtifact: importPath
    },
    summary: {
      sourceType,
      lineCount: parsed.length,
      statements: stats
    }
  };
}

// src/tools/amos.ts
var import_promises2 = require("fs/promises");
var import_node_path2 = __toESM(require("path"), 1);
function slugify2(value) {
  return value.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-+|-+$/g, "").slice(0, 80);
}
function parseAmosLine(line) {
  const result = {
    sprites: [],
    bobs: [],
    sounds: [],
    moves: [],
    rems: [],
    otherLines: []
  };
  const trimmed = line.trim();
  const upper = trimmed.toUpperCase();
  const spriteMatch = upper.match(/^\s*SPRITE\s+(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*$/);
  if (spriteMatch) {
    result.sprites.push({
      number: Number(spriteMatch[1]),
      x: Number(spriteMatch[2]),
      y: Number(spriteMatch[3]),
      image: Number(spriteMatch[4])
    });
    return result;
  }
  const bobMatch = trimmed.match(/^\s*BOB\s+(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*,\s*"([^"]*)"\s*$/i);
  if (bobMatch) {
    result.bobs.push({
      number: Number(bobMatch[1]),
      x: Number(bobMatch[2]),
      y: Number(bobMatch[3]),
      image: bobMatch[4]
    });
    return result;
  }
  const soundMatch = upper.match(/^\s*SOUND\s+(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*$/);
  if (soundMatch) {
    result.sounds.push({
      channel: Number(soundMatch[1]),
      freq: Number(soundMatch[2]),
      duration: Number(soundMatch[3]),
      volume: Number(soundMatch[4])
    });
    return result;
  }
  const moveMatch = upper.match(/^\s*MOVE\s+(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*$/);
  if (moveMatch) {
    result.moves.push({
      spriteNumber: Number(moveMatch[1]),
      targetX: Number(moveMatch[2]),
      targetY: Number(moveMatch[3]),
      steps: Number(moveMatch[4])
    });
    return result;
  }
  if (upper.startsWith("REM") || trimmed.startsWith("'")) {
    result.rems.push(trimmed);
    return result;
  }
  result.otherLines.push(trimmed);
  return result;
}
function parseAmosProgram(program) {
  const lines = program.split(/\r?\n/).map((l) => l.trimEnd()).filter(Boolean);
  const merged = {
    sprites: [],
    bobs: [],
    sounds: [],
    moves: [],
    rems: [],
    otherLines: []
  };
  for (const line of lines) {
    const parsed = parseAmosLine(line);
    merged.sprites.push(...parsed.sprites);
    merged.bobs.push(...parsed.bobs);
    merged.sounds.push(...parsed.sounds);
    merged.moves.push(...parsed.moves);
    merged.rems.push(...parsed.rems);
    merged.otherLines.push(...parsed.otherLines);
  }
  return merged;
}
async function importAmosProgram(programOrPath, worldName) {
  const maybeFile = import_node_path2.default.resolve(programOrPath);
  let source = programOrPath;
  let sourceType = "inline";
  try {
    source = await (0, import_promises2.readFile)(maybeFile, "utf-8");
    sourceType = "file";
  } catch {
    sourceType = "inline";
  }
  const parsed = parseAmosProgram(source);
  const totalAssets = parsed.sprites.length + parsed.bobs.length + parsed.sounds.length + parsed.moves.length;
  const slug = slugify2(worldName || "amos-world") || "amos-world";
  const workspaceRoot = import_node_path2.default.resolve(process.cwd(), "workspaces/gridcore");
  const scriptsDir = import_node_path2.default.join(workspaceRoot, "scripts/amos");
  const worldsDir = import_node_path2.default.join(workspaceRoot, "worlds/libraries");
  const importsDir = import_node_path2.default.join(workspaceRoot, "grids/imports");
  await (0, import_promises2.mkdir)(scriptsDir, { recursive: true });
  await (0, import_promises2.mkdir)(worldsDir, { recursive: true });
  await (0, import_promises2.mkdir)(importsDir, { recursive: true });
  const scriptPath = import_node_path2.default.join(scriptsDir, `${slug}.amos`);
  const worldPath = import_node_path2.default.join(worldsDir, `${slug}.json`);
  const importPath = import_node_path2.default.join(importsDir, `${slug}.json`);
  const world = {
    id: slug,
    name: worldName,
    type: "dungeon",
    source: "amos",
    sourceType,
    grid: {
      cols: 80,
      rows: Math.max(totalAssets, 1),
      cellSize: 24
    },
    layers: ["terrain", "details", "entities"],
    assets: {
      sprites: parsed.sprites,
      bobs: parsed.bobs,
      sounds: parsed.sounds,
      moves: parsed.moves,
      commentCount: parsed.rems.length
    },
    metrics: {
      totalLines: parsed.sprites.length + parsed.bobs.length + parsed.sounds.length + parsed.moves.length + parsed.rems.length + parsed.otherLines.length,
      spriteCount: parsed.sprites.length,
      bobCount: parsed.bobs.length,
      soundCount: parsed.sounds.length,
      moveCount: parsed.moves.length,
      commentCount: parsed.rems.length
    }
  };
  const importArtifact = {
    worldId: slug,
    spriteTable: parsed.sprites,
    bobTable: parsed.bobs,
    soundTable: parsed.sounds,
    moveTable: parsed.moves
  };
  await (0, import_promises2.writeFile)(scriptPath, source, "utf-8");
  await (0, import_promises2.writeFile)(worldPath, JSON.stringify(world, null, 2), "utf-8");
  await (0, import_promises2.writeFile)(importPath, JSON.stringify(importArtifact, null, 2), "utf-8");
  return {
    world,
    files: {
      script: scriptPath,
      manifest: worldPath,
      importArtifact: importPath
    },
    summary: {
      sourceType,
      totalAssets,
      sprites: parsed.sprites.length,
      bobs: parsed.bobs.length,
      sounds: parsed.sounds.length,
      moves: parsed.moves.length
    }
  };
}

// src/tools/cell.ts
var import_gridcore = require("@udos/gridcore");
function editCell(grid, x, y, layer, data) {
  const existing = (0, import_gridcore.getCell)(grid, x, y, layer);
  const coord = existing?.coord ?? `L340-${x.toString(36).toUpperCase().padStart(2, "0")}${y.toString(36).toUpperCase().padStart(2, "0")}-0000-0`;
  const cell = (0, import_gridcore.createCell)(coord, x, y, layer);
  if (data.char !== void 0) cell.char = data.char;
  if (data.fg !== void 0) cell.fg = data.fg;
  if (data.bg !== void 0) cell.bg = data.bg;
  (0, import_gridcore.setCell)(grid, cell);
  return {
    cell: { x: cell.x, y: cell.y, layer: cell.layer, char: cell.char, fg: cell.fg, bg: cell.bg },
    previous: existing ? { x: existing.x, y: existing.y, layer: existing.layer, char: existing.char, fg: existing.fg, bg: existing.bg } : null
  };
}

// src/tools/layers.ts
var import_gridcore2 = require("@udos/gridcore");
function composeGridLayers(grid, layerIndices) {
  const layers = [];
  for (const z of layerIndices) {
    const cells = [];
    for (let y = 0; y < grid.rows; y++) {
      for (let x = 0; x < grid.cols; x++) {
        const cell = (0, import_gridcore2.getCell)(grid, x, y, z);
        if (cell) {
          cells.push(cell);
        }
      }
    }
    layers.push((0, import_gridcore2.createLayer)(z, cells));
  }
  const composed = (0, import_gridcore2.composeLayers)(layers);
  return {
    layers: layers.map((l) => ({ z: l.z, cellCount: l.cells.length })),
    composed,
    cellCount: composed.length
  };
}

// src/tools/uvox.ts
var import_promises3 = require("fs/promises");
var import_node_path3 = __toESM(require("path"), 1);
var import_gridcore3 = require("@udos/gridcore");
async function exportUvox(grid, gridId, outputPath) {
  const resolved = import_node_path3.default.resolve(outputPath);
  await (0, import_promises3.mkdir)(import_node_path3.default.dirname(resolved), { recursive: true });
  const cells = (0, import_gridcore3.listCells)(grid).map((cell) => ({
    x: cell.x,
    y: cell.y,
    layer: cell.layer,
    char: cell.char ?? " ",
    fg: cell.fg ?? 7,
    bg: cell.bg ?? 0,
    coord: cell.coord
  }));
  const manifest = {
    format: "uvox/1.0",
    gridId,
    cols: grid.cols,
    rows: grid.rows,
    createdAt: (/* @__PURE__ */ new Date()).toISOString(),
    cells
  };
  const json = JSON.stringify(manifest, null, 2);
  await (0, import_promises3.writeFile)(resolved, json, "utf-8");
  return {
    path: resolved,
    bytes: Buffer.byteLength(json, "utf-8"),
    cellCount: cells.length
  };
}

// src/tools/pathfind.ts
var import_gridcore4 = require("@udos/gridcore");
function heuristic(a, b) {
  return Math.abs(a.x - b.x) + Math.abs(a.y - b.y);
}
function neighbors(node, grid, layer) {
  const dirs = [
    { dx: 0, dy: -1 },
    // up
    { dx: 0, dy: 1 },
    // down
    { dx: -1, dy: 0 },
    // left
    { dx: 1, dy: 0 }
    // right
  ];
  const result = [];
  for (const { dx, dy } of dirs) {
    const nx = node.x + dx;
    const ny = node.y + dy;
    if (nx >= 0 && nx < grid.cols && ny >= 0 && ny < grid.rows) {
      const cell = (0, import_gridcore4.getCell)(grid, nx, ny, layer);
      if (cell && cell.char !== "#") {
        result.push({ x: nx, y: ny, layer });
      }
    }
  }
  return result;
}
function reconstructPath(cameFrom, current) {
  const path5 = [current];
  let key = `${current.x},${current.y},${current.layer}`;
  while (cameFrom.has(key)) {
    current = cameFrom.get(key);
    key = `${current.x},${current.y},${current.layer}`;
    path5.unshift(current);
  }
  return path5;
}
function findPath(grid, startX, startY, endX, endY, layer = 0) {
  const start = { x: startX, y: startY, layer };
  const goal = { x: endX, y: endY, layer };
  if (startX < 0 || startX >= grid.cols || startY < 0 || startY >= grid.rows || endX < 0 || endX >= grid.cols || endY < 0 || endY >= grid.rows) {
    return { path: [], steps: 0, found: false };
  }
  const openSet = [{ node: start, f: heuristic(start, goal) }];
  const cameFrom = /* @__PURE__ */ new Map();
  const gScore = /* @__PURE__ */ new Map();
  gScore.set(`${start.x},${start.y},${start.layer}`, 0);
  while (openSet.length > 0) {
    openSet.sort((a, b) => a.f - b.f);
    const current = openSet.shift();
    if (current.node.x === goal.x && current.node.y === goal.y) {
      const path5 = reconstructPath(cameFrom, current.node);
      return { path: path5, steps: path5.length - 1, found: true };
    }
    const currentKey = `${current.node.x},${current.node.y},${current.node.layer}`;
    const currentG = gScore.get(currentKey) ?? Infinity;
    for (const neighbor of neighbors(current.node, grid, layer)) {
      const tentG = currentG + 1;
      const nKey = `${neighbor.x},${neighbor.y},${neighbor.layer}`;
      if (tentG < (gScore.get(nKey) ?? Infinity)) {
        cameFrom.set(nKey, current.node);
        gScore.set(nKey, tentG);
        openSet.push({ node: neighbor, f: tentG + heuristic(neighbor, goal) });
      }
    }
  }
  return { path: [], steps: 0, found: false };
}

// src/tools/world.ts
var import_promises4 = require("fs/promises");
var import_node_path4 = __toESM(require("path"), 1);
var import_gridcore5 = require("@udos/gridcore");
function createWorldManifest(id, name, type, seed, source = "generated") {
  return { id, name, type, seed, source };
}
async function createWorld(options) {
  const cols = options.cols ?? 80;
  const rows = options.rows ?? 24;
  const slug = options.name.toLowerCase().replace(/[^a-z0-9]+/g, "-").slice(0, 80);
  const grid = (0, import_gridcore5.createGrid)(cols, rows);
  if (options.terrain) {
    for (const [coord, char] of Object.entries(options.terrain)) {
      const parts = coord.split(",");
      if (parts.length === 2) {
        const x = Number(parts[0]);
        const y = Number(parts[1]);
        if (!isNaN(x) && !isNaN(y)) {
          editCell(grid, x, y, 0, { char });
        }
      }
    }
  }
  const manifest = createWorldManifest(slug, options.name, options.type, options.seed);
  const workspaceRoot = import_node_path4.default.resolve(process.cwd(), "workspaces/gridcore");
  const worldDir = import_node_path4.default.join(workspaceRoot, "worlds", slug);
  const manifestPath = import_node_path4.default.join(worldDir, "manifest.json");
  const gridPath = import_node_path4.default.join(worldDir, "grid.json");
  await (0, import_promises4.mkdir)(worldDir, { recursive: true });
  const gridExport = {
    id: slug,
    cols: grid.cols,
    rows: grid.rows,
    cells: [...grid.cells.values()].map((c) => ({
      x: c.x,
      y: c.y,
      layer: c.layer,
      char: c.char,
      fg: c.fg,
      bg: c.bg,
      coord: c.coord
    }))
  };
  await (0, import_promises4.writeFile)(manifestPath, JSON.stringify(manifest, null, 2), "utf-8");
  await (0, import_promises4.writeFile)(gridPath, JSON.stringify(gridExport, null, 2), "utf-8");
  return {
    manifest,
    grid: { cols: grid.cols, rows: grid.rows, cellCount: grid.cells.size },
    files: {
      manifest: manifestPath,
      grid: gridPath
    }
  };
}

// src/index.ts
var GRIDSMITH_TOOLS = [
  {
    name: "create_world",
    description: "Create a new world with optional terrain.",
    parameters: {
      name: { type: "string", description: "World name" },
      type: { type: "string", description: "World type: earth, dungeon, vault, or library" },
      cols: { type: "number", description: "Grid column count", default: 80 },
      rows: { type: "number", description: "Grid row count", default: 24 },
      seed: { type: "number", description: "Random seed", default: 0 },
      terrain: { type: "object", description: 'Map of "x,y" -> character for terrain' }
    }
  },
  {
    name: "import_basic_program",
    description: "Import a BASIC program as a grid world.",
    parameters: {
      program: { type: "string", description: "BASIC program code or file path" },
      world_name: { type: "string", description: "Name for the generated world" }
    }
  },
  {
    name: "import_amos_program",
    description: "Import an AMOS program as a grid world.",
    parameters: {
      program: { type: "string", description: "AMOS program code or file path" },
      world_name: { type: "string", description: "Name for the generated world" }
    }
  },
  {
    name: "create_grid",
    description: "Create a new grid.",
    parameters: {
      cols: { type: "number", description: "Grid column count", default: 80 },
      rows: { type: "number", description: "Grid row count", default: 24 },
      cell_size: { type: "number", description: "Logical cell size", default: 24 }
    }
  },
  {
    name: "edit_cell",
    description: "Edit a specific cell.",
    parameters: {
      grid_id: { type: "string", description: "Grid identifier" },
      x: { type: "number", description: "X cell coordinate" },
      y: { type: "number", description: "Y cell coordinate" },
      layer: { type: "number", description: "Layer index", default: 0 },
      data: { type: "object", description: "Cell payload (char, fg, bg)" }
    }
  },
  {
    name: "compose_layers",
    description: "Compose layers into a single view.",
    parameters: {
      grid_id: { type: "string", description: "Grid identifier" },
      layers: {
        type: "array",
        description: "Ordered layer list",
        default: [0, 1, 2, 3, 4, 5],
        items: { type: "number" }
      }
    }
  },
  {
    name: "export_uvox",
    description: "Export a grid as a .uvox artifact.",
    parameters: {
      grid_id: { type: "string", description: "Grid identifier" },
      output_path: { type: "string", description: "Output file path" }
    }
  },
  {
    name: "pathfind",
    description: "Find path between two points on a grid (A*).",
    parameters: {
      grid_id: { type: "string", description: "Grid identifier" },
      start_x: { type: "number", description: "Start X coordinate" },
      start_y: { type: "number", description: "Start Y coordinate" },
      end_x: { type: "number", description: "End X coordinate" },
      end_y: { type: "number", description: "End Y coordinate" },
      layer: { type: "number", description: "Layer index", default: 0 }
    }
  },
  {
    name: "latlon_to_ucode",
    description: "Convert lat/lon to uCode.",
    parameters: {
      lat: { type: "number", description: "Latitude" },
      lon: { type: "number", description: "Longitude" },
      level: { type: "number", description: "uCode level", default: 340 }
    }
  },
  {
    name: "ucode_to_latlon",
    description: "Convert uCode to lat/lon.",
    parameters: {
      coord: { type: "string", description: "uCode coordinate" }
    }
  }
];
function createGridWorld(cols = 80, rows = 24) {
  const grid = (0, import_gridcore6.createGrid)(cols, rows);
  return {
    grid,
    cols: grid.cols,
    rows: grid.rows,
    cellCount: (0, import_gridcore6.listCells)(grid).length
  };
}
function convertLatLonToUCode(lat, lon, level = 340) {
  return (0, import_gridcore6.latLonToUCode)(lat, lon, level);
}
function convertUCodeToLatLon(coord) {
  return (0, import_gridcore6.uCodeToLatLon)(coord);
}

// src/cli.ts
function argValue(args, flag, fallback) {
  const index = args.indexOf(flag);
  if (index === -1 || index + 1 >= args.length) return fallback;
  return args[index + 1];
}
function printJson(value) {
  process.stdout.write(`${JSON.stringify(value, null, 2)}
`);
}
function printUsage() {
  process.stdout.write(
    [
      "GridSmith CLI",
      "",
      "Commands:",
      "  tools list",
      '  world create --name "My World" --type dungeon [--cols 80 --rows 24 --seed 42]',
      '  world import-basic --program <file|code> --world-name "Name"',
      '  world import-amos --program <file|code> --world-name "Name"',
      "  grid create [--grid-id mygrid] [--cols 80 --rows 24]",
      "  cell edit --grid-id mygrid --x 0 --y 0 [--layer 0] --char X --fg 7 --bg 0",
      "  layers compose --grid-id mygrid [--layers 0,1,2]",
      "  uvox export --grid-id mygrid --output output.uvox",
      "  path find --grid-id mygrid --start-x 0 --start-y 0 --end-x 10 --end-y 10 [--layer 0]",
      "  location latlon-to-ucode --lat -33.8688 --lon 151.2093 --level 340",
      "  location ucode-to-latlon --coord L340-0A0B-0000-0"
    ].join("\n") + "\n"
  );
}
var gridRegistry = /* @__PURE__ */ new Map();
function getOrCreateGrid(id, cols = 80, rows = 24) {
  let grid = gridRegistry.get(id);
  if (!grid) {
    grid = (0, import_gridcore7.createGrid)(cols, rows);
    gridRegistry.set(id, grid);
  }
  return grid;
}
function main() {
  const args = process.argv.slice(2);
  const [section, action] = args;
  if (!section) {
    printUsage();
    process.exitCode = 1;
    return;
  }
  if (section === "tools" && action === "list") {
    printJson({ tools: GRIDSMITH_TOOLS });
    return;
  }
  if (section === "world" && action === "create") {
    const name = argValue(args, "--name", "New World") || "New World";
    const type = argValue(args, "--type", "earth");
    const cols = Number(argValue(args, "--cols", "80"));
    const rows = Number(argValue(args, "--rows", "24"));
    const seed = Number(argValue(args, "--seed", "0")) || void 0;
    createWorld({ name, type, cols, rows, seed }).then((result) => printJson(result)).catch((error) => {
      process.stderr.write(`${String(error)}
`);
      process.exitCode = 1;
    });
    return;
  }
  if (section === "world" && action === "import-basic") {
    const program = argValue(args, "--program", "") || "";
    const worldName = argValue(args, "--world-name", "Imported BASIC World") || "Imported BASIC World";
    importBasicProgram(program, worldName).then((result) => printJson(result)).catch((error) => {
      process.stderr.write(`${String(error)}
`);
      process.exitCode = 1;
    });
    return;
  }
  if (section === "world" && action === "import-amos") {
    const program = argValue(args, "--program", "") || "";
    const worldName = argValue(args, "--world-name", "Imported AMOS World") || "Imported AMOS World";
    importAmosProgram(program, worldName).then((result) => printJson(result)).catch((error) => {
      process.stderr.write(`${String(error)}
`);
      process.exitCode = 1;
    });
    return;
  }
  if (section === "grid" && action === "create") {
    const gridId = argValue(args, "--grid-id", `grid-${Date.now()}`) || `grid-${Date.now()}`;
    const cols = Number(argValue(args, "--cols", "80"));
    const rows = Number(argValue(args, "--rows", "24"));
    const world = createGridWorld(cols, rows);
    gridRegistry.set(gridId, world.grid);
    printJson({ gridId, cols: world.cols, rows: world.rows, cellCount: world.cellCount });
    return;
  }
  if (section === "cell" && action === "edit") {
    const gridId = argValue(args, "--grid-id", "default") || "default";
    const grid = getOrCreateGrid(gridId);
    const x = Number(argValue(args, "--x", "0"));
    const y = Number(argValue(args, "--y", "0"));
    const layer = Number(argValue(args, "--layer", "0"));
    const char = argValue(args, "--char");
    const fg = argValue(args, "--fg");
    const bg = argValue(args, "--bg");
    const data = {};
    if (char !== void 0) data.char = char;
    if (fg !== void 0) data.fg = Number(fg);
    if (bg !== void 0) data.bg = Number(bg);
    printJson(editCell(grid, x, y, layer, data));
    return;
  }
  if (section === "layers" && action === "compose") {
    const gridId = argValue(args, "--grid-id", "default") || "default";
    const grid = getOrCreateGrid(gridId);
    const layersStr = argValue(args, "--layers", "0,1,2,3,4,5");
    const layers = (layersStr || "0,1,2,3,4,5").split(",").map(Number);
    const result = composeGridLayers(grid, layers);
    printJson({ cellCount: result.cellCount, layerCount: result.layers.length });
    return;
  }
  if (section === "uvox" && action === "export") {
    const gridId = argValue(args, "--grid-id", "default") || "default";
    const grid = getOrCreateGrid(gridId);
    const output = argValue(args, "--output", "output.uvox") || "output.uvox";
    exportUvox(grid, gridId, output).then((result) => printJson(result)).catch((error) => {
      process.stderr.write(`${String(error)}
`);
      process.exitCode = 1;
    });
    return;
  }
  if (section === "path" && action === "find") {
    const gridId = argValue(args, "--grid-id", "default") || "default";
    const grid = getOrCreateGrid(gridId);
    const startX = Number(argValue(args, "--start-x", "0"));
    const startY = Number(argValue(args, "--start-y", "0"));
    const endX = Number(argValue(args, "--end-x", "0"));
    const endY = Number(argValue(args, "--end-y", "0"));
    const layer = Number(argValue(args, "--layer", "0"));
    printJson(findPath(grid, startX, startY, endX, endY, layer));
    return;
  }
  if (section === "location" && action === "latlon-to-ucode") {
    const lat = Number(argValue(args, "--lat"));
    const lon = Number(argValue(args, "--lon"));
    const level = Number(argValue(args, "--level", "340"));
    printJson({ coord: convertLatLonToUCode(lat, lon, level) });
    return;
  }
  if (section === "location" && action === "ucode-to-latlon") {
    const coord = argValue(args, "--coord", "") || "";
    printJson({ location: convertUCodeToLatLon(coord) });
    return;
  }
  printUsage();
  process.exitCode = 1;
}
main();
