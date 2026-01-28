'use client'

import { useState, useEffect, useCallback } from 'react'
import dynamic from 'next/dynamic'
import { Activity, Zap } from 'lucide-react'
import { useWebSocket } from '@/hooks/useWebSocket'
import apiService from '@/lib/api-service'
import { StrategyLogEntry, WebSocketMessage, ForecastPrediction } from '@/lib/types'
import StatsGrid from '@/components/StatsGrid'
import StrategyNarrator from '@/components/StrategyNarrator'
import EnergyChart from '@/components/EnergyChart'
import BrightnessControl from '@/components/BrightnessControl'

// Dynamic imports for 3D components (client-side only)
const DigitalTwin = dynamic(() => import('@/components/DigitalTwin'), {
  ssr: false,
  loading: () => (
    <div className="w-full h-full flex items-center justify-center bg-gray-900/50 rounded-lg">
      <div className="text-gray-500">Loading 3D View...</div>
    </div>
  ),
})

const EnergyFlow = dynamic(() => import('@/components/EnergyFlow'), {
  ssr: false,
  loading: () => (
    <div className="w-full h-full flex items-center justify-center bg-gray-900/50 rounded-lg">
      <div className="text-gray-500">Loading Energy Flow...</div>
    </div>
  ),
})

export default function Dashboard() {
  // State management
  const [activeSource, setActiveSource] = useState<'solar' | 'battery' | 'grid'>('grid')
  const [lightIntensity, setLightIntensity] = useState(50)
  const [brightnessThreshold, setBrightnessThreshold] = useState(50)
  const [weatherCondition, setWeatherCondition] = useState('sunny')
  const [strategyLogs, setStrategyLogs] = useState<StrategyLogEntry[]>([])
  const [forecastData, setForecastData] = useState<ForecastPrediction[]>([])
  const [stats, setStats] = useState({
    carbonSavings: 0,
    costSavings: 0,
    powerConsumption: 0,
    efficiency: 85,
  })
  const [energyOutputs, setEnergyOutputs] = useState({
    solar: 0,
    battery: 0,
    grid: 0,
    home: 0,
  })

  // WebSocket connection for real-time updates
  const { isConnected, lastMessage } = useWebSocket(undefined, {
    onMessage: handleWebSocketMessage,
    autoReconnect: true,
  })

  function handleWebSocketMessage(message: WebSocketMessage) {
    console.log('WebSocket message:', message)

    if (message.type === 'sensor_update' && message.data) {
      const { sensor_type, value, location } = message.data

      // Update sensor readings
      if (sensor_type === 'ldr') {
        setLightIntensity(Math.min(100, Math.max(0, value)))
        
        addLog({
          id: Date.now().toString(),
          timestamp: new Date().toISOString(),
          type: 'info',
          message: `Light intensity updated: ${value.toFixed(1)}%`,
        })
      }

      if (sensor_type === 'current') {
        setEnergyOutputs(prev => ({ ...prev, home: value / 1000 })) // Convert to kW
      }
    }

    if (message.type === 'source_switch' && message.data) {
      const { to_source, reason } = message.data
      setActiveSource(to_source as 'solar' | 'battery' | 'grid')
      
      addLog({
        id: Date.now().toString(),
        timestamp: new Date().toISOString(),
        type: 'decision',
        message: `Energy source switched to ${to_source.toUpperCase()}`,
        details: reason,
      })
    }

    if (message.type === 'ai_decision' && message.data) {
      addLog({
        id: Date.now().toString(),
        timestamp: new Date().toISOString(),
        type: 'success',
        message: message.data.reasoning || 'AI decision executed',
      })
    }
  }

  const addLog = useCallback((log: StrategyLogEntry) => {
    setStrategyLogs(prev => [...prev.slice(-50), log]) // Keep last 50 logs
  }, [])

  // Fetch initial data and AI forecast
  useEffect(() => {
    const fetchInitialData = async () => {
      try {
        // Check AI status
        const aiStatus = await apiService.getAIStatus()
        
        addLog({
          id: Date.now().toString(),
          timestamp: new Date().toISOString(),
          type: aiStatus.available ? 'success' : 'warning',
          message: aiStatus.available 
            ? 'AI models loaded successfully. Predictive engine online.'
            : 'AI models unavailable. Using rule-based optimization.',
        })

        // Get AI forecast if available
        if (aiStatus.available) {
          const forecast = await apiService.getAIForecast(6)
          setForecastData(forecast.predictions)
          
          addLog({
            id: (Date.now() + 1).toString(),
            timestamp: new Date().toISOString(),
            type: 'info',
            message: `AI forecast generated for next ${forecast.forecast_horizon} hours`,
          })
        }

        // Get energy sources status
        const sources = await apiService.getAvailableSources()
        const solarSource = sources.find(s => s.source_type === 'solar')
        const batterySource = sources.find(s => s.source_type === 'battery')
        const gridSource = sources.find(s => s.source_type === 'grid')

        setEnergyOutputs({
          solar: solarSource?.current_output || 0,
          battery: batterySource?.current_output || 0,
          grid: gridSource?.current_output || 0,
          home: 1.5, // Default value
        })

        // Get current carbon intensity
        const carbonData = await apiService.getCurrentCarbonIntensity()
        
        addLog({
          id: (Date.now() + 2).toString(),
          timestamp: new Date().toISOString(),
          type: 'info',
          message: `Grid carbon intensity: ${carbonData.value} ${carbonData.unit}`,
          details: carbonData.value > 400 ? 'High carbon intensity detected' : 'Clean energy available',
        })

        // Get current weather
        try {
          const weatherData = await apiService.getCurrentWeather()
          if (weatherData.metadata && weatherData.metadata.weather) {
            const weatherDesc = weatherData.metadata.weather.description || 'sunny'
            setWeatherCondition(weatherDesc.toLowerCase())
            
            addLog({
              id: (Date.now() + 3).toString(),
              timestamp: new Date().toISOString(),
              type: 'info',
              message: `Current weather: ${weatherDesc}`,
            })
          }
        } catch (error) {
          console.log('Weather data not available, using default sunny conditions')
          setWeatherCondition('sunny')
        }

      } catch (error) {
        console.error('Failed to fetch initial data:', error)
        addLog({
          id: Date.now().toString(),
          timestamp: new Date().toISOString(),
          type: 'warning',
          message: 'Failed to connect to backend API',
          details: 'Please ensure the Django backend is running',
        })
      }
    }

    fetchInitialData()
  }, [addLog])

  // Periodic data refresh
  useEffect(() => {
    const interval = setInterval(async () => {
      try {
        // Simulate stats update (in production, fetch from API)
        setStats(prev => ({
          ...prev,
          carbonSavings: prev.carbonSavings + Math.random() * 0.1,
          costSavings: prev.costSavings + Math.random() * 0.05,
          powerConsumption: 1.0 + Math.random() * 0.5,
        }))
      } catch (error) {
        console.error('Failed to refresh data:', error)
      }
    }, 5000) // Refresh every 5 seconds

    return () => clearInterval(interval)
  }, [])

  // Handle brightness threshold change
  const handleBrightnessChange = async (value: number) => {
    setBrightnessThreshold(value)
    
    try {
      await apiService.updatePreference('brightness_threshold', value)
      
      addLog({
        id: Date.now().toString(),
        timestamp: new Date().toISOString(),
        type: 'info',
        message: `Brightness threshold updated to ${value}%`,
      })
    } catch (error) {
      console.error('Failed to update preference:', error)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900">
      {/* Header */}
      <header className="border-b border-gray-700/50 bg-gray-900/80 backdrop-blur-sm sticky top-0 z-50">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg">
                <Zap className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-white">HyperVolt</h1>
                <p className="text-xs text-gray-400">AI-Driven Energy Orchestrator</p>
              </div>
            </div>
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-2 px-3 py-1.5 bg-gray-800 rounded-full border border-gray-700">
                <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-500 animate-pulse' : 'bg-red-500'}`} />
                <span className="text-xs text-gray-300">
                  {isConnected ? 'Connected' : 'Disconnected'}
                </span>
              </div>
              <div className="flex items-center gap-2 px-3 py-1.5 bg-gray-800 rounded-full border border-gray-700">
                <Activity className="w-4 h-4 text-blue-400" />
                <span className="text-xs text-gray-300">
                  {energyOutputs.home.toFixed(2)} kW
                </span>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Dashboard */}
      <main className="container mx-auto px-6 py-8">
        {/* Stats Grid */}
        <div className="mb-8">
          <StatsGrid
            carbonSavings={stats.carbonSavings}
            costSavings={stats.costSavings}
            powerConsumption={stats.powerConsumption}
            efficiency={stats.efficiency}
          />
        </div>

        {/* Main Grid Layout */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
          {/* Digital Twin - 3D Visualization */}
          <div className="lg:col-span-2">
            <div className="bg-gray-900/50 rounded-lg p-4 border border-gray-700/50">
              <h2 className="text-lg font-semibold text-white mb-4">Digital Twin - Real-time Room Model</h2>
              <div className="h-[400px]">
                <DigitalTwin 
                  lightIntensity={lightIntensity} 
                  activeSource={activeSource}
                  brightnessThreshold={brightnessThreshold}
                  weatherCondition={weatherCondition}
                  className="w-full h-full"
                />
              </div>
            </div>
          </div>

          {/* Brightness Control */}
          <div>
            <BrightnessControl
              value={brightnessThreshold}
              onChange={handleBrightnessChange}
            />
          </div>
        </div>

        {/* Energy Flow Visualization */}
        <div className="mb-8">
          <div className="h-[400px]">
            <EnergyFlow
              activeSource={activeSource}
              solarOutput={energyOutputs.solar}
              batteryOutput={energyOutputs.battery}
              gridOutput={energyOutputs.grid}
              homeConsumption={energyOutputs.home}
            />
          </div>
        </div>

        {/* Bottom Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Energy Forecast Chart */}
          <div>
            <EnergyChart forecastData={forecastData} />
          </div>

          {/* Strategy Narrator */}
          <div>
            <div className="h-[400px]">
              <StrategyNarrator logs={strategyLogs} />
            </div>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-gray-700/50 bg-gray-900/80 backdrop-blur-sm mt-12">
        <div className="container mx-auto px-6 py-4">
          <div className="text-center text-sm text-gray-400">
            <p>HyperVolt - SMVIT Sustainergy Hackathon 2026</p>
            <p className="text-xs mt-1">Built with ❤️ by HyperHawks Team</p>
          </div>
        </div>
      </footer>
    </div>
  )
}
