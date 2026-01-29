'use client'

import { useState, useEffect, useCallback, useRef } from 'react'
import dynamic from 'next/dynamic'
import { Activity, Zap } from 'lucide-react'
import { motion } from 'framer-motion'
import { useWebSocket } from '@/hooks/useWebSocket'
import apiService from '@/lib/api-service'
import { StrategyLogEntry, WebSocketMessage, ForecastPrediction } from '@/lib/types'
import StatsGrid from '@/components/StatsGrid'
import StrategyNarrator from '@/components/StrategyNarrator'
import EnergyChart from '@/components/EnergyChart'
import BrightnessControl from '@/components/BrightnessControl'
import CarbonIntensityChart from '@/components/CarbonIntensityChart'
import PowerDistribution from '@/components/PowerDistribution'
import EfficiencyChart from '@/components/EfficiencyChart'
import RealTimeMetrics from '@/components/RealTimeMetrics'
import HeroSection from '@/components/HeroSection'
import LogsViewer from '@/components/LogsViewer'
import SensorMetrics from '@/components/SensorMetrics'

// Constants
const MAX_HISTORY_ENTRIES = 20

// Dynamic imports for 3D components (client-side only)
const EnergyFlow = dynamic(() => import('@/components/EnergyFlow'), {
  ssr: false,
  loading: () => (
    <div className="w-full h-full flex items-center justify-center bg-gray-900/50 rounded-lg">
      <div className="flex flex-col items-center gap-3">
        <div className="w-8 h-8 border-4 border-purple-500 border-t-transparent rounded-full animate-spin" />
        <div className="text-gray-400">Loading Energy Flow...</div>
      </div>
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
  const [temperature, setTemperature] = useState(25) // Temperature in Celsius
  const [solarVoltage, setSolarVoltage] = useState(0) // Solar panel voltage
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
  const [carbonHistory, setCarbonHistory] = useState<Array<{ timestamp: string; value: number }>>([])
  const [efficiencyHistory, setEfficiencyHistory] = useState<Array<{ timestamp: string; efficiency: number }>>([])
  
  // Scroll state
  const [scrolled, setScrolled] = useState(false)
  const dashboardRef = useRef<HTMLDivElement>(null)

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

      if (sensor_type === 'temperature') {
        setTemperature(value)
        addLog({
          id: Date.now().toString(),
          timestamp: new Date().toISOString(),
          type: 'info',
          message: `Temperature updated: ${value.toFixed(1)}°C`,
        })
      }

      if (sensor_type === 'voltage') {
        setSolarVoltage(value)
        addLog({
          id: Date.now().toString(),
          timestamp: new Date().toISOString(),
          type: 'info',
          message: `Solar voltage updated: ${value.toFixed(1)}V`,
        })
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

  // Scroll detection
  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 100)
    }

    window.addEventListener('scroll', handleScroll)
    return () => window.removeEventListener('scroll', handleScroll)
  }, [])

  // Scroll to dashboard function
  const scrollToDashboard = () => {
    dashboardRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

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
        
        // Add to history
        setCarbonHistory(prev => {
          const newHistory = [...prev, { timestamp: new Date().toISOString(), value: carbonData.value }]
          return newHistory.slice(-MAX_HISTORY_ENTRIES)
        })
        
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
        // Use console.warn instead of console.error to reduce noise when backend is unavailable
        console.warn('Failed to fetch initial data - backend may not be running')
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
        // Update stats with more realistic variations
        const newEfficiency = await new Promise<number>((resolve) => {
          setStats(prev => {
            const efficiency = Math.min(100, Math.max(70, prev.efficiency + (Math.random() - 0.5) * 3))
            resolve(efficiency)
            return {
              ...prev,
              carbonSavings: prev.carbonSavings + Math.random() * 0.1,
              costSavings: prev.costSavings + Math.random() * 0.05,
              powerConsumption: 1.0 + Math.random() * 0.5,
              efficiency: efficiency,
            }
          })
        })
        
        // Add efficiency to history (separate from stats update)
        setEfficiencyHistory(prevHistory => {
          const newHistory = [...prevHistory, { 
            timestamp: new Date().toISOString(), 
            efficiency: newEfficiency 
          }]
          return newHistory.slice(-MAX_HISTORY_ENTRIES)
        })

        // Periodically fetch carbon data
        try {
          const carbonData = await apiService.getCurrentCarbonIntensity()
          setCarbonHistory(prev => {
            const newHistory = [...prev, { timestamp: new Date().toISOString(), value: carbonData.value }]
            return newHistory.slice(-MAX_HISTORY_ENTRIES)
          })
        } catch (error) {
          // Log error but don't disrupt periodic updates
          console.debug('Carbon data fetch failed during periodic update:', error)
        }
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
      {/* Hero Section - Full Viewport 3D Model */}
      <HeroSection
        lightIntensity={lightIntensity}
        activeSource={activeSource}
        brightnessThreshold={brightnessThreshold}
        weatherCondition={weatherCondition}
        onScrollClick={scrollToDashboard}
      />

      {/* Dashboard Content - Fades in on scroll */}
      <motion.div
        ref={dashboardRef}
        initial={{ opacity: 0 }}
        animate={{ opacity: scrolled ? 1 : 0.3 }}
        transition={{ duration: 0.6 }}
      >
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
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: scrolled ? 1 : 0, y: scrolled ? 0 : 20 }}
            transition={{ duration: 0.6, delay: 0.1 }}
            className="mb-8"
          >
            <StatsGrid
              carbonSavings={stats.carbonSavings}
              costSavings={stats.costSavings}
              powerConsumption={stats.powerConsumption}
              efficiency={stats.efficiency}
            />
          </motion.div>

          {/* Main Grid Layout */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: scrolled ? 1 : 0, y: scrolled ? 0 : 20 }}
            transition={{ duration: 0.6, delay: 0.2 }}
            className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8"
          >
            {/* Brightness Control and Real-Time Metrics */}
            <div className="space-y-6">
              <BrightnessControl
                value={brightnessThreshold}
                onChange={handleBrightnessChange}
              />
              <RealTimeMetrics
                powerConsumption={stats.powerConsumption}
                costRate={stats.costSavings * 60}
                carbonRate={stats.carbonSavings * 1000 / 24}
                efficiency={stats.efficiency}
              />
              <SensorMetrics
                temperature={temperature}
                solarVoltage={solarVoltage}
              />
            </div>
            
            {/* Energy Flow and Power Distribution */}
            <div className="lg:col-span-2 space-y-6">
              <div className="h-[400px]">
                <EnergyFlow
                  activeSource={activeSource}
                  solarOutput={energyOutputs.solar}
                  batteryOutput={energyOutputs.battery}
                  gridOutput={energyOutputs.grid}
                  homeConsumption={energyOutputs.home}
                />
              </div>
              <div>
                <PowerDistribution
                  solarOutput={energyOutputs.solar}
                  batteryOutput={energyOutputs.battery}
                  gridOutput={energyOutputs.grid}
                />
              </div>
            </div>
          </motion.div>

          {/* Charts Grid */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: scrolled ? 1 : 0, y: scrolled ? 0 : 20 }}
            transition={{ duration: 0.6, delay: 0.3 }}
            className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8"
          >
            {/* Carbon Intensity History */}
            <div>
              <CarbonIntensityChart data={carbonHistory} />
            </div>

            {/* Efficiency Chart */}
            <div>
              <EfficiencyChart data={efficiencyHistory} />
            </div>
          </motion.div>

          {/* Bottom Grid - Energy Forecast */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: scrolled ? 1 : 0, y: scrolled ? 0 : 20 }}
            transition={{ duration: 0.6, delay: 0.4 }}
            className="mb-8"
          >
            <EnergyChart forecastData={forecastData} />
          </motion.div>
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
      </motion.div>

      {/* Floating Logs Viewer */}
      <LogsViewer logs={strategyLogs} />
    </div>
  )
}
