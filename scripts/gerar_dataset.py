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

    # ------------------------------------------------------------------
    # CRM · CLIENTES
    # ------------------------------------------------------------------
    SEGMENTOS = ['Perfumaria', 'Farmácia', 'Loja de shopping', 
                 'Revendedora autônoma', 'E-commerce', 'Salão de beleza']

    RAZAO_PREFIXO = ['Perfumaria', 'Farmácia', 'Boutique', 'Essência', 
                     'Comercial', 'Espaço Beleza', 'Aroma']
    RAZAO_NOME    = ['Aurora', 'Bella Vita', 'Essenza', 'Flor de Liz', 
                     'Vitória', 'Encanto', 'Nobre', 'Lumiar']
    RAZAO_SUFIXO  = ['LTDA', 'ME', 'EIRELI', 'LTDA ME']

    clientes = []
    for i in range(1, N_CLIENTES + 1):
        regiao, uf = rng.choice(REGIOES)
        cadastro = INICIO - timedelta(days=rng.randint(0, 1200))
        razao = f'{rng.choice(RAZAO_PREFIXO)} {rng.choice(RAZAO_NOME)} {rng.choice(RAZAO_SUFIXO)}'
        porte = rng.choices(['P', 'M', 'G'], weights=[0.55, 0.33, 0.12])[0]

        # SUJEIRA 1: razão social às vezes em caixa alta
        if rng.random() < 0.08:
            razao = razao.upper()

        # SUJEIRA 2: data de cadastro em dois formatos
        if rng.random() < 0.12:
            dt = cadastro.strftime('%d/%m/%Y')
        else:
            dt = cadastro.isoformat()

        clientes.append([
            i,
            razao,
            rng.choice(SEGMENTOS),
            regiao,
            uf,
            porte,
            dt,
        ])

    escrever(
        os.path.join(crm, 'clientes.csv'),
        ['cliente_id', 'razao_social', 'segmento', 'cidade', 'uf', 'porte', 'data_cadastro'],
        clientes
    )

    # ------------------------------------------------------------------
    # ERP · PRODUTOS
    # ------------------------------------------------------------------
    CATEGORIAS = {
        'Eau de Parfum':       (89.00,  420.00, 0.44),
        'Óleo Concentrado':    (45.00,  260.00, 0.52),
        'Bakhoor':             (28.00,  180.00, 0.48),
        'Difusor de Ambiente': (62.00,  210.00, 0.41),
        'Body Splash':         (32.00,   98.00, 0.38),
        'Kit Presente':        (120.00, 690.00, 0.35),
    }

    MARCAS = ['Nadir', 'Sahra', 'Layali', 'Mizan', 'Qamar', 'Rihan', 'Dahab']
    NOTAS  = ['Oud', 'Âmbar', 'Almíscar', 'Rosa', 'Sândalo', 'Baunilha']

    produtos = []
    sku_id = 1
    for cat, (pmin, pmax, margem) in CATEGORIAS.items():
        for _ in range(N_PRODUTOS // len(CATEGORIAS)):
            marca = rng.choice(MARCAS)
            nota  = rng.choice(NOTAS)
            preco = round(rng.uniform(pmin, pmax), 2)
            custo = round(preco * (1 - margem - rng.uniform(-0.04, 0.04)), 2)
            ativo = 'S' if rng.random() > 0.09 else 'N'
            produtos.append([
                f'SKU{sku_id:05d}',
                f'{marca} {nota} {cat}',
                cat,
                marca,
                nota,
                preco,
                custo,
                ativo,
            ])
            sku_id += 1

    escrever(
        os.path.join(erp, 'produtos.csv'),
        ['sku', 'descricao', 'categoria', 'marca', 'nota_olfativa',
         'preco_tabela', 'custo_unitario', 'ativo'],
        produtos
    )

    
if __name__ == '__main__':
    main()

