const TELEMETRY_WS_URL = import.meta.env.VITE_TELEMETRY_WS_URL || 'wss://backendserver-production-d286.up.railway.app/ws'

const actions = [
  { label: 'Session mode', value: 'Practice' },
  { label: 'Fuel target', value: 'Auto' },
  { label: 'ERS strategy', value: 'Balanced' },
  { label: 'Pit window', value: 'Lap 18-22' },
]

const controls = [
  'Driver radio',
  'Pit confirmation',
  'Telemetry notes',
]

export default function RaceCommandSidebar({ connectionState = 'offline' }) {
  return (
    <aside className="flex h-full flex-col gap-6 bg-carbon-900/95 p-5 text-slate-100 shadow-panel shadow-black/30">
      <div>
        <div className="text-xs uppercase tracking-[0.32em] text-slate-500">Race Command</div>
        <h1 className="mt-2 text-2xl font-semibold tracking-tight text-slate-50">Command Center</h1>
        <p className="mt-2 text-sm leading-6 text-slate-400">
          Clean operational controls for engineering and strategy without visual noise.
        </p>
      </div>

      <div className="rounded-2xl border border-carbon-700 bg-shell-gradient p-4 shadow-insetPanel">
        <div className="flex items-center justify-between">
          <span className="text-sm font-medium text-slate-200">Telemetry Link</span>
          <span
            className={[
              'rounded-full px-2.5 py-1 text-[11px] uppercase tracking-[0.2em]',
              connectionState === 'live'
                ? 'bg-ers/10 text-ers'
                : connectionState === 'degraded'
                  ? 'bg-telemetry/10 text-telemetry'
                  : 'bg-pit/10 text-pit',
            ].join(' ')}
          >
            {connectionState}
          </span>
        </div>
        <p className="mt-3 text-sm text-slate-400">WS feed: {TELEMETRY_WS_URL}</p>
      </div>

      <div className="space-y-3">
        {actions.map((action) => (
          <div key={action.label} className="flex items-center justify-between rounded-xl border border-carbon-700 bg-carbon-850 px-4 py-3">
            <span className="text-sm text-slate-400">{action.label}</span>
            <span className="text-sm font-medium text-slate-100">{action.value}</span>
          </div>
        ))}
      </div>

      <div className="rounded-2xl border border-carbon-700 bg-carbon-850/80 p-4">
        <div className="text-sm font-medium text-slate-200">Quick Controls</div>
        <div className="mt-3 space-y-2">
          {controls.map((control) => (
            <button
              key={control}
              type="button"
              className="flex w-full items-center justify-between rounded-xl border border-carbon-700 bg-carbon-900/70 px-3 py-2 text-left text-sm text-slate-300"
            >
              <span>{control}</span>
              <span className="text-ers">Ready</span>
            </button>
          ))}
        </div>
      </div>
    </aside>
  )
}
