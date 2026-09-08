#!/usr/bin/env python3
"""
Gerador do dataset pipeline-dados-ia.

Gera 10 CSVs divididos em dois sistemas de origem:
  ERP  → produtos, pedidos, itens_pedido, pagamentos, estoque
  CRM  → clientes, vendedores, carteira, oportunidades, visitas

Uso: python scripts/gerar_dataset.py [--saida ./dados] [--seed 42]
"""

import argparse
import csv
import os
import random
from datetime import date, timedelta
from decimal import Decimal, ROUND_HALF_UP

# ----------------------------------------------------------------------
# PARÂMETROS
# ----------------------------------------------------------------------
INICIO = date(2024, 9, 1)
FIM    = date(2026, 8, 31)
N_CLIENTES   = 3000
N_VENDEDORES = 42
N_PRODUTOS   = 320


def main():
    ap = argparse.ArgumentParser(
        description='Gerador do dataset pipeline-dados-ia'
    )
    ap.add_argument('--saida', default='./dados', help='Pasta de saída dos CSVs')
    ap.add_argument('--seed', type=int, default=42, help='Seed para reprodutibilidade')
    args = ap.parse_args()

    rng = random.Random(args.seed)

    os.makedirs(args.saida, exist_ok=True)
    crm = os.path.join(args.saida, 'crm')
    erp = os.path.join(args.saida, 'erp')
    os.makedirs(crm, exist_ok=True)
    os.makedirs(erp, exist_ok=True)

    print(f'\nGerando dataset  ·  seed={args.seed}')
    print(f'Período: {INICIO} a {FIM}\n')


if __name__ == '__main__':
    main()