import { Route, Routes } from 'react-router-dom'
import { Layout } from './components/Layout'
import { UploadPage } from './pages/UploadPage'
import { RevisaoPage } from './pages/RevisaoPage'
import { DashboardPage } from './pages/DashboardPage'

function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route path="/" element={<UploadPage />} />
        <Route path="/revisao" element={<RevisaoPage />} />
        <Route path="/dashboard" element={<DashboardPage />} />
      </Route>
    </Routes>
  )
}

export default App
