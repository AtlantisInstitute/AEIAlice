#!/usr/bin/env node
/**
 * Safe MCP Memory Server Wrapper
 *
 * Patches @modelcontextprotocol/server-memory with:
 *  1. A write mutex so concurrent saveGraph() calls don't race on the file
 *  2. Resilient loadGraph() that skips corrupted JSON lines instead of crashing
 *
 * Root cause: when the LLM dispatches create_entities + create_relations in
 * the same turn, OpenClaw calls both tools in parallel. The upstream server
 * uses bare fs.writeFile() with no locking, so the two writes interleave and
 * corrupt the JSONL file. Once corrupted, JSON.parse throws on every load
 * and all memory tools silently fail forever.
 *
 * Usage in openclaw.json:
 *   "memory": {
 *     "command": "node",
 *     "args": ["/Users/danielvargas/Documents/Alice/scripts/memory-server-safe.mjs"],
 *     "env": { "MEMORY_FILE_PATH": "..." }
 *   }
 */

import { promises as fs } from "node:fs";

// --- Async mutex: serializes all file writes ---
let locked = false;
const queue = [];

function acquireLock() {
  return new Promise((resolve) => {
    if (!locked) {
      locked = true;
      resolve();
    } else {
      queue.push(resolve);
    }
  });
}

function releaseLock() {
  if (queue.length > 0) {
    const next = queue.shift();
    next();
  } else {
    locked = false;
  }
}

// --- Resolve the upstream module path so we can patch before main() runs ---
const upstreamPath = import.meta.resolve(
  "@modelcontextprotocol/server-memory/dist/index.js"
);

// Dynamically read and patch the upstream module's prototype before it starts.
// We import it, patch the class, then let main() proceed.
const upstream = await import(upstreamPath);
const KnowledgeGraphManager = upstream.KnowledgeGraphManager;

// Save reference to original methods
const originalSaveGraph = KnowledgeGraphManager.prototype.saveGraph;
const originalLoadGraph = KnowledgeGraphManager.prototype.loadGraph;

// Patch saveGraph with mutex
KnowledgeGraphManager.prototype.saveGraph = async function (graph) {
  await acquireLock();
  try {
    return await originalSaveGraph.call(this, graph);
  } finally {
    releaseLock();
  }
};

// Patch loadGraph to be resilient to corrupted lines
KnowledgeGraphManager.prototype.loadGraph = async function () {
  try {
    return await originalLoadGraph.call(this);
  } catch (error) {
    if (error instanceof SyntaxError) {
      // File has corrupted JSON lines — recover what we can
      process.stderr.write(
        `[memory-server-safe] Detected corrupted memory file, attempting recovery...\n`
      );
      try {
        const data = await fs.readFile(this.memoryFilePath, "utf-8");
        const lines = data.split("\n").filter((line) => line.trim() !== "");
        const graph = { entities: [], relations: [] };
        let skipped = 0;
        for (const line of lines) {
          try {
            const item = JSON.parse(line);
            if (item.type === "entity") {
              graph.entities.push({
                name: item.name,
                entityType: item.entityType,
                observations: item.observations,
              });
            }
            if (item.type === "relation") {
              graph.relations.push({
                from: item.from,
                to: item.to,
                relationType: item.relationType,
              });
            }
          } catch {
            skipped++;
            process.stderr.write(
              `[memory-server-safe] Skipping corrupted line: ${line.slice(0, 100)}...\n`
            );
          }
        }
        // Re-save the clean graph to repair the file
        await originalSaveGraph.call(this, graph);
        process.stderr.write(
          `[memory-server-safe] Repaired memory file: ${graph.entities.length} entities, ${graph.relations.length} relations (${skipped} corrupted lines removed)\n`
        );
        return graph;
      } catch (readError) {
        if (readError.code === "ENOENT") {
          return { entities: [], relations: [] };
        }
        throw readError;
      }
    }
    throw error;
  }
};

process.stderr.write("[memory-server-safe] Write mutex and corruption recovery active\n");

// The upstream module's main() already ran when we imported it above.
// The patched prototypes are in effect for all subsequent tool calls.
