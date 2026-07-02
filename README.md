# Análise de Latência e Saltos de Rede por Continentes e Países

Este projeto processa arquivos de telemetria de rede (no formato JSON) obtidos através de sondas espalhadas pelo mundo. O objetivo é analisar o desempenho de rotas de rede para grandes portais (`cnn.com`, `ft.com`, `apnews.com`), comparando as métricas de **Latência** e **Quantidade de Saltos (Hops)** entre os protocolos **IPv4** e **IPv6**.

O projeto gera gráficos temporais agrupados de duas formas:
1. **Por Continente:** Média geral do continente dividida por IPv4 vs IPv6.
2. **Por País:** Detalhamento de cada país pertencente àquele continente, divididos por IPv4 vs IPv6.

---

## Estrutura dos Scripts

* `graficos_continente.py`: Agrupa os dados no nível do continente e gera gráficos comparativos entre IPv4 e IPv6. Os resultados são salvos em `continentes/graficos_latencia` e `continentes/graficos_saltos`.
* `graficos_paises.py`: Mantém o agrupamento por continente/site, mas plota linhas individuais para cada **país e IP** (ex: `Brasil - IPv4`, `Chile - IPv6`), permitindo uma análise mais granular. Os resultados são salvos em `graficos_latencia` e `graficos_saltos`.

---

## Pré-requisitos

Antes de executar, você precisa ter o Python instalado e as seguintes bibliotecas:

```bash
pip install pandas matplotlib
