import { useState } from 'react'
import { Loader2, Thermometer, AlertCircle } from 'lucide-react'
import { useObservations } from '../hooks/useObservations'
import { FilterBar } from '../components/FilterBar'
import { OniChart } from '../components/OniChart'
import type { DateRange, Phase } from '../types'

const PHASE_LABELS: Record<Phase, string> = {
  el_nino: 'El Niño',
  la_nina: 'La Niña',
  neutral: 'Neutre',
}

const PHASE_COLORS: Record<Phase, string> = {
  el_nino: '#ea580c',
  la_nina: '#1d4ed8',
  neutral: '#525252',
}

export function Dashboard() {
  const today = new Date().toISOString().split('T')[0]
  const tenYearsAgo = (() => {
    const d = new Date()
    d.setFullYear(d.getFullYear() - 10)
    return d.toISOString().split('T')[0]
  })()

  const [dateRange, setDateRange] = useState<DateRange>({
    start: tenYearsAgo,
    end: today,
  })

  const { data, stats, loading, error } = useObservations(dateRange, 200)

  return (
    <div>

      {/* Header */}
      <header className="header">
        <Thermometer size={22} />
        <h1>ENSO Monitor</h1>
        <span className="source">Source : NOAA CPC — ONI v6</span>
      </header>

      <main className="main">

        <h2 className="page-title">Indice ONI — Oceanic Niño Index</h2>
        <p className="page-subtitle">
          Anomalie de température de surface de la mer dans la région Niño 3.4.
          Données officielles NOAA, moyennes glissantes sur 3 mois.
        </p>

        {/* Filtres */}
        <FilterBar dateRange={dateRange} onChange={setDateRange} />

        {/* Chargement */}
        {loading && (
          <div className="loading">
            <Loader2 size={20} className="spin" />
            <span>Chargement des données NOAA…</span>
          </div>
        )}

        {/* Erreur */}
        {error && !loading && (
          <div className="error-box">
            <AlertCircle size={18} />
            <strong> Impossible de charger les données.</strong>
            <p>{error}</p>
            <p>Vérifiez que l'API FastAPI est démarrée sur le port 8000.</p>
          </div>
        )}

        {/* Contenu */}
        {!loading && !error && data && (
          <>
            {/* Statistiques en lignes */}
            {stats && (
              <div className="stats-lines">
                <p className="stat-line">
                  <span className="stat-line-label">Dernière observation</span>
                  <span className="stat-line-value">
                    {stats.current!.oni >= 0 ? '+' : ''}{Number(stats.current!.oni).toFixed(2)} °C
                  </span>
                  <span className="stat-line-sub">{stats.current!.season} {stats.current!.year}</span>
                </p>
                <p className="stat-line">
                  <span className="stat-line-label">Phase actuelle</span>
                  <span className="stat-line-value">
                    {PHASE_LABELS[stats.phase]}
                  </span>
                  <span className="stat-line-sub">seuil ±0.5 °C</span>
                </p>
                <p className="stat-line">
                  <span className="stat-line-label">Maximum</span>
                  <span className="stat-line-value">
                    +{Number(stats.max!.oni).toFixed(2)} °C
                  </span>
                  <span className="stat-line-sub">{stats.max!.season} {stats.max!.year}</span>
                </p>
                <p className="stat-line">
                  <span className="stat-line-label">Minimum</span>
                  <span className="stat-line-value">
                    {Number(stats.min!.oni).toFixed(2)} °C
                  </span>
                  <span className="stat-line-sub">{stats.min!.season} {stats.min!.year}</span>
                </p>
                <p className="stat-line">
                  <span className="stat-line-label">Observations</span>
                  <span className="stat-line-value">{stats.totalCount}</span>
                  <span className="stat-line-sub">saisons de 3 mois</span>
                </p>
              </div>
            )}

            {/* Graphique */}
            <OniChart observations={data.results} />

            {/* Attribution */}
            <p className="footer-note">
              Données : NOAA CPC — Oceanic Niño Index v6 —{' '}
              <a
                href="https://www.cpc.ncep.noaa.gov/products/analysis_monitoring/enso/oni/v6/index.php"
                target="_blank"
                rel="noopener noreferrer"
              >
                cpc.ncep.noaa.gov
              </a>
            </p>
          </>
        )}
      </main>
    </div>
  )
}
