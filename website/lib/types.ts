// API Response Types
export interface SensorReading {
  id: number
  sensor_type: 'ldr' | 'current' | 'temperature' | 'humidity' | 'voltage'
  sensor_id: string
  value: number
  unit: string
  location: string
  timestamp: string
  created_at: string
}

export interface GridData {
  id: number
  data_type: 'carbon_intensity' | 'weather' | 'electricity_price'
  value: number
  unit: string
  zone: string
  metadata: Record<string, any>
  timestamp: string
  created_at: string
}

export interface AIDecision {
  id: number
  decision_type: 'power_source' | 'light_dim' | 'load_shift' | 'general'
  decision: Record<string, any>
  confidence: number
  reasoning: string
  applied: boolean
  timestamp: string
  created_at: string
}

export interface EnergySource {
  id: number
  name: string
  source_type: 'solar' | 'battery' | 'grid'
  current_output: number
  max_capacity: number
  efficiency: number
  carbon_intensity: number
  cost_per_kwh: number
  is_available: boolean
  metadata: Record<string, any>
  last_updated: string
}

export interface Load {
  id: number
  name: string
  load_type: string
  power_watts: number
  priority: number
  is_critical: boolean
  current_source: string
  is_active: boolean
  location: string
  metadata: Record<string, any>
  last_updated: string
}

export interface SourceSwitchEvent {
  id: number
  from_source: string
  to_source: string
  reason: string
  power_watts: number
  load_name: string
  success: boolean
  metadata: Record<string, any>
  timestamp: string
  created_at: string
}

// WebSocket Message Types
export interface WebSocketMessage {
  type: 'sensor_update' | 'source_switch' | 'ai_decision' | 'error' | 'echo'
  data?: any
  message?: string
  payload: any;
}

// AI Forecast Types
export interface ForecastPrediction {
  hour: number
  predicted_kwh: number
  timestamp: string
}

export interface AIForecast {
  timestamp: string
  forecast_horizon: number
  predictions: ForecastPrediction[]
  available: boolean
  model_type: string
}

// AI Recommendation Types
export interface SourceAllocation {
  source: string
  power: number
}

export interface AIRecommendation {
  timestamp: string
  load_name: string
  load_priority: number
  load_power: number
  recommended_source: string
  source_allocation: [string, number][]
  metrics: {
    estimated_cost: number
    estimated_carbon: number
    battery_charge: number
  }
  reasoning: string
  confidence: number
  algorithm: string
  available: boolean
}

// Dashboard State Types
export interface DashboardState {
  activeSource: 'solar' | 'battery' | 'grid'
  sensorReadings: {
    ldr: number
    current: number
    temperature: number
    humidity: number
    voltage: number
  }
  energySources: {
    solar: { output: number; available: boolean }
    battery: { charge: number; output: number; available: boolean }
    grid: { output: number; available: boolean }
  }
  carbonSavings: number
  costSavings: number
  lastUpdate: string
}

// UI Component Props
export interface EnergyFlowProps {
  activeSource: 'solar' | 'battery' | 'grid'
  solarOutput: number
  batteryOutput: number
  gridOutput: number
  homeConsumption: number
}

export interface StrategyLogEntry {
  id: string
  timestamp: string
  type: 'info' | 'warning' | 'success' | 'decision'
  message: string
  details?: string
}
