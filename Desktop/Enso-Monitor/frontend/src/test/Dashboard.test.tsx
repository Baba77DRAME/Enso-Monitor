/**
 * Tests du composant Dashboard.
 *
 * IMPORTANT : les données utilisées ici sont des FIXTURES DE TEST.
 * Elles ne représentent pas des valeurs ONI officielles.
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { Dashboard } from '../pages/Dashboard'

// ---------------------------------------------------------------------------
// Fixtures de test (données fictives, identifiées comme telles)
// ---------------------------------------------------------------------------
const FIXTURE_PAGE_1 = {
  total: 3,
  page: 1,
  page_size: 200,
  results: [
    { id: 1, season: 'DJF', year: 2010, period_start: '2010-01-01', sst_total: 26.5, oni: 1.4,  source: 'TEST' },
    { id: 2, season: 'JJA', year: 2015, period_start: '2015-07-01', sst_total: 28.0, oni: -0.7, source: 'TEST' },
    { id: 3, season: 'DJF', year: 2020, period_start: '2020-01-01', sst_total: 27.0, oni: 0.2,  source: 'TEST' },
  ],
}

const FIXTURE_FILTERED = {
  total: 1,
  page: 1,
  page_size: 200,
  results: [
    { id: 2, season: 'JJA', year: 2015, period_start: '2015-07-01', sst_total: 28.0, oni: -0.7, source: 'TEST' },
  ],
}

// ---------------------------------------------------------------------------
// Mock de fetch
// ---------------------------------------------------------------------------
beforeEach(() => {
  vi.restoreAllMocks()
})

function mockFetch(payload: object) {
  vi.stubGlobal(
    'fetch',
    vi.fn().mockResolvedValue({
      ok: true,
      json: async () => payload,
    })
  )
}

// ---------------------------------------------------------------------------
// Test 1 : chargement initial — les statistiques sont affichées
// ---------------------------------------------------------------------------
it('affiche les statistiques après chargement', async () => {
  mockFetch(FIXTURE_PAGE_1)
  render(<Dashboard />)

  await waitFor(() => {
    expect(screen.getByText('Dernière observation')).toBeInTheDocument()
    expect(screen.getByText('Phase actuelle')).toBeInTheDocument()
    expect(screen.getByText('Observations')).toBeInTheDocument()
  })
})

// ---------------------------------------------------------------------------
// Test 2 : état de chargement visible
// ---------------------------------------------------------------------------
it('affiche un indicateur de chargement', async () => {
  // fetch qui ne se résout jamais
  vi.stubGlobal('fetch', vi.fn(() => new Promise(() => {})))
  render(<Dashboard />)
  expect(screen.getByText(/chargement/i)).toBeInTheDocument()
})

// ---------------------------------------------------------------------------
// Test 3 : état d'erreur visible
// ---------------------------------------------------------------------------
it("affiche un message d'erreur si l'API est inaccessible", async () => {
  vi.stubGlobal(
    'fetch',
    vi.fn().mockRejectedValue(new Error('Network Error'))
  )
  render(<Dashboard />)
  await waitFor(() => {
    expect(screen.getByText(/impossible de charger/i)).toBeInTheDocument()
  })
})

// ---------------------------------------------------------------------------
// Test 4 : changement de période → nouvelle requête fetch
// ---------------------------------------------------------------------------
it('envoie une nouvelle requête fetch quand la période change', async () => {
  const fetchMock = vi.fn().mockResolvedValue({
    ok: true,
    json: async () => FIXTURE_FILTERED,
  })
  vi.stubGlobal('fetch', fetchMock)

  render(<Dashboard />)
  await waitFor(() => screen.getByText('Observations'))

  const callsBefore = fetchMock.mock.calls.length

  // Changer la date de début
  const startInput = screen.getByLabelText('Du')
  fireEvent.change(startInput, { target: { value: '2014-01-01' } })

  await waitFor(() => {
    expect(fetchMock.mock.calls.length).toBeGreaterThan(callsBefore)
  })
})

// ---------------------------------------------------------------------------
// Test 5 : zéro résultat → pas d'erreur, message "Aucune observation"
// ---------------------------------------------------------------------------
it('affiche "Aucune observation" quand la période ne contient pas de données', async () => {
  mockFetch({ total: 0, page: 1, page_size: 200, results: [] })
  render(<Dashboard />)
  await waitFor(() => {
    expect(screen.getByText(/aucune observation/i)).toBeInTheDocument()
  })
})

// ===========================================================================
// TEST FONCTIONNEL 3 — FRONTEND (exigé)
// Vérifier que le changement de période met à jour les valeurs affichées.
// ===========================================================================

it('[FONCTIONNEL 3] les valeurs affichées se mettent à jour quand la période change', async () => {
  /**
   * Scénario :
   * 1. Chargement initial → FIXTURE_PAGE_1
   *    → dernière obs DJF 2020 (oni=0.2) → phase = Neutre
   * 2. Changement de date de début → FIXTURE_FILTERED
   *    → dernière obs JJA 2015 (oni=-0.7) → phase = La Niña
   * On vérifie que la phase affichée change, prouvant que les données
   * sont bien mises à jour et pas simplement gardées en cache.
   */
  const fetchMock = vi.fn()
    .mockResolvedValueOnce({ ok: true, json: async () => FIXTURE_PAGE_1 })
    .mockResolvedValue({ ok: true, json: async () => FIXTURE_FILTERED })

  vi.stubGlobal('fetch', fetchMock)
  render(<Dashboard />)

  // État initial : phase Neutre (DJF 2020, oni=0.2 est entre -0.5 et +0.5)
  await waitFor(() => {
    expect(screen.getByText('Neutre')).toBeInTheDocument()
  })

  // Changer la date de début → déclenche un nouveau fetch
  const startInput = screen.getByLabelText('Du')
  fireEvent.change(startInput, { target: { value: '2014-01-01' } })

  // Après le refetch : phase La Niña (JJA 2015, oni=-0.7 ≤ -0.5)
  await waitFor(() => {
    expect(screen.getByText('La Niña')).toBeInTheDocument()
    // La phase précédente ne doit plus être affichée
    expect(screen.queryByText('Neutre')).not.toBeInTheDocument()
  })
})
