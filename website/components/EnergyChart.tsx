'use client'

import { LineChart, Line, AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import { cn } from '@/lib/utils'
import { ForecastPrediction } from '@/lib/types'

interface EnergyChartProps {
  forecastData: ForecastPrediction[]
  historicalData?: { timestamp: string; actual_kwh: number }[]
  className?: string
}

export default function EnergyChart({ forecastData, historicalData = [], className }: EnergyChartProps) {
  // Combine historical and forecast data
  const chartData = [
    ...historicalData.map((item, idx) => ({
      time: new Date(item.timestamp).toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' }),
      actual: item.actual_kwh,
      forecast: null,
      index: -historicalData.length + idx,
    })),
    ...forecastData.map((item, idx) => ({
      time: new Date(item.timestamp).toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' }),
      actual: null,
      forecast: item.predicted_kwh,
      index: idx,
    })),
  ]

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-gray-800 border border-gray-700 rounded-lg p-3 shadow-lg">
          <p className="text-gray-300 text-sm mb-2">{label}</p>
          {payload.map((entry: any, index: number) => (
            <p key={index} className="text-sm" style={{ color: entry.color }}>
              {entry.name}: {entry.value?.toFixed(2)} kWh
            </p>
          ))}
        </div>
      )
    }
    return null
  }

  return (
    <div className={cn('bg-gray-900/50 rounded-lg p-6', className)}>
      <div className="mb-4">
        <h3 className="text-lg font-semibold text-white flex items-center gap-2">
          Energy Forecast
        </h3>
        <p className="text-xs text-gray-400 mt-1">
          Predicted vs. Actual Energy Consumption
        </p>
      </div>

      <ResponsiveContainer width="100%" height={300}>
        <AreaChart data={chartData}>
          <defs>
            <linearGradient id="colorActual" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#3B82F6" stopOpacity={0.3} />
              <stop offset="95%" stopColor="#3B82F6" stopOpacity={0} />
            </linearGradient>
            <linearGradient id="colorForecast" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#A855F7" stopOpacity={0.3} />
              <stop offset="95%" stopColor="#A855F7" stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
          <XAxis 
            dataKey="time" 
            stroke="#9CA3AF"
            style={{ fontSize: '12px' }}
          />
          <YAxis 
            stroke="#9CA3AF"
            style={{ fontSize: '12px' }}
            label={{ value: 'kWh', angle: -90, position: 'insideLeft', style: { fill: '#9CA3AF' } }}
          />
          <Tooltip content={<CustomTooltip />} />
          <Legend 
            wrapperStyle={{ fontSize: '12px' }}
            iconType="line"
          />
          <Area
            type="monotone"
            dataKey="actual"
            stroke="#3B82F6"
            strokeWidth={2}
            fill="url(#colorActual)"
            name="Actual Usage"
            connectNulls
          />
          <Area
            type="monotone"
            dataKey="forecast"
            stroke="#A855F7"
            strokeWidth={2}
            strokeDasharray="5 5"
            fill="url(#colorForecast)"
            name="AI Forecast"
            connectNulls
          />
        </AreaChart>
      </ResponsiveContainer>

      {/* Legend info */}
      <div className="mt-4 flex items-center gap-6 text-xs text-gray-400">
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full bg-blue-500" />
          <span>Historical Data</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full bg-purple-500" />
          <span>AI Prediction</span>
        </div>
      </div>
    </div>
  )
}
