import { useState, useEffect } from 'react'
import type { EpisodeDetail, EpisodeSummary } from '../types'

const API_BASE = '/api/v1'

interface UseEpisodesResult {
  episodes: EpisodeSummary[]
  loading: boolean
  error: string | null
}

export function useEpisodes(): UseEpisodesResult {
  const [episodes, setEpisodes] = useState<EpisodeSummary[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetch(`${API_BASE}/episodes/`)
      .then(r => {
        if (!r.ok) throw new Error(`Erreur API : ${r.status}`)
        return r.json()
      })
      .then(setEpisodes)
      .catch(e => setError(e instanceof Error ? e.message : 'Erreur inconnue'))
      .finally(() => setLoading(false))
  }, [])

  return { episodes, loading, error }
}

export async function fetchEpisodeDetail(id: number): Promise<EpisodeDetail> {
  const r = await fetch(`${API_BASE}/episodes/${id}`)
  if (!r.ok) throw new Error(`Erreur API : ${r.status}`)
  return r.json()
}
