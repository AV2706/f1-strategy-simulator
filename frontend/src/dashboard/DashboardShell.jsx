import { lazy, Suspense } from 'react'
import RaceCommandSidebar from './RaceCommandSidebar'
import useTelemetryStream from '../websocket_handlers/useTelemetryStream'

const LiveTelemetryDashboard = lazy(() => import('../telemetry_panels/LiveTelemetryDashboard'))

function buildSnapshot(telemetry, history) {
  const lapNumber = Math.max(1, history.length + 7)
  const basePace = Math.max(84.2, 95 - telemetry.speedKmh / 18)
  const sectorTime = `${Math.floor(basePace / 60)}:${(basePace % 60).toFixed(3).padStart(6, '0')}`

  const paceTrend = history.map((sample, index) => {
    const lap = lapNumber - history.length + index + 1
    const pace = Number((basePace + (sample - 50) * 0.03).toFixed(1))
    const sector1 = Number((30.8 + (sample - 50) * 0.01).toFixed(1))
    const sector2 = Number((29.4 + (telemetry.throttlePercent - 50) * 0.01).toFixed(1))
    const sector3 = Number((30.5 + (telemetry.engineRpm - 9000) / 1800).toFixed(1))

    return { lap, pace, sector1, sector2, sector3 }
  })

  const tyreWear = Math.min(100, Math.round(18 + telemetry.throttlePercent * 0.22 + history.at(-1) * 0.15))
  const ersBattery = Math.max(5, Math.round(100 - telemetry.throttlePercent * 0.38 - telemetry.speedKmh * 0.04))

  return {
    lapNumber,
    sectorTime,
    tyreWear,
    ersBattery,
    paceTrend,
    insight:
      tyreWear > 42
        ? 'Tyre overheating risk detected in the rear axle. Recommend a short lift-and-coast window.'
        : 'Car balance looks stable. Hold current strategy and monitor ERS deploy consistency.',
  }
}

export default function DashboardShell() {
  const { telemetry, history, connectionState } = useTelemetryStream()
  const snapshot = buildSnapshot(telemetry, history)

  return (
    <div className="min-h-screen bg-carbon-950 text-slate-100">
      <div className="grid min-h-screen grid-cols-1 xl:grid-cols-[320px_minmax(0,1fr)]">
        <RaceCommandSidebar connectionState={connectionState} />

        <main className="flex min-h-screen flex-col bg-shell-gradient px-4 py-4 sm:px-6 lg:px-8">
          <header className="mb-5 flex flex-col gap-4 rounded-2xl border border-carbon-700 bg-carbon-850/80 px-5 py-4 shadow-panel shadow-black/20 md:flex-row md:items-center md:justify-between">
            <div>
              <div className="text-xs uppercase tracking-[0.28em] text-slate-500">Race Command Center</div>
              <h2 className="mt-1 text-2xl font-semibold tracking-tight text-slate-50">Telemetry Dashboard Shell</h2>
              <p className="mt-1 text-sm text-slate-400">
                A restrained, engineer-friendly interface for live race simulation oversight.
              </p>
            </div>

            <div className="grid grid-cols-3 gap-3 text-sm">
              <div className="rounded-xl border border-carbon-700 bg-carbon-900 px-3 py-2 text-center">
                <div className="text-[11px] uppercase tracking-[0.2em] text-slate-500">Session</div>
                <div className="mt-1 text-slate-100">Practice</div>
              </div>
              <div className="rounded-xl border border-carbon-700 bg-carbon-900 px-3 py-2 text-center">
                <div className="text-[11px] uppercase tracking-[0.2em] text-slate-500">Lap</div>
                <div className="mt-1 text-slate-100">12</div>
              </div>
              <div className="rounded-xl border border-carbon-700 bg-carbon-900 px-3 py-2 text-center">
                <div className="text-[11px] uppercase tracking-[0.2em] text-slate-500">Track</div>
                <div className="mt-1 text-slate-100">Dry</div>
              </div>
            </div>
          </header>

          <section className="flex-1">
            <Suspense
              fallback={(
                <div className="grid gap-4 xl:grid-cols-[minmax(0,1.15fr)_minmax(0,0.85fr)]">
                  <div className="rounded-3xl border border-carbon-700 bg-carbon-850/90 p-5 shadow-panel shadow-black/20">
                    <div className="h-4 w-40 rounded bg-carbon-700" />
                    <div className="mt-3 h-3 w-72 max-w-full rounded bg-carbon-800" />
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
