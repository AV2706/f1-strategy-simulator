export default function TelemetryMetric({ label, value, detail, tone = 'ers' }) {
  const toneClasses = {
    ers: 'text-ers',
    pit: 'text-pit',
    telemetry: 'text-telemetry',
  }

  return (
    <article className="rounded-xl border border-carbon-700 bg-carbon-850/90 p-4 shadow-panel shadow-black/20">
      <div className="flex items-start justify-between gap-3">
        <div>
          <p className="text-xs uppercase tracking-[0.24em] text-slate-400">{label}</p>
          <div className={`mt-2 text-2xl font-semibold leading-none ${toneClasses[tone] || toneClasses.ers}`}>
            {value}
          </div>
        </div>
        {detail ? (
          <span className="rounded-full border border-carbon-700 bg-carbon-800 px-2 py-1 text-[11px] uppercase tracking-[0.18em] text-slate-300">
            {detail}
          </span>
        ) : null}
      </div>
    </article>
  )
}
