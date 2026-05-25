/** Geração de grafos para melhor, médio e pior caso. */

function mulberry32(seed) {
  return function next() {
    let t = (seed += 0x6d2b79f5);
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

function emptyGraph(n) {
  return Array.from({ length: n }, () => []);
}

function addUndirectedEdge(graph, u, v, weight) {
  graph[u].push({ to: v, weight });
  graph[v].push({ to: u, weight });
}

/** Melhor caso: grafo estrela na origem (vértice 0). */
export function buildBestCase(n, seed = 42) {
  const rng = mulberry32(seed);
  const graph = emptyGraph(n);
  for (let v = 1; v < n; v++) {
    addUndirectedEdge(graph, 0, v, 1 + rng() * 9);
  }
  return graph;
}

/** Caso médio: grafo aleatório esparsificado. */
export function buildAverageCase(n, seed = 42) {
  const rng = mulberry32(seed);
  const graph = emptyGraph(n);
  if (n <= 1) return graph;

  const p = Math.min(1, Math.max((2 * Math.log(n)) / n, 8 / n));
  for (let u = 0; u < n; u++) {
    for (let v = u + 1; v < n; v++) {
      if (rng() < p) {
        addUndirectedEdge(graph, u, v, 1 + rng() * 99);
      }
    }
  }
  if (graph[0].length === 0 && n > 1) {
    addUndirectedEdge(graph, 0, 1, 1);
  }
  return graph;
}

/** Pior caso: grafo completo denso. */
export function buildWorstCase(n, seed = 42) {
  const rng = mulberry32(seed);
  const graph = emptyGraph(n);
  for (let u = 0; u < n; u++) {
    for (let v = u + 1; v < n; v++) {
      addUndirectedEdge(graph, u, v, 1 + rng() * 999);
    }
  }
  return graph;
}

export function edgeCount(graph) {
  return graph.reduce((sum, adj) => sum + adj.length, 0) / 2;
}
