import {
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ReferenceLine,
  Legend,
} from 'recharts'
import type { Observation } from '../types'

interface OniChartProps {
  observations: Observation[]
}

interface TooltipPayload {
  value: number
  payload: Observation
}

function CustomTooltip({ active, payload }: { active?: boolean; payload?: TooltipPayload[] }) {
  if (!active || !payload || payload.length === 0) return null
  const obs = payload[0].payload
  const oni = Number(obs.oni)
  const color = oni >= 0.5 ? '#c2410c' : oni <= -0.5 ? '#1e40af' : '#333'
  return (
    <div style={{ background: '#fff', border: '1px solid #ccc', borderRadius: 6, padding: '10px 14px' }}>
      <p style={{ fontSize: 12, color: '#666' }}>{obs.season} {obs.year}</p>
      <p style={{ fontSize: 16, fontWeight: 'bold', color }}>
        ONI : {oni >= 0 ? '+' : ''}{oni.toFixed(2)} °C
      </p>
      {obs.sst_total !== null && (
        <p style={{ fontSize: 12, color: '#999' }}>
          SST : {Number(obs.sst_total).toFixed(2)} °C
        </p>
      )}
    </div>
  )
}

function formatXAxis(periodStart: string): string {
  return periodStart.split('-')[0]
}

export function OniChart({ observations }: OniChartProps) {
  if (observations.length === 0) {
    return <div className="no-data">Aucune observation pour cette période.</div>
  }

  const tickEvery = observations.length > 100 ? 60 : observations.length > 40 ? 24 : 12

  return (
    <div className="chart-box">
      <p className="chart-title">
        Anomalie ONI (°C) — Source : {observations[0]?.source ?? 'NOAA'}
      </p>
      <ResponsiveContainer width="100%" height={340}>
        <AreaChart data={observations} margin={{ top: 10, right: 20, left: 0, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#eee" />
          <XAxis
            dataKey="period_start"
            tickFormatter={formatXAxis}
            interval={tickEvery - 1}
            tick={{ fontSize: 11 }}
            tickLine={false}
          />
          <YAxis
            tick={{ fontSize: 11 }}
            tickLine={false}
            axisLine={false}
            tickFormatter={v => `${v > 0 ? '+' : ''}${v}`}
          />
          <Tooltip content={<CustomTooltip />} />
          <ReferenceLine y={0.5}  stroke="#c2410c" strokeDasharray="4 4" label={{ value: 'El Niño', position: 'right', fontSize: 10, fill: '#c2410c' }} />
          <ReferenceLine y={-0.5} stroke="#1e40af" strokeDasharray="4 4" label={{ value: 'La Niña', position: 'right', fontSize: 10, fill: '#1e40af' }} />
          <ReferenceLine y={0} stroke="#ccc" />
          <Area
            type="monotone"
            dataKey="oni"
            stroke="#1e3a5f"
            strokeWidth={1.5}
            fill="#dbeafe"
            dot={false}
            activeDot={{ r: 4 }}
            name="ONI"
          />
          <Legend wrapperStyle={{ fontSize: 12, paddingTop: 8 }} />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  )
}
