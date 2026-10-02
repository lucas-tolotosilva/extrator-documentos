"""Modelos ORM: Documento (nota fiscal, boleto ou pedido) e seus Itens."""

from __future__ import annotations

from datetime import UTC, date, datetime

from sqlalchemy import JSON, Date, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Documento(Base):
    __tablename__ = "documentos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nome_arquivo: Mapped[str] = mapped_column(String(255))
    tipo_documento: Mapped[str] = mapped_column(String(50), default="desconhecido")
    fornecedor: Mapped[str | None] = mapped_column(String(255), nullable=True)
    cnpj_fornecedor: Mapped[str | None] = mapped_column(String(32), nullable=True)
    valor: Mapped[float | None] = mapped_column(Float, nullable=True)
    data_emissao: Mapped[date | None] = mapped_column(Date, nullable=True)
    data_vencimento: Mapped[date | None] = mapped_column(Date, nullable=True)
    status: Mapped[str] = mapped_column(String(30), default="pendente_revisao")
    confiancas: Mapped[dict] = mapped_column(JSON, default=dict)
    texto_bruto: Mapped[str | None] = mapped_column(String, nullable=True)
    criado_em: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC))

    itens: Mapped[list["ItemDocumento"]] = relationship(
        back_populates="documento", cascade="all, delete-orphan"
    )

    @property
    def confianca_media(self) -> float:
        if not self.confiancas:
            return 0.0
        valores = [v for v in self.confiancas.values() if isinstance(v, (int, float))]
        return round(sum(valores) / len(valores), 2) if valores else 0.0


class ItemDocumento(Base):
    __tablename__ = "itens_documento"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    documento_id: Mapped[int] = mapped_column(ForeignKey("documentos.id"))
    descricao: Mapped[str] = mapped_column(String(255))
    quantidade: Mapped[float] = mapped_column(Float, default=1.0)
    valor_unitario: Mapped[float] = mapped_column(Float, default=0.0)

    documento: Mapped[Documento] = relationship(back_populates="itens")

    @property
    def valor_total(self) -> float:
        return round(self.quantidade * self.valor_unitario, 2)
