import { Routes, Route } from 'react-router-dom'
import Navbar from './components/Navbar'
import Sidebar from './components/Sidebar'
import Home from './pages/Home'
import MachineAnalysis from './pages/MachineAnalysis'
import './styles/dashboard.css'

function App() {
  return (
    <div className="app-shell">
      <Navbar />
      <div className="app-layout">
        <Sidebar />
        <main className="app-main">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/analysis" element={<MachineAnalysis />} />
          </Routes>
        </main>
      </div>
    </div>
  )
}

export default App
