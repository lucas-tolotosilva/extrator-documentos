"""Extração de texto bruto de arquivos PDF."""

from __future__ import annotations

from io import BytesIO

import pdfplumber


def extrair_texto(conteudo_pdf: bytes) -> str:
    """Extrai todo o texto de um PDF (todas as páginas), concatenado."""

    try:
        with pdfplumber.open(BytesIO(conteudo_pdf)) as pdf:
            paginas = [pagina.extract_text() or "" for pagina in pdf.pages]
        return "\n".join(paginas).strip()
    except Exception as exc:  # noqa: BLE001
        raise ValueError(f"Não foi possível ler o PDF: {exc}") from exc
