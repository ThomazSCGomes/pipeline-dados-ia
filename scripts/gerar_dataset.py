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

# ----------------------------------------------------------------------
# FUNÇÕES AUXILIARES
# ----------------------------------------------------------------------
def escrever(caminho, cabecalho, linhas):
    """Salva uma lista de linhas como arquivo CSV."""
    with open(caminho, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(cabecalho)
        w.writerows(linhas)
    print(f'  {os.path.basename(caminho):24} {len(linhas):>8,} linhas'.replace(',', '.'))

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

    # ------------------------------------------------------------------
    # CRM · VENDEDORES
    # ------------------------------------------------------------------
    NOMES = ['Ana','Bruno','Carla','Diego','Eduarda','Felipe','Gabriela',
             'Henrique','Isabela','João','Karina','Lucas','Mariana','Nathan',
             'Olívia','Paulo','Queila','Rafael','Sabrina','Thiago']
    
    SOBRENOMES = ['Silva','Santos','Oliveira','Souza','Rodrigues','Ferreira',
                  'Alves','Pereira','Lima','Gomes','Costa','Ribeiro']

    REGIOES = [('São Paulo','SP'), ('Rio de Janeiro','RJ'), 
               ('Belo Horizonte','MG'), ('Curitiba','PR'),
               ('Porto Alegre','RS'), ('Salvador','BA')]

    vendedores = []
    for i in range(1, N_VENDEDORES + 1):
        regiao, uf = rng.choice(REGIOES)
        admissao = INICIO - timedelta(days=rng.randint(30, 1500))
        vendedores.append([
            i,
            f'{rng.choice(NOMES)} {rng.choice(SOBRENOMES)}',
            regiao,
            uf,
            admissao.isoformat(),
            rng.choice([40000, 55000, 70000, 85000, 100000]),
        ])

    escrever(
        os.path.join(crm, 'vendedores.csv'),
        ['vendedor_id', 'nome', 'regiao', 'uf', 'data_admissao', 'meta_mensal'],
        vendedores
    )


if __name__ == '__main__':
    main()

