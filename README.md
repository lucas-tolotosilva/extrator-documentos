# Extrator Inteligente de Documentos

## Problema de negócio

Empresas que recebem dezenas de notas fiscais, boletos e pedidos de compra em PDF
por mês gastam horas digitando manualmente fornecedor, CNPJ, valor, vencimento e
itens em uma planilha ou sistema financeiro. Além do tempo gasto, a digitação
manual é uma fonte comum de erros (valores trocados, vencimentos errados).

Este sistema automatiza essa etapa: o usuário faz upload dos PDFs e o sistema
extrai os campos automaticamente, classifica o tipo de documento, aponta quais
campos têm baixa confiança (para revisão humana rápida) e consolida tudo em um
dashboard com totais por fornecedor e por mês — pronto para exportar para Excel
ou Google Sheets.

## Funcionalidades

- **Upload múltiplo** de PDFs (notas fiscais, boletos, pedidos de compra).
- **Extração automática**: fornecedor, CNPJ, valor, data de emissão, vencimento e
  itens (descrição, quantidade, valor unitário).
- **Classificação automática** do tipo de documento.
- **Pontuação de confiança por campo**, para sinalizar o que precisa de revisão
  humana.
- **Tela de revisão**: edição inline dos campos, com destaque visual (vermelho +
  aviso) para os campos de baixa confiança.
- **Dashboard** com totais gerais, gráficos de valor por fornecedor e por mês, e
  tabela detalhada.
- **Exportação para Excel** (download direto) e **mock de exportação para Google
  Sheets** (sem necessidade de credenciais reais para a demonstração).
- **Modo demonstração**: funciona 100% sem chave de API, usando um extrator
  heurístico local (regex). Se a variável `GROQ_API_KEY` estiver configurada
  (gratuita, via [console.groq.com](https://console.groq.com/keys)), o sistema
  usa um modelo de linguagem real (gpt-oss-120b via Groq) para uma extração mais
  robusta, com fallback automático para a heurística em caso de falha.
  Alternativamente, `ANTHROPIC_API_KEY` também é suportada para quem preferir o
  Claude (requer créditos pagos na Anthropic).

## Stack

- **Backend**: Python, FastAPI, SQLAlchemy, SQLite, pdfplumber (leitura de PDF),
  openpyxl (exportação Excel), Groq SDK (extração via IA gratuita, gpt-oss-120b),
  com suporte opcional ao Anthropic SDK (Claude), pytest.
- **Frontend**: React, TypeScript, Vite, React Router, Recharts (gráficos),
  Vitest + Testing Library.

## Como rodar localmente

### Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# (Opcional) gerar os PDFs fictícios de exemplo
cd ..
python seed_samples.py
cd backend

# Rodar os testes
pytest tests/ -v

# Subir a API (porta 8000)
uvicorn app.main:app --reload
```

Para usar extração via IA real em vez do modo demonstração, gere uma chave
gratuita em [console.groq.com/keys](https://console.groq.com/keys), copie
`backend/.env.example` para `backend/.env` e preencha `GROQ_API_KEY`. O backend
carrega esse arquivo automaticamente (via `python-dotenv`) ao iniciar.

### Frontend

```bash
cd frontend
npm install
npm run test   # roda os testes com Vitest
npm run dev    # sobe em http://localhost:5173, já com proxy para a API em :8000
```

Abra `http://localhost:5173`, vá em **Upload**, envie os PDFs de `/samples` e
acompanhe o fluxo completo (extração → revisão → dashboard).

## Estrutura do projeto

```
extrator-documentos/
├── backend/
│   ├── app/
│   │   ├── main.py            # App FastAPI
│   │   ├── models.py          # Documento e ItemDocumento (SQLAlchemy)
│   │   ├── schemas.py         # Schemas Pydantic
│   │   ├── database.py        # Configuração do SQLite
│   │   ├── pdf_reader.py      # Extração de texto do PDF (pdfplumber)
│   │   ├── extractor.py       # Extração heurística + integração opcional com Groq/Claude
│   │   └── routers/           # documentos, dashboard, export
│   └── tests/                 # Testes pytest (extractor + API)
├── frontend/
│   └── src/
│       ├── pages/             # UploadPage, RevisaoPage, DashboardPage
│       ├── components/        # Layout, Badges
│       └── lib/                # Cliente de API e formatação (pt-BR)
├── seed_samples.py             # Gera os PDFs fictícios de /samples
├── samples/                    # PDFs de exemplo (notas, boletos, pedidos)
├── scripts/
│   └── gerar_screenshots.py    # Automação Playwright para /screenshots
└── screenshots/
```

## Resultado para o cliente

O lançamento manual de um lote de documentos, que levava em média **3 a 4 horas
por mês** entre digitar, conferir e organizar por fornecedor, passa a levar
**minutos**: o usuário envia os PDFs, revisa apenas os campos sinalizados com
baixa confiança (tipicamente uma minoria dos campos) e já sai com o dashboard e
a planilha consolidada prontos.
