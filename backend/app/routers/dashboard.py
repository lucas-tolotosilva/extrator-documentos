"""Endpoint de resumo para o dashboard (totais por fornecedor e por mês)."""

from __future__ import annotations

from collections import defaultdict

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Documento
from app.schemas import ResumoDashboard, ResumoFornecedor, ResumoMes

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/resumo", response_model=ResumoDashboard)
def resumo_dashboard(db: Session = Depends(get_db)):
    documentos = db.execute(select(Documento)).scalars().all()

    totais_fornecedor: dict[str, dict] = defaultdict(lambda: {"total_documentos": 0, "valor_total": 0.0})
    totais_mes: dict[str, dict] = defaultdict(lambda: {"total_documentos": 0, "valor_total": 0.0})

    valor_total = 0.0
    pendentes = 0

    for doc in documentos:
        valor = doc.valor or 0.0
        valor_total += valor
        if doc.status == "pendente_revisao":
            pendentes += 1

        fornecedor = doc.fornecedor or "Fornecedor não identificado"
        totais_fornecedor[fornecedor]["total_documentos"] += 1
        totais_fornecedor[fornecedor]["valor_total"] += valor

        if doc.data_emissao:
            chave_mes = doc.data_emissao.strftime("%Y-%m")
        else:
            chave_mes = "Sem data"
        totais_mes[chave_mes]["total_documentos"] += 1
        totais_mes[chave_mes]["valor_total"] += valor

    por_fornecedor = sorted(
        [
            ResumoFornecedor(fornecedor=f, total_documentos=v["total_documentos"], valor_total=round(v["valor_total"], 2))
            for f, v in totais_fornecedor.items()
        ],
        key=lambda x: x.valor_total,
        reverse=True,
    )
    por_mes = sorted(
        [
            ResumoMes(mes=m, total_documentos=v["total_documentos"], valor_total=round(v["valor_total"], 2))
            for m, v in totais_mes.items()
        ],
        key=lambda x: x.mes,
    )

    return ResumoDashboard(
        total_documentos=len(documentos),
        valor_total=round(valor_total, 2),
        pendentes_revisao=pendentes,
        por_fornecedor=por_fornecedor,
        por_mes=por_mes,
    )
