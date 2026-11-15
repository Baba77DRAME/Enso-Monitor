export interface Observation {
  id: number
  season: string
  year: number
  period_start: string // "YYYY-MM-DD"
  sst_total: number | null
  oni: number
  source: string
}

export interface ObservationPage {
  total: number
  page: number
  page_size: number
  results: Observation[]
}

export interface DateRange {
  start: string
  end: string
}

export type Phase = 'el_nino' | 'la_nina' | 'neutral'

export interface Stats {
  current: Observation | null
  max: Observation | null
  min: Observation | null
  phase: Phase
  totalCount: number
}
