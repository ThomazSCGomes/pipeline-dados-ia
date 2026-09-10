#!/usr/bin/env python3
"""
Exploração e manipulação do dataset pipeline-dados-ia.

Demonstra como ler, inspecionar e transformar dados de arquivos CSV
usando Python puro e Pandas — habilidades essenciais de engenharia de dados.

Uso: python scripts/explorar_dados.py
"""

import csv
import os

# ----------------------------------------------------------------------
# 1. LENDO CSV COM PYTHON PURO
# ----------------------------------------------------------------------
caminho_vendedores = './dados/crm/vendedores.csv'

with open(caminho_vendedores, 'r', encoding='utf-8') as f:
    reader = csv.reader(f)
    cabecalho = next(reader)      # lê a primeira linha — o cabeçalho
    linhas    = list(reader)      # lê o resto — os dados

print('=== VENDEDORES ===')
print(f'Colunas:  {cabecalho}')
print(f'Total de registros: {len(linhas)}')
print(f'Primeiro registro:  {linhas[0]}')
print(f'Último registro:    {linhas[-1]}')