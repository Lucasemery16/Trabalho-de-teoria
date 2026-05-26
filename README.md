# Trabalho da cadeira de Teoria da Computação (4º período de CC) ministrada pelo professor Daniel Bezerra.
## Tema: Algoritmo de Dijkstra

Implementação em **Python** e **JavaScript**, com análise no Jupyter Notebook.

## Estrutura

```
python/              código + benchmark Python
javascript/          código + benchmark JavaScript
data/                CSVs gerados pelos experimentos
notebooks/           relatório interativo (análise + gráficos)
requirements.txt     dependências Python
package.json         atalho npm run benchmark
```

## Passo a passo

```bash
# 1. Experimentos (30 rodadas cada — demora no pior caso grande)
python3 python/benchmark.py
npm run benchmark

# 2. Análise, gráficos e texto do relatório
pip3 install -r requirements.txt
jupyter notebook notebooks/analise_dijkstra.ipynb
```

Teste rápido dos benchmarks: `python3 python/benchmark.py --quick` e `npm run benchmark:quick`.


## Grupo
- Lucas Emery
- Pedro Ferraz
- Gustavo Laporte
- Luis Berard
