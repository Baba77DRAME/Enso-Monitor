import { useState } from 'react'
import { Loader2, AlertCircle } from 'lucide-react'
import { useEpisodes, fetchEpisodeDetail } from '../hooks/useEpisodes'
import { EpisodeSelector } from '../components/EpisodeSelector'
import { ComparisonChart } from '../components/ComparisonChart'
import type { EpisodeDetail } from '../types'

const PHASE_LABELS: Record<string, string> = {
  el_nino: 'El Niño',
  la_nina: 'La Niña',
}

function EpisodeStats({ episode, color }: { episode: EpisodeDetail; color: string }) {
  const sign = (v: number) => (v >= 0 ? '+' : '')
  return (
    <div className="episode-stats">
      <div className="stats-lines">
        <p className="stat-line">
          <span className="stat-line-label">Type</span>
          <span className="stat-line-value" style={{ color }}>{PHASE_LABELS[episode.type]}</span>
        </p>
        <p className="stat-line">
          <span className="stat-line-label">Période</span>
          <span className="stat-line-value" style={{ fontSize: 15 }}>
            {episode.start_season} {episode.start_year} → {episode.end_season} {episode.end_year}
          </span>
        </p>
        <p className="stat-line">
          <span className="stat-line-label">Durée</span>
          <span className="stat-line-value">{episode.duration}</span>
          <span className="stat-line-sub">saisons</span>
        </p>
        <p className="stat-line">
          <span className="stat-line-label">Pic</span>
          <span className="stat-line-value" style={{ color }}>
            {sign(episode.peak_oni)}{episode.peak_oni.toFixed(2)} °C
          </span>
          <span className="stat-line-sub">{episode.peak_season} {episode.peak_year}</span>
        </p>
      </div>
    </div>
  )
}

export function Comparison() {
  const { episodes, loading: loadingList, error: errorList } = useEpisodes()

  const [id1, setId1] = useState<number | null>(null)
  const [id2, setId2] = useState<number | null>(null)
  const [detail1, setDetail1] = useState<EpisodeDetail | null>(null)
  const [detail2, setDetail2] = useState<EpisodeDetail | null>(null)
  const [loadingDetail, setLoadingDetail] = useState(false)
  const [errorDetail, setErrorDetail] = useState<string | null>(null)

  async function handleSelect(slot: 1 | 2, id: number) {
    if (slot === 1) setId1(id)
    else setId2(id)

    setLoadingDetail(true)
    setErrorDetail(null)
    try {
      const detail = await fetchEpisodeDetail(id)
      if (slot === 1) setDetail1(detail)
      else setDetail2(detail)
    } catch (e) {
      setErrorDetail(e instanceof Error ? e.message : 'Erreur inconnue')
    } finally {
      setLoadingDetail(false)
    }
  }

  return (
    <main className="main">
      <h2 className="page-title">Comparaison d'épisodes <em>ENSO</em></h2>
      <p className="page-subtitle">
        Sélectionnez deux épisodes historiques pour comparer leur évolution.
        Les séries sont alignées depuis le début de chaque épisode, non par date calendaire.
      </p>

      {loadingList && (
        <div className="loading">
          <Loader2 size={18} className="spin" />
          <span>Chargement des épisodes…</span>
        </div>
      )}

      {errorList && (
        <div className="error-box">
          <AlertCircle size={18} />
          <strong>Impossible de charger les épisodes.</strong>
          <p>{errorList}</p>
        </div>
      )}

      {!loadingList && !errorList && (
        <>
          {/* Sélecteurs */}
          <div className="comparison-selectors">
            <EpisodeSelector
              episodes={episodes}
              value={id1}
              onChange={id => handleSelect(1, id)}
              label="Épisode A"
            />
            <EpisodeSelector
              episodes={episodes}
              value={id2}
              onChange={id => handleSelect(2, id)}
              label="Épisode B"
            />
          </div>

          {loadingDetail && (
            <div className="loading">
              <Loader2 size={18} className="spin" />
              <span>Chargement…</span>
            </div>
          )}

          {errorDetail && (
            <div className="error-box">
              <AlertCircle size={18} />
              <strong>Erreur lors du chargement de l'épisode.</strong>
              <p>{errorDetail}</p>
            </div>
          )}

          {/* Statistiques côte à côte */}
          {(detail1 || detail2) && (
            <div className="comparison-stats">
              <div>
                {detail1 ? <EpisodeStats episode={detail1} color="#ea580c" /> : <p className="comparison-placeholder">Épisode A non sélectionné</p>}
              </div>
              <div>
                {detail2 ? <EpisodeStats episode={detail2} color="#1d4ed8" /> : <p className="comparison-placeholder">Épisode B non sélectionné</p>}
              </div>
            </div>
          )}

          {/* Graphique comparatif */}
          {detail1 && detail2 && (
            <ComparisonChart episode1={detail1} episode2={detail2} />
          )}

          {/* Interprétation */}
          {detail1 && detail2 && (
            <div className="interpretation-box">
              <p className="interpretation-title">Lecture des résultats</p>
              <p>
                L'axe horizontal représente le rang de la saison au sein de chaque épisode
                (saison 1 = première saison dépassant le seuil ±0.5 °C), pas une date calendaire.
                Deux épisodes de durées différentes ne partagent donc aucun repère temporel commun.
              </p>
              <p className="interpretation-limits">Limites à garder en tête :</p>
              <ul>
                <li>L'algorithme applique le critère NOAA strictement : 5 saisons consécutives sans interruption. NOAA publie parfois des classifications différentes pour les épisodes mixtes.</li>
                <li>L'indice ONI mesure une anomalie régionale (Niño 3.4). Il ne capte pas les variabilités locales ni les événements Modoki (El Niño à déplacement ouest).</li>
                <li>Une ressemblance de forme entre deux courbes n'implique pas que les impacts climatiques ont été identiques.</li>
                <li>Les données NOAA sont révisées périodiquement : les valeurs historiques peuvent changer légèrement d'une version à l'autre.</li>
              </ul>
            </div>
          )}

          {/* Invitation à sélectionner */}
          {!detail1 && !detail2 && !loadingDetail && (
            <div className="no-data">
              Sélectionnez deux épisodes pour comparer leur évolution.
            </div>
          )}
        </>
      )}
    </main>
  )
}
