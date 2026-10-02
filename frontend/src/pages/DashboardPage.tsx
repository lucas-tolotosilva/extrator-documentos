import { useEffect, useState } from 'react'
import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import { api, type ResumoDashboard } from '../lib/api'
import { formatarMoeda } from '../lib/format'

const COR_BARRA = '#2F5F8A'

export function DashboardPage() {
  const [resumo, setResumo] = useState<ResumoDashboard | null>(null)
  const [mensagemExport, setMensagemExport] = useState<string | null>(null)

  useEffect(() => {
    api.obterResumoDashboard().then(setResumo)
  }, [])

  async function exportarGoogleSheets() {
    const resultado = await api.exportarGoogleSheetsMock()
    setMensagemExport(resultado.mensagem)
  }

  if (!resumo) return <div className="pagina">Carregando dashboard…</div>

  return (
    <div className="pagina">
      <h1>📊 Dashboard</h1>
      <p className="subtitulo">Totais consolidados de todos os documentos processados.</p>

      <div className="cartoes-metricas">
        <div className="cartao-metrica">
          <span className="cartao-metrica-label">Documentos processados</span>
          <span className="cartao-metrica-valor">{resumo.total_documentos}</span>
        </div>
        <div className="cartao-metrica">
          <span className="cartao-metrica-label">Valor total</span>
          <span className="cartao-metrica-valor">{formatarMoeda(resumo.valor_total)}</span>
        </div>
        <div className="cartao-metrica">
          <span className="cartao-metrica-label">Pendentes de revisão</span>
          <span className="cartao-metrica-valor">{resumo.pendentes_revisao}</span>
        </div>
      </div>

      <div className="exportacoes">
        <a className="botao botao-primario" href={api.urlExportarExcel()}>
          📊 Baixar Excel
        </a>
        <button className="botao botao-secundario" onClick={exportarGoogleSheets}>
          🔗 Exportar para Google Sheets
        </button>
      </div>
      {mensagemExport && <div className="alerta alerta-info">{mensagemExport}</div>}

      <div className="graficos">
        <div className="grafico-card">
          <h3>Valor total por fornecedor</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={resumo.por_fornecedor} layout="vertical" margin={{ left: 24 }}>
              <CartesianGrid strokeDasharray="3 3" horizontal={false} />
              <XAxis type="number" tickFormatter={(v) => formatarMoeda(v)} />
              <YAxis type="category" dataKey="fornecedor" width={180} tick={{ fontSize: 12 }} />
              <Tooltip formatter={(valor) => formatarMoeda(Number(valor))} />
              <Bar dataKey="valor_total" fill={COR_BARRA} radius={[0, 4, 4, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="grafico-card">
          <h3>Valor total por mês</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={resumo.por_mes}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} />
              <XAxis dataKey="mes" tick={{ fontSize: 12 }} />
              <YAxis tickFormatter={(v) => formatarMoeda(v)} width={90} />
              <Tooltip formatter={(valor) => formatarMoeda(Number(valor))} />
              <Bar dataKey="valor_total" fill={COR_BARRA} radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="tabela-fornecedores">
        <h3>Detalhamento por fornecedor</h3>
        <table className="tabela">
          <thead>
            <tr>
              <th>Fornecedor</th>
              <th>Documentos</th>
              <th>Valor total</th>
            </tr>
          </thead>
          <tbody>
            {resumo.por_fornecedor.map((item) => (
              <tr key={item.fornecedor}>
                <td>{item.fornecedor}</td>
                <td>{item.total_documentos}</td>
                <td>{formatarMoeda(item.valor_total)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
