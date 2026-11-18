import type { EpisodeSummary } from '../types'

interface EpisodeSelectorProps {
  episodes: EpisodeSummary[]
  value: number | null
  onChange: (id: number) => void
  label: string
}

const PHASE_LABELS: Record<string, string> = {
  el_nino: 'El Niño',
  la_nina: 'La Niña',
}

export function EpisodeSelector({ episodes, value, onChange, label }: EpisodeSelectorProps) {
  return (
    <div className="episode-selector">
      <span className="episode-selector-label">{label}</span>
      <select
        value={value ?? ''}
        onChange={e => onChange(Number(e.target.value))}
        className="episode-select"
        aria-label={label}
      >
        <option value="" disabled>— choisir un épisode —</option>
        {episodes.map(ep => (
          <option key={ep.id} value={ep.id}>
            {PHASE_LABELS[ep.type]} {ep.start_season} {ep.start_year}
            {' → '}
            {ep.end_season} {ep.end_year}
            {' '}(pic {ep.peak_oni >= 0 ? '+' : ''}{ep.peak_oni.toFixed(2)} °C)
          </option>
        ))}
      </select>
    </div>
  )
}
