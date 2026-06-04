"""Funções de gráficos e análise do benchmark Dijkstra."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

SIZE_ORDER = ["pequeno", "medio", "grande"]
CASE_ORDER = ["melhor", "medio", "pior"]

CASE_LABELS = {
    "melhor": "Melhor caso (grafo estrela)",
    "medio": "Caso médio (grafo aleatório esparsificado)",
    "pior": "Pior caso (grafo completo)",
}

LANG_LABELS = {"python": "Python", "javascript": "JavaScript"}
PALETTE = {"python": "#2563eb", "javascript": "#ea580c"}



def find_project_root() -> Path:
    cwd = Path.cwd().resolve()
    for candidate in (cwd, cwd.parent):
        if (candidate / "data").is_dir():
            return candidate
    return cwd


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


def theoretical_time(n, edges):
    n = np.asarray(n, dtype=float)
    edges = np.asarray(edges, dtype=float)
    return (n + edges) * np.log2(np.maximum(n, 2))


def fit_constant(measured, n, edges):
    model = theoretical_time(n, edges)
    mask = model > 0
    if not np.any(mask):
        return 1.0
    return float(np.mean(measured[mask] / model[mask]))


def enrich_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["n"] = out["n"].astype(int)
    out["arestas"] = out["arestas"].astype(int)
    if "densidade" not in out.columns:
        denom = np.maximum(out["n"] * (out["n"] - 1), 1)
        out["densidade"] = out["arestas"] / denom
    if "cv" not in out.columns and "desvio_s" in out.columns:
        out["cv"] = out["desvio_s"] / out["media_s"].replace(0, np.nan)
    if "tempo_ms" not in out.columns:
        out["tempo_ms"] = out["media_s"] * 1000
    if "tempo_por_aresta_us" not in out.columns:
        out["tempo_por_aresta_us"] = (out["media_s"] / out["arestas"].replace(0, np.nan)) * 1e6
    if "throughput_arestas_s" not in out.columns:
        out["throughput_arestas_s"] = out["arestas"] / out["media_s"].replace(0, np.nan)
    if "modelo_teorico" not in out.columns:
        out["modelo_teorico"] = theoretical_time(out["n"].to_numpy(), out["arestas"].to_numpy())
    out["razao_empirico_teorico"] = out["media_s"] / out["modelo_teorico"].replace(0, np.nan)
    out["tamanho"] = pd.Categorical(out["tamanho"], categories=SIZE_ORDER, ordered=True)
    return out.sort_values(["caso", "linguagem", "tamanho"])


def load_rounds(data_dir: Path):
    frames = []
    for name in ("rodadas_python.csv", "rodadas_javascript.csv"):
        path = data_dir / name
        if path.exists():
            frames.append(pd.read_csv(path))
    return pd.concat(frames, ignore_index=True) if frames else None


def comparison_table(df):
    table = df.copy()
    table["formatado"] = table.apply(
        lambda r: f"{r['tempo_ms']:.3f} ± {r.get('desvio_s', 0) * 1000:.3f}", axis=1
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


def metrics_summary_table(df):
    cols = [
        c
        for c in [
            "linguagem",
            "caso",
            "tamanho",
            "n",
            "arestas",
            "rodadas",
            "media_s",
            "mediana_s",
            "desvio_s",
            "min_s",
            "max_s",
            "p25_s",
            "p75_s",
            "p95_s",
            "cv",
            "densidade",
            "tempo_por_aresta_us",
            "throughput_arestas_s",
            "razao_empirico_teorico",
        ]
        if c in df.columns
    ]
    view = df[cols].copy()
    for c in ("media_s", "mediana_s", "desvio_s", "min_s", "max_s", "p25_s", "p75_s", "p95_s"):
        if c in view.columns:
            view[c] = view[c].map(lambda x: f"{x * 1000:.4f} ms" if pd.notna(x) else "—")
    if "cv" in view.columns:
        view["cv"] = view["cv"].map(lambda x: f"{x:.3f}" if pd.notna(x) else "—")
    if "densidade" in view.columns:
        view["densidade"] = view["densidade"].map(lambda x: f"{x:.6f}" if pd.notna(x) else "—")
    return view


def plot_case(df, caso, *, use_log=False, ax=None):
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
        desvio = lang_df["desvio_s"].to_numpy() if "desvio_s" in lang_df else np.zeros_like(media)
        edges = lang_df["arestas"].to_numpy()
        label = LANG_LABELS.get(lang, lang)
        ax.errorbar(
            n,
            media,
            yerr=desvio,
            fmt="o-",
            capsize=4,
            linewidth=1.5,
            markersize=7,
            color=PALETTE.get(lang),
            label=f"{label} (medido)",
        )
        c = fit_constant(media, n, edges)
        edges_smooth = np.interp(n_smooth, n, edges)
        ax.plot(
            n_smooth,
            c * theoretical_time(n_smooth, edges_smooth),
            "--",
            linewidth=1.8,
            alpha=0.85,
            color=PALETTE.get(lang),
            label=f"{label} — O((V+E) log V)",
        )
    ax.set_xlabel("n (vértices)")
    ax.set_ylabel("Tempo médio (s)")
    ax.set_title(CASE_LABELS.get(caso, caso))
    ax.legend(loc="best", fontsize=8)
    ax.grid(True, alpha=0.3)
    if use_log:
        ax.set_xscale("log")
        ax.set_yscale("log")
    fig.tight_layout()
    return fig


def plot_interval_range(df, caso, ax=None):
    subset = df[df["caso"] == caso].sort_values(["linguagem", "n"])
    if ax is None:
        fig, ax = plt.subplots(figsize=(10, 5))
    else:
        fig = ax.figure
    x_labels = []
    positions = []
    pos = 0
    pct_cols = ["min_s", "p25_s", "mediana_s", "p75_s", "max_s"]
    has_pct = all(c in subset.columns for c in pct_cols)
    for lang in subset["linguagem"].unique():
        lang_df = subset[subset["linguagem"] == lang]
        for _, row in lang_df.iterrows():
            x_labels.append(f"{LANG_LABELS.get(lang, lang)}\n{row['tamanho']}\nn={row['n']}")
            color = PALETTE.get(lang, "#888")
            if has_pct:
                y = [row[c] * 1000 for c in pct_cols]
                ax.plot([pos + j * 0.08 for j in range(len(pct_cols))], y, "o-", color=color, alpha=0.75)
                ax.vlines(pos, row["min_s"] * 1000, row["max_s"] * 1000, color=color, linewidth=2, alpha=0.4)
            else:
                ax.errorbar(
                    pos,
                    row["media_s"] * 1000,
                    yerr=row.get("desvio_s", 0) * 1000,
                    fmt="D",
                    color=color,
                    capsize=5,
                )
            positions.append(pos)
            pos += 1
    ax.set_xticks(positions)
    ax.set_xticklabels(x_labels, fontsize=7)
    ax.set_ylabel("Tempo (ms)")
    ax.set_title(f"Dispersão empírica — {CASE_LABELS.get(caso, caso)}")
    ax.grid(True, axis="y", alpha=0.3)
    fig.tight_layout()
    return fig


def _pivot_metric(df, value_col, lang):
    sub = df[df["linguagem"] == lang]
    pivot = sub.pivot(index="caso", columns="tamanho", values=value_col)
    return pivot.reindex(CASE_ORDER).reindex(columns=SIZE_ORDER)


def plot_heatmap_times(df, lang, ax=None):
    pivot = _pivot_metric(df, "tempo_ms", lang)
    if ax is None:
        fig, ax = plt.subplots(figsize=(5.5, 3.8))
    else:
        fig = ax.figure
    im = ax.imshow(pivot.to_numpy(), aspect="auto", cmap="YlOrRd")
    ax.set_xticks(range(len(SIZE_ORDER)))
    ax.set_xticklabels(SIZE_ORDER)
    ax.set_yticks(range(len(CASE_ORDER)))
    ax.set_yticklabels(CASE_ORDER)
    ax.set_title(f"Tempo médio (ms) — {LANG_LABELS.get(lang, lang)}")
    for i in range(pivot.shape[0]):
        for j in range(pivot.shape[1]):
            val = pivot.iloc[i, j]
            if pd.notna(val):
                ax.text(j, i, f"{val:.2f}", ha="center", va="center", fontsize=8)
    fig.colorbar(im, ax=ax, fraction=0.046)
    fig.tight_layout()
    return fig


def plot_speedup_heatmap(df, ax=None):
    py = df[df["linguagem"] == "python"][["caso", "tamanho", "media_s"]].rename(columns={"media_s": "py"})
    js = df[df["linguagem"] == "javascript"][["caso", "tamanho", "media_s"]].rename(columns={"media_s": "js"})
    merged = py.merge(js, on=["caso", "tamanho"], how="inner")
    merged["speedup"] = merged["py"] / merged["js"].replace(0, np.nan)
    pivot = merged.pivot(index="caso", columns="tamanho", values="speedup").reindex(CASE_ORDER).reindex(columns=SIZE_ORDER)
    if ax is None:
        fig, ax = plt.subplots(figsize=(6, 3.8))
    else:
        fig = ax.figure
    im = ax.imshow(pivot.to_numpy(), aspect="auto", cmap="RdYlGn", vmin=0.5, vmax=2.5)
    ax.set_xticks(range(len(SIZE_ORDER)))
    ax.set_xticklabels(SIZE_ORDER)
    ax.set_yticks(range(len(CASE_ORDER)))
    ax.set_yticklabels(CASE_ORDER)
    ax.set_title("Speedup Python/JS (>1 = JS mais rápido)")
    for i in range(pivot.shape[0]):
        for j in range(pivot.shape[1]):
            val = pivot.iloc[i, j]
            if pd.notna(val):
                ax.text(j, i, f"{val:.2f}x", ha="center", va="center", fontsize=8)
    fig.colorbar(im, ax=ax, fraction=0.046)
    fig.tight_layout()
    return fig


def _scatter_by_case(df, x_col, y_col, title, xlabel, ylabel, loglog=True, ax=None):
    if ax is None:
        fig, ax = plt.subplots(figsize=(9, 5.5))
    else:
        fig = ax.figure
    for caso in CASE_ORDER:
        for lang in df["linguagem"].unique():
            sub = df[(df["caso"] == caso) & (df["linguagem"] == lang)]
            if sub.empty:
                continue
            ax.scatter(
                sub[x_col],
                sub[y_col],
                s=70,
                alpha=0.85,
                label=f"{caso} — {LANG_LABELS.get(lang, lang)}",
            )
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    if loglog:
        ax.set_xscale("log")
        ax.set_yscale("log")
    ax.legend(fontsize=7, loc="best")
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    return fig


def plot_tempo_vs_arestas(df, ax=None):
    return _scatter_by_case(
        df, "arestas", "media_s", "Tempo vs arestas (log-log)", "Arestas (E)", "Tempo médio (s)", ax=ax
    )


def plot_tempo_vs_densidade(df, ax=None):
    return _scatter_by_case(
        df,
        "densidade",
        "media_s",
        "Tempo vs densidade do grafo",
        "Densidade E/(V(V-1))",
        "Tempo médio (s)",
        loglog=False,
        ax=ax,
    )


def plot_throughput(df, ax=None):
    if "throughput_arestas_s" not in df.columns:
        return None
    if ax is None:
        fig, ax = plt.subplots(figsize=(9, 5))
    else:
        fig = ax.figure
    for caso in CASE_ORDER:
        sub = df[df["caso"] == caso]
        for lang in sub["linguagem"].unique():
            s = sub[sub["linguagem"] == lang].sort_values("n")
            ax.plot(
                s["n"],
                s["throughput_arestas_s"],
                "o-",
                label=f"{caso} — {LANG_LABELS.get(lang, lang)}",
            )
    ax.set_xlabel("n")
    ax.set_ylabel("Arestas / segundo")
    ax.set_title("Throughput (arestas processadas por segundo)")
    ax.set_xscale("log")
    ax.legend(fontsize=7)
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    return fig


def plot_coeficiente_variacao(df, ax=None):
    if "cv" not in df.columns:
        return None
    if ax is None:
        fig, ax = plt.subplots(figsize=(9, 5))
    else:
        fig = ax.figure
    x = np.arange(len(df))
    colors = [PALETTE.get(lang, "#666") for lang in df["linguagem"]]
    ax.bar(x, df["cv"], color=colors, alpha=0.8)
    ax.set_xticks(x)
    ax.set_xticklabels(
        [
            f"{r['caso']}/{r['tamanho']}\n{LANG_LABELS.get(r['linguagem'], r['linguagem'])}"
            for _, r in df.iterrows()
        ],
        rotation=45,
        ha="right",
        fontsize=7,
    )
    ax.set_ylabel("Coeficiente de variação (σ/μ)")
    ax.set_title("Estabilidade das rodadas (menor = mais estável)")
    ax.grid(True, axis="y", alpha=0.3)
    fig.tight_layout()
    return fig


def plot_comparison_bars(df, ax=None):
    if ax is None:
        fig, ax = plt.subplots(figsize=(11, 5))
    else:
        fig = ax.figure
    labels, py_vals, js_vals = [], [], []
    for keys, g in df.groupby(["caso", "tamanho"], observed=True):
        caso, tam = keys
        py = g.loc[g["linguagem"] == "python", "media_s"]
        js = g.loc[g["linguagem"] == "javascript", "media_s"]
        if len(py) and len(js):
            labels.append(f"{caso}\n{tam}")
            py_vals.append(py.iloc[0] * 1000)
            js_vals.append(js.iloc[0] * 1000)
    x = np.arange(len(labels))
    w = 0.35
    ax.bar(x - w / 2, py_vals, w, label="Python", color=PALETTE["python"])
    ax.bar(x + w / 2, js_vals, w, label="JavaScript", color=PALETTE["javascript"])
    ax.set_yscale("log")
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=8)
    ax.set_ylabel("Tempo médio (ms)")
    ax.set_title("Comparação direta Python vs JavaScript")
    ax.legend()
    ax.grid(True, axis="y", alpha=0.3)
    fig.tight_layout()
    return fig


def plot_residual_model(df, ax=None):
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    langs = list(df["linguagem"].unique())[:2]
    for i, lang in enumerate(langs):
        sub = df[df["linguagem"] == lang].copy()
        c = fit_constant(sub["media_s"].to_numpy(), sub["n"].to_numpy(), sub["arestas"].to_numpy())
        pred = c * sub["modelo_teorico"]
        resid = sub["media_s"] - pred
        axes[i].scatter(pred, resid, c=PALETTE.get(lang, "#333"), s=60, alpha=0.85)
        axes[i].axhline(0, color="gray", linestyle="--")
        axes[i].set_xlabel("Tempo previsto pelo modelo")
        axes[i].set_ylabel("Resíduo (medido − previsto)")
        axes[i].set_title(f"Resíduos — {LANG_LABELS.get(lang, lang)}")
        axes[i].grid(True, alpha=0.3)
    fig.suptitle("Aderência a O((V+E) log V)", y=1.02)
    fig.tight_layout()
    return fig


def plot_rounds_distribution(rounds_df, ax=None):
    if rounds_df is None or rounds_df.empty:
        if ax is None:
            fig, ax = plt.subplots(figsize=(8, 4))
            ax.text(
                0.5,
                0.5,
                "Sem rodadas_python.csv\nExecute: python3 python/benchmark.py",
                ha="center",
                va="center",
                transform=ax.transAxes,
            )
            ax.set_axis_off()
            return fig
        return None
    if ax is None:
        fig, ax = plt.subplots(figsize=(10, 5))
    else:
        fig = ax.figure
    col = "tempo_s" if "tempo_s" in rounds_df.columns else rounds_df.columns[-1]
    for (caso, tam), g in rounds_df.groupby(["caso", "tamanho"], observed=True):
        ax.hist(g[col], bins=12, alpha=0.5, label=f"{caso}/{tam}")
    ax.set_xlabel("Tempo por rodada (s)")
    ax.set_title("Distribuição das rodadas individuais")
    ax.legend(fontsize=7)
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    return fig


def plot_dashboard(df, ax=None):
    fig, axes = plt.subplots(2, 3, figsize=(14, 8))
    plot_case(df, "melhor", ax=axes[0, 0])
    plot_case(df, "pior", ax=axes[0, 1])
    plot_speedup_heatmap(df, ax=axes[0, 2])
    plot_tempo_vs_arestas(df, ax=axes[1, 0])
    if "cv" in df.columns:
        plot_coeficiente_variacao(df, ax=axes[1, 1])
    else:
        axes[1, 1].set_visible(False)
    plot_comparison_bars(df, ax=axes[1, 2])
    fig.suptitle("Painel resumo — Dijkstra Python vs JavaScript", fontsize=13, y=1.01)
    fig.tight_layout()
    return fig


def plot_correlacao(df, ax=None):
    num_cols = [
        c
        for c in [
            "n",
            "arestas",
            "densidade",
            "media_s",
            "mediana_s",
            "desvio_s",
            "cv",
            "tempo_por_aresta_us",
            "throughput_arestas_s",
            "modelo_teorico",
        ]
        if c in df.columns
    ]
    if len(num_cols) < 3:
        return None
    corr = df[num_cols].corr()
    if ax is None:
        fig, ax = plt.subplots(figsize=(8, 6))
    else:
        fig = ax.figure
    im = ax.imshow(corr.to_numpy(), cmap="coolwarm", vmin=-1, vmax=1)
    ax.set_xticks(range(len(num_cols)))
    ax.set_yticks(range(len(num_cols)))
    ax.set_xticklabels(num_cols, rotation=45, ha="right", fontsize=8)
    ax.set_yticklabels(num_cols, fontsize=8)
    for i in range(len(num_cols)):
        for j in range(len(num_cols)):
            ax.text(j, i, f"{corr.iloc[i, j]:.2f}", ha="center", va="center", fontsize=7)
    ax.set_title("Matriz de correlação (métricas numéricas)")
    fig.colorbar(im, ax=ax, fraction=0.046)
    fig.tight_layout()
    return fig


def plot_mediana_vs_media(df, ax=None):
    if "mediana_s" not in df.columns:
        return None
    if ax is None:
        fig, ax = plt.subplots(figsize=(7, 6))
    else:
        fig = ax.figure
    for lang in df["linguagem"].unique():
        sub = df[df["linguagem"] == lang]
        ax.scatter(
            sub["media_s"] * 1000,
            sub["mediana_s"] * 1000,
            s=80,
            label=LANG_LABELS.get(lang, lang),
            color=PALETTE.get(lang),
        )
    lims = ax.get_xlim()
    ax.plot(lims, lims, "k--", alpha=0.4, label="y = x")
    ax.set_xlabel("Média (ms)")
    ax.set_ylabel("Mediana (ms)")
    ax.set_title("Mediana vs média — assimetria / outliers")
    ax.legend()
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    return fig


def plot_fator_crescimento(df, ax=None):
    if ax is None:
        fig, ax = plt.subplots(figsize=(9, 5))
    else:
        fig = ax.figure
    for (caso, lang), g in df.groupby(["caso", "linguagem"], observed=True):
        g = g.sort_values("n")
        if len(g) < 2:
            continue
        ratios = g["media_s"].iloc[1:].to_numpy() / g["media_s"].iloc[:-1].to_numpy()
        labels = [f"{a}→{b}" for a, b in zip(g["tamanho"].iloc[:-1], g["tamanho"].iloc[1:])]
        ax.plot(labels, ratios, "o-", label=f"{caso} — {LANG_LABELS.get(lang, lang)}")
    ax.axhline(1, color="gray", linestyle=":")
    ax.set_ylabel("Fator (tempo maior / tempo menor)")
    ax.set_title("Crescimento entre tamanhos consecutivos")
    ax.legend(fontsize=7)
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    return fig


def plot_tempo_por_aresta(df, ax=None):
    if "tempo_por_aresta_us" not in df.columns:
        return None
    if ax is None:
        fig, ax = plt.subplots(figsize=(9, 5))
    else:
        fig = ax.figure
    for caso in CASE_ORDER:
        for lang in df["linguagem"].unique():
            s = df[(df["caso"] == caso) & (df["linguagem"] == lang)].sort_values("n")
            if s.empty:
                continue
            ax.plot(
                s["n"],
                s["tempo_por_aresta_us"],
                "o-",
                label=f"{caso} — {LANG_LABELS.get(lang, lang)}",
            )
    ax.set_xlabel("n")
    ax.set_ylabel("μs por aresta")
    ax.set_title("Custo normalizado por aresta")
    ax.set_xscale("log")
    ax.legend(fontsize=6, ncol=2)
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    return fig


def plot_percentis_caso(df, caso, ax=None):
    cols = ["min_s", "p25_s", "mediana_s", "p75_s", "p95_s", "max_s"]
    if not all(c in df.columns for c in cols):
        return None
    sub = df[df["caso"] == caso].sort_values(["linguagem", "n"])
    if ax is None:
        fig, ax = plt.subplots(figsize=(10, 5))
    else:
        fig = ax.figure
    for _, row in sub.iterrows():
        ys = [row[c] * 1000 for c in cols]
        ax.plot(
            range(len(cols)),
            ys,
            "o-",
            color=PALETTE.get(row["linguagem"], "#333"),
            alpha=0.7,
            label=f"{LANG_LABELS.get(row['linguagem'])} {row['tamanho']}",
        )
    ax.set_xticks(range(len(cols)))
    ax.set_xticklabels(["min", "P25", "mediana", "P75", "P95", "max"])
    ax.set_ylabel("Tempo (ms)")
    ax.set_title(f"Perfil de percentis — {CASE_LABELS.get(caso, caso)}")
    ax.legend(fontsize=6, ncol=2)
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    return fig


def plot_arestas_vs_n(df, ax=None):
    if ax is None:
        fig, ax = plt.subplots(figsize=(8, 5))
    else:
        fig = ax.figure
    for caso in CASE_ORDER:
        s = df[df["caso"] == caso].drop_duplicates(["n", "arestas"])
        ax.plot(s["n"], s["arestas"], "o-", label=caso)
    ax.set_xlabel("n")
    ax.set_ylabel("Arestas (E)")
    ax.set_title("Estrutura dos grafos gerados por caso")
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.legend()
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    return fig


def plot_razao_empirico_teorico(df, ax=None):
    if ax is None:
        fig, ax = plt.subplots(figsize=(9, 5))
    else:
        fig = ax.figure
    labels = []
    for i, (_, row) in enumerate(df.sort_values(["caso", "linguagem", "n"]).iterrows()):
        labels.append(f"{row['caso'][0]}/{row['tamanho'][0]}\n{row['linguagem'][0]}")
        ax.bar(
            i,
            row["razao_empirico_teorico"],
            color=PALETTE.get(row["linguagem"], "#666"),
            alpha=0.85,
        )
    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels, fontsize=6, rotation=45, ha="right")
    ax.set_ylabel("Tempo medido / modelo O((V+E) log V)")
    ax.set_title("Constante multiplicativa empírica por cenário")
    ax.grid(True, axis="y", alpha=0.3)
    fig.tight_layout()
    return fig


def describe_numeric(df):
    return df.select_dtypes(include=[np.number]).describe().T


def export_all_figures(df, out_dir: Path, rounds_df=None):
    out_dir.mkdir(parents=True, exist_ok=True)
    saved = []

    def save(name):
        path = out_dir / f"{name}.png"
        plt.savefig(path, dpi=150, bbox_inches="tight")
        plt.close("all")
        saved.append(path)

    for name, caso in [
        ("dijkstra_melhor", "melhor"),
        ("dijkstra_medio", "medio"),
        ("dijkstra_pior", "pior"),
    ]:
        plot_case(df, caso)
        save(name)
        plot_case(df, caso, use_log=True)
        save(f"{name}_log")

    for caso in CASE_ORDER:
        plot_interval_range(df, caso)
        save(f"intervalo_{caso}")

    fig, axes = plt.subplots(1, 2, figsize=(11, 4))
    plot_heatmap_times(df, "python", ax=axes[0])
    plot_heatmap_times(df, "javascript", ax=axes[1])
    save("heatmap_tempos")

    for plot_fn, name in [
        (plot_speedup_heatmap, "speedup_heatmap"),
        (plot_tempo_vs_arestas, "tempo_vs_arestas"),
        (plot_tempo_vs_densidade, "tempo_vs_densidade"),
        (plot_throughput, "throughput"),
        (plot_coeficiente_variacao, "coeficiente_variacao"),
        (plot_comparison_bars, "comparacao_linguagens"),
        (plot_residual_model, "residual_modelo"),
        (plot_correlacao, "correlacao"),
        (plot_mediana_vs_media, "mediana_vs_media"),
        (plot_fator_crescimento, "fator_crescimento"),
        (plot_tempo_por_aresta, "tempo_por_aresta"),
        (plot_arestas_vs_n, "arestas_vs_n"),
        (plot_razao_empirico_teorico, "razao_empirico_teorico"),
        (plot_dashboard, "dashboard"),
    ]:
        if plot_fn(df) is not None:
            save(name)

    if plot_rounds_distribution(rounds_df) is not None:
        save("distribuicao_rodadas")

    for caso in CASE_ORDER:
        if plot_percentis_caso(df, caso) is not None:
            save(f"percentis_{caso}")

    metrics_summary_table(df).to_csv(out_dir / "tabela_metricas_completa.csv", index=False)
    comparison_table(df).to_csv(out_dir / "tabela_comparacao.csv", index=False)
    describe_numeric(df).to_csv(out_dir / "estatisticas_descritivas.csv")
    return saved


__all__ = [
    "CASE_LABELS",
    "CASE_ORDER",
    "LANG_LABELS",
    "PALETTE",
    "SIZE_ORDER",
    "comparison_table",
    "describe_numeric",
    "enrich_dataframe",
    "export_all_figures",
    "find_project_root",
    "fit_constant",
    "load_results",
    "load_rounds",
    "metrics_summary_table",
    "plot_arestas_vs_n",
    "plot_case",
    "plot_coeficiente_variacao",
    "plot_comparison_bars",
    "plot_correlacao",
    "plot_dashboard",
    "plot_fator_crescimento",
    "plot_heatmap_times",
    "plot_interval_range",
    "plot_mediana_vs_media",
    "plot_percentis_caso",
    "plot_razao_empirico_teorico",
    "plot_residual_model",
    "plot_rounds_distribution",
    "plot_speedup_heatmap",
    "plot_tempo_por_aresta",
    "plot_tempo_vs_arestas",
    "plot_tempo_vs_densidade",
    "plot_throughput",
    "theoretical_time",
]
