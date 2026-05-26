import { useEffect, useMemo, useRef, useState } from 'react'

const TELEMETRY_WS_URL = import.meta.env.VITE_TELEMETRY_WS_URL || 'wss://backendserver-2eul.onrender.com/ws'

const FALLBACK_TELEMETRY = {
  speedKmh: 0,
  engineRpm: 0,
  gear: 0,
  throttlePercent: 0,
  brakeBias: 58.5,
  ersDeploy: 24,
  tireTempFrontLeft: 92,
  tireTempFrontRight: 94,
  tireTempRearLeft: 88,
  tireTempRearRight: 89,
}

const FALLBACK_HISTORY = [42, 44, 45, 47, 50, 54, 58, 61, 67, 70, 72, 74]

function toTelemetryFrame(raw) {
  return {
    speedKmh:           Number(raw.speed_kmh          ?? raw.speedKmh          ?? 0),
    engineRpm:          Number(raw.engine_rpm          ?? raw.engineRpm         ?? 0),
    gear:               Number(raw.gear                ?? 0),
    throttlePercent:    Number(raw.throttle_percent    ?? raw.throttlePercent   ?? 0),
    brakeBias:          Number(raw.brake_bias          ?? 58.5),
    ersDeploy:          Number(raw.ers_deploy          ?? 24),
    tireTempFrontLeft:  Number(raw.tire_temp_fl        ?? 92),
    tireTempFrontRight: Number(raw.tire_temp_fr        ?? 94),
    tireTempRearLeft:   Number(raw.tire_temp_rl        ?? 88),
    tireTempRearRight:  Number(raw.tire_temp_rr        ?? 89),
    // Extra fields for DashboardShell
    lap:                Number(raw.lap                 ?? 0),
    total_laps:         Number(raw.total_laps          ?? 57),
    tyre_wear:          Number(raw.tyre_wear           ?? 0),
    tyre_age:           Number(raw.tyre_age            ?? 0),
    compound:           raw.compound                   ?? 'SOFT',
    fuel_remaining:     Number(raw.fuel_remaining      ?? 0),
    ers_battery:        Number(raw.ers_battery         ?? raw.ers ?? 100),
    gap_to_leader:      Number(raw.gap_to_leader       ?? 0),
    optimal_pit_lap:    Number(raw.optimal_pit_lap     ?? 0),
    latest_safe_lap:    Number(raw.latest_safe_lap     ?? 0),
    pit_urgency:        raw.pit_urgency                ?? 'LOW',
    laps_remaining:     Number(raw.laps_remaining      ?? 0),
    speed:              Number(raw.speed               ?? raw.speed_kmh ?? 0),
    rpm:                Number(raw.rpm                 ?? raw.engine_rpm ?? 0),
    throttle:           Number(raw.throttle            ?? raw.throttle_percent ?? 0),
    drs:                raw.drs                        ?? false,
    brake_pressure:     Number(raw.brake_pressure      ?? 0),
  }
}

export default function useTelemetryStream() {
  const [telemetry,       setTelemetry]       = useState(FALLBACK_TELEMETRY)
  const [connectionState, setConnectionState] = useState('offline')
  const [history,         setHistory]         = useState(FALLBACK_HISTORY)

  const wsRef      = useRef(null)
  const retryRef   = useRef(null)
  const cancelRef  = useRef(false)

  const wsUrl = TELEMETRY_WS_URL

  function connect() {
    if (cancelRef.current) return

    // Wake up backend first via HTTP ping
    fetch(wsUrl.replace('wss://', 'https://').replace('/ws', ''))
      .catch(() => {}) // ignore errors — just wake it up

    try {
      const ws = new WebSocket(wsUrl)
      wsRef.current = ws
      setConnectionState('connecting')

      ws.onopen = () => {
        if (!cancelRef.current) {
          setConnectionState('live')
          // Clear any pending retry
          if (retryRef.current) {
            clearTimeout(retryRef.current)
            retryRef.current = null
          }
        }
      }

      ws.onmessage = (event) => {
        try {
          const parsed = JSON.parse(event.data)

          // Race finished — restart after 3 seconds
          if (parsed.status === 'RACE_FINISHED') {
            setConnectionState('finished')
            retryRef.current = setTimeout(() => {
              if (!cancelRef.current) connect()
            }, 3000)
            return
          }

          const frame  = toTelemetryFrame(parsed)
          const sample = Math.max(0, Math.min(100, Math.round(frame.throttlePercent || 0)))

          if (!cancelRef.current) {
            setTelemetry(frame)
            setHistory((current) => [
              ...current.slice(-11),
              sample || Math.round(frame.speedKmh / 4),
            ])
          }
        } catch {
          if (!cancelRef.current) setConnectionState('degraded')
        }
      }

      ws.onerror = () => {
        if (!cancelRef.current) setConnectionState('degraded')
      }

      ws.onclose = () => {
        if (!cancelRef.current) {
          setConnectionState('offline')
          // Auto reconnect after 3 seconds
          retryRef.current = setTimeout(() => {
            if (!cancelRef.current) connect()
          }, 3000)
        }
      }
    } catch {
      setConnectionState('offline')
      retryRef.current = setTimeout(() => {
        if (!cancelRef.current) connect()
      }, 3000)
    }
  }

  useEffect(() => {
    cancelRef.current = false
    connect()

    return () => {
      cancelRef.current = true
      if (retryRef.current) clearTimeout(retryRef.current)
      if (wsRef.current) {
        try { wsRef.current.close() } catch { }
      }
    }
  }, [])

  return { telemetry, history, connectionState }
}
