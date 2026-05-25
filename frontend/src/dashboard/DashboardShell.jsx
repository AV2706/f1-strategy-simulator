import { lazy, Suspense, useEffect, useState } from 'react'
import RaceCommandSidebar from './RaceCommandSidebar'
import useTelemetryStream from '../websocket_handlers/useTelemetryStream'

const LiveTelemetryDashboard = lazy(() => import('../telemetry_panels/LiveTelemetryDashboard'))

// ── Backend URL — single source of truth ─────────────────────────────────────
const BACKEND_URL =
  import.meta.env.VITE_BACKEND_URL || 'https://backendserver-2eul.onrender.com'

// ── AI Insight — calls our backend /ai-insight (API key is safe on server) ───
async function fetchAiInsight(telemetry, tyreWear, ersBattery, lap) {
  try {
    const prompt = `You are an F1 race engineer AI. Analyze this live telemetry and give a short, precise tactical insight (max 2 sentences):
- Lap: ${lap}
- Speed: ${telemetry.speedKmh} km/h
- Engine RPM: ${telemetry.engineRpm}
- Gear: ${telemetry.gear}
- Throttle: ${telemetry.throttlePercent}%
- ERS Battery: ${ersBattery}%
- Tyre Wear: ${tyreWear}%
- ERS Deploy: ${telemetry.ersDeploy}%
Give a direct race engineering recommendation.`

    const response = await fetch(`${BACKEND_URL}/ai-insight`, {
      method:  'POST',
      headers: { 'Content-Type': 'application/json' },
      body:    JSON.stringify({ prompt }),
    })

    const data = await response.json()
    return data?.insight || null

  } catch (err) {
    console.warn('AI insight fetch failed:', err)
    return null
  }
}

// ── Build snapshot from live telemetry ───────────────────────────────────────
function buildSnapshot(telemetry, history, aiInsight, lapNumber) {
  const basePace   = Math.max(84.2, 95 - telemetry.speedKmh / 18)
  const sectorTime = `${Math.floor(basePace / 60)}:${(basePace % 60).toFixed(3).padStart(6, '0')}`

  const paceTrend = history.map((sample, index) => {
    const lap     = lapNumber - history.length + index + 1
    const pace    = Number((basePace + (sample - 50) * 0.03).toFixed(1))
    const sector1 = Number((30.8 + (sample - 50) * 0.01).toFixed(1))
    const sector2 = Number((29.4 + (telemetry.throttlePercent - 50) * 0.01).toFixed(1))
    const sector3 = Number((30.5 + (telemetry.engineRpm - 9000) / 1800).toFixed(1))
    return { lap, pace, sector1, sector2, sector3 }
  })

  const tyreWear   = Math.min(100, Math.round(18 + telemetry.throttlePercent * 0.22 + (history.at(-1) ?? 50) * 0.15))
  const ersBattery = Math.max(5,   Math.round(100 - telemetry.throttlePercent * 0.38 - telemetry.speedKmh * 0.04))

  const fallbackInsight = tyreWear > 42
    ? 'Tyre overheating risk detected in the rear axle. Recommend a short lift-and-coast window.'
    : 'Car balance looks stable. Hold current strategy and monitor ERS deploy consistency.'

  return {
    lapNumber,
    sectorTime,
    tyreWear,
    ersBattery,
    paceTrend,
    insight: aiInsight || fallbackInsight,
  }
}

