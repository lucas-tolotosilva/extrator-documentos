"""Extração estruturada de campos a partir do texto do documento.

Por padrão (sem chave de API configurada), usa um extrator heurístico baseado em
regex — suficiente para a demonstração e totalmente offline/gratuito. Se a
variável de ambiente GROQ_API_KEY estiver definida, usa um modelo de linguagem
real (modelo aberto via Groq, gratuito) para uma extração mais robusta. Como alternativa,
ANTHROPIC_API_KEY também é suportada para quem tiver créditos na Anthropic.
Prioridade: Groq > Anthropic > heurística.
"""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass, field

from dotenv import load_dotenv

load_dotenv()

CNPJ_REGEX = re.compile(r"\d{2}\.?\d{3}\.?\d{3}/?\d{4}-?\d{2}")
VALOR_REGEX = re.compile(r"R\$\s*([\d.]+,\d{2})")
DATA_REGEX = re.compile(r"\b(\d{2}/\d{2}/\d{4})\b")
ITEM_REGEX = re.compile(
    r"^(?P<descricao>[A-Za-zÀ-ú0-9 .\-]{4,60}?)\s+(?P<qtd>\d+(?:,\d+)?)\s*x\s*R\$\s*(?P<valor_unit>[\d.]+,\d{2})",
    re.IGNORECASE | re.MULTILINE,
)

PALAVRAS_NOTA_FISCAL = ["nota fiscal", "nfe", "nf-e", "danfe"]
PALAVRAS_BOLETO = ["boleto", "ficha de compensação", "cedente", "linha digitável"]
PALAVRAS_PEDIDO = ["pedido de compra", "ordem de compra", "pedido nº", "pedido n."]


@dataclass
class ResultadoExtracao:
    tipo_documento: str
    fornecedor: str | None
    cnpj_fornecedor: str | None
    valor: float | None
    data_emissao: str | None
    data_vencimento: str | None
    itens: list[dict] = field(default_factory=list)
    confiancas: dict = field(default_factory=dict)


def _para_float(valor_str: str) -> float:
    return float(valor_str.replace(".", "").replace(",", "."))


def _classificar_tipo(texto_lower: str) -> tuple[str, float]:
    if any(p in texto_lower for p in PALAVRAS_BOLETO):
        return "boleto", 0.9
    if any(p in texto_lower for p in PALAVRAS_NOTA_FISCAL):
        return "nota_fiscal", 0.9
    if any(p in texto_lower for p in PALAVRAS_PEDIDO):
        return "pedido", 0.85
    return "desconhecido", 0.3


def _extrair_fornecedor(texto: str) -> tuple[str | None, float]:
    for linha in texto.splitlines():
        linha_limpa = linha.strip()
        if re.match(r"^(fornecedor|emitente|cedente)\s*[:\-]", linha_limpa, re.IGNORECASE):
            valor = re.split(r"[:\-]", linha_limpa, maxsplit=1)[1].strip()
            if valor:
                return valor, 0.9
    linhas_nao_vazias = [l.strip() for l in texto.splitlines() if l.strip()]
    if linhas_nao_vazias:
        return linhas_nao_vazias[0][:120], 0.4
    return None, 0.0


def _extrair_com_heuristica(texto: str) -> ResultadoExtracao:
    texto_lower = texto.lower()
    tipo, conf_tipo = _classificar_tipo(texto_lower)
    fornecedor, conf_fornecedor = _extrair_fornecedor(texto)

    cnpj_match = CNPJ_REGEX.search(texto)
    cnpj = cnpj_match.group(0) if cnpj_match else None
    conf_cnpj = 0.95 if cnpj else 0.0

    valores_encontrados = [_para_float(v) for v in VALOR_REGEX.findall(texto)]
    valor = max(valores_encontrados) if valores_encontrados else None
    conf_valor = 0.85 if valor is not None else 0.0

    datas_encontradas = DATA_REGEX.findall(texto)
    data_emissao = datas_encontradas[0] if len(datas_encontradas) >= 1 else None
    data_vencimento = datas_encontradas[1] if len(datas_encontradas) >= 2 else data_emissao
    conf_data_emissao = 0.8 if data_emissao else 0.0
    conf_data_vencimento = 0.8 if len(datas_encontradas) >= 2 else 0.4

    itens = []
    for match in ITEM_REGEX.finditer(texto):
        itens.append(
            {
                "descricao": match.group("descricao").strip(),
                "quantidade": float(match.group("qtd").replace(",", ".")),
                "valor_unitario": _para_float(match.group("valor_unit")),
            }
        )
    conf_itens = 0.8 if itens else 0.3

    return ResultadoExtracao(
        tipo_documento=tipo,
        fornecedor=fornecedor,
        cnpj_fornecedor=cnpj,
        valor=valor,
        data_emissao=data_emissao,
        data_vencimento=data_vencimento,
        itens=itens,
        confiancas={
            "tipo_documento": conf_tipo,
            "fornecedor": conf_fornecedor,
            "cnpj_fornecedor": conf_cnpj,
            "valor": conf_valor,
            "data_emissao": conf_data_emissao,
            "data_vencimento": conf_data_vencimento,
            "itens": conf_itens,
        },
    )


