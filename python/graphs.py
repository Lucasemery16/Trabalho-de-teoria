"""Geração de grafos para cenários de melhor, médio e pior caso."""

from __future__ import annotations

import random
from typing import List, Tuple

Graph = List[List[Tuple[int, float]]]


def _empty_graph(n: int) -> Graph:
    return [[] for _ in range(n)]


def build_best_case(n: int, seed: int = 42) -> Graph:
    """
    Melhor caso: grafo estrela centrado na origem (vértice 0).
    Poucas arestas (E = n - 1), relaxações mínimas após a origem.
    """
    rng = random.Random(seed)
    graph = _empty_graph(n)
    for v in range(1, n):
        w = rng.uniform(1.0, 10.0)
        graph[0].append((v, w))
    return graph


def build_average_case(n: int, seed: int = 42) -> Graph:
    """
    Caso médio: grafo aleatório esparsificado (p ≈ 2 ln(n) / n).
    """
    rng = random.Random(seed)
    graph = _empty_graph(n)
    if n <= 1:
        return graph

    p = min(1.0, max(2.0 * __import__("math").log(n) / n, 8.0 / n))
    for u in range(n):
        for v in range(u + 1, n):
            if rng.random() < p:
                w = rng.uniform(1.0, 100.0)
                graph[u].append((v, w))
                graph[v].append((u, w))
    if not graph[0]:
        v = 1 if n > 1 else 0
        graph[0].append((v, 1.0))
    return graph


def build_worst_case(n: int, seed: int = 42) -> Graph:
    """
    Pior caso: grafo completo denso (E ≈ n(n-1)/2).
    Força o máximo de extrações e relaxações na fila de prioridade.
    """
    rng = random.Random(seed)
    graph = _empty_graph(n)
    for u in range(n):
        for v in range(u + 1, n):
            w = rng.uniform(1.0, 1000.0)
            graph[u].append((v, w))
            graph[v].append((u, w))
    return graph


def edge_count(graph: Graph) -> int:
    return sum(len(adj) for adj in graph) // 2
