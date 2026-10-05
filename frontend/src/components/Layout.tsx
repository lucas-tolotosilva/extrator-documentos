import { NavLink, Outlet } from 'react-router-dom'
import { useEffect, useState } from 'react'
import { api } from '../lib/api'

export function Layout() {
  const [modoDemonstracao, setModoDemonstracao] = useState<boolean | null>(null)

  useEffect(() => {
    api
      .obterConfig()
      .then((config) => setModoDemonstracao(config.modo_demonstracao))
      .catch(() => setModoDemonstracao(true))
  }, [])

  return (
    <div className="app-shell">
      <header className="topbar">
        <div className="topbar-titulo">
          <span className="topbar-icone">📄</span>
          <span>Extrator Inteligente de Documentos</span>
        </div>
        <nav className="topbar-nav">
          <NavLink to="/" end className={({ isActive }) => (isActive ? 'ativo' : '')}>
            Upload
          </NavLink>
          <NavLink to="/revisao" className={({ isActive }) => (isActive ? 'ativo' : '')}>
            Revisão
          </NavLink>
          <NavLink to="/dashboard" className={({ isActive }) => (isActive ? 'ativo' : '')}>
            Dashboard
          </NavLink>
        </nav>
      </header>

      {modoDemonstracao && (
        <div className="banner-demo">
          🧪 Modo demonstração ativo — extração por heurística local, sem custo de API. Configure
          <code> GROQ_API_KEY </code> (gratuito) para usar um modelo de linguagem real.
        </div>
      )}

      <main className="conteudo">
        <Outlet />
      </main>
    </div>
  )
}
