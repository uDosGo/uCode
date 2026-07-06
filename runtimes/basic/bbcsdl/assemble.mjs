#!/usr/bin/env node

import { copyFileSync, mkdirSync, readdirSync, statSync } from "node:fs";
import { join } from "node:path";

const BBCSDL_CANDIDATES = [
  "/usr/local/bin/bbcsdl",
  "/opt/homebrew/bin/bbcsdl",
  "/usr/bin/bbcsdl",
];

const ROOT = new URL(".", import.meta.url).pathname;

function findBinary() {
  for (const candidate of BBCSDL_CANDIDATES) {
    try {
      if (statSync(candidate).isFile()) return candidate;
    } catch {}
  }
  console.error("BBCSDL binary not found in standard locations.");
  console.error("Set BBCOUT_BBCSDL_PATH env var or install bbcsdl first.");
  process.exit(1);
}

function assemble() {
  // Find and copy the binary
  const binPath = process.env.BBCSDL_PATH || findBinary();
  const destBin = join(ROOT, "bbcsdl");
  copyFileSync(binPath, destBin);
  console.log(`Copied ${binPath} -> ${destBin}`);

  // Copy standard library
  const libSrc = process.env.BBCSDL_LIB_PATH || "/usr/local/share/bbcsdl/lib";
  const libDest = join(ROOT, "lib");
  try {
    mkdirSync(libDest, { recursive: true });
    const entries = readdirSync(libSrc);
    for (const entry of entries) {
      const src = join(libSrc, entry);
      const dest = join(libDest, entry);
      if (statSync(src).isFile()) {
        copyFileSync(src, dest);
      }
    }
    console.log(`Copied ${entries.length} library files to ${libDest}`);
  } catch {
    console.error(`BBCSDL library not found at ${libSrc}.`);
    console.error("Set BBCOUT_BBCOUT_LIB_PATH to the correct path.");
    process.exit(1);
  }

  console.log("\nAssembly complete. runtimes/basic/bbcsdl/ is ready.");
}

assemble();