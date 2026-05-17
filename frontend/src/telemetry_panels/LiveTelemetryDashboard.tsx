import {
  Area,
  AreaChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import type { LiveTelemetrySnapshot, TelemetryPoint } from '../types/telemetry'

type MetricCardProps = {
  label: string
  value: string
  accent: 'ers' | 'pit' | 'telemetry'
  helper?: string
}

type InsightCardProps = {
  title: string
  message: string
}

const defaultSnapshot: LiveTelemetrySnapshot = {
  lapNumber: 12,
  sectorTime: '1:24.816',
  tyreWear: 37,
  ersBattery: 68,
  paceTrend: [
    { lap: 8, pace: 92.1, sector1: 31.2, sector2: 29.8, sector3: 31.1 },
    { lap: 9, pace: 91.4, sector1: 31.0, sector2: 29.6, sector3: 30.8 },
    { lap: 10, pace: 90.7, sector1: 30.8, sector2: 29.4, sector3: 30.5 },
    { lap: 11, pace: 90.3, sector1: 30.7, sector2: 29.2, sector3: 30.4 },
    { lap: 12, pace: 89.8, sector1: 30.5, sector2: 29.0, sector3: 30.3 },
  ],
  insight: 'Tyre overheating risk detected in the rear axle. Recommend a short lift-and-coast window.',
}

const accentMap = {
  ers: 'text-ers',
  pit: 'text-pit',
  telemetry: 'text-telemetry',
}

function MetricCard({ label, value, accent, helper }: MetricCardProps) {
  return (
    <article className="rounded-2xl border border-carbon-700 bg-carbon-850/90 p-4 shadow-panel shadow-black/20">
      <p className="text-[11px] uppercase tracking-[0.24em] text-slate-500">{label}</p>
      <div className={`mt-3 text-3xl font-semibold tracking-tight ${accentMap[accent]}`}>{value}</div>
      {helper ? <p className="mt-2 text-sm text-slate-400">{helper}</p> : null}
    </article>
  )
}

function InsightCard({ title, message }: InsightCardProps) {
  return (
    <article className="rounded-2xl border border-telemetry/30 bg-telemetry/10 p-4 shadow-panel shadow-black/20">
      <div className="flex items-center justify-between gap-3">
        <div>
          <p className="text-[11px] uppercase tracking-[0.24em] text-telemetry-soft">AI Insight</p>
          <h3 className="mt-2 text-base font-semibold text-slate-50">{title}</h3>
        </div>
        <div className="rounded-full border border-telemetry/25 bg-carbon-900 px-2.5 py-1 text-[11px] uppercase tracking-[0.18em] text-telemetry-soft">
          Priority
        </div>
      </div>
      <p className="mt-3 max-w-prose text-sm leading-6 text-slate-300">{message}</p>
    </article>
  )
}

type PaceChartTooltipProps = {
  active?: boolean
  payload?: Array<{ value?: number }>
  label?: string | number
}

function PaceChartTooltip({ active, payload, label }: PaceChartTooltipProps) {
  if (!active || !payload?.length) {
    return null
  }

  return (
    <div className="rounded-xl border border-carbon-700 bg-carbon-900/95 px-3 py-2 shadow-panel shadow-black/30">
      <p className="text-xs uppercase tracking-[0.22em] text-slate-500">Lap {label}</p>
      <p className="mt-1 text-sm text-ers">Pace: {payload[0]?.value ?? 0} s</p>
    </div>
  )
}

type LiveTelemetryDashboardProps = {
  snapshot?: LiveTelemetrySnapshot
}

function formatSectorTime(sectorTime: string) {
  return sectorTime
}

function getTrendGradientId() {
  return 'paceTrendGradient'
}

export default function LiveTelemetryDashboard({ snapshot = defaultSnapshot }: LiveTelemetryDashboardProps) {
  const trendData: TelemetryPoint[] = snapshot.paceTrend

  return (
    <section className="grid gap-4 xl:grid-cols-[minmax(0,1.15fr)_minmax(0,0.85fr)]">
      <div className="grid gap-4">
        <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
          <MetricCard label="Lap Number" value={String(snapshot.lapNumber)} accent="ers" helper="Current stint" />
          <MetricCard label="Sector Timing" value={formatSectorTime(snapshot.sectorTime)} accent="pit" helper="Last sector average" />
          <MetricCard label="Tyre Wear" value={`${snapshot.tyreWear}%`} accent="telemetry" helper="Rear axle focus" />
          <MetricCard label="ERS / Battery" value={`${snapshot.ersBattery}%`} accent="ers" helper="Deploy headroom" />
        </div>

        <div className="min-w-0 rounded-3xl border border-carbon-700 bg-panel-gradient p-5 shadow-panel shadow-black/20">
          <div className="mb-4 flex items-start justify-between gap-4">
            <div>
              <h2 className="text-base font-semibold text-slate-50">Pace Trend</h2>
              <p className="text-sm text-slate-400">A restrained performance graph for race engineering review</p>
            </div>
            <div className="rounded-full border border-carbon-700 bg-carbon-900 px-3 py-1 text-[11px] uppercase tracking-[0.2em] text-pit">
              Live Pace
            </div>
          </div>

          <div className="w-full min-w-0">
            <ResponsiveContainer width="100%" height={288}>
              <AreaChart data={trendData} margin={{ top: 8, right: 8, left: 0, bottom: 0 }}>
                <defs>
                  <linearGradient id={getTrendGradientId()} x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#19f28a" stopOpacity={0.32} />
                    <stop offset="95%" stopColor="#19f28a" stopOpacity={0.02} />
                  </linearGradient>
                </defs>
                <CartesianGrid stroke="rgba(148, 163, 184, 0.12)" strokeDasharray="3 6" vertical={false} />
                <XAxis dataKey="lap" stroke="#64748b" tickLine={false} axisLine={false} tick={{ fill: '#94a3b8', fontSize: 12 }} />
                <YAxis stroke="#64748b" tickLine={false} axisLine={false} tick={{ fill: '#94a3b8', fontSize: 12 }} width={44} domain={[84, 95]} />
                <Tooltip content={<PaceChartTooltip />} cursor={{ stroke: 'rgba(25, 242, 138, 0.2)' }} />
                <Area
                  type="monotone"
                  dataKey="pace"
                  stroke="#19f28a"
                  strokeWidth={2.5}
                  fill={`url(#${getTrendGradientId()})`}
                  dot={false}
                  activeDot={{ r: 4, stroke: '#19f28a', strokeWidth: 2, fill: '#050607' }}
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      <div className="grid gap-4">
        <InsightCard title="Tyre overheating risk detected" message={snapshot.insight} />

        <div className="rounded-3xl border border-carbon-700 bg-carbon-850/90 p-5 shadow-panel shadow-black/20">
          <div className="flex items-start justify-between gap-4">
            <div>
              <h3 className="text-sm font-semibold text-slate-100">Sector Split</h3>
              <p className="text-xs text-slate-400">Balanced for quick engineer review</p>
            </div>
            <span className="rounded-full border border-carbon-700 bg-carbon-900 px-2.5 py-1 text-[11px] uppercase tracking-[0.18em] text-slate-300">
              Clean view
            </span>
          </div>

          <div className="mt-4 grid gap-3">
            {trendData.slice(-3).map((point) => (
              <div key={point.lap} className="rounded-2xl border border-carbon-700 bg-carbon-800/75 px-4 py-3">
                <div className="flex items-center justify-between text-sm text-slate-300">
                  <span>Lap {point.lap}</span>
                  <span className="text-ers">{point.pace.toFixed(1)} s pace</span>
                </div>
                <div className="mt-3 grid grid-cols-3 gap-2 text-xs text-slate-400">
                  <div className="rounded-lg bg-carbon-900 px-2 py-2">S1 {point.sector1.toFixed(1)}</div>
                  <div className="rounded-lg bg-carbon-900 px-2 py-2">S2 {point.sector2.toFixed(1)}</div>
                  <div className="rounded-lg bg-carbon-900 px-2 py-2">S3 {point.sector3.toFixed(1)}</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  )
}