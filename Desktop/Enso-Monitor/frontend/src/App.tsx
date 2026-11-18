import { useState } from 'react'
import { Thermometer } from 'lucide-react'
import { Dashboard } from './pages/Dashboard'
import { Comparison } from './pages/Comparison'

type Page = 'dashboard' | 'comparison'

function App() {
  const [page, setPage] = useState<Page>('dashboard')

  return (
    <div>
      <header className="header">
        <Thermometer size={22} />
        <h1>ENSO Monitor</h1>

        <nav className="header-nav">
          <button
            className={page === 'dashboard' ? 'active' : ''}
            onClick={() => setPage('dashboard')}
          >
            Dashboard
          </button>
          <button
            className={page === 'comparison' ? 'active' : ''}
            onClick={() => setPage('comparison')}
          >
            Comparaison
          </button>
        </nav>

        <span className="source">Source : NOAA CPC — ONI v6</span>
      </header>

      {page === 'dashboard' ? <Dashboard /> : <Comparison />}
    </div>
  )
}

export default App
