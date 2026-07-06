// src/index.ts
import { createGrid as createGrid2, listCells as listCells3, latLonToUCode, uCodeToLatLon } from "@udos/gridcore";

// src/tools/basic.ts
import { mkdir, readFile, writeFile } from "fs/promises";
import path from "path";
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
  const maybeFile = path.resolve(programOrPath);
  let source = programOrPath;
  let sourceType = "inline";
  try {
    source = await readFile(maybeFile, "utf-8");
    sourceType = "file";
  } catch {
    sourceType = "inline";
  }
  const parsed = parseBasicLines(source);
  const stats = classifyStatements(parsed);
  const slug = slugify(worldName || "basic-world") || "basic-world";
  const workspaceRoot = path.resolve(process.cwd(), "workspaces/gridcore");
  const scriptsDir = path.join(workspaceRoot, "scripts/basic");
  const worldsDir = path.join(workspaceRoot, "worlds/libraries");
  const importsDir = path.join(workspaceRoot, "grids/imports");
  await mkdir(scriptsDir, { recursive: true });
  await mkdir(worldsDir, { recursive: true });
  await mkdir(importsDir, { recursive: true });
  const scriptPath = path.join(scriptsDir, `${slug}.bas`);
  const worldPath = path.join(worldsDir, `${slug}.json`);
  const importPath = path.join(importsDir, `${slug}.json`);
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
  await writeFile(scriptPath, source, "utf-8");
  await writeFile(worldPath, JSON.stringify(world, null, 2), "utf-8");
  await writeFile(importPath, JSON.stringify(importArtifact, null, 2), "utf-8");
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
import { mkdir as mkdir2, readFile as readFile2, writeFile as writeFile2 } from "fs/promises";
import path2 from "path";
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
  const maybeFile = path2.resolve(programOrPath);
  let source = programOrPath;
  let sourceType = "inline";
  try {
    source = await readFile2(maybeFile, "utf-8");
    sourceType = "file";
  } catch {
    sourceType = "inline";
  }
  const parsed = parseAmosProgram(source);
  const totalAssets = parsed.sprites.length + parsed.bobs.length + parsed.sounds.length + parsed.moves.length;
  const slug = slugify2(worldName || "amos-world") || "amos-world";
  const workspaceRoot = path2.resolve(process.cwd(), "workspaces/gridcore");
  const scriptsDir = path2.join(workspaceRoot, "scripts/amos");
  const worldsDir = path2.join(workspaceRoot, "worlds/libraries");
  const importsDir = path2.join(workspaceRoot, "grids/imports");
  await mkdir2(scriptsDir, { recursive: true });
  await mkdir2(worldsDir, { recursive: true });
  await mkdir2(importsDir, { recursive: true });
  const scriptPath = path2.join(scriptsDir, `${slug}.amos`);
  const worldPath = path2.join(worldsDir, `${slug}.json`);
  const importPath = path2.join(importsDir, `${slug}.json`);
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
  await writeFile2(scriptPath, source, "utf-8");
  await writeFile2(worldPath, JSON.stringify(world, null, 2), "utf-8");
  await writeFile2(importPath, JSON.stringify(importArtifact, null, 2), "utf-8");
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
import { setCell, getCell, createCell } from "@udos/gridcore";
function editCell(grid, x, y, layer, data) {
  const existing = getCell(grid, x, y, layer);
  const coord = existing?.coord ?? `L340-${x.toString(36).toUpperCase().padStart(2, "0")}${y.toString(36).toUpperCase().padStart(2, "0")}-0000-0`;
  const cell = createCell(coord, x, y, layer);
  if (data.char !== void 0) cell.char = data.char;
  if (data.fg !== void 0) cell.fg = data.fg;
  if (data.bg !== void 0) cell.bg = data.bg;
  setCell(grid, cell);
  return {
    cell: { x: cell.x, y: cell.y, layer: cell.layer, char: cell.char, fg: cell.fg, bg: cell.bg },
    previous: existing ? { x: existing.x, y: existing.y, layer: existing.layer, char: existing.char, fg: existing.fg, bg: existing.bg } : null
  };
}

// src/tools/layers.ts
import { createLayer, composeLayers, getCell as getCell2 } from "@udos/gridcore";
function composeGridLayers(grid, layerIndices) {
  const layers = [];
  for (const z of layerIndices) {
    const cells = [];
    for (let y = 0; y < grid.rows; y++) {
      for (let x = 0; x < grid.cols; x++) {
        const cell = getCell2(grid, x, y, z);
        if (cell) {
          cells.push(cell);
        }
      }
    }
    layers.push(createLayer(z, cells));
  }
  const composed = composeLayers(layers);
  return {
    layers: layers.map((l) => ({ z: l.z, cellCount: l.cells.length })),
    composed,
    cellCount: composed.length
  };
}

// src/tools/uvox.ts
import { writeFile as writeFile3, mkdir as mkdir3 } from "fs/promises";
import path3 from "path";
import { listCells as listCells2 } from "@udos/gridcore";
async function exportUvox(grid, gridId, outputPath) {
  const resolved = path3.resolve(outputPath);
  await mkdir3(path3.dirname(resolved), { recursive: true });
  const cells = listCells2(grid).map((cell) => ({
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
  await writeFile3(resolved, json, "utf-8");
  return {
    path: resolved,
    bytes: Buffer.byteLength(json, "utf-8"),
    cellCount: cells.length
  };
}

// src/tools/pathfind.ts
import { getCell as getCell3 } from "@udos/gridcore";
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
      const cell = getCell3(grid, nx, ny, layer);
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
import { mkdir as mkdir4, writeFile as writeFile4 } from "fs/promises";
import path4 from "path";
import { createGrid } from "@udos/gridcore";
function createWorldManifest(id, name, type, seed, source = "generated") {
  return { id, name, type, seed, source };
}
async function createWorld(options) {
  const cols = options.cols ?? 80;
  const rows = options.rows ?? 24;
  const slug = options.name.toLowerCase().replace(/[^a-z0-9]+/g, "-").slice(0, 80);
  const grid = createGrid(cols, rows);
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
  const workspaceRoot = path4.resolve(process.cwd(), "workspaces/gridcore");
  const worldDir = path4.join(workspaceRoot, "worlds", slug);
  const manifestPath = path4.join(worldDir, "manifest.json");
  const gridPath = path4.join(worldDir, "grid.json");
  await mkdir4(worldDir, { recursive: true });
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
  await writeFile4(manifestPath, JSON.stringify(manifest, null, 2), "utf-8");
  await writeFile4(gridPath, JSON.stringify(gridExport, null, 2), "utf-8");
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
  const grid = createGrid2(cols, rows);
  return {
    grid,
    cols: grid.cols,
    rows: grid.rows,
    cellCount: listCells3(grid).length
  };
}
function convertLatLonToUCode(lat, lon, level = 340) {
  return latLonToUCode(lat, lon, level);
}
function convertUCodeToLatLon(coord) {
  return uCodeToLatLon(coord);
}

export {
  importBasicProgram,
  importAmosProgram,
  editCell,
  composeGridLayers,
  exportUvox,
  findPath,
  createWorldManifest,
  createWorld,
  GRIDSMITH_TOOLS,
  createGridWorld,
  convertLatLonToUCode,
  convertUCodeToLatLon
};
