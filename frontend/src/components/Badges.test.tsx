import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import { ConfiancaBarra, StatusBadge, TipoBadge } from './Badges'

describe('TipoBadge', () => {
  it('exibe o rótulo em português para nota_fiscal', () => {
    render(<TipoBadge tipo="nota_fiscal" />)
    expect(screen.getByText('Nota Fiscal')).toBeInTheDocument()
  })

  it('usa o valor bruto quando o tipo é desconhecido do mapa', () => {
    render(<TipoBadge tipo="outro" />)
    expect(screen.getByText('outro')).toBeInTheDocument()
  })
})

describe('StatusBadge', () => {
  it('exibe revisado quando status é revisado', () => {
    render(<StatusBadge status="revisado" />)
    expect(screen.getByText(/Revisado/)).toBeInTheDocument()
  })

  it('exibe pendente quando status é pendente_revisao', () => {
    render(<StatusBadge status="pendente_revisao" />)
    expect(screen.getByText(/Pendente de revisão/)).toBeInTheDocument()
  })
})

describe('ConfiancaBarra', () => {
  it('mostra o percentual formatado', () => {
    render(<ConfiancaBarra valor={0.85} />)
    expect(screen.getByText('85%')).toBeInTheDocument()
  })
})
