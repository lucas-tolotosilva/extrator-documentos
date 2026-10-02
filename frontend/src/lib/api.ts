export interface ItemDocumento {
  id: number
  descricao: string
  quantidade: number
  valor_unitario: number
  valor_total: number
}

export interface Documento {
  id: number
  nome_arquivo: string
  tipo_documento: 'nota_fiscal' | 'boleto' | 'pedido' | 'desconhecido'
  fornecedor: string | null
  cnpj_fornecedor: string | null
  valor: number | null
  data_emissao: string | null
  data_vencimento: string | null
  status: 'pendente_revisao' | 'revisado'
  confiancas: Record<string, number>
  confianca_media: number
  criado_em: string
  itens: ItemDocumento[]
}

export interface DocumentoUpdatePayload {
  fornecedor?: string | null
  cnpj_fornecedor?: string | null
  valor?: number | null
  data_emissao?: string | null
  data_vencimento?: string | null
  tipo_documento?: string
  status?: string
}

export interface ResumoFornecedor {
  fornecedor: string
  total_documentos: number
  valor_total: number
}

export interface ResumoMes {
  mes: string
  total_documentos: number
  valor_total: number
}

export interface ResumoDashboard {
  total_documentos: number
  valor_total: number
  pendentes_revisao: number
  por_fornecedor: ResumoFornecedor[]
  por_mes: ResumoMes[]
}

export interface ConfigApi {
  modo_demonstracao: boolean
}

async function tratarResposta<T>(resposta: Response): Promise<T> {
  if (!resposta.ok) {
    let detalhe = `Erro ${resposta.status}`
    try {
      const corpo = await resposta.json()
      detalhe = corpo.detail ?? detalhe
    } catch {
      // mantém a mensagem padrão
    }
    throw new Error(detalhe)
  }
  return resposta.json() as Promise<T>
}

export const api = {
  async obterConfig(): Promise<ConfigApi> {
    const resposta = await fetch('/api/config')
    return tratarResposta(resposta)
  },

  async enviarDocumentos(arquivos: File[]): Promise<Documento[]> {
    const formData = new FormData()
    arquivos.forEach((arquivo) => formData.append('arquivos', arquivo))
    const resposta = await fetch('/api/documentos/upload', {
      method: 'POST',
      body: formData,
    })
    return tratarResposta(resposta)
  },

  async listarDocumentos(filtros?: { status?: string; fornecedor?: string }): Promise<Documento[]> {
    const params = new URLSearchParams()
    if (filtros?.status) params.set('status', filtros.status)
    if (filtros?.fornecedor) params.set('fornecedor', filtros.fornecedor)
    const resposta = await fetch(`/api/documentos?${params.toString()}`)
    return tratarResposta(resposta)
  },

  async obterDocumento(id: number): Promise<Documento> {
    const resposta = await fetch(`/api/documentos/${id}`)
    return tratarResposta(resposta)
  },

  async atualizarDocumento(id: number, dados: DocumentoUpdatePayload): Promise<Documento> {
    const resposta = await fetch(`/api/documentos/${id}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(dados),
    })
    return tratarResposta(resposta)
  },

  async obterResumoDashboard(): Promise<ResumoDashboard> {
    const resposta = await fetch('/api/dashboard/resumo')
    return tratarResposta(resposta)
  },

  urlExportarExcel(): string {
    return '/api/export/excel'
  },

  async exportarGoogleSheetsMock(): Promise<{ modo_demonstracao: boolean; mensagem: string; planilha_url_simulada: string }> {
    const resposta = await fetch('/api/export/google-sheets', { method: 'POST' })
    return tratarResposta(resposta)
  },
}
