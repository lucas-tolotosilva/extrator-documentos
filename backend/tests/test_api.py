from pathlib import Path

SAMPLES_DIR = Path(__file__).parent.parent.parent / "samples"


def _upload_pdf(client, nome_arquivo: str):
    caminho = SAMPLES_DIR / nome_arquivo
    with open(caminho, "rb") as f:
        return client.post(
            "/api/documentos/upload",
            files=[("arquivos", (nome_arquivo, f, "application/pdf"))],
        )


def test_config_modo_demonstracao(client):
    resposta = client.get("/api/config")
    assert resposta.status_code == 200
    assert resposta.json()["modo_demonstracao"] is True


def test_upload_nota_fiscal(client):
    resposta = _upload_pdf(client, "nota_fiscal_01.pdf")
    assert resposta.status_code == 200
    dados = resposta.json()
    assert len(dados) == 1
    documento = dados[0]
    assert documento["tipo_documento"] == "nota_fiscal"
    assert documento["status"] == "pendente_revisao"
    assert documento["fornecedor"] is not None
    assert len(documento["itens"]) > 0


def test_upload_rejeita_arquivo_nao_pdf(client, tmp_path):
    arquivo_txt = tmp_path / "documento.txt"
    arquivo_txt.write_text("não é um pdf")
    with open(arquivo_txt, "rb") as f:
        resposta = client.post(
            "/api/documentos/upload",
            files=[("arquivos", ("documento.txt", f, "text/plain"))],
        )
    assert resposta.status_code == 400


def test_listar_documentos_apos_upload(client):
    _upload_pdf(client, "boleto_01.pdf")
    _upload_pdf(client, "pedido_01.pdf")

    resposta = client.get("/api/documentos")
    assert resposta.status_code == 200
    assert len(resposta.json()) == 2


def test_obter_documento_por_id(client):
    criado = _upload_pdf(client, "nota_fiscal_01.pdf").json()[0]

    resposta = client.get(f"/api/documentos/{criado['id']}")
    assert resposta.status_code == 200
    assert resposta.json()["id"] == criado["id"]


def test_documento_inexistente_retorna_404(client):
    resposta = client.get("/api/documentos/9999")
    assert resposta.status_code == 404


def test_revisar_documento_atualiza_e_muda_status(client):
    criado = _upload_pdf(client, "nota_fiscal_06.pdf").json()[0]
    assert criado["fornecedor"] is None or criado["status"] == "pendente_revisao"

    resposta = client.patch(
        f"/api/documentos/{criado['id']}",
        json={"fornecedor": "Fornecedor Corrigido Ltda", "cnpj_fornecedor": "11.111.111/0001-11"},
    )
    assert resposta.status_code == 200
    atualizado = resposta.json()
    assert atualizado["fornecedor"] == "Fornecedor Corrigido Ltda"
    assert atualizado["status"] == "revisado"
    assert atualizado["confiancas"]["fornecedor"] == 1.0


def test_dashboard_resumo(client):
    _upload_pdf(client, "nota_fiscal_01.pdf")
    _upload_pdf(client, "boleto_01.pdf")

    resposta = client.get("/api/dashboard/resumo")
    assert resposta.status_code == 200
    resumo = resposta.json()
    assert resumo["total_documentos"] == 2
    assert resumo["pendentes_revisao"] == 2
    assert len(resumo["por_fornecedor"]) >= 1


def test_exportar_excel(client):
    _upload_pdf(client, "nota_fiscal_01.pdf")

    resposta = client.get("/api/export/excel")
    assert resposta.status_code == 200
    assert "spreadsheetml" in resposta.headers["content-type"]


def test_exportar_google_sheets_mock(client):
    resposta = client.post("/api/export/google-sheets")
    assert resposta.status_code == 200
    dados = resposta.json()
    assert dados["modo_demonstracao"] is True
