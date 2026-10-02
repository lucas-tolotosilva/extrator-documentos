"""Schemas Pydantic para request/response da API."""

from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


class ItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    descricao: str
    quantidade: float
    valor_unitario: float
    valor_total: float


class DocumentoOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nome_arquivo: str
    tipo_documento: str
    fornecedor: str | None
    cnpj_fornecedor: str | None
    valor: float | None
    data_emissao: date | None
    data_vencimento: date | None
    status: str
    confiancas: dict
    confianca_media: float
    criado_em: datetime
    itens: list[ItemOut]


class DocumentoUpdate(BaseModel):
    fornecedor: str | None = None
    cnpj_fornecedor: str | None = None
    valor: float | None = None
    data_emissao: date | None = None
    data_vencimento: date | None = None
    tipo_documento: str | None = None
    status: str | None = None


class ResumoFornecedor(BaseModel):
    fornecedor: str
    total_documentos: int
    valor_total: float


class ResumoMes(BaseModel):
    mes: str
    total_documentos: int
    valor_total: float


class ResumoDashboard(BaseModel):
    total_documentos: int
    valor_total: float
    pendentes_revisao: int
    por_fornecedor: list[ResumoFornecedor]
    por_mes: list[ResumoMes]


class ConfigOut(BaseModel):
    modo_demonstracao: bool
