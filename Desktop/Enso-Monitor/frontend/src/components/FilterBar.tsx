import type { DateRange } from '../types'

interface FilterBarProps {
  dateRange: DateRange
  onChange: (range: DateRange) => void
}

const PRESETS = [
  { label: '10 ans', years: 10 },
  { label: '30 ans', years: 30 },
  { label: '50 ans', years: 50 },
  { label: 'Tout',   years: 0  },
]

function toISODate(date: Date): string {
  return date.toISOString().split('T')[0]
}

export function FilterBar({ dateRange, onChange }: FilterBarProps) {
  const today = toISODate(new Date())

  function applyPreset(years: number) {
    if (years === 0) {
      onChange({ start: '1950-01-01', end: today })
    } else {
      const start = new Date()
      start.setFullYear(start.getFullYear() - years)
      onChange({ start: toISODate(start), end: today })
    }
  }

  return (
    <div className="filter-row">

      <span className="filter-title">Période</span>

      <label htmlFor="start-date" className="filter-sep">Du</label>
      <input
        id="start-date"
        type="date"
        value={dateRange.start}
        min="1950-01-01"
        max={dateRange.end}
        onChange={e => onChange({ ...dateRange, start: e.target.value })}
      />

      <label htmlFor="end-date" className="filter-sep">au</label>

      <input
        id="end-date"
        type="date"
        value={dateRange.end}
        min={dateRange.start}
        max={today}
        onChange={e => onChange({ ...dateRange, end: e.target.value })}
      />

      <div className="presets">
        {PRESETS.map(p => (
          <button key={p.label} onClick={() => applyPreset(p.years)}>
            {p.label}
          </button>
        ))}
      </div>

    </div>
  )
}
