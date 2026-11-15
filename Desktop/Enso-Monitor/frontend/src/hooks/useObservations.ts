import { useState, useEffect, useCallback } from 'react'
import type { ObservationPage, DateRange, Stats, Phase } from '../types'

const API_BASE = '/api/v1'

function getPhase(oni: number): Phase {
  if (oni >= 0.5) return 'el_nino'
  if (oni <= -0.5) return 'la_nina'
  return 'neutral'
}

interface UseObservationsResult {
  data: ObservationPage | null
  stats: Stats | null
  loading: boolean
  error: string | null
  refetch: () => void
}

export function useObservations(
  dateRange: DateRange,
  pageSize: number = 500
): UseObservationsResult {
  const [data, setData] = useState<ObservationPage | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchData = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const params = new URLSearchParams({
        start_date: dateRange.start,
        end_date: dateRange.end,
        page_size: String(pageSize),
      })
      const response = await fetch(`${API_BASE}/observations?${params}`)
      if (!response.ok) {
        throw new Error(`Erreur API : ${response.status} ${response.statusText}`)
      }
      const json: ObservationPage = await response.json()
      setData(json)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erreur inconnue')
    } finally {
      setLoading(false)
    }
  }, [dateRange.start, dateRange.end, pageSize])

  useEffect(() => {
    fetchData()
  }, [fetchData])

  const stats: Stats | null = data
    ? (() => {
        const results = data.results
        if (results.length === 0) return null
        const last = results[results.length - 1]
        const maxObs = results.reduce((a, b) => (a.oni > b.oni ? a : b))
        const minObs = results.reduce((a, b) => (a.oni < b.oni ? a : b))
        return {
          current: last,
          max: maxObs,
          min: minObs,
          phase: getPhase(last.oni),
          totalCount: data.total,
        }
      })()
    : null

  return { data, stats, loading, error, refetch: fetchData }
}
