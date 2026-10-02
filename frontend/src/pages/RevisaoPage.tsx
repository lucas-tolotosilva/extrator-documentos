import { useEffect, useState } from 'react'
import { api, type Documento, type DocumentoUpdatePayload } from '../lib/api'
import { TipoBadge, StatusBadge, ConfiancaBarra } from '../components/Badges'
import { formatarMoeda, formatarData } from '../lib/format'

const LIMIAR_BAIXA_CONFIANCA = 0.6

export function RevisaoPage() {
  const [documentos, setDocumentos] = useState<Documento[]>([])
  const [carregando, setCarregando] = useState(true)
  const [filtroStatus, setFiltroStatus] = useState<string>('')
  const [filtroFornecedor, setFiltroFornecedor] = useState('')
  const [expandidoId, setExpandidoId] = useState<number | null>(null)

  async function carregar() {
    setCarregando(true)
    try {
      const dados = await api.listarDocumentos({
        status: filtroStatus || undefined,
        fornecedor: filtroFornecedor || undefined,
      })
      setDocumentos(dados)
    } finally {
      setCarregando(false)
    }
  }

  useEffect(() => {
    carregar()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [filtroStatus])

  function campoComBaixaConfianca(doc: Documento, campo: string) {
    return (doc.confiancas[campo] ?? 1) < LIMIAR_BAIXA_CONFIANCA
  }

  return (
    <div className="pagina">
      <h1>🔍 Revisão de Documentos</h1>
      <p className="subtitulo">
        Corrija os campos extraídos automaticamente. Campos destacados em laranja tiveram baixa
        confiança na extração e merecem atenção.
      </p>

      <div className="filtros">
        <select value={filtroStatus} onChange={(e) => setFiltroStatus(e.target.value)}>
          <option value="">Todos os status</option>
          <option value="pendente_revisao">Pendentes de revisão</option>
          <option value="revisado">Revisados</option>
        </select>
        <input
          type="text"
          placeholder="Filtrar por fornecedor…"
          value={filtroFornecedor}
          onChange={(e) => setFiltroFornecedor(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && carregar()}
        />
        <button className="botao botao-secundario" onClick={carregar}>
          Filtrar
        </button>
      </div>

      {carregando && <p>Carregando documentos…</p>}
      {!carregando && documentos.length === 0 && (
        <p className="estado-vazio">Nenhum documento encontrado. Envie documentos na tela de Upload.</p>
      )}

      <div className="lista-documentos">
        {documentos.map((doc) => (
          <DocumentoCard
            key={doc.id}
            documento={doc}
            expandido={expandidoId === doc.id}
            onToggle={() => setExpandidoId(expandidoId === doc.id ? null : doc.id)}
            onSalvo={(atualizado) => {
              setDocumentos((atual) => atual.map((d) => (d.id === atualizado.id ? atualizado : d)))
            }}
            campoComBaixaConfianca={campoComBaixaConfianca}
          />
        ))}
      </div>
    </div>
  )
}

function DocumentoCard({
  documento,
  expandido,
  onToggle,
  onSalvo,
  campoComBaixaConfianca,
}: {
  documento: Documento
  expandido: boolean
  onToggle: () => void
  onSalvo: (doc: Documento) => void
  campoComBaixaConfianca: (doc: Documento, campo: string) => boolean
}) {
  const [form, setForm] = useState<DocumentoUpdatePayload>({
    fornecedor: documento.fornecedor,
    cnpj_fornecedor: documento.cnpj_fornecedor,
    valor: documento.valor,
    data_emissao: documento.data_emissao,
    data_vencimento: documento.data_vencimento,
    tipo_documento: documento.tipo_documento,
  })
  const [salvando, setSalvando] = useState(false)

  async function salvar() {
    setSalvando(true)
    try {
      const atualizado = await api.atualizarDocumento(documento.id, form)
      onSalvo(atualizado)
    } finally {
      setSalvando(false)
    }
  }

  return (
    <div className={`card-documento ${expandido ? 'expandido' : ''}`}>
      <button type="button" className="card-documento-resumo" onClick={onToggle}>
        <div className="card-documento-info">
          <strong>{documento.nome_arquivo}</strong>
          <TipoBadge tipo={documento.tipo_documento} />
          <StatusBadge status={documento.status} />
        </div>
        <div className="card-documento-info">
          <span>{documento.fornecedor ?? 'Fornecedor não identificado'}</span>
          <span>{formatarMoeda(documento.valor)}</span>
          <span>Venc.: {formatarData(documento.data_vencimento)}</span>
          <div style={{ width: 120 }}>
            <ConfiancaBarra valor={documento.confianca_media} />
          </div>
          <span className="expandir-seta">{expandido ? '▲' : '▼'}</span>
        </div>
      </button>

      {expandido && (
        <div className="card-documento-detalhe">
          <div className="form-grid">
            <label className={campoComBaixaConfianca(documento, 'fornecedor') ? 'campo-baixa-confianca' : ''}>
              Fornecedor
              <input
                type="text"
                value={form.fornecedor ?? ''}
                onChange={(e) => setForm({ ...form, fornecedor: e.target.value })}
              />
            </label>
            <label className={campoComBaixaConfianca(documento, 'cnpj_fornecedor') ? 'campo-baixa-confianca' : ''}>
              CNPJ
              <input
                type="text"
                value={form.cnpj_fornecedor ?? ''}
                onChange={(e) => setForm({ ...form, cnpj_fornecedor: e.target.value })}
              />
            </label>
            <label className={campoComBaixaConfianca(documento, 'valor') ? 'campo-baixa-confianca' : ''}>
              Valor (R$)
              <input
                type="number"
                step="0.01"
                value={form.valor ?? ''}
                onChange={(e) => setForm({ ...form, valor: parseFloat(e.target.value) })}
              />
            </label>
            <label className={campoComBaixaConfianca(documento, 'data_emissao') ? 'campo-baixa-confianca' : ''}>
              Data de Emissão
              <input
                type="date"
                value={form.data_emissao ?? ''}
                onChange={(e) => setForm({ ...form, data_emissao: e.target.value })}
              />
            </label>
            <label className={campoComBaixaConfianca(documento, 'data_vencimento') ? 'campo-baixa-confianca' : ''}>
              Vencimento
              <input
                type="date"
                value={form.data_vencimento ?? ''}
                onChange={(e) => setForm({ ...form, data_vencimento: e.target.value })}
              />
            </label>
            <label>
              Tipo de documento
              <select
                value={form.tipo_documento}
                onChange={(e) => setForm({ ...form, tipo_documento: e.target.value })}
              >
                <option value="nota_fiscal">Nota Fiscal</option>
                <option value="boleto">Boleto</option>
                <option value="pedido">Pedido de Compra</option>
                <option value="desconhecido">Desconhecido</option>
              </select>
            </label>
          </div>

          {documento.itens.length > 0 && (
            <div className="itens-documento">
              <h4>Itens extraídos</h4>
              <table className="tabela">
                <thead>
                  <tr>
                    <th>Descrição</th>
                    <th>Qtd.</th>
                    <th>Valor Unit.</th>
                    <th>Total</th>
                  </tr>
                </thead>
                <tbody>
                  {documento.itens.map((item) => (
                    <tr key={item.id}>
                      <td>{item.descricao}</td>
                      <td>{item.quantidade}</td>
                      <td>{formatarMoeda(item.valor_unitario)}</td>
                      <td>{formatarMoeda(item.valor_total)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          <button className="botao botao-primario" onClick={salvar} disabled={salvando}>
            {salvando ? 'Salvando…' : '💾 Salvar revisão'}
          </button>
        </div>
      )}
    </div>
  )
}
