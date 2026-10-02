const ROTULOS_TIPO: Record<string, string> = {
  nota_fiscal: 'Nota Fiscal',
  boleto: 'Boleto',
  pedido: 'Pedido de Compra',
  desconhecido: 'Desconhecido',
}

const CORES_TIPO: Record<string, string> = {
  nota_fiscal: '#D9E1F2',
  boleto: '#FCE4D6',
  pedido: '#E2EFDA',
  desconhecido: '#EDEDED',
}

export function TipoBadge({ tipo }: { tipo: string }) {
  return (
    <span className="badge" style={{ backgroundColor: CORES_TIPO[tipo] ?? '#EDEDED' }}>
      {ROTULOS_TIPO[tipo] ?? tipo}
    </span>
  )
}

export function StatusBadge({ status }: { status: string }) {
  const revisado = status === 'revisado'
  return (
    <span className={`badge ${revisado ? 'badge-sucesso' : 'badge-alerta'}`}>
      {revisado ? '✅ Revisado' : '⏳ Pendente de revisão'}
    </span>
  )
}

export function ConfiancaBarra({ valor }: { valor: number }) {
  const percentual = Math.round(valor * 100)
  const nivel = valor >= 0.8 ? 'alta' : valor >= 0.5 ? 'media' : 'baixa'
  return (
    <div className="confianca" title={`Confiança: ${percentual}%`}>
      <div className={`confianca-barra confianca-${nivel}`} style={{ width: `${percentual}%` }} />
      <span className="confianca-texto">{percentual}%</span>
    </div>
  )
}
