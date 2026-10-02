from app.extractor import extrair_documento, modo_demonstracao_ativo


def test_modo_demonstracao_ativo_sem_chave(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    assert modo_demonstracao_ativo() is True


def test_classifica_nota_fiscal():
    texto = "NOTA FISCAL ELETRÔNICA - DANFE\nFornecedor: Acme Ltda\nCNPJ: 12.345.678/0001-90"
    resultado = extrair_documento(texto)
    assert resultado.tipo_documento == "nota_fiscal"
    assert resultado.fornecedor == "Acme Ltda"
    assert resultado.cnpj_fornecedor == "12.345.678/0001-90"


def test_classifica_boleto():
    texto = "BOLETO BANCÁRIO - FICHA DE COMPENSAÇÃO\nCedente: Banco Exemplo"
    resultado = extrair_documento(texto)
    assert resultado.tipo_documento == "boleto"


def test_classifica_pedido():
    texto = "PEDIDO DE COMPRA Nº 123\nFornecedor: Fulano Ltda"
    resultado = extrair_documento(texto)
    assert resultado.tipo_documento == "pedido"


def test_extrai_valor_maximo_como_total():
    texto = (
        "NOTA FISCAL\nFornecedor: X\nCNPJ: 11.111.111/0001-11\n"
        "Produto A 2 x R$ 10,00\nProduto B 1 x R$ 5,00\nValor Total: R$ 25,00"
    )
    resultado = extrair_documento(texto)
    assert resultado.valor == 25.00


def test_extrai_itens():
    texto = (
        "PEDIDO DE COMPRA Nº 1\nFornecedor: X\n"
        "Parafuso M8  10 x R$ 2,50\nPorca M8  10 x R$ 1,00\nValor Total do Pedido: R$ 35,00"
    )
    resultado = extrair_documento(texto)
    assert len(resultado.itens) == 2
    assert resultado.itens[0]["descricao"].strip() == "Parafuso M8"
    assert resultado.itens[0]["quantidade"] == 10
    assert resultado.itens[0]["valor_unitario"] == 2.50


def test_extrai_duas_datas_emissao_e_vencimento():
    texto = (
        "NOTA FISCAL\nFornecedor: X\nData de Emissão: 01/08/2026\nVencimento: 15/08/2026"
    )
    resultado = extrair_documento(texto)
    assert resultado.data_emissao == "01/08/2026"
    assert resultado.data_vencimento == "15/08/2026"


def test_documento_sem_fornecedor_tem_baixa_confianca():
    texto = "Documento sem identificação clara\nValor Total: R$ 100,00"
    resultado = extrair_documento(texto)
    assert resultado.confiancas["fornecedor"] < 0.5
    assert resultado.confiancas["cnpj_fornecedor"] == 0.0


def test_documento_vazio_nao_quebra():
    resultado = extrair_documento("")
    assert resultado.tipo_documento == "desconhecido"
    assert resultado.valor is None
    assert resultado.itens == []
