# Trabalho da cadeira de Teoria da Computação (4º período de CC) ministrada pelo professor Daniel Bezerra.
## Tema: Algoritmo de Dijkstra

Implementação em **Python** e **JavaScript**, com análise no Jupyter Notebook.

## Estrutura

```
python/
├── dijkstra.py       implementação
├── graphs.py         geração de grafos de teste
└── benchmark.py      benchmark (30 rodadas, --quick disponível)
javascript/
├── dijkstra.js       implementação
├── graphs.js         geração de grafos
├── benchmark.js      benchmark (--quick disponível)
└── package.json      scripts do benchmark JS
data/
├── resultados_*.csv  CSVs brutos dos experimentos
└── graficos/         gráficos (.png) e tabelas geradas
notebooks/
├── analise_dijkstra.ipynb  relatório interativo (análise + gráficos)
└── plot_utils.py           funções auxiliares de plotagem
requirements.txt     dependências Python
package.json         atalho npm run benchmark
```

## Passo a passo

```bash
# 1. Instalar dependências Python
pip3 install -r requirements.txt   # no Windows: pip install -r requirements.txt

# 2. Experimentos (30 rodadas cada — demora no pior caso grande)
python3 python/benchmark.py        # no Windows: python python/benchmark.py
npm run benchmark

# 3. Análise, gráficos e texto do relatório
jupyter notebook notebooks/analise_dijkstra.ipynb

```

Teste rápido dos benchmarks: `python3 python/benchmark.py --quick` e `npm run benchmark:quick`.


## Grupo
- Lucas Emery
- Pedro Ferraz
- Gustavo Laporte
- Luis Berard
