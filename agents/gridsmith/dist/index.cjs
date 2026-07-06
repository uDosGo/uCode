"use strict";
var __create = Object.create;
var __defProp = Object.defineProperty;
var __getOwnPropDesc = Object.getOwnPropertyDescriptor;
var __getOwnPropNames = Object.getOwnPropertyNames;
var __getProtoOf = Object.getPrototypeOf;
var __hasOwnProp = Object.prototype.hasOwnProperty;
var __export = (target, all) => {
  for (var name in all)
    __defProp(target, name, { get: all[name], enumerable: true });
};
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
var __toCommonJS = (mod) => __copyProps(__defProp({}, "__esModule", { value: true }), mod);

// src/index.ts
var index_exports = {};
__export(index_exports, {
  GRIDSMITH_TOOLS: () => GRIDSMITH_TOOLS,
  composeGridLayers: () => composeGridLayers,
  convertLatLonToUCode: () => convertLatLonToUCode,
  convertUCodeToLatLon: () => convertUCodeToLatLon,
  createGridWorld: () => createGridWorld,
  createWorld: () => createWorld,
  createWorldManifest: () => createWorldManifest,
  editCell: () => editCell,
  exportUvox: () => exportUvox,
  findPath: () => findPath,
  importAmosProgram: () => importAmosProgram,
  importBasicProgram: () => importBasicProgram,
  lensCraft: () => lensCraft,
  sourceMiner: () => sourceMiner
});
module.exports = __toCommonJS(index_exports);
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

