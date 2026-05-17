import { useEffect, useMemo, useRef, useState } from 'react'

const TELEMETRY_WS_URL = import.meta.env.VITE_TELEMETRY_WS_URL || 'wss://exception-manhole-oxygen.ngrok-free.dev/ws'

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

const FALLBACK_HISTORY = [
  42, 44, 45, 47, 50, 54, 58, 61, 67, 70, 72, 74,
]

function toTelemetryFrame(raw) {
  return {
    speedKmh: Number(raw.speed_kmh ?? raw.speedKmh ?? 0),
    engineRpm: Number(raw.engine_rpm ?? raw.engineRpm ?? 0),
    gear: Number(raw.gear ?? 0),
    throttlePercent: Number(raw.throttle_percent ?? raw.throttlePercent ?? 0),
    brakeBias: Number(raw.brake_bias ?? 58.5),
    ersDeploy: Number(raw.ers_deploy ?? 24),
    tireTempFrontLeft: Number(raw.tire_temp_fl ?? 92),
    tireTempFrontRight: Number(raw.tire_temp_fr ?? 94),
    tireTempRearLeft: Number(raw.tire_temp_rl ?? 88),
    tireTempRearRight: Number(raw.tire_temp_rr ?? 89),
  }
}

export default function useTelemetryStream() {
  const [telemetry, setTelemetry] = useState(FALLBACK_TELEMETRY)
  const [connectionState, setConnectionState] = useState('offline')
  const [history, setHistory] = useState(FALLBACK_HISTORY)
  const wsRef = useRef(null)

  const wsUrl = useMemo(() => {
    if (typeof window === 'undefined') {
      return TELEMETRY_WS_URL
    }

    return TELEMETRY_WS_URL
  }, [])

  useEffect(() => {
    let cancelled = false

    try {
      const ws = new WebSocket(wsUrl)
      wsRef.current = ws
      setConnectionState('connecting')

      ws.onopen = () => {
        if (!cancelled) {
          setConnectionState('live')
        }
      }

      ws.onmessage = (event) => {
        try {
          const parsed = JSON.parse(event.data)
          const frame = toTelemetryFrame(parsed)
          const sample = Math.max(0, Math.min(100, Math.round(frame.throttlePercent || 0)))

          if (!cancelled) {
            setTelemetry(frame)
            setHistory((current) => [...current.slice(-11), sample || Math.round(frame.speedKmh / 4)])
          }
        } catch {
          if (!cancelled) {
            setConnectionState('degraded')
          }
        }
      }

      ws.onerror = () => {
        if (!cancelled) {
          setConnectionState('degraded')
        }
      }

      ws.onclose = () => {
        if (!cancelled) {
          setConnectionState('offline')
        }
      }
    } catch {
      setConnectionState('offline')
    }

    return () => {
      cancelled = true
      if (wsRef.current) {
        try {
          wsRef.current.close()
        } catch {
          // ignore shutdown errors
        }
      }
    }
  }, [wsUrl])

  return {
    telemetry,
    history,
    connectionState,
  }
}
