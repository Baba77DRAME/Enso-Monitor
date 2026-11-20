/**
 * Tests du composant Comparison.
 *
 * IMPORTANT : les données utilisées ici sont des FIXTURES DE TEST.
 * Elles ne représentent pas des épisodes NOAA officiels.
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { Comparison } from '../pages/Comparison'

// ---------------------------------------------------------------------------
// Fixtures de test
// ---------------------------------------------------------------------------
const FIXTURE_EPISODES = [
  {
    id: 1,
    type: 'el_nino',
    start_season: 'DJF', start_year: 1997,
    end_season: 'MJJ',   end_year: 1997,
    duration: 6,
    peak_oni: 2.3, peak_season: 'MAM', peak_year: 1997,
  },
  {
    id: 2,
    type: 'la_nina',
    start_season: 'DJF', start_year: 1999,
    end_season: 'AMJ',   end_year: 1999,
    duration: 5,
    peak_oni: -1.2, peak_season: 'FMA', peak_year: 1999,
  },
]

const FIXTURE_EPISODE_1_DETAIL = {
  ...FIXTURE_EPISODES[0],
  observations: [
    { id: 10, season: 'DJF', year: 1997, period_start: '1997-01-01', oni: 1.2, sst_total: 28.0, source: 'TEST' },
    { id: 11, season: 'JFM', year: 1997, period_start: '1997-02-01', oni: 1.6, sst_total: 28.1, source: 'TEST' },
    { id: 12, season: 'FMA', year: 1997, period_start: '1997-03-01', oni: 1.9, sst_total: 28.2, source: 'TEST' },
    { id: 13, season: 'MAM', year: 1997, period_start: '1997-04-01', oni: 2.3, sst_total: 28.3, source: 'TEST' },
    { id: 14, season: 'AMJ', year: 1997, period_start: '1997-05-01', oni: 2.1, sst_total: 28.1, source: 'TEST' },
    { id: 15, season: 'MJJ', year: 1997, period_start: '1997-06-01', oni: 1.8, sst_total: 27.9, source: 'TEST' },
  ],
}

const FIXTURE_EPISODE_2_DETAIL = {
  ...FIXTURE_EPISODES[1],
  observations: [
    { id: 20, season: 'DJF', year: 1999, period_start: '1999-01-01', oni: -0.8,  sst_total: 26.5, source: 'TEST' },
    { id: 21, season: 'JFM', year: 1999, period_start: '1999-02-01', oni: -1.0,  sst_total: 26.3, source: 'TEST' },
    { id: 22, season: 'FMA', year: 1999, period_start: '1999-03-01', oni: -1.2,  sst_total: 26.1, source: 'TEST' },
    { id: 23, season: 'MAM', year: 1999, period_start: '1999-04-01', oni: -1.1,  sst_total: 26.2, source: 'TEST' },
    { id: 24, season: 'AMJ', year: 1999, period_start: '1999-05-01', oni: -0.9,  sst_total: 26.4, source: 'TEST' },
  ],
}

// ---------------------------------------------------------------------------
// Setup
// ---------------------------------------------------------------------------
beforeEach(() => {
  vi.restoreAllMocks()
})

function mockEpisodesApi(detailMap: Record<number, object> = {}) {
  vi.stubGlobal(
    'fetch',
    vi.fn((url: string) => {
      const matchDetail = url.match(/\/episodes\/(\d+)$/)
      if (matchDetail) {
        const id = Number(matchDetail[1])
        const detail = detailMap[id]
        return Promise.resolve({
          ok: !!detail,
          status: detail ? 200 : 404,
          json: async () => detail ?? { detail: 'Not found' },
        })
      }
      // Liste des épisodes
      return Promise.resolve({
        ok: true,
        json: async () => FIXTURE_EPISODES,
      })
    })
  )
}

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

it('affiche les sélecteurs d\'épisodes après chargement', async () => {
  mockEpisodesApi()
  render(<Comparison />)

  await waitFor(() => {
    expect(screen.getByLabelText('Épisode A')).toBeInTheDocument()
    expect(screen.getByLabelText('Épisode B')).toBeInTheDocument()
  })
})

it('affiche les épisodes dans les sélecteurs', async () => {
  mockEpisodesApi()
  render(<Comparison />)

  await waitFor(() => {
    // Les deux types apparaissent dans les options des selects (getAllBy car présents 2x)
    expect(screen.getAllByText(/El Niño/).length).toBeGreaterThan(0)
    expect(screen.getAllByText(/La Niña/).length).toBeGreaterThan(0)
  })
})

it('affiche l\'état de chargement initial', () => {
  vi.stubGlobal('fetch', vi.fn(() => new Promise(() => {})))
  render(<Comparison />)
  expect(screen.getByText(/chargement/i)).toBeInTheDocument()
})

it('affiche les statistiques de l\'épisode A après sélection', async () => {
  mockEpisodesApi({ 1: FIXTURE_EPISODE_1_DETAIL })
  render(<Comparison />)

  await waitFor(() => screen.getByLabelText('Épisode A'))

  fireEvent.change(screen.getByLabelText('Épisode A'), {
    target: { value: '1' },
  })

  await waitFor(() => {
    // "Durée" et "Pic" sont des labels exclusifs à la section stats (pas dans les options)
    expect(screen.getByText('Durée')).toBeInTheDocument()
    expect(screen.getByText('Pic')).toBeInTheDocument()
    // Vérifier la valeur de durée : 6 saisons
    expect(screen.getByText('6')).toBeInTheDocument()
  })
})

it('affiche le graphique comparatif quand les deux épisodes sont sélectionnés', async () => {
  mockEpisodesApi({
    1: FIXTURE_EPISODE_1_DETAIL,
    2: FIXTURE_EPISODE_2_DETAIL,
  })
  render(<Comparison />)

  await waitFor(() => screen.getByLabelText('Épisode A'))

  fireEvent.change(screen.getByLabelText('Épisode A'), { target: { value: '1' } })
  // Attendre que les stats de l'épisode A soient affichées
  await waitFor(() => screen.getByText('Durée'))

  fireEvent.change(screen.getByLabelText('Épisode B'), { target: { value: '2' } })

  await waitFor(() => {
    // Le bloc interprétation n'apparaît que quand les deux épisodes sont chargés
    expect(screen.getByText(/lecture des résultats/i)).toBeInTheDocument()
  })
})

it('affiche les limites méthodologiques dans la section interprétation', async () => {
  mockEpisodesApi({
    1: FIXTURE_EPISODE_1_DETAIL,
    2: FIXTURE_EPISODE_2_DETAIL,
  })
  render(<Comparison />)

  await waitFor(() => screen.getByLabelText('Épisode A'))
  fireEvent.change(screen.getByLabelText('Épisode A'), { target: { value: '1' } })
  await waitFor(() => screen.getByText('Durée'))
  fireEvent.change(screen.getByLabelText('Épisode B'), { target: { value: '2' } })

  await waitFor(() => {
    // La section limites doit être visible (texte présent dans Comparison.tsx)
    expect(screen.getByText(/limites à garder en tête/i)).toBeInTheDocument()
    // Vérifier qu'une limite spécifique est présente
    expect(screen.getByText(/5 saisons consécutives/i)).toBeInTheDocument()
  })
})
