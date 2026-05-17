export default function TelemetrySparkline({ values = [] }) {
  const width = 320
  const height = 96
  const padding = 10

  const safeValues = values.length > 1 ? values : [20, 28, 34, 30, 38, 44, 40, 48]
  const min = Math.min(...safeValues)
  const max = Math.max(...safeValues)
  const range = Math.max(max - min, 1)

  const points = safeValues
    .map((value, index) => {
      const x = padding + (index * (width - padding * 2)) / (safeValues.length - 1)
      const y = height - padding - ((value - min) * (height - padding * 2)) / range
      return `${x},${y}`
    })
    .join(' ')

  return (
    <div className="rounded-xl border border-carbon-700 bg-carbon-850/70 p-4 shadow-panel shadow-black/20">
      <div className="mb-3 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold tracking-wide text-slate-100">Telemetry Trend</h3>
          <p className="text-xs text-slate-400">Low-noise overview for race operations</p>
        </div>
        <span className="rounded-full border border-carbon-700 bg-carbon-800 px-2 py-1 text-[11px] uppercase tracking-[0.18em] text-ers">
          Live
        </span>
      </div>

      <svg viewBox={`0 0 ${width} ${height}`} className="h-24 w-full" role="img" aria-label="Telemetry sparkline">
        <defs>
          <linearGradient id="sparklineFill" x1="0" x2="0" y1="0" y2="1">
            <stop offset="0%" stopColor="rgba(25, 242, 138, 0.35)" />
            <stop offset="100%" stopColor="rgba(25, 242, 138, 0.02)" />
          </linearGradient>
        </defs>
        <polyline
          fill="none"
          stroke="rgba(159, 252, 207, 0.28)"
          strokeWidth="2"
          points={points}
        />
        <polyline
          fill="url(#sparklineFill)"
          stroke="rgba(25, 242, 138, 0.95)"
          strokeWidth="2.5"
          strokeLinejoin="round"
          strokeLinecap="round"
          points={points}
        />
      </svg>
    </div>
  )
}
