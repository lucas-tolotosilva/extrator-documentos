"""Endpoints de upload, listagem, detalhe e revisão de documentos."""

from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.extractor import extrair_documento
from app.models import Documento, ItemDocumento
from app.pdf_reader import extrair_texto
from app.schemas import DocumentoOut, DocumentoUpdate

router = APIRouter(prefix="/api/documentos", tags=["documentos"])


def _parse_data_br(valor: str | None):
    if not valor:
        return None
    try:
        return datetime.strptime(valor, "%d/%m/%Y").date()
    except ValueError:
        return None


@router.post("/upload", response_model=list[DocumentoOut])
async def upload_documentos(arquivos: list[UploadFile], db: Session = Depends(get_db)):
    if not arquivos:
        raise HTTPException(status_code=400, detail="Nenhum arquivo enviado.")

    criados: list[Documento] = []

    for arquivo in arquivos:
        if not arquivo.filename.lower().endswith(".pdf"):
            raise HTTPException(
                status_code=400, detail=f"Arquivo '{arquivo.filename}' não é um PDF."
            )

        conteudo = await arquivo.read()
        try:
            texto = extrair_texto(conteudo)
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc

        resultado = extrair_documento(texto)

        documento = Documento(
            nome_arquivo=arquivo.filename,
            tipo_documento=resultado.tipo_documento,
            fornecedor=resultado.fornecedor,
            cnpj_fornecedor=resultado.cnpj_fornecedor,
            valor=resultado.valor,
            data_emissao=_parse_data_br(resultado.data_emissao),
            data_vencimento=_parse_data_br(resultado.data_vencimento),
            confiancas=resultado.confiancas,
            texto_bruto=texto[:5000],
            status="pendente_revisao",
        )
        for item in resultado.itens:
            documento.itens.append(
                ItemDocumento(
                    descricao=item["descricao"],
                    quantidade=item["quantidade"],
                    valor_unitario=item["valor_unitario"],
                )
            )

        db.add(documento)
        criados.append(documento)

    db.commit()
    for documento in criados:
        db.refresh(documento)

    return criados


@router.get("", response_model=list[DocumentoOut])
def listar_documentos(
    fornecedor: str | None = None,
    status: str | None = None,
    tipo_documento: str | None = None,
    db: Session = Depends(get_db),
):
    query = select(Documento).order_by(Documento.criado_em.desc())
    if fornecedor:
        query = query.where(Documento.fornecedor.ilike(f"%{fornecedor}%"))
    if status:
        query = query.where(Documento.status == status)
    if tipo_documento:
        query = query.where(Documento.tipo_documento == tipo_documento)
    return db.execute(query).scalars().all()


@router.get("/{documento_id}", response_model=DocumentoOut)
def obter_documento(documento_id: int, db: Session = Depends(get_db)):
    documento = db.get(Documento, documento_id)
    if not documento:
        raise HTTPException(status_code=404, detail="Documento não encontrado.")
    return documento


@router.patch("/{documento_id}", response_model=DocumentoOut)
def revisar_documento(
    documento_id: int, dados: DocumentoUpdate, db: Session = Depends(get_db)
):
    documento = db.get(Documento, documento_id)
    if not documento:
        raise HTTPException(status_code=404, detail="Documento não encontrado.")

    atualizacoes = dados.model_dump(exclude_unset=True)
    novas_confiancas = dict(documento.confiancas)
    for campo, valor in atualizacoes.items():
        setattr(documento, campo, valor)
        if campo in novas_confiancas:
            novas_confiancas[campo] = 1.0
    documento.confiancas = novas_confiancas

    if atualizacoes and "status" not in atualizacoes:
        documento.status = "revisado"

    db.commit()
    db.refresh(documento)
    return documento


@router.delete("/{documento_id}", status_code=204)
def excluir_documento(documento_id: int, db: Session = Depends(get_db)):
    documento = db.get(Documento, documento_id)
    if not documento:
        raise HTTPException(status_code=404, detail="Documento não encontrado.")
    db.delete(documento)
    db.commit()
