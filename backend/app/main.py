"""Extrator Inteligente de Documentos — API FastAPI."""

from __future__ import annotations

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import init_db
from app.extractor import modo_demonstracao_ativo
from app.routers import dashboard, documentos, export
from app.schemas import ConfigOut

ORIGENS_PADRAO = ["http://localhost:5173", "http://127.0.0.1:5173"]


def _origens_permitidas() -> list[str]:
    """Em produção, defina ALLOWED_ORIGINS com a URL do frontend
    (ex.: https://extrator-documentos.vercel.app), separadas por vírgula
    se houver mais de uma."""
    extras = os.getenv("ALLOWED_ORIGINS", "")
    origens_extras = [o.strip() for o in extras.split(",") if o.strip()]
    return ORIGENS_PADRAO + origens_extras


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="Extrator Inteligente de Documentos", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=_origens_permitidas(),
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/config", response_model=ConfigOut)
def obter_config():
    return ConfigOut(modo_demonstracao=modo_demonstracao_ativo())


app.include_router(documentos.router)
app.include_router(dashboard.router)
app.include_router(export.router)
