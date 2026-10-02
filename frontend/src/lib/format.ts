export function formatarMoeda(valor: number | null | undefined): string {
  if (valor === null || valor === undefined) return '—'
  return valor.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })
}

export function formatarData(iso: string | null | undefined): string {
  if (!iso) return '—'
  const [ano, mes, dia] = iso.split('-')
  if (!ano || !mes || !dia) return iso
  return `${dia}/${mes}/${ano}`
}

export function formatarDataParaInput(iso: string | null | undefined): string {
  return iso ?? ''
}
