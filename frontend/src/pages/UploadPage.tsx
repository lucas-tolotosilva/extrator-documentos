import { useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { api, type Documento } from '../lib/api'
import { TipoBadge, ConfiancaBarra } from '../components/Badges'
import { formatarMoeda } from '../lib/format'

export function UploadPage() {
  const [arquivos, setArquivos] = useState<File[]>([])
  const [enviando, setEnviando] = useState(false)
  const [erro, setErro] = useState<string | null>(null)
  const [resultado, setResultado] = useState<Documento[] | null>(null)
  const inputRef = useRef<HTMLInputElement>(null)
  const navigate = useNavigate()

  function adicionarArquivos(novos: FileList | null) {
    if (!novos) return
    const pdfs = Array.from(novos).filter((arquivo) => arquivo.name.toLowerCase().endsWith('.pdf'))
    setArquivos((atual) => [...atual, ...pdfs])
    setErro(null)
  }

  function removerArquivo(indice: number) {
    setArquivos((atual) => atual.filter((_, i) => i !== indice))
  }

  async function enviarArquivos() {
    if (arquivos.length === 0) return
    setEnviando(true)
    setErro(null)
    try {
      const documentos = await api.enviarDocumentos(arquivos)
      setResultado(documentos)
      setArquivos([])
    } catch (e) {
      setErro(e instanceof Error ? e.message : 'Erro ao enviar os documentos.')
    } finally {
      setEnviando(false)
    }
  }

  return (
    <div className="pagina">
      <h1>📤 Upload de Documentos</h1>
      <p className="subtitulo">
        Envie notas fiscais, boletos ou pedidos de compra em PDF. O sistema identifica o tipo de
        documento e extrai automaticamente fornecedor, CNPJ, valor, vencimento e itens.
      </p>

      <div
        className="dropzone"
        onDragOver={(e) => e.preventDefault()}
        onDrop={(e) => {
          e.preventDefault()
          adicionarArquivos(e.dataTransfer.files)
        }}
        onClick={() => inputRef.current?.click()}
      >
        <span className="dropzone-icone">📎</span>
        <p>Arraste os PDFs aqui ou clique para selecionar</p>
        <input
          ref={inputRef}
          type="file"
          accept="application/pdf"
          multiple
          hidden
          onChange={(e) => adicionarArquivos(e.target.files)}
        />
      </div>

      {arquivos.length > 0 && (
        <div className="lista-arquivos">
          <h3>Arquivos selecionados ({arquivos.length})</h3>
          <ul>
            {arquivos.map((arquivo, indice) => (
              <li key={`${arquivo.name}-${indice}`}>
                <span>📄 {arquivo.name}</span>
                <button type="button" className="botao-link" onClick={() => removerArquivo(indice)}>
                  remover
                </button>
              </li>
            ))}
          </ul>
          <button className="botao botao-primario" onClick={enviarArquivos} disabled={enviando}>
            {enviando ? 'Extraindo dados…' : `Extrair dados de ${arquivos.length} documento(s)`}
          </button>
        </div>
      )}

      {erro && <div className="alerta alerta-erro">{erro}</div>}

      {resultado && (
        <div className="resultado-upload">
          <h3>✅ {resultado.length} documento(s) processado(s)</h3>
          <table className="tabela">
            <thead>
              <tr>
                <th>Arquivo</th>
                <th>Tipo</th>
                <th>Fornecedor</th>
                <th>Valor</th>
                <th>Confiança</th>
              </tr>
            </thead>
            <tbody>
              {resultado.map((doc) => (
                <tr key={doc.id}>
                  <td>{doc.nome_arquivo}</td>
                  <td>
                    <TipoBadge tipo={doc.tipo_documento} />
                  </td>
                  <td>{doc.fornecedor ?? '—'}</td>
                  <td>{formatarMoeda(doc.valor)}</td>
                  <td style={{ minWidth: 140 }}>
                    <ConfiancaBarra valor={doc.confianca_media} />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          <button className="botao botao-secundario" onClick={() => navigate('/revisao')}>
            Ir para a tela de revisão →
          </button>
        </div>
      )}
    </div>
  )
}