// src/tools/source-miner.ts
var import_node_fs = require("fs");
var import_node_path5 = require("path");
var import_node_fs2 = require("fs");
var ASM_EXTENSIONS = /* @__PURE__ */ new Set([".asm", ".s", ".6502", ".a65", ".inc", ".eq", ".bbc"]);
var KNOWN_HARDWARE = {
  "0xfe00": "VIA port B (user port)",
  "0xfe01": "VIA port A (keyboard/sound)",
  "0xfe04": "VIA timer 1 counter low",
  "0xfe05": "VIA timer 1 counter high",
  "0xfe08": "VIA ACR (auxiliary control register)",
  "0xfe09": "VIA PCR (peripheral control register)",
  "0xfe0a": "VIA IFR (interrupt flag register)",
  "0xfe0b": "VIA IER (interrupt enable register)",
  "0xfe40": "6845 CRTC address register",
  "0xfe41": "6845 CRTC data register",
  "0xfe60": "ACIA 6850 status/control",
  "0xfe61": "ACIA 6850 data",
  "0xfe80": "INTON (interrupt enable flip-flop)",
  "0xfe84": "ROMSEL (paging register)",
  "0xfea0": "System VIA IER",
  "0xfec0": "ADC data high",
  "0xfec1": "ADC data low",
  "0xfee0": "Tube ULA data",
  "0xfee1": "Tube ULA status",
  "0xff00": "OSBYTE entry point",
  "0xffe3": "OSBYTE indirect",
  "0xffe7": "OSWORD entry point",
  "0xfff4": "OSCLI entry point"
};
var ASSET_PATH_PATTERNS = [
  { regex: /(?:^|[./])gfx[/\\]/i, type: "sprite_data" },
  { regex: /(?:^|[./])sprites?[/\\]/i, type: "sprite_data" },
  { regex: /(?:^|[./])graphics?[/\\]/i, type: "sprite_data" },
  { regex: /(?:^|[./])text[/\\]/i, type: "teletext_pages" },
  { regex: /(?:^|[./])data[/\\]/i, type: "game_data" },
  { regex: /(?:^|[./])levels?[/\\]/i, type: "level_data" },
  { regex: /(?:^|[./])maps?[/\\]/i, type: "map_data" },
  { regex: /(?:^|[./])sound(s)?[/\\]/i, type: "audio_data" },
  { regex: /(?:^|[./])music[/\\]/i, type: "audio_data" },
  { regex: /(?:^|[./])chars?[/\\]/i, type: "character_data" },
  { regex: /\.(?:bin|raw|dat|spr)$/i, type: "binary_asset" },
  { regex: /\.(?:png|bmp|gif)$/i, type: "image_asset" },
  { regex: /\.(?:wav|ogg|mp3)$/i, type: "audio_asset" }
];
function isAsmFile(path5) {
  const ext = (0, import_node_path5.extname)(path5).toLowerCase();
  if (ASM_EXTENSIONS.has(ext)) return true;
  const base = path5.split("/").pop() || "";
  if (!base.includes(".") && !ext) {
    return true;
  }
  return false;
}
function matchesTarget(path5, patterns) {
  if (patterns.length === 0) return isAsmFile(path5);
  return patterns.some((p) => {
    try {
      return new RegExp(
        "^" + p.replace(/\./g, "\\.").replace(/\*/g, ".*").replace(/\?/g, ".") + "$",
        "i"
      ).test(path5);
    } catch {
      return path5.toLowerCase().includes(p.toLowerCase().replace(/\*/g, ""));
    }
  });
}
function matchesExclude(path5, patterns) {
  if (patterns.length === 0) return false;
  return patterns.some((p) => {
    try {
      return new RegExp(
        "^" + p.replace(/\./g, "\\.").replace(/\*/g, ".*").replace(/\?/g, ".") + "$",
        "i"
      ).test(path5);
    } catch {
      return path5.toLowerCase().includes(p.toLowerCase().replace(/\*/g, ""));
    }
  });
}
function scanFile(filePath, fileContent, currentOrg) {
  const lines = fileContent.split("\n");
  const memoryEntries = [];
  const functions = [];
  const structures = [];
  let org = currentOrg;
  let prevLabel = null;
  let inDataBlock = false;
  let dataBlockFields = [];
  let dataBlockName = "";
  let dataBlockOffset = 0;
  let addressCounter = 0;
  let commentBuffer = "";
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i].trim();
    const lineNo = i + 1;
    if (/^[;*\\]/.test(line)) {
      commentBuffer = line.replace(/^[;*\\]+\s*/, "");
      continue;
    }
    const orgMatch = line.match(/^(?:ORG|\*)\s*(?:=)?\s*[$&]?([0-9A-Fa-f]+)/i);
    if (orgMatch) {
      org = parseInt(orgMatch[1], 16);
      addressCounter = 0;
      continue;
    }
    const equMatch = line.match(/^(\w+)\s+(?:EQU|=)\s*[$&]?([0-9A-Fa-f]+)/i);
    if (equMatch) {
      const label = equMatch[1];
      const addr = parseInt(equMatch[2], 16);
      const addrHex = "0x" + addr.toString(16).padStart(4, "0");
      if (/^(PAGE|OS|VIA|SHEILA|CRTC|ACIA|ADC|TUBE|ULA|USER|INTON|ROMSEL|SYSTEM)/i.test(label)) {
        commentBuffer = "";
        continue;
      }
      const hwDesc = KNOWN_HARDWARE[addrHex];
      if (hwDesc) {
        memoryEntries.push({
          label,
          address: addrHex,
          type: "byte",
          description: hwDesc,
          confidence: 0.95
        });
      } else {
        memoryEntries.push({
          label,
          address: addrHex,
          type: "byte",
          description: commentBuffer || `${label} constant`,
          confidence: commentBuffer ? 0.85 : 0.7
        });
      }
      commentBuffer = "";
      continue;
    }
    const labelMatch = line.match(/^\.(\w+)(?:\s*$|\s*;|\s*[\\*;])/);
    if (labelMatch) {
      prevLabel = labelMatch[1];
      if (org !== null) {
        const addr = org + addressCounter;
        const addrHex = "0x" + addr.toString(16).padStart(4, "0");
        const prevLine = i > 0 ? lines[i - 1].trim() : "";
        const nextLine = i + 1 < lines.length ? lines[i + 1].trim() : "";
        const looksLikeFunction = nextLine && /^(?:LDA|LDX|LDY|STA|STX|STY|JSR|JMP|PHA|PHP|PLA|PLP|TXA|TYA|TAX|TAY|CLC|SEC|CLI|SEI|CLD|SED|CLV|INX|INY|DEX|DEY|RTS|RTI|BIT)/i.test(nextLine);
        if (looksLikeFunction) {
          functions.push({
            name: prevLabel,
            address: addrHex,
            description: commentBuffer || `${prevLabel} subroutine`,
            parameters: extractParameters(lines, i + 1)
          });
        } else {
          memoryEntries.push({
            label: prevLabel,
            address: addrHex,
            type: "byte",
            description: commentBuffer || `${prevLabel} data label`,
            confidence: 0.75
          });
        }
      }
      commentBuffer = "";
      continue;
    }
    if (/^(?:EQUB|EQUD|EQUW|DEFB|DEFW|DEFM|EQUS)\s/i.test(line)) {
      if (prevLabel && inDataBlock) {
        const sizeHint = /^(EQUB|DEFB|DEFM|EQUS)/i.test(line) ? 1 : /^(EQUW|DEFW)/i.test(line) ? 2 : 4;
        dataBlockFields.push({ offset: dataBlockOffset, name: prevLabel, size: sizeHint });
        dataBlockOffset += sizeHint;
      }
      const dataMatch = line.match(/^(?:EQUB|EQUD|EQUW|DEFB|DEFW|DEFM|EQUS)\s+(.+)/i);
      if (dataMatch) {
        const data = dataMatch[1];
        const quotedMatch = data.match(/^"([^"]*)"/);
        if (quotedMatch) {
          addressCounter += quotedMatch[1].length;
        } else {
          addressCounter += data.split(",").length * (/^(EQUD)/i.test(line) ? 4 : /^(EQUW|DEFW)/i.test(line) ? 2 : 1);
        }
      }
      prevLabel = null;
      commentBuffer = "";
      continue;
    }
    if (/^(?:SKIP|RES|DS|RMB)\s+(?:[$&])?([0-9A-Fa-f]+)/i.test(line)) {
      const skipMatch = line.match(/^(?:SKIP|RES|DS|RMB)\s+(?:[$&])?([0-9A-Fa-f]+)/i);
      const rawVal = skipMatch[1];
      const isHex = /^[$&]/.test(line.match(/^(?:SKIP|RES|DS|RMB)\s+([$&])/i)?.[1] || "");
      const skipBytes = isHex ? parseInt(rawVal, 16) : parseInt(rawVal, 10);
      if (prevLabel) {
        structures.push({
          name: prevLabel,
          size: skipBytes,
          fields: []
        });
        memoryEntries.push({
          label: prevLabel,
          address: org !== null ? "0x" + (org + addressCounter).toString(16).padStart(4, "0") : "unknown",
          type: "struct",
          description: commentBuffer || `${prevLabel} data structure`,
          confidence: 0.6,
          length: skipBytes
        });
      }
      addressCounter += skipBytes;
      prevLabel = null;
      commentBuffer = "";
      continue;
    }
    if (prevLabel && !/^(?:LDA|LDX|LDY|STA|STX|STY|JSR|JMP|RTS|RTI|BNE|BEQ|BCC|BCS|BPL|BMI|BVC|BVS|CMP|CPX|CPY|ADC|SBC|AND|ORA|EOR|ASL|LSR|ROL|ROR|INC|DEC|INX|INY|DEX|DEY|PHA|PHP|PLA|PLP|TXA|TYA|TAX|TAY|CLC|SEC|CLI|SEI|CLD|SED|CLV|NOP|BRK)/i.test(line)) {
      if (!inDataBlock) {
        dataBlockName = prevLabel;
        dataBlockFields = [];
        dataBlockOffset = 0;
        inDataBlock = true;
      }
      commentBuffer = "";
      continue;
    }
    if (/^(?:LDA|LDX|LDY|STA|STX|STY|JSR|JMP|RTS|RTI|BNE|BEQ|BCC|BCS|BPL|BMI|BVC|BVS|CMP|CPX|CPY|ADC|SBC|AND|ORA|EOR|ASL|LSR|ROL|ROR|INC|DEC|INX|INY|DEX|DEY|PHA|PHP|PLA|PLP|TXA|TYA|TAX|TAY|CLC|SEC|CLI|SEI|CLD|SED|CLV|NOP|BRK)/i.test(line)) {
      addressCounter += line.startsWith("JSR") || line.startsWith("JMP") ? 3 : line.startsWith("BNE") || line.startsWith("BEQ") || line.startsWith("BCC") || line.startsWith("BCS") || line.startsWith("BPL") || line.startsWith("BMI") || line.startsWith("BVC") || line.startsWith("BVS") ? 2 : 1;
      if (inDataBlock && dataBlockName) {
        structures.push({
          name: dataBlockName,
          size: dataBlockOffset,
          fields: dataBlockFields
        });
        inDataBlock = false;
        dataBlockName = "";
        dataBlockFields = [];
      }
      prevLabel = null;
      commentBuffer = "";
      continue;
    }
    prevLabel = null;
    commentBuffer = "";
  }
  if (inDataBlock && dataBlockName) {
    structures.push({
      name: dataBlockName,
      size: dataBlockOffset,
      fields: dataBlockFields
    });
  }
  return { memoryEntries, functions, structures, org };
}
function extractParameters(lines, startIndex) {
  const params = [];
  for (let i = startIndex; i < Math.min(startIndex + 20, lines.length); i++) {
    const line = lines[i].trim();
    const ldaMatch = line.match(/LDA\s+#?\$?\w+/i);
    if (ldaMatch && !params.some((p) => p.register === "A")) {
      params.push({ register: "A", description: line });
    }
    const ldxMatch = line.match(/LDX\s+#?\$?\w+/i);
    if (ldxMatch && !params.some((p) => p.register === "X")) {
      params.push({ register: "X", description: line });
    }
    const ldyMatch = line.match(/LDY\s+#?\$?\w+/i);
    if (ldyMatch && !params.some((p) => p.register === "Y")) {
      params.push({ register: "Y", description: line });
    }
    if (line.startsWith("RTS") || line.startsWith("JMP")) break;
  }
  return params;
}
function scanDirectory(rootPath, patterns, excludePatterns) {
  const results = [];
  function walk(dir) {
    try {
      const entries = (0, import_node_fs2.readdirSync)(dir);
      for (const entry of entries) {
        const fullPath = (0, import_node_path5.join)(dir, entry);
        try {
          const st = (0, import_node_fs2.statSync)(fullPath);
          if (st.isDirectory()) {
            if (!entry.startsWith(".") && entry !== "node_modules" && entry !== ".git") {
              walk(fullPath);
            }
          } else {
            const relPath = fullPath.replace(rootPath + "/", "");
            if (!matchesExclude(relPath, excludePatterns)) {
              if (patterns.length === 0) {
                if (isAsmFile(fullPath)) results.push(fullPath);
              } else if (matchesTarget(relPath, patterns)) {
                results.push(fullPath);
              }
            }
          }
        } catch {
        }
      }
    } catch {
    }
  }
  walk(rootPath);
  return results;
}
function detectAssetReferences(rootPath) {
  const refs = [];
  const seen = /* @__PURE__ */ new Set();
  function walk(dir) {
    try {
      const entries = (0, import_node_fs2.readdirSync)(dir);
      for (const entry of entries) {
        const fullPath = (0, import_node_path5.join)(dir, entry);
        try {
          const st = (0, import_node_fs2.statSync)(fullPath);
          if (st.isDirectory()) {
            if (!entry.startsWith(".") && entry !== "node_modules" && entry !== ".git") {
              walk(fullPath);
            }
          } else {
            const relPath = fullPath.replace(rootPath + "/", "");
            for (const { regex, type } of ASSET_PATH_PATTERNS) {
              if (regex.test(relPath) && !seen.has(relPath)) {
                seen.add(relPath);
                refs.push({
                  path: relPath,
                  type,
                  description: `${type.replace(/_/g, " ")}: ${entry}`
                });
              }
            }
          }
        } catch {
        }
      }
    } catch {
    }
  }
  walk(rootPath);
  const collapsed = {};
  for (const ref of refs) {
    if (!collapsed[ref.type]) {
      collapsed[ref.type] = { count: 0, type: ref.type, examples: [] };
    }
    collapsed[ref.type].count++;
    if (collapsed[ref.type].examples.length < 3) {
      collapsed[ref.type].examples.push(ref.path);
    }
  }
  return Object.values(collapsed).map((c) => ({
    path: c.examples[0] || rootPath,
    type: c.type,
    count: c.count,
    description: `${c.count} ${c.type.replace(/_/g, " ")} file(s)`
  }));
}
function generateRecommendations(findings, sourcePath) {
  const recs = [];
  const stateLabels = findings.memory_map.filter(
    (m) => /score|status|state|lives|level|time|health|energy|position|x_pos|y_pos|inventory|ship/i.test(
      m.label
    ) && m.confidence >= 0.7
  );
  for (const entry of stateLabels.slice(0, 5)) {
    recs.push({
      action: "create_lens_extractor",
      target: entry.label,
      priority: entry.confidence >= 0.85 ? "high" : "medium",
      rationale: `Game state variable for save/load and telemetry (${entry.description})`
    });
  }
  const commandLabels = ["MainLoop", "Dock", "Jump", "Launch", "Start", "Init", "Title", "Death", "Win", "Lose", "Pause", "Save", "Load"];
  for (const fn of findings.functions) {
    if (commandLabels.some((c) => fn.name.toLowerCase().includes(c.toLowerCase()))) {
      recs.push({
        action: "create_mcp_command",
        target: fn.name,
        priority: "medium",
        rationale: `${fn.name} is a game event trigger point`
      });
    }
  }
  if (findings.asset_references.length > 0) {
    recs.push({
      action: "create_skin_manifest",
      target: sourcePath,
      priority: "high",
      rationale: `${findings.asset_references.length} asset type(s) found \u2014 create SKIN theme`
    });
  }
  if (findings.data_structures.length > 0) {
    recs.push({
      action: "run_lens_craft",
      target: findings.data_structures.map((s) => s.name).join(", "),
      priority: "medium",
      rationale: `${findings.data_structures.length} data structure(s) found \u2014 generate LENS extractors`
    });
  }
  return recs;
}
function sourceMiner(input) {
  const patterns = input.options.target_patterns || [];
  const excludePatterns = input.options.exclude_patterns || [];
  const sourcePath = input.source.url;
  if (!(0, import_node_fs.existsSync)(sourcePath)) {
    throw new Error(`Source path not found: ${sourcePath}`);
  }
  const st = (0, import_node_fs2.statSync)(sourcePath);
  const files = st.isDirectory() ? scanDirectory(sourcePath, patterns, excludePatterns) : [sourcePath];
  const allMemory = [];
  const allFunctions = [];
  const allStructures = [];
  let currentOrg = null;
  for (const file of files) {
    try {
      const content = (0, import_node_fs.readFileSync)(file, "utf-8");
      const result = scanFile(file, content, currentOrg);
      allMemory.push(...result.memoryEntries);
      allFunctions.push(...result.functions);
      allStructures.push(...result.structures);
      if (result.org !== null) currentOrg = result.org;
    } catch {
    }
  }
  const rootPath = st.isDirectory() ? sourcePath : sourcePath.split("/").slice(0, -1).join("/") || ".";
  const assets = detectAssetReferences(rootPath);
  const findings = {
    memory_map: allMemory,
    functions: allFunctions,
    data_structures: allStructures,
    asset_references: assets
  };
  const recommendations = generateRecommendations(findings, sourcePath);
  return {
    skill: "Source-Miner",
    version: "1.0",
    executed_at: (/* @__PURE__ */ new Date()).toISOString(),
    source: sourcePath,
    findings,
    recommendations
  };
}

// src/tools/lens-craft.ts
var import_node_fs3 = require("fs");
var import_node_path6 = require("path");
function pascalCase(name) {
  return name.replace(/[^a-zA-Z0-9]/g, " ").split(/[\s_]+/).map((w) => w.charAt(0).toUpperCase() + w.slice(1).toLowerCase()).join("");
}
function snakeCase(name) {
  return name.replace(/[^a-zA-Z0-9]/g, "_").replace(/([a-z])([A-Z])/g, "$1_$2").toLowerCase();
}
function pythonType(ext) {
  switch (ext.type) {
    case "bitmask":
    case "uint8":
      return "int";
    case "uint16":
    case "int16":
      return "int";
    case "uint32":
    case "int32":
      return "int";
    case "array":
      return "dict";
    case "struct":
      return "dict";
    default:
      return "int";
  }
}
function pythonDocstring(description) {
  return `"""${description}"""`;
}
function generateBitmaskGetter(ext, addr) {
  const cases = ext.labels ? Object.entries(ext.labels).map(([val, label]) => `        ${val}: "${label}"`).join(",\n") : "";
  const classLabel = ext.labels ? `        labels = {${cases ? "\n" + cases + "\n" : ""}        }
        return labels.get(val, "unknown")` : "return val";
  return [
    `    @property`,
    `    def ${snakeCase(ext.name)}(self) -> str:`,
    `        ${pythonDocstring(ext.description)}`,
    `        val = self._emu.read_byte(0x${addr.toString(16)})`,
    classLabel
  ].join("\n");
}
function generateSimpleGetter(ext, addr) {
  const method = ext.type === "uint32" || ext.type === "int32" ? `read_uint32(0x${addr.toString(16)})` : ext.type === "uint16" || ext.type === "int16" ? `read_uint16(0x${addr.toString(16)})` : `read_byte(0x${addr.toString(16)})`;
  return [
    `    @property`,
    `    def ${snakeCase(ext.name)}(self) -> ${pythonType(ext)}:`,
    `        ${pythonDocstring(ext.description)}`,
    `        return self._emu.${method}`
  ].join("\n");
}
function generateStructGetter(ext, addr) {
  const fieldLines = ext.fields?.map((f) => {
    const readMethod = f.type === "uint32" ? `read_uint32(0x${(addr + f.offset).toString(16)})` : f.type === "uint16" ? `read_uint16(0x${(addr + f.offset).toString(16)})` : `read_byte(0x${(addr + f.offset).toString(16)})`;
    return `            "${f.name}": self._emu.${readMethod}`;
  }) || [];
  return [
    `    @property`,
    `    def ${snakeCase(ext.name)}(self) -> dict:`,
    `        ${pythonDocstring(ext.description)}`,
    "        return {",
    ...fieldLines,
    "        }"
  ].join("\n");
}
function generateArrayGetter(ext, addr) {
  const size = ext.size || 1;
  const labels = ext.labels ? Object.entries(ext.labels).map(([idx, label]) => `        items = ${JSON.stringify(Object.values(ext.labels))}`).join("\n") : "";
  const labelBlock = labels ? `
${labels}
        result = {}
        for i, label in enumerate(items):
            result[label] = self._emu.read_byte(0x${addr.toString(16)} + i)
        return result` : `        result = {}
        for i in range(${size}):
            result[i] = self._emu.read_byte(0x${addr.toString(16)} + i)
        return result`;
  return [
    `    @property`,
    `    def ${snakeCase(ext.name)}(self) -> dict:`,
    `        ${pythonDocstring(ext.description)}`,
    labelBlock
  ].join("\n");
}
function generateProperty(ext) {
  const addr = parseInt(ext.address, 16);
  switch (ext.type) {
    case "bitmask":
      return generateBitmaskGetter(ext, addr);
    case "struct":
      return generateStructGetter(ext, addr);
    case "array":
      return generateArrayGetter(ext, addr);
    case "uint8":
    case "uint16":
    case "uint32":
    case "int16":
    case "int32":
      return generateSimpleGetter(ext, addr);
    default:
      return generateSimpleGetter(ext, addr);
  }
}
function extractorToProvider(mem, programName) {
  const providers = [];
  for (const entry of mem) {
    if (entry.confidence < 0.6) continue;
    const snaked = snakeCase(entry.label);
    const name = `${programName}_${snaked}`.replace(/^[^a-z_]+/, "");
    switch (entry.type) {
      case "byte":
        if (entry.description && /stat(e|us)|flag|mode|bit/i.test(entry.description)) {
          providers.push({
            name,
            type: "bitmask",
            address: entry.address,
            size: 1,
            labels: guessBitmaskLabels(entry.label, entry.description),
            description: entry.description
          });
        } else if (entry.length && entry.length > 1) {
          providers.push({
            name,
            type: "array",
            address: entry.address,
            size: entry.length,
            description: entry.description
          });
        } else {
          providers.push({
            name,
            type: "uint8",
            address: entry.address,
            size: 1,
            description: entry.description
          });
        }
        break;
      case "struct":
        providers.push({
          name,
          type: "struct",
          address: entry.address,
          size: entry.length || 4,
          fields: [],
          description: entry.description
        });
        break;
      default:
        providers.push({
          name,
          type: "uint8",
          address: entry.address,
          size: 1,
          description: entry.description
        });
    }
  }
  return providers;
}
function guessBitmaskLabels(label, description) {
  const lower = description.toLowerCase();
  if (/docked|docking|flight|land/.test(lower)) {
    return { "0": "docked", "1": "in_flight", "2": "docking", "3": "jumping" };
  }
  if (/paused|running|stopped|title/i.test(lower)) {
    return { "0": "title_screen", "1": "running", "2": "paused", "3": "game_over" };
  }
  if (/alive|dead|hurt|invincible/i.test(lower)) {
    return { "0": "alive", "1": "dead", "2": "hurt", "3": "invincible" };
  }
  return { "0": "off", "1": "on" };
}
function generatePythonCode(extractors, moduleName, sourcePath) {
  const className = pascalCase(moduleName) + "Extractor";
  const propertyBlocks = extractors.map(generateProperty).join("\n\n");
  const captureItems = extractors.map((e) => `            "${snakeCase(e.name)}": self.${snakeCase(e.name)}`).join(",\n");
  const header = [
    "# Auto-generated by LENS-Craft v1.0",
    `# Source: ${sourcePath}`,
    `# ${extractors.length} extractors generated`,
    "",
    "",
    `class ${className}:`
  ].join("\n");
  const init = [
    "    def __init__(self, emu):",
    '        """Initialize with a 6502 emulator instance.',
    "",
    "        Args:",
    "            emu: Emulator providing read_byte(addr), read_uint16(addr),",
    "                 read_uint32(addr) in little-endian byte order.",
    '        """',
    "        self._emu = emu"
  ].join("\n");
  const captureAll = [
    "",
    "    def capture_all(self) -> dict:",
    '        """Capture all known state in a single snapshot."""',
    "        return {",
    captureItems,
    "        }"
  ].join("\n");
  return [header, init, propertyBlocks, captureAll, ""].join("\n\n");
}
function lensCraft(input) {
  const memoryMap = input.source_miner_report.findings.memory_map || [];
  const sourcePath = input.source_miner_report.source || "unknown";
  const pathSegments = sourcePath.replace(/\/$/, "").split("/");
  const programName = pathSegments[pathSegments.length - 1] || "unknown";
  const extractors = extractorToProvider(memoryMap, programName);
  const moduleName = input.output.module_name;
  const generatedCode = generatePythonCode(extractors, moduleName, sourcePath);
  let writtenTo;
  if (input.output.path) {
    const outPath = input.output.path.endsWith(".py") ? input.output.path : (0, import_node_path6.join)(input.output.path, `${moduleName}.py`);
    const dir = (0, import_node_path6.dirname)(outPath);
    if (!(0, import_node_fs3.existsSync)(dir)) {
      (0, import_node_fs3.mkdirSync)(dir, { recursive: true });
    }
    (0, import_node_fs3.writeFileSync)(outPath, generatedCode, "utf-8");
    writtenTo = outPath;
  }
  return {
    skill: "LENS-Craft",
    version: "1.0",
    executed_at: (/* @__PURE__ */ new Date()).toISOString(),
    module_path: input.output.path || `${moduleName}.py`,
    extractors,
    generated_code: generatedCode,
    written_to: writtenTo
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
  },
  {
    name: "source_miner",
    description: "Scan 6502 assembly source code for LENS-extractable integration points.",
    parameters: {
      source_path: { type: "string", description: "Path to source directory or file" },
      language: { type: "string", description: "Source language(s) as CSV", default: "6502" },
      target_patterns: { type: "string", description: "File patterns as CSV (e.g. *.asm,*.s)", default: "" },
      exclude_patterns: { type: "string", description: "Exclude patterns as CSV (e.g. test_*,*.tmp)", default: "" }
    }
  },
  {
    name: "lens_craft",
    description: "Generate Python LENS extractor code from a Source-Miner report.",
    parameters: {
      source_miner_json: { type: "string", description: "Source-Miner output as JSON string" },
      module_name: { type: "string", description: "Python module name (e.g. elite_lens)" },
      output_path: { type: "string", description: "Output file path (e.g. runtimes/basic/bridge/lens/extractors/)", default: "" }
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
// Annotate the CommonJS export names for ESM import in node:
0 && (module.exports = {
  GRIDSMITH_TOOLS,
  composeGridLayers,
  convertLatLonToUCode,
  convertUCodeToLatLon,
  createGridWorld,
  createWorld,
  createWorldManifest,
  editCell,
  exportUvox,
  findPath,
  importAmosProgram,
  importBasicProgram,
  lensCraft,
  sourceMiner
});
