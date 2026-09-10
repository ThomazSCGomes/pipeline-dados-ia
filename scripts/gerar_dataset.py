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

    # ------------------------------------------------------------------
    # ERP · PEDIDOS E ITENS
    # ------------------------------------------------------------------
    CANAIS = ['Visita', 'Telefone', 'App', 'WhatsApp']
    STATUS = ['Faturado', 'Entregue', 'Cancelado']

    pedidos = []
    itens   = []
    ped_id  = 1
    item_id = 1

    freq = {'P': (55, 130), 'M': (32, 70), 'G': (16, 38)}
    itens_por_pedido = {'P': (2, 6), 'M': (4, 10), 'G': (6, 16)}

    produtos_ativos = [p for p in produtos if p[7] == 'S']

    for c in clientes:
        cliente_id = c[0]
        porte      = c[5]
        cadastro   = date.fromisoformat(c[6]) if '/' not in c[6] else INICIO
        d = max(cadastro, INICIO) + timedelta(days=rng.randint(0, 20))
        lo, hi = freq[porte]

        while d <= FIM:
            canal     = rng.choice(CANAIS)
            cancelado = rng.random() < 0.035
            status    = 'Cancelado' if cancelado else rng.choices(
                ['Faturado', 'Entregue'], weights=[0.34, 0.62])[0]

            # SUJEIRA: data em dois formatos
            if rng.random() < 0.12:
                d_str = d.strftime('%d/%m/%Y')
            else:
                d_str = d.isoformat()

            n_it  = rng.randint(*itens_por_pedido[porte])
            skus  = rng.sample(produtos_ativos, min(n_it, len(produtos_ativos)))
            total = 0.0

            for p in skus:
                qtd       = rng.randint(1, 12)
                preco     = p[5]
                desc_pct  = rng.choices([0, 0.05, 0.10], weights=[0.6, 0.3, 0.1])[0]
                praticado = round(preco * (1 - desc_pct), 2)
                valor     = round(praticado * qtd, 2)
                total    += valor

                # SUJEIRA: devolução como quantidade negativa
                if rng.random() < 0.012:
                    qtd = -abs(qtd)

                itens.append([
                    item_id, ped_id, p[0], qtd, praticado,
                    round(desc_pct * 100, 2), valor
                ])
                item_id += 1

            valor_pedido = 0.0 if cancelado else round(total, 2)
            pedidos.append([ped_id, cliente_id, d_str, canal, status, valor_pedido])
            ped_id += 1
            d += timedelta(days=rng.randint(lo, hi))

    escrever(
        os.path.join(erp, 'pedidos.csv'),
        ['pedido_id', 'cliente_id', 'data_pedido', 'canal', 'status', 'valor_total'],
        pedidos
    )
    escrever(
        os.path.join(erp, 'itens_pedido.csv'),
        ['item_id', 'pedido_id', 'sku', 'quantidade', 'preco_praticado',
         'desconto_pct', 'valor_bruto'],
        itens
    )

    # ------------------------------------------------------------------
    # ERP · PAGAMENTOS
    # ------------------------------------------------------------------
    FORMAS_PAGAMENTO = ['Boleto 28 dias', 'PIX', 'Cartão de crédito', 
                        'Cartão de débito', 'Dinheiro']
    pagamentos = []
    pag_id = 1
    for p in pedidos:
        if p[4] == 'Cancelado':
            continue
        forma   = rng.choice(FORMAS_PAGAMENTO)
        venc    = date.fromisoformat(p[2]) if '/' not in p[2] else INICIO
        venc   += timedelta(days=rng.randint(0, 30))
        status  = rng.choices(
            ['Pago', 'Pago com atraso', 'Inadimplente', 'Em aberto'],
            weights=[0.76, 0.14, 0.05, 0.05])[0]
        pagamentos.append([pag_id, p[0], forma, p[5], venc.isoformat(), status])
        pag_id += 1

    escrever(
        os.path.join(erp, 'pagamentos.csv'),
        ['pagamento_id', 'pedido_id', 'forma_pagamento', 
         'valor', 'data_vencimento', 'status_pagamento'],
        pagamentos
    )

    # ------------------------------------------------------------------
    # ERP · ESTOQUE
    # ------------------------------------------------------------------
    estoque = []
    d = INICIO
    while d <= FIM:
        for p in rng.sample(produtos, min(80, len(produtos))):
            saldo = rng.randint(0, 800)
            if rng.random() < 0.11:
                saldo = 0
            estoque.append([d.isoformat(), p[0], saldo, 'S' if saldo == 0 else 'N'])
        d += timedelta(days=7)

    escrever(
        os.path.join(erp, 'estoque.csv'),
        ['data_snapshot', 'sku', 'saldo', 'ruptura'],
        estoque
    )

    # ------------------------------------------------------------------
    # CRM · OPORTUNIDADES
    # ------------------------------------------------------------------
    ETAPAS  = ['Prospecção', 'Qualificação', 'Proposta enviada', 
               'Negociação', 'Fechado ganho', 'Fechado perdido']
    ORIGENS = ['Prospecção ativa', 'Indicação', 'Inbound site', 
               'Feira de beleza', 'Reativação']

    oportunidades = []
    op_id = 1
    for c in clientes:
        n_op = rng.randint(0, 4)
        for _ in range(n_op):
            abertura = INICIO + timedelta(days=rng.randint(0, (FIM - INICIO).days))
            etapa    = rng.choice(ETAPAS)
            valor    = round(rng.uniform(2500, 95000), 2)
            oportunidades.append([
                op_id, c[0], rng.choice(ORIGENS),
                abertura.isoformat(), etapa, valor
            ])
            op_id += 1

    escrever(
        os.path.join(crm, 'oportunidades.csv'),
        ['oportunidade_id', 'cliente_id', 'origem', 
         'data_abertura', 'etapa', 'valor_estimado'],
        oportunidades
    )

    # ------------------------------------------------------------------
    # CRM · VISITAS
    # ------------------------------------------------------------------
    RESULTADOS = ['Pedido realizado', 'Sem pedido', 'Cliente ausente', 
                  'Reagendada', 'Apenas relacionamento']

    visitas = []
    vis_id  = 1
    for c in clientes:
        d = INICIO
        while d <= FIM:
            d += timedelta(days=rng.randint(16, 55))
            if d > FIM: break
            if d.weekday() >= 5: continue
            visitas.append([
                vis_id, c[0], d.isoformat(),
                rng.choices(RESULTADOS, weights=[.46,.24,.13,.09,.08])[0],
                rng.randint(10, 90)
            ])
            vis_id += 1

    escrever(
        os.path.join(crm, 'visitas.csv'),
        ['visita_id', 'cliente_id', 'data_visita', 'resultado', 'duracao_min'],
        visitas
    )

    print(f'\nPronto! Arquivos em: {os.path.abspath(args.saida)}')

    
if __name__ == '__main__':
    main()

