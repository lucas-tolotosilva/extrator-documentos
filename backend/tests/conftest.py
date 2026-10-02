import sys

import pytest


@pytest.fixture()
def client(tmp_path, monkeypatch):
    """Cliente de teste com um banco SQLite temporário e isolado por teste."""

    db_file = tmp_path / "test.db"
    monkeypatch.setenv("DATABASE_PATH", str(db_file))
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_file}")
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)

    for nome_modulo in list(sys.modules):
        if nome_modulo == "app" or nome_modulo.startswith("app."):
            del sys.modules[nome_modulo]

    from fastapi.testclient import TestClient

    from app.main import app

    with TestClient(app) as test_client:
        yield test_client

    for nome_modulo in list(sys.modules):
        if nome_modulo == "app" or nome_modulo.startswith("app."):
            del sys.modules[nome_modulo]
