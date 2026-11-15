interface StatCardProps {
  label: string
  value: string | number
  sub?: string
  accent?: 'blue' | 'orange' | 'teal' | 'neutral'
}

export function StatCard({ label, value, sub, accent = 'blue' }: StatCardProps) {
  return (
    <div className={`stat-card ${accent}`}>
      <p className="stat-label">{label}</p>
      <p className="stat-value">{value}</p>
      {sub && <p className="stat-sub">{sub}</p>}
    </div>
  )
}