export default function DashboardShell() {
  const { telemetry, history, connectionState } = useTelemetryStream()
  const [aiInsight, setAiInsight] = useState('System initializing — waiting for telemetry...')
  const [lastAiLap, setLastAiLap] = useState(0)

  const lapNumber  = telemetry.lap ?? Math.max(1, history.length + 1)
  const tyreWear   = Math.min(100, Math.round(18 + telemetry.throttlePercent * 0.22 + (history.at(-1) ?? 50) * 0.15))
  const ersBattery = Math.max(5,   Math.round(100 - telemetry.throttlePercent * 0.38 - telemetry.speedKmh * 0.04))

  // ── Fetch AI insight every 5 laps when live ───────────────────────────────
  useEffect(() => {
    if (connectionState !== 'live') return
    if (telemetry.speedKmh === 0)   return
    if (lapNumber - lastAiLap < 5 && lastAiLap !== 0) return

    setLastAiLap(lapNumber)
    setAiInsight('Analyzing telemetry...')

    fetchAiInsight(telemetry, tyreWear, ersBattery, lapNumber).then((insight) => {
      if (insight) {
        setAiInsight(insight)
      } else {
        setAiInsight(
          tyreWear > 42
            ? 'Tyre overheating risk detected. Recommend lift-and-coast.'
            : 'Car balance stable. Monitor ERS deployment.'
        )
      }
    })
  }, [lapNumber, connectionState])

  const snapshot = buildSnapshot(telemetry, history, aiInsight, lapNumber)

  return (
    <div className="min-h-screen bg-carbon-950 text-slate-100">
      <div className="grid min-h-screen grid-cols-1 xl:grid-cols-[320px_minmax(0,1fr)]">
        <RaceCommandSidebar connectionState={connectionState} />

        <main className="flex min-h-screen flex-col bg-shell-gradient px-4 py-4 sm:px-6 lg:px-8">
          <header className="mb-5 flex flex-col gap-4 rounded-2xl border border-carbon-700 bg-carbon-850/80 px-5 py-4 shadow-panel shadow-black/20 md:flex-row md:items-center md:justify-between">
            <div>
              <div className="text-xs uppercase tracking-[0.28em] text-slate-500">Race Command Center</div>
              <h2 className="mt-1 text-2xl font-semibold tracking-tight text-slate-50">Telemetry Dashboard</h2>
              <p className="mt-1 text-sm text-slate-400">
                Live race simulation — AI insights refresh every 5 laps.
              </p>
            </div>

            <div className="grid grid-cols-3 gap-3 text-sm">
              <div className="rounded-xl border border-carbon-700 bg-carbon-900 px-3 py-2 text-center">
                <div className="text-[11px] uppercase tracking-[0.2em] text-slate-500">Session</div>
                <div className="mt-1 text-slate-100">Race</div>
              </div>
              <div className="rounded-xl border border-carbon-700 bg-carbon-900 px-3 py-2 text-center">
                <div className="text-[11px] uppercase tracking-[0.2em] text-slate-500">Lap</div>
                <div className="mt-1 text-slate-100">{lapNumber}</div>
              </div>
              <div className="rounded-xl border border-carbon-700 bg-carbon-900 px-3 py-2 text-center">
                <div className="text-[11px] uppercase tracking-[0.2em] text-slate-500">Status</div>
                <div className={`mt-1 ${connectionState === 'live' ? 'text-ers' : 'text-slate-400'}`}>
                  {connectionState === 'live'       ? 'Live'
                   : connectionState === 'connecting' ? 'Connecting...'
                   : connectionState === 'finished'   ? 'Finished 🏁'
                   : 'Offline'}
                </div>
              </div>
            </div>
          </header>

          <section className="flex-1">
            <Suspense
              fallback={(
                <div className="grid gap-4 xl:grid-cols-[minmax(0,1.15fr)_minmax(0,0.85fr)]">
                  <div className="rounded-3xl border border-carbon-700 bg-carbon-850/90 p-5">
                    <div className="h-4 w-40 rounded bg-carbon-700" />
                    <div className="mt-6 h-72 rounded-2xl border border-carbon-700 bg-carbon-900/80" />
                  </div>
                  <div className="grid gap-4">
                    <div className="h-28 rounded-2xl border border-carbon-700 bg-carbon-850/90" />
                    <div className="h-64 rounded-3xl border border-carbon-700 bg-carbon-850/90" />
                  </div>
                </div>
              )}
            >
              <LiveTelemetryDashboard snapshot={snapshot} />
            </Suspense>
          </section>
        </main>
      </div>
    </div>
  )
}
