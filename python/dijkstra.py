"""Algoritmo de Dijkstra com fila de prioridade (heap binário)."""

from __future__ import annotations

import heapq
from typing import List, Tuple

Graph = List[List[Tuple[int, float]]]


def dijkstra(graph: Graph, source: int) -> List[float]:
    """
    Calcula distâncias mínimas da origem para todos os vértices.

    Complexidade: O((V + E) log V) com heap binário.
    """
    n = len(graph)
    dist = [float("inf")] * n
    dist[source] = 0.0
    heap: List[Tuple[float, int]] = [(0.0, source)]

    while heap:
        d, u = heapq.heappop(heap)
        if d > dist[u]:
            continue
        for v, w in graph[u]:
            nd = d + w
            if nd < dist[v]:
                dist[v] = nd
                heapq.heappush(heap, (nd, v))

    return dist
