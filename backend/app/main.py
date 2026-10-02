"""Extrator Inteligente de Documentos — API FastAPI."""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import init_db
from app.extractor import modo_demonstracao_ativo
from app.routers import dashboard, documentos, export
from app.schemas import ConfigOut


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="Extrator Inteligente de Documentos", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/config", response_model=ConfigOut)
def obter_config():
    return ConfigOut(modo_demonstracao=modo_demonstracao_ativo())


app.include_router(documentos.router)
app.include_router(dashboard.router)
app.include_router(export.router)