PROMPT_EXTRACAO = """Você é um sistema de extração de dados de documentos fiscais brasileiros \
(notas fiscais, boletos e pedidos de compra). Leia o texto abaixo, extraído de um PDF, e \
retorne APENAS um JSON (sem markdown, sem explicação) com este formato exato:

{{
  "tipo_documento": "nota_fiscal" | "boleto" | "pedido" | "desconhecido",
  "fornecedor": string ou null,
  "cnpj_fornecedor": string ou null,
  "valor": number ou null,
  "data_emissao": "DD/MM/AAAA" ou null,
  "data_vencimento": "DD/MM/AAAA" ou null,
  "itens": [{{"descricao": string, "quantidade": number, "valor_unitario": number}}],
  "confiancas": {{"tipo_documento": 0-1, "fornecedor": 0-1, "cnpj_fornecedor": 0-1, "valor": 0-1, \
"data_emissao": 0-1, "data_vencimento": 0-1, "itens": 0-1}}
}}

Texto do documento:
---
{texto}
---
"""


def _parsear_resposta_json(bruto: str) -> ResultadoExtracao:
    bruto = re.sub(r"^```(json)?|```$", "", bruto.strip(), flags=re.MULTILINE).strip()
    dados = json.loads(bruto)

    return ResultadoExtracao(
        tipo_documento=dados.get("tipo_documento", "desconhecido"),
        fornecedor=dados.get("fornecedor"),
        cnpj_fornecedor=dados.get("cnpj_fornecedor"),
        valor=dados.get("valor"),
        data_emissao=dados.get("data_emissao"),
        data_vencimento=dados.get("data_vencimento"),
        itens=dados.get("itens", []),
        confiancas=dados.get("confiancas", {}),
    )


def _extrair_com_groq(texto: str) -> ResultadoExtracao:
    from groq import Groq

    client = Groq()
    resposta = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        max_tokens=1024,
        response_format={"type": "json_object"},
        messages=[{"role": "user", "content": PROMPT_EXTRACAO.format(texto=texto[:6000])}],
    )
    return _parsear_resposta_json(resposta.choices[0].message.content)


def _extrair_com_anthropic(texto: str) -> ResultadoExtracao:
    import anthropic

    client = anthropic.Anthropic()
    resposta = client.messages.create(
        model="claude-sonnet-5",
        max_tokens=1024,
        messages=[{"role": "user", "content": PROMPT_EXTRACAO.format(texto=texto[:6000])}],
    )
    return _parsear_resposta_json(resposta.content[0].text)


def modo_demonstracao_ativo() -> bool:
    return not bool(os.getenv("GROQ_API_KEY") or os.getenv("ANTHROPIC_API_KEY"))


def extrair_documento(texto: str) -> ResultadoExtracao:
    """Extrai os campos estruturados do texto do documento.

    Usa um modelo de linguagem real quando GROQ_API_KEY (gratuito) ou
    ANTHROPIC_API_KEY estiver configurada — Groq tem prioridade por ser gratuito.
    Sem nenhuma das duas, cai automaticamente no extrator heurístico (modo
    demonstração). Qualquer falha na chamada de API também cai na heurística,
    para nunca quebrar o upload.
    """

    if os.getenv("GROQ_API_KEY"):
        try:
            return _extrair_com_groq(texto)
        except Exception:  # noqa: BLE001
            return _extrair_com_heuristica(texto)

    if os.getenv("ANTHROPIC_API_KEY"):
        try:
            return _extrair_com_anthropic(texto)
        except Exception:  # noqa: BLE001
            return _extrair_com_heuristica(texto)

    return _extrair_com_heuristica(texto)
