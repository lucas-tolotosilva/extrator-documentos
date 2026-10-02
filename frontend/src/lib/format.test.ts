import { describe, expect, it } from 'vitest'
import { formatarData, formatarMoeda } from './format'

describe('formatarMoeda', () => {
  it('formata um número como moeda brasileira', () => {
    expect(formatarMoeda(1234.5)).toBe('R$ 1.234,50')
  })

  it('retorna travessão quando o valor é nulo', () => {
    expect(formatarMoeda(null)).toBe('—')
    expect(formatarMoeda(undefined)).toBe('—')
  })
})

describe('formatarData', () => {
  it('converte data ISO para formato brasileiro', () => {
    expect(formatarData('2026-08-15')).toBe('15/08/2026')
  })

  it('retorna travessão quando a data é nula', () => {
    expect(formatarData(null)).toBe('—')
  })
})
