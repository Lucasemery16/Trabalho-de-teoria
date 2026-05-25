#!/usr/bin/env node
/** Benchmark experimental do Dijkstra (JavaScript) — 30 rodadas por cenário. */

import { performance } from "node:perf_hooks";
import { writeFileSync, mkdirSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

import { dijkstra } from "./dijkstra.js";
import {
  buildBestCase,
  buildAverageCase,
  buildWorstCase,
  edgeCount,
} from "./graphs.js";

const ROUNDS = 30;
const SIZES = {
  pequeno: 300,
  medio: 1500,
  grande: 4000,
};

const BUILDERS = {
  melhor: buildBestCase,
  medio: buildAverageCase,
  pior: buildWorstCase,
};

function mean(values) {
  return values.reduce((a, b) => a + b, 0) / values.length;
}

function stdev(values) {
  if (values.length < 2) return 0;
  const m = mean(values);
  const variance = values.reduce((s, x) => s + (x - m) ** 2, 0) / (values.length - 1);
  return Math.sqrt(variance);
}

function runSingle(graph, source = 0) {
  const start = performance.now();
  dijkstra(graph, source);
  return (performance.now() - start) / 1000;
}

function benchmarkCase(caseName, sizeLabel, n, rounds) {
  const builder = BUILDERS[caseName];
  const times = [];
  let edges = 0;

  for (let r = 0; r < rounds; r++) {
    const graph = builder(n, 42 + r);
    if (r === 0) edges = edgeCount(graph);
    times.push(runSingle(graph));
  }

  return {
    linguagem: "javascript",
    caso: caseName,
    tamanho: sizeLabel,
    n,
    arestas: edges,
    rodadas: rounds,
    media_s: mean(times),
    desvio_s: stdev(times),
    min_s: Math.min(...times),
    max_s: Math.max(...times),
  };
}

function toCsv(rows) {
  const headers = Object.keys(rows[0]);
  const lines = [headers.join(",")];
  for (const row of rows) {
    lines.push(headers.map((h) => row[h]).join(","));
  }
  return lines.join("\n");
}

function parseArgs() {
  const args = process.argv.slice(2);
  const opts = {
    output: join(dirname(fileURLToPath(import.meta.url)), "..", "data", "resultados_javascript.csv"),
    rounds: ROUNDS,
    quick: false,
  };
  for (let i = 0; i < args.length; i++) {
    if (args[i] === "--output" && args[i + 1]) opts.output = args[++i];
    else if (args[i] === "--rounds" && args[i + 1]) opts.rounds = Number(args[++i]);
    else if (args[i] === "--quick") opts.quick = true;
  }
  return opts;
}

function main() {
  const opts = parseArgs();
  const rounds = opts.quick ? 3 : opts.rounds;
  const sizes = opts.quick
    ? { pequeno: 100, medio: 400, grande: 800 }
    : SIZES;

  const rows = [];
  for (const caseName of ["melhor", "medio", "pior"]) {
    for (const [label, n] of Object.entries(sizes)) {
      console.log(`[JavaScript] ${caseName} / ${label} (n=${n}) — ${rounds} rodadas...`);
      rows.push(benchmarkCase(caseName, label, n, rounds));
    }
  }

  mkdirSync(dirname(opts.output), { recursive: true });
  writeFileSync(opts.output, toCsv(rows), "utf-8");
  console.log(`Resultados salvos em ${opts.output}`);
}

main();
