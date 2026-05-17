export type TelemetryPoint = {
  lap: number
  pace: number
  sector1: number
  sector2: number
  sector3: number
}

export type LiveTelemetrySnapshot = {
  lapNumber: number
  sectorTime: string
  tyreWear: number
  ersBattery: number
  paceTrend: TelemetryPoint[]
  insight: string
}