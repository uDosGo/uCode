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

// src/index.ts
var import_gridcore = require("@udos/gridcore");

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

// src/index.ts
var GRIDSMITH_TOOLS = [
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
      data: { type: "object", description: "Cell payload" }
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
  const grid = (0, import_gridcore.createGrid)(cols, rows);
  return {
    cols: grid.cols,
    rows: grid.rows,
    cellCount: (0, import_gridcore.listCells)(grid).length
  };
}
function convertLatLonToUCode(lat, lon, level = 340) {
  return (0, import_gridcore.latLonToUCode)(lat, lon, level);
}
function convertUCodeToLatLon(coord) {
  return (0, import_gridcore.uCodeToLatLon)(coord);
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
      "  grid create --cols 80 --rows 24",
      "  location latlon-to-ucode --lat -33.8688 --lon 151.2093 --level 340",
      "  location ucode-to-latlon --coord L340-0A0B-0000-0"
    ].join("\n") + "\n"
  );
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
  if (section === "grid" && action === "create") {
    const cols = Number(argValue(args, "--cols", "80"));
    const rows = Number(argValue(args, "--rows", "24"));
    printJson({ grid: createGridWorld(cols, rows) });
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
