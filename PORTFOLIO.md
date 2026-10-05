# Extrator Inteligente de Documentos com IA

Sistema que lê notas fiscais, boletos e pedidos de compra em PDF e extrai
automaticamente fornecedor, CNPJ, valor, vencimento e itens, classificando o tipo
de documento e sinalizando campos de baixa confiança para revisão rápida. Inclui
dashboard de totais por fornecedor/mês e exportação para Excel. Funciona sem
nenhuma chave de API (modo demonstração com extração heurística) ou com IA real
(Llama via Groq, gratuito — ou Claude, opcional) quando configurada. Resultado
para o cliente: um lote de documentos que levava 3-4 horas de digitação manual
por mês passa a ser processado em minutos, com revisão humana concentrada
apenas nos campos duvidosos.

## Tecnologias

- Python, FastAPI, SQLAlchemy, SQLite
- pdfplumber (leitura de PDF)
- Groq (Llama 3.3 70B) para extração via IA gratuita, com fallback heurístico
  e suporte opcional ao Anthropic Claude
- openpyxl (exportação Excel)
- React, TypeScript, Vite, React Router, Recharts
- Pytest, Vitest + Testing Library

## Ordem sugerida das capturas de tela

1. `01_upload_inicial.png` — tela inicial de upload.
2. `02_arquivos_selecionados.png` — múltiplos PDFs selecionados antes do envio.
3. `03_resultado_extracao.png` — resultado da extração com badges de tipo e confiança.
4. `04_tela_revisao_lista.png` — lista de documentos na tela de revisão.
5. `05_revisao_campo_baixa_confianca.png` — formulário de revisão destacando campos de baixa confiança.
6. `06_dashboard.png` — dashboard com gráficos e totais por fornecedor/mês.
7. `07_mobile_upload.png` — versão mobile da tela de upload (responsividade).
