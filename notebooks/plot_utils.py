"""Funções de gráficos usadas pelo notebook de análise."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

SIZE_ORDER = ["pequeno", "medio", "grande"]

CASE_LABELS = {
    "melhor": "Melhor caso (grafo estrela)",
    "medio": "Caso médio (grafo aleatório esparsificado)",
    "pior": "Pior caso (grafo completo)",
}


def find_project_root() -> Path:
    cwd = Path.cwd().resolve()
    for candidate in (cwd, cwd.parent):
        if (candidate / "data").is_dir():
            return candidate
    return cwd


def theoretical_time(n: np.ndarray, edges: np.ndarray) -> np.ndarray:
    n = np.asarray(n, dtype=float)
    edges = np.asarray(edges, dtype=float)
    return (n + edges) * np.log2(np.maximum(n, 2))


def fit_constant(measured: np.ndarray, n: np.ndarray, edges: np.ndarray) -> float:
    model = theoretical_time(n, edges)
    mask = model > 0
    if not np.any(mask):
        return 1.0
    return float(np.mean(measured[mask] / model[mask]))


def load_results(data_dir: Path) -> pd.DataFrame:
    frames = []
    for name in ("resultados_python.csv", "resultados_javascript.csv"):
        path = data_dir / name
        if path.exists():
            frames.append(pd.read_csv(path))
    if not frames:
        raise FileNotFoundError(
            f"CSVs não encontrados em {data_dir}. "
            "Execute python/benchmark.py e npm run benchmark antes."
        )
    df = pd.concat(frames, ignore_index=True)
    df["tamanho"] = pd.Categorical(df["tamanho"], categories=SIZE_ORDER, ordered=True)
    return df.sort_values(["caso", "linguagem", "tamanho"])


def plot_case(
    df: pd.DataFrame,
    caso: str,
    *,
    use_log: bool = False,
    ax: plt.Axes | None = None,
) -> plt.Figure:
    subset = df[df["caso"] == caso]
    n_vals = subset["n"].unique()
    n_smooth = np.linspace(n_vals.min(), n_vals.max(), 200)

    if ax is None:
        fig, ax = plt.subplots(figsize=(9, 5.5))
    else:
        fig = ax.figure

    for lang in subset["linguagem"].unique():
        lang_df = subset[subset["linguagem"] == lang].sort_values("n")
        n = lang_df["n"].to_numpy()
        media = lang_df["media_s"].to_numpy()
        desvio = lang_df["desvio_s"].to_numpy()
        edges = lang_df["arestas"].to_numpy()
        label = "Python" if lang == "python" else "JavaScript"

        ax.errorbar(
            n, media, yerr=desvio, fmt="o-", capsize=4, linewidth=1.5,
            markersize=7, label=f"{label} (medido)",
        )
        c = fit_constant(media, n, edges)
        edges_smooth = np.interp(n_smooth, n, edges)
        teorico = c * theoretical_time(n_smooth, edges_smooth)
        ax.plot(
            n_smooth, teorico, "--", linewidth=1.8, alpha=0.85,
            label=f"{label} — O((V+E) log V)",
        )

    ax.set_xlabel("Tamanho da entrada (n — vértices)")
    ax.set_ylabel("Tempo médio de execução (s)")
    ax.set_title(CASE_LABELS.get(caso, caso))
    ax.legend(loc="best", fontsize=8)
    ax.grid(True, alpha=0.3)
    if use_log:
        ax.set_xscale("log")
        ax.set_yscale("log")
    fig.tight_layout()
    return fig


def comparison_table(df: pd.DataFrame) -> pd.DataFrame:
    table = df.copy()
    table["tempo_ms"] = table["media_s"] * 1000
    table["desvio_ms"] = table["desvio_s"] * 1000
    table["formatado"] = table.apply(
        lambda r: f"{r['tempo_ms']:.3f} ± {r['desvio_ms']:.3f}", axis=1
    )
    rows = []
    for keys, group in table.groupby(["caso", "tamanho", "n", "arestas"], observed=True):
        caso, tamanho, n, arestas = keys
        py = group.loc[group["linguagem"] == "python", "formatado"]
        js = group.loc[group["linguagem"] == "javascript", "formatado"]
        rows.append({
            "Caso": caso,
            "Tamanho": tamanho,
            "n": n,
            "Arestas": arestas,
            "Python (ms)": py.iloc[0] if len(py) else "—",
            "JavaScript (ms)": js.iloc[0] if len(js) else "—",
        })
    return pd.DataFrame(rows)
