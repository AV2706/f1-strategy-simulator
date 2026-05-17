export default function TelemetrySummaryPanel({ telemetry }) {
  const items = [
    { label: 'Speed', value: `${telemetry.speedKmh} km/h`, tone: 'ers' },
    { label: 'RPM', value: `${telemetry.engineRpm}`, tone: 'telemetry' },
    { label: 'Gear', value: `${telemetry.gear}`, tone: 'pit' },
    { label: 'Throttle', value: `${telemetry.throttlePercent}%`, tone: 'ers' },
  ]

  return (
    <section className="rounded-2xl border border-carbon-700 bg-panel-gradient p-5 shadow-panel shadow-black/20">
      <div className="mb-4 flex items-start justify-between gap-4">
        <div>
          <h2 className="text-base font-semibold text-slate-100">Telemetry Summary</h2>
          <p className="text-sm text-slate-400">Primary race metrics at a glance</p>
        </div>
        <div className="rounded-full border border-carbon-700 bg-carbon-800 px-3 py-1 text-xs uppercase tracking-[0.22em] text-ers">
          Active Feed
        </div>
      </div>

      <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 xl:grid-cols-4">
        {items.map((item) => (
          <div key={item.label} className="rounded-xl border border-carbon-700 bg-carbon-800/80 px-4 py-3">
            <div className="text-xs uppercase tracking-[0.2em] text-slate-500">{item.label}</div>
            <div className={`mt-2 text-xl font-semibold ${item.tone === 'pit' ? 'text-pit' : item.tone === 'telemetry' ? 'text-telemetry' : 'text-ers'}`}>
              {item.value}
            </div>
          </div>
        ))}
      </div>
    </section>
  )
}
