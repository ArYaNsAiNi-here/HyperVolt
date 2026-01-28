import { AIForecast, AIRecommendation, SensorReading, GridData, EnergySource, Load, SourceSwitchEvent } from './types'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

class APIService {
  private baseURL: string

  constructor(baseURL: string = API_URL) {
    this.baseURL = baseURL
  }

  private async request<T>(endpoint: string, options?: RequestInit): Promise<T> {
    const url = `${this.baseURL}${endpoint}`
    const response = await fetch(url, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options?.headers,
      },
    })

    if (!response.ok) {
      throw new Error(`API Error: ${response.statusText}`)
    }

    return response.json()
  }

  // Sensor Readings
  async getSensorReadings(params?: { sensor_type?: string; limit?: number }) {
    const queryParams = new URLSearchParams()
    if (params?.sensor_type) queryParams.append('sensor_type', params.sensor_type)
    if (params?.limit) queryParams.append('limit', params.limit.toString())
    
    return this.request<{ results: SensorReading[] }>(`/api/sensor-readings/?${queryParams}`)
  }

  async getLatestSensorReading(sensorType: string) {
    return this.request<SensorReading>(`/api/sensor-readings/latest/?sensor_type=${sensorType}`)
  }

  // Grid Data
  async getGridData(params?: { data_type?: string; limit?: number }) {
    const queryParams = new URLSearchParams()
    if (params?.data_type) queryParams.append('data_type', params.data_type)
    if (params?.limit) queryParams.append('limit', params.limit.toString())
    
    return this.request<{ results: GridData[] }>(`/api/grid-data/?${queryParams}`)
  }

  async getCurrentCarbonIntensity() {
    return this.request<GridData>(`/api/grid-data/current_carbon_intensity/`)
  }

  async getCurrentWeather() {
    return this.request<GridData>(`/api/grid-data/current_weather/`)
  }

  // Energy Sources
  async getEnergySources() {
    return this.request<{ results: EnergySource[] }>(`/api/energy-sources/`)
  }

  async getAvailableSources() {
    return this.request<EnergySource[]>(`/api/energy-sources/available/`)
  }

  // Loads
  async getLoads() {
    return this.request<{ results: Load[] }>(`/api/loads/`)
  }

  async getCriticalLoads() {
    return this.request<Load[]>(`/api/loads/critical/`)
  }

  // Switch Events
  async getSwitchEvents(limit?: number) {
    const queryParams = limit ? `?limit=${limit}` : ''
    return this.request<{ results: SourceSwitchEvent[] }>(`/api/switch-events/${queryParams}`)
  }

  // AI Endpoints
  async getAIStatus() {
    return this.request<{ available: boolean; models_loaded: boolean }>(`/api/ai/status/`)
  }

  async getAIForecast(hours: number = 6) {
    return this.request<AIForecast>(`/api/ai/forecast/?hours=${hours}`)
  }

  async recommendSource(data: {
    load_name: string
    load_priority?: number
    load_power?: number
  }) {
    return this.request<AIRecommendation>(`/api/ai/recommend_source/`, {
      method: 'POST',
      body: JSON.stringify(data),
    })
  }

  async makeAIDecision() {
    return this.request<{
      timestamp: string
      forecast: any[]
      current_decision: any
      recommendation: string
      available: boolean
    }>(`/api/ai/decide/`, {
      method: 'POST',
    })
  }

  // Energy Optimization
  async optimizeSource(data: { loads: any[] }) {
    return this.request<any>(`/api/optimization/recommend/`, {
      method: 'POST',
      body: JSON.stringify(data),
    })
  }

  // User Preferences
  async getUserPreferences() {
    return this.request<any>(`/api/preferences/`)
  }

  async updatePreference(key: string, value: any) {
    return this.request<any>(`/api/preferences/${key}/`, {
      method: 'PATCH',
      body: JSON.stringify({ preference_value: value }),
    })
  }
}

export const apiService = new APIService()
export default apiService
