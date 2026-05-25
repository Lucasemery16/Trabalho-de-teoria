# Tabela de resultados experimentais

Tempo médio ± desvio-padrão (ms), 30 rodadas por cenário.

| Caso | Tamanho | n | Arestas | Python (ms) | JavaScript (ms) |
| --- | --- | --- | --- | --- | --- |
| medio | pequeno | 300 | 1651 | — | 0.081 ± 0.019 |
| medio | medio | 1500 | 11073 | — | 0.685 ± 0.216 |
| medio | grande | 4000 | 33318 | — | 2.423 ± 0.481 |
| medio | pequeno | 300 | 1706 | 0.263 ± 0.060 | — |
| medio | medio | 1500 | 10933 | 2.028 ± 0.157 | — |
| medio | grande | 4000 | 32834 | 7.786 ± 0.659 | — |
| melhor | pequeno | 300 | 299 | — | 0.124 ± 0.130 |
| melhor | medio | 1500 | 1499 | — | 0.232 ± 0.052 |
| melhor | grande | 4000 | 3999 | — | 0.684 ± 0.185 |
| melhor | pequeno | 300 | 149 | 0.080 ± 0.006 | — |
| melhor | medio | 1500 | 749 | 0.449 ± 0.047 | — |
| melhor | grande | 4000 | 1999 | 1.460 ± 0.182 | — |
| pior | pequeno | 300 | 44850 | 3.860 ± 0.330 | 0.993 ± 0.418 |
| pior | medio | 1500 | 1124250 | 192.206 ± 9.378 | 25.204 ± 5.645 |
| pior | grande | 4000 | 7998000 | 1387.642 ± 28.347 | 119.065 ± 10.307 |

## Dados brutos (segundos)

| linguagem | caso | tamanho | n | arestas | rodadas | media_s | desvio_s | min_s | max_s |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| javascript | medio | pequeno | 300 | 1651 | 30 | 0.000081 | 0.000019 | 0.000070 | 0.000172 |
| javascript | medio | medio | 1500 | 11073 | 30 | 0.000685 | 0.000216 | 0.000511 | 0.001561 |
| javascript | medio | grande | 4000 | 33318 | 30 | 0.002423 | 0.000481 | 0.001955 | 0.004342 |
| python | medio | pequeno | 300 | 1706 | 30 | 0.000263 | 0.000060 | 0.000228 | 0.000563 |
| python | medio | medio | 1500 | 10933 | 30 | 0.002028 | 0.000157 | 0.001819 | 0.002478 |
| python | medio | grande | 4000 | 32834 | 30 | 0.007786 | 0.000659 | 0.007094 | 0.010718 |
| javascript | melhor | pequeno | 300 | 299 | 30 | 0.000124 | 0.000130 | 0.000034 | 0.000737 |
| javascript | melhor | medio | 1500 | 1499 | 30 | 0.000232 | 0.000052 | 0.000162 | 0.000352 |
| javascript | melhor | grande | 4000 | 3999 | 30 | 0.000684 | 0.000185 | 0.000498 | 0.001308 |
| python | melhor | pequeno | 300 | 149 | 30 | 0.000080 | 0.000006 | 0.000074 | 0.000107 |
| python | melhor | medio | 1500 | 749 | 30 | 0.000449 | 0.000047 | 0.000418 | 0.000670 |
| python | melhor | grande | 4000 | 1999 | 30 | 0.001460 | 0.000182 | 0.001337 | 0.002291 |
| javascript | pior | pequeno | 300 | 44850 | 30 | 0.000993 | 0.000418 | 0.000705 | 0.002083 |
| javascript | pior | medio | 1500 | 1124250 | 30 | 0.025204 | 0.005645 | 0.017476 | 0.044622 |
| javascript | pior | grande | 4000 | 7998000 | 30 | 0.119065 | 0.010307 | 0.109639 | 0.155606 |
| python | pior | pequeno | 300 | 44850 | 30 | 0.003860 | 0.000330 | 0.003436 | 0.004870 |
| python | pior | medio | 1500 | 1124250 | 30 | 0.192206 | 0.009378 | 0.186680 | 0.236625 |
| python | pior | grande | 4000 | 7998000 | 30 | 1.387642 | 0.028347 | 1.347337 | 1.443250 |
