import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ReferenceLine,
  Legend,
} from 'recharts'
import type { EpisodeDetail } from '../types'

interface ComparisonChartProps {
  episode1: EpisodeDetail
  episode2: EpisodeDetail
}

interface ComparisonPoint {
  offset: number
  oni1?: number
  oni2?: number
  label1?: string
  label2?: string
}

interface TooltipPayload {
  dataKey: string
  value: number
  payload: ComparisonPoint
  color: string
  name: string
}

function buildComparisonData(ep1: EpisodeDetail, ep2: EpisodeDetail): ComparisonPoint[] {
  const maxLen = Math.max(ep1.observations.length, ep2.observations.length)
  const points: ComparisonPoint[] = []

  for (let i = 0; i < maxLen; i++) {
    const point: ComparisonPoint = { offset: i + 1 }
    if (ep1.observations[i]) {
      point.oni1 = Number(ep1.observations[i].oni)
      point.label1 = `${ep1.observations[i].season} ${ep1.observations[i].year}`
    }
    if (ep2.observations[i]) {
      point.oni2 = Number(ep2.observations[i].oni)
      point.label2 = `${ep2.observations[i].season} ${ep2.observations[i].year}`
    }
    points.push(point)
  }
  return points
}

function episodeLabel(ep: EpisodeDetail): string {
  const type = ep.type === 'el_nino' ? 'El Niño' : 'La Niña'
  return `${type} ${ep.start_year}`
}

function CustomTooltip({
  active,
  payload,
  episode1,
  episode2,
}: {
  active?: boolean
  payload?: TooltipPayload[]
  episode1: EpisodeDetail
  episode2: EpisodeDetail
}) {
  if (!active || !payload || payload.length === 0) return null

  const point = payload[0].payload

  return (
    <div style={{
      background: '#fff',
      border: '1px solid #e7e5e4',
      borderRadius: 8,
      padding: '10px 14px',
      fontSize: 12,
    }}>
      <p style={{ fontWeight: 700, marginBottom: 6 }}>Saison {point.offset}</p>
      {point.label1 !== undefined && (
        <p style={{ color: '#ea580c' }}>
          {episodeLabel(episode1)} — {point.label1} : {point.oni1 !== undefined ? `${point.oni1 >= 0 ? '+' : ''}${point.oni1.toFixed(2)} °C` : '—'}
        </p>
      )}
      {point.label2 !== undefined && (
        <p style={{ color: '#1d4ed8' }}>
          {episodeLabel(episode2)} — {point.label2} : {point.oni2 !== undefined ? `${point.oni2 >= 0 ? '+' : ''}${point.oni2.toFixed(2)} °C` : '—'}
        </p>
      )}
    </div>
  )
}

export function ComparisonChart({ episode1, episode2 }: ComparisonChartProps) {
  const data = buildComparisonData(episode1, episode2)

  return (
    <div className="chart-box">
      <p className="chart-title">Comparaison ONI — alignement depuis le début de chaque épisode</p>
      <ResponsiveContainer width="100%" height={340}>
        <LineChart data={data} margin={{ top: 10, right: 20, left: 0, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#eee" />
          <XAxis
            dataKey="offset"
            tick={{ fontSize: 11 }}
            tickLine={false}
            label={{ value: 'Saison n° depuis le début', position: 'insideBottom', offset: -2, fontSize: 10, fill: '#8a8a8a' }}
          />
          <YAxis
            tick={{ fontSize: 11 }}
            tickLine={false}
            axisLine={false}
            tickFormatter={v => `${v > 0 ? '+' : ''}${v}`}
          />
          <Tooltip content={<CustomTooltip episode1={episode1} episode2={episode2} />} />
          <ReferenceLine y={0.5}  stroke="#c2410c" strokeDasharray="4 4" />
          <ReferenceLine y={-0.5} stroke="#1e40af" strokeDasharray="4 4" />
          <ReferenceLine y={0}    stroke="#ccc" />
          <Line
            type="monotone"
            dataKey="oni1"
            stroke="#ea580c"
            strokeWidth={2}
            dot={false}
            activeDot={{ r: 4 }}
            name={episodeLabel(episode1)}
            connectNulls={false}
          />
          <Line
            type="monotone"
            dataKey="oni2"
            stroke="#1d4ed8"
            strokeWidth={2}
            dot={false}
            activeDot={{ r: 4 }}
            name={episodeLabel(episode2)}
            connectNulls={false}
          />
          <Legend wrapperStyle={{ fontSize: 12, paddingTop: 8 }} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}
