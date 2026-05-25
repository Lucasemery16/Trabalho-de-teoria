#!/usr/bin/env python3
"""Benchmark experimental do Dijkstra (Python) — 30 rodadas por cenário."""

from __future__ import annotations

import argparse
import csv
import statistics
import time
from pathlib import Path

from dijkstra import dijkstra
from graphs import build_average_case, build_best_case, build_worst_case, edge_count

ROUNDS = 30
SIZES = {
    "pequeno": 300,
    "medio": 1500,
    "grande": 4000,
}

BUILDERS = {
    "melhor": build_best_case,
    "medio": build_average_case,
    "pior": build_worst_case,
}


def run_single(graph, source: int = 0) -> float:
    start = time.perf_counter()
    dijkstra(graph, source)
    return time.perf_counter() - start


def benchmark_case(case: str, size_label: str, n: int, rounds: int) -> dict:
    builder = BUILDERS[case]
    times = []
    edges = 0
    for r in range(rounds):
        graph = builder(n, seed=42 + r)
        if r == 0:
            edges = edge_count(graph)
        times.append(run_single(graph))

    return {
        "linguagem": "python",
        "caso": case,
        "tamanho": size_label,
        "n": n,
        "arestas": edges,
        "rodadas": rounds,
        "media_s": statistics.mean(times),
        "desvio_s": statistics.stdev(times) if len(times) > 1 else 0.0,
        "min_s": min(times),
        "max_s": max(times),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Benchmark Dijkstra (Python)")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).resolve().parent.parent / "data" / "resultados_python.csv",
    )
    parser.add_argument("--rounds", type=int, default=ROUNDS)
    parser.add_argument("--quick", action="store_true", help="3 rodadas e tamanhos reduzidos")
    args = parser.parse_args()

    rounds = 3 if args.quick else args.rounds
    sizes = {"pequeno": 100, "medio": 400, "grande": 800} if args.quick else SIZES

    args.output.parent.mkdir(parents=True, exist_ok=True)
    rows = []
    for case in ("melhor", "medio", "pior"):
        for label, n in sizes.items():
            print(f"[Python] {case} / {label} (n={n}) — {rounds} rodadas...")
            rows.append(benchmark_case(case, label, n, rounds))

    fieldnames = list(rows[0].keys())
    with args.output.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Resultados salvos em {args.output}")


if __name__ == "__main__":
    main()
