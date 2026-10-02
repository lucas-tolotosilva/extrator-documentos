"""Gera PDFs fictícios (notas fiscais, boletos e pedidos de compra) em /samples
para demonstração do Extrator Inteligente de Documentos.

Os documentos usam nomes de empresas e CNPJs 100% fictícios.
"""

import random
from datetime import date, timedelta
from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas

random.seed(7)

SAMPLES_DIR = Path(__file__).parent / "samples"

FORNECEDORES = [
    ("Tech Suprimentos Ltda", "12.345.678/0001-90"),
    ("Distribuidora Fênix Comércio Ltda", "23.456.789/0001-11"),
    ("Office Center Papelaria e Informática Ltda", "34.567.890/0001-22"),
    ("Metalúrgica Santa Rita S.A.", "45.678.901/0001-33"),
    ("Construsul Materiais de Construção Ltda", "56.789.012/0001-44"),
    ("Gráfica Horizonte Ltda", "67.890.123/0001-55"),
    ("Elétrica Bom Jesus Ltda", "78.901.234/0001-66"),
    ("Auto Peças Vitória Ltda", "89.012.345/0001-77"),
    ("Limpeza Total Produtos de Higiene Ltda", "90.123.456/0001-88"),
    ("Informática Prime Soluções Ltda", "01.234.567/0001-99"),
]

ITENS_POSSIVEIS = [
    ("Monitor LED 24 polegadas", 650.00),
    ("Teclado mecânico ABNT2", 180.00),
    ("Mouse óptico sem fio", 45.00),
    ("Papel A4 500 folhas", 24.90),
    ("Caneta esferográfica azul", 1.20),
    ("Grampeador médio", 18.50),
    ("Cimento CP-II 50kg", 32.00),
    ("Tinta acrílica 18 litros", 210.00),
    ("Cabo elétrico 2,5mm (rolo 100m)", 165.00),
    ("Disjuntor bipolar 40A", 28.00),
    ("Luva de proteção par", 12.00),
    ("Detergente neutro 5 litros", 22.00),
    ("Álcool 70% 1 litro", 9.50),
    ("Pneu aro 15", 420.00),
    ("Filtro de óleo", 38.00),
    ("Notebook 15 polegadas i5", 3200.00),
    ("Licença de software anual", 890.00),
]

DATA_INICIAL = date(2026, 8, 1)


def _data_aleatoria(offset_min=0, offset_max=45) -> date:
    return DATA_INICIAL + timedelta(days=random.randint(offset_min, offset_max))


def _fmt(d: date) -> str:
    return d.strftime("%d/%m/%Y")


def _fmt_valor(v: float) -> str:
    inteiro, centavos = f"{v:.2f}".split(".")
    inteiro_formatado = f"{int(inteiro):,}".replace(",", ".")
    return f"{inteiro_formatado},{centavos}"


def _escrever_linhas(c: canvas.Canvas, linhas: list[str], x=2 * cm, y_inicial=27 * cm):
    y = y_inicial
    for linha in linhas:
        c.drawString(x, y, linha)
        y -= 0.7 * cm
    return y


def _gerar_itens(qtd_itens: int):
    escolhidos = random.sample(ITENS_POSSIVEIS, qtd_itens)
    itens = []
    for descricao, valor_base in escolhidos:
        quantidade = random.choice([1, 2, 3, 5, 10, 20])
        itens.append((descricao, quantidade, valor_base))
    return itens


