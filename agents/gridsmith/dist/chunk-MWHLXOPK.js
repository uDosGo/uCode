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

// src/tools/source-miner.ts
import { readFileSync, existsSync } from "fs";
import { join, extname } from "path";
import { readdirSync, statSync } from "fs";
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
  const ext = extname(path5).toLowerCase();
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
      const entries = readdirSync(dir);
      for (const entry of entries) {
        const fullPath = join(dir, entry);
        try {
          const st = statSync(fullPath);
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
      const entries = readdirSync(dir);
      for (const entry of entries) {
        const fullPath = join(dir, entry);
        try {
          const st = statSync(fullPath);
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
  if (!existsSync(sourcePath)) {
    throw new Error(`Source path not found: ${sourcePath}`);
  }
  const st = statSync(sourcePath);
  const files = st.isDirectory() ? scanDirectory(sourcePath, patterns, excludePatterns) : [sourcePath];
  const allMemory = [];
  const allFunctions = [];
  const allStructures = [];
  let currentOrg = null;
  for (const file of files) {
    try {
      const content = readFileSync(file, "utf-8");
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
import { writeFileSync, mkdirSync, existsSync as existsSync2 } from "fs";
import { dirname, join as join2 } from "path";
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
    const outPath = input.output.path.endsWith(".py") ? input.output.path : join2(input.output.path, `${moduleName}.py`);
    const dir = dirname(outPath);
    if (!existsSync2(dir)) {
      mkdirSync(dir, { recursive: true });
    }
    writeFileSync(outPath, generatedCode, "utf-8");
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

// src/tools/skin-weaver.ts
import { writeFileSync as writeFileSync2, mkdirSync as mkdirSync2, existsSync as existsSync3 } from "fs";
import { join as join3 } from "path";
var PALETTES = {
  bbc_mode7: {
    "0": "#000000",
    "1": "#ff0000",
    "2": "#00ff00",
    "3": "#ffff00",
    "4": "#0000ff",
    "5": "#ff00ff",
    "6": "#00ffff",
    "7": "#ffffff"
  },
  teletext_classic: {
    "0": "#000000",
    "1": "#ff0000",
    "2": "#00cc00",
    "3": "#cccc00",
    "4": "#0000cc",
    "5": "#cc00cc",
    "6": "#00cccc",
    "7": "#cccccc"
  },
  dark_fantasy: {
    "0": "#0a0a0a",
    "1": "#8b0000",
    "2": "#2e8b57",
    "3": "#b8860b",
    "4": "#191970",
    "5": "#4b0082",
    "6": "#5f9ea0",
    "7": "#a9a9a9"
  },
  repton_classic: {
    "0": "#000000",
    "1": "#ff8800",
    "2": "#00cc00",
    "3": "#ffff00",
    "4": "#0044cc",
    "5": "#cc44cc",
    "6": "#00cccc",
    "7": "#cccccc"
  },
  elite_wireframe: {
    "0": "#000000",
    "1": "#00ff00",
    "2": "#00ff00",
    "3": "#ffff00",
    "4": "#0000ff",
    "5": "#ff00ff",
    "6": "#00ffff",
    "7": "#00ff00"
  }
};
var CHAR_MAP = {
  wireframe_model: { char: "@", fg: 2, bg: 0, desc: "Wireframe ship model" },
  sprite_data: { char: "*", fg: 3, bg: 0, desc: "Sprite character" },
  teletext_pages: { char: " ", fg: 7, bg: 0, desc: "Teletext page" },
  audio_data: { char: "~", fg: 5, bg: 0, desc: "Audio asset" },
  map_data: { char: "#", fg: 6, bg: 0, desc: "Map tile" },
  level_data: { char: "#", fg: 1, bg: 0, desc: "Level layout" },
  game_data: { char: "?", fg: 7, bg: 0, desc: "Game data file" },
  image_asset: { char: "&", fg: 4, bg: 0, desc: "Image asset" },
  binary_asset: { char: "%", fg: 5, bg: 0, desc: "Binary asset" },
  character_data: { char: "C", fg: 2, bg: 0, desc: "Character definition" }
};
function guessCharMapping(asset) {
  const type = asset.format || asset.type;
  const mapping = CHAR_MAP[type] || { char: "?", fg: 7, bg: 0, desc: asset.type };
  return {
    source: asset.path,
    target_char: mapping.char,
    target_fg: mapping.fg,
    target_bg: mapping.bg,
    description: mapping.desc
  };
}
function buildManifest(assets, skinName, paletteName, resolution) {
  const palette = PALETTES[paletteName] || PALETTES.bbc_mode7;
  const mappings = assets.map((a) => guessCharMapping(a));
  const seen = /* @__PURE__ */ new Set();
  const unique = mappings.filter((m) => {
    const key = `${m.target_char}-${m.target_fg}`;
    if (seen.has(key)) return false;
    seen.add(key);
    return true;
  });
  const overrides = {
    header_row: { fg: 2, bg: 0, bold: true },
    hud_row: { fg: 3, bg: 0, bold: false },
    alert_row: { fg: 1, bg: 0, bold: true }
  };
  return {
    name: skinName,
    version: "1.0",
    palette,
    character_mappings: unique,
    teletext_overrides: overrides
  };
}
function generateYamlManifest(manifest) {
  const lines = [
    `# Auto-generated by SKIN-Weaver v1.0`,
    `skin:`,
    `  name: "${manifest.name}"`,
    `  version: "${manifest.version}"`,
    ``,
    `palette:`
  ];
  for (const [idx, color] of Object.entries(manifest.palette)) {
    lines.push(`  '${idx}': '${color}'`);
  }
  lines.push("");
  lines.push("character_mappings:");
  for (const m of manifest.character_mappings) {
    lines.push(`  - source: "${m.source}"`);
    lines.push(`    target_char: "${m.target_char}"`);
    lines.push(`    target_fg: ${m.target_fg}`);
    lines.push(`    target_bg: ${m.target_bg}`);
    lines.push(`    description: "${m.description}"`);
  }
  lines.push("");
  lines.push("teletext_overrides:");
  if (manifest.teletext_overrides.header_row) {
    const h = manifest.teletext_overrides.header_row;
    lines.push(`  header_row:`);
    lines.push(`    fg: ${h.fg}`);
    lines.push(`    bg: ${h.bg}`);
    lines.push(`    bold: ${h.bold || false}`);
  }
  if (manifest.teletext_overrides.hud_row) {
    const h = manifest.teletext_overrides.hud_row;
    lines.push(`  hud_row:`);
    lines.push(`    fg: ${h.fg}`);
    lines.push(`    bg: ${h.bg}`);
    lines.push(`    bold: ${h.bold || false}`);
  }
  if (manifest.teletext_overrides.alert_row) {
    const h = manifest.teletext_overrides.alert_row;
    lines.push(`  alert_row:`);
    lines.push(`    fg: ${h.fg}`);
    lines.push(`    bg: ${h.bg}`);
    lines.push(`    bold: ${h.bold || false}`);
  }
  return lines.join("\n") + "\n";
}
function generateJsonManifest(manifest) {
  return JSON.stringify(
    {
      generated_by: "SKIN-Weaver v1.0",
      skin: {
        name: manifest.name,
        version: manifest.version
      },
      palette: manifest.palette,
      character_mappings: manifest.character_mappings,
      teletext_overrides: manifest.teletext_overrides
    },
    null,
    2
  );
}
function skinWeaver(input) {
  const skinName = input.source_assets[0]?.path ? input.source_assets[0].path.split("/").filter((s) => !s.startsWith(".")).join("_").replace(/[_/]/g, "_").replace(/\.[^.]+$/, "").slice(0, 30) || "default_skin" : "default_skin";
  if (!/^[a-z]/i.test(skinName)) {
    const idx = skinName.search(/[a-z]/i);
    if (idx > 0) {
    }
  }
  const manifest = buildManifest(
    input.source_assets,
    `${skinName} (${input.target.locale})`,
    input.target.palette,
    input.target.resolution
  );
  const exportedAssets = input.source_assets.map((a) => ({
    source: a.path,
    output: `skins/${skinName}/chars/${a.path.split("/").pop() || "asset"}.json`
  }));
  return {
    skill: "SKIN-Weaver",
    version: "1.0",
    executed_at: (/* @__PURE__ */ new Date()).toISOString(),
    skin_name: skinName,
    manifest,
    exported_assets: exportedAssets
  };
}
function writeSkinManifest(output, outputDir, format = "yaml") {
  if (!existsSync3(outputDir)) {
    mkdirSync2(outputDir, { recursive: true });
  }
  const ext = format === "yaml" ? ".yaml" : ".json";
  const outPath = join3(outputDir, `${output.skin_name}.skin${ext}`);
  const content = format === "yaml" ? generateYamlManifest(output.manifest) : generateJsonManifest(output.manifest);
  writeFileSync2(outPath, content, "utf-8");
  return outPath;
}

// src/tools/mcp-scribe.ts
function generateStandardCommands(programName, memoryMap) {
  const prefix = programName.toLowerCase().replace(/[^a-z]/g, "_");
  const commands = [];
  const stateKeys = memoryMap.filter(
    (m) => /score|status|state|lives|level|time|health|energy|position|inventory|credits|ship/i.test(
      m.label
    ) && m.confidence >= 0.7
  ).map((m) => {
    return m.label.replace(/([a-z])([A-Z])/g, "$1_$2").toLowerCase().replace(/^_/, "");
  });
  const uniqueKeys = [...new Set(stateKeys)].slice(0, 10);
  commands.push({
    name: `${prefix}_save`,
    description: `Save current game state via LENS capture`,
    parameters: {
      slot: { type: "string", description: "Save slot name", default: "autosave" }
    },
    action: "lens_capture",
    payload: {
      target: "variables",
      scope: `${prefix}_save`,
      keys: uniqueKeys
    }
  });
  commands.push({
    name: `${prefix}_load`,
    description: `Restore saved game state`,
    parameters: {
      slot: { type: "string", description: "Save slot to load", default: "autosave" }
    },
    action: "lens_restore",
    payload: {
      target: "variables",
      scope: `${prefix}_save`,
      keys: uniqueKeys
    }
  });
  commands.push({
    name: `${prefix}_status`,
    description: `Query current game state`,
    parameters: {},
    action: "lens_query",
    payload: {
      extractor: `${prefix}_lens_extractor`,
      method: "capture_all"
    }
  });
  commands.push({
    name: `${prefix}_pause`,
    description: `Pause/resume game execution`,
    parameters: {},
    action: "emulator_control",
    payload: {
      command: "toggle_pause"
    }
  });
  const injectableFunctions = memoryMap.filter(
    (f) => /Dock|Jump|Launch|Title|Death|Win|Lose|Reset/i.test(f.label) && f.confidence >= 0.6
  ).slice(0, 5);
  for (const fn of injectableFunctions) {
    const actionName = fn.label.toLowerCase().replace(/[^a-z0-9]/g, "_");
    commands.push({
      name: `${prefix}_${actionName}`,
      description: fn.description || `Trigger ${fn.label}`,
      parameters: {},
      action: "mcp_inject",
      payload: {
        target: "6502_execute",
        address: fn.address,
        description: `Call ${fn.label} routine`
      }
    });
  }
  return commands;
}
function mcpScribe(input) {
  const memoryMap = input.source_miner_report.findings.memory_map || [];
  const commands = generateStandardCommands(input.program_name, memoryMap);
  return {
    skill: "MCP-Scribe",
    version: "1.0",
    executed_at: (/* @__PURE__ */ new Date()).toISOString(),
    program: input.program_name,
    commands
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
  },
  {
    name: "skin_weaver",
    description: "Convert original game assets to uCode SKIN manifest.",
    parameters: {
      assets_json: { type: "string", description: "JSON array of asset objects [{path, type, format?}]" },
      skin_name: { type: "string", description: "Name for the generated skin" },
      palette: { type: "string", description: "Palette: bbc_mode7, teletext_classic, dark_fantasy, repton_classic, elite_wireframe", default: "bbc_mode7" },
      output_dir: { type: "string", description: "Output directory for .skin.yaml manifest", default: "" }
    }
  },
  {
    name: "mcp_scribe",
    description: "Generate MCP command specifications from Source-Miner report.",
    parameters: {
      source_miner_json: { type: "string", description: "Source-Miner output as JSON string" },
      program_name: { type: "string", description: "Program name (e.g. Elite, Repton)" },
      program_type: { type: "string", description: "adapt-source, rewrite, port-c-to-basic, or rewrite_inspired_by", default: "adapt-source" }
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
  sourceMiner,
  lensCraft,
  skinWeaver,
  writeSkinManifest,
  mcpScribe,
  GRIDSMITH_TOOLS,
  createGridWorld,
  convertLatLonToUCode,
  convertUCodeToLatLon
};
