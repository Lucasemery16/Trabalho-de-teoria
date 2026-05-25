/**
 * Algoritmo de Dijkstra com fila de prioridade (heap binário).
 * Complexidade: O((V + E) log V).
 */

class MinHeap {
  constructor() {
    this.data = [];
  }

  push(dist, vertex) {
    this.data.push([dist, vertex]);
    this._bubbleUp(this.data.length - 1);
  }

  pop() {
    if (this.data.length === 0) return null;
    const top = this.data[0];
    const last = this.data.pop();
    if (this.data.length > 0) {
      this.data[0] = last;
      this._sinkDown(0);
    }
    return top;
  }

  get size() {
    return this.data.length;
  }

  _bubbleUp(i) {
    while (i > 0) {
      const parent = (i - 1) >> 1;
      if (this.data[parent][0] <= this.data[i][0]) break;
      [this.data[parent], this.data[i]] = [this.data[i], this.data[parent]];
      i = parent;
    }
  }

  _sinkDown(i) {
    const n = this.data.length;
    while (true) {
      let smallest = i;
      const left = 2 * i + 1;
      const right = 2 * i + 2;
      if (left < n && this.data[left][0] < this.data[smallest][0]) smallest = left;
      if (right < n && this.data[right][0] < this.data[smallest][0]) smallest = right;
      if (smallest === i) break;
      [this.data[smallest], this.data[i]] = [this.data[i], this.data[smallest]];
      i = smallest;
    }
  }
}

/**
 * @param {Array<Array<{to: number, weight: number}>>} graph
 * @param {number} source
 * @returns {Float64Array}
 */
export function dijkstra(graph, source) {
  const n = graph.length;
  const dist = new Float64Array(n).fill(Infinity);
  dist[source] = 0;
  const heap = new MinHeap();
  heap.push(0, source);

  while (heap.size > 0) {
    const [d, u] = heap.pop();
    if (d > dist[u]) continue;
    for (const { to: v, weight: w } of graph[u]) {
      const nd = d + w;
      if (nd < dist[v]) {
        dist[v] = nd;
        heap.push(nd, v);
      }
    }
  }
  return dist;
}