def gerar_nota_fiscal(indice: int, fornecedor: str, cnpj: str, ambiguo: bool = False) -> Path:
    nome_arquivo = SAMPLES_DIR / f"nota_fiscal_{indice:02d}.pdf"
    c = canvas.Canvas(str(nome_arquivo), pagesize=A4)

    emissao = _data_aleatoria(0, 30)
    vencimento = emissao + timedelta(days=random.choice([15, 30, 45]))
    itens = _gerar_itens(random.choice([2, 3, 4]))
    total = sum(q * v for _, q, v in itens)

    linhas = [
        "NOTA FISCAL ELETRÔNICA - DANFE",
        f"Número: NF-{2026000 + indice}",
        "" if ambiguo else f"Fornecedor: {fornecedor}",
        "" if ambiguo else f"CNPJ: {cnpj}",
        f"Data de Emissão: {_fmt(emissao)}",
        f"Vencimento: {_fmt(vencimento)}",
        "",
        "Itens:",
    ]
    for descricao, quantidade, valor_unit in itens:
        linhas.append(f"{descricao}  {quantidade} x R$ {_fmt_valor(valor_unit)}")
    linhas += ["", f"Valor Total: R$ {_fmt_valor(total)}"]

    _escrever_linhas(c, [l for l in linhas if l != ""] if not ambiguo else linhas)
    c.save()
    return nome_arquivo


def gerar_boleto(indice: int, fornecedor: str, cnpj: str) -> Path:
    nome_arquivo = SAMPLES_DIR / f"boleto_{indice:02d}.pdf"
    c = canvas.Canvas(str(nome_arquivo), pagesize=A4)

    emissao = _data_aleatoria(0, 30)
    vencimento = emissao + timedelta(days=random.choice([10, 20, 30]))
    valor = round(random.uniform(300, 5000), 2)

    linhas = [
        "BOLETO BANCÁRIO - FICHA DE COMPENSAÇÃO",
        f"Cedente: {fornecedor}",
        f"CNPJ: {cnpj}",
        f"Data de Emissão: {_fmt(emissao)}",
        f"Vencimento: {_fmt(vencimento)}",
        "Linha Digitável: 23793.39128 60082.063305 71000.063305 1 99860000012345",
        "",
        f"Valor do Documento: R$ {_fmt_valor(valor)}",
    ]
    _escrever_linhas(c, linhas)
    c.save()
    return nome_arquivo


def gerar_pedido(indice: int, fornecedor: str, cnpj: str) -> Path:
    nome_arquivo = SAMPLES_DIR / f"pedido_{indice:02d}.pdf"
    c = canvas.Canvas(str(nome_arquivo), pagesize=A4)

    emissao = _data_aleatoria(0, 30)
    entrega = emissao + timedelta(days=random.choice([7, 14, 21]))
    itens = _gerar_itens(random.choice([2, 3, 4]))
    total = sum(q * v for _, q, v in itens)

    linhas = [
        f"PEDIDO DE COMPRA Nº {2026000 + indice}",
        f"Fornecedor: {fornecedor}",
        f"CNPJ: {cnpj}",
        f"Data de Emissão: {_fmt(emissao)}",
        f"Vencimento: {_fmt(entrega)}",
        "",
        "Itens do Pedido:",
    ]
    for descricao, quantidade, valor_unit in itens:
        linhas.append(f"{descricao}  {quantidade} x R$ {_fmt_valor(valor_unit)}")
    linhas += ["", f"Valor Total do Pedido: R$ {_fmt_valor(total)}"]

    _escrever_linhas(c, linhas)
    c.save()
    return nome_arquivo


def gerar_amostras():
    SAMPLES_DIR.mkdir(exist_ok=True)
    gerados = []

    for i in range(1, 7):
        fornecedor, cnpj = FORNECEDORES[(i - 1) % len(FORNECEDORES)]
        ambiguo = i == 6  # uma nota fiscal sem fornecedor/CNPJ legíveis (baixa confiança)
        gerados.append(gerar_nota_fiscal(i, fornecedor, cnpj, ambiguo=ambiguo))

    for i in range(1, 7):
        fornecedor, cnpj = FORNECEDORES[(i + 2) % len(FORNECEDORES)]
        gerados.append(gerar_boleto(i, fornecedor, cnpj))

    for i in range(1, 7):
        fornecedor, cnpj = FORNECEDORES[(i + 5) % len(FORNECEDORES)]
        gerados.append(gerar_pedido(i, fornecedor, cnpj))

    print(f"Gerados {len(gerados)} PDFs fictícios em {SAMPLES_DIR}")


if __name__ == "__main__":
    gerar_amostras()
