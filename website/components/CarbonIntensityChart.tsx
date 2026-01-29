'use client'

import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'
import { cn } from '@/lib/utils'
import { Cloud } from 'lucide-react'

interface CarbonDataPoint {
  timestamp: string
  value: number
}

interface CarbonIntensityChartProps {
  data: CarbonDataPoint[]
  className?: string
}

export default function CarbonIntensityChart({ data, className }: CarbonIntensityChartProps) {
  // Format data for chart
  const chartData = data.map(item => ({
    time: new Date(item.timestamp).toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' }),
    carbon: item.value,
  }))

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-gray-800 border border-gray-700 rounded-lg p-3 shadow-lg">
          <p className="text-gray-300 text-sm mb-2">{label}</p>
          <p className="text-sm text-green-400">
            Carbon: {payload[0].value?.toFixed(0)} gCO₂/kWh
          </p>
        </div>
      )
    }
    return null
  }

  // Calculate average
  const avgCarbon = chartData.length > 0
    ? chartData.reduce((sum, d) => sum + d.carbon, 0) / chartData.length
    : 0

  return (
    <div className={cn('bg-gray-900/50 rounded-lg p-6 border border-gray-700/50', className)}>
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-lg font-semibold text-white flex items-center gap-2">
            <Cloud className="w-5 h-5 text-green-400" />
            Grid Carbon Intensity
          </h3>
          <p className="text-xs text-gray-400 mt-1">
            Historical carbon emissions from grid power
          </p>
        </div>
        <div className="text-right">
          <div className="text-xs text-gray-400">Average</div>
          <div className="text-lg font-bold text-green-400">{avgCarbon.toFixed(0)} <span className="text-xs">gCO₂/kWh</span></div>
        </div>
      </div>

      {chartData.length > 0 ? (
        <ResponsiveContainer width="100%" height={250}>
          <LineChart data={chartData}>
            <defs>
              <linearGradient id="colorCarbon" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#10B981" stopOpacity={0.3} />
                <stop offset="95%" stopColor="#10B981" stopOpacity={0} />
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
              label={{ value: 'gCO₂/kWh', angle: -90, position: 'insideLeft', style: { fill: '#9CA3AF' } }}
            />
            <Tooltip content={<CustomTooltip />} />
            <Line
              type="monotone"
              dataKey="carbon"
              stroke="#10B981"
              strokeWidth={2}
              dot={{ fill: '#10B981', r: 4 }}
              activeDot={{ r: 6 }}
            />
          </LineChart>
        </ResponsiveContainer>
      ) : (
        <div className="h-[250px] flex items-center justify-center text-gray-500">
          <p>No carbon intensity data available</p>
        </div>
      )}

      {/* Info footer */}
      <div className="mt-4 pt-4 border-t border-gray-700/50 text-xs text-gray-400">
        <p>Lower values indicate cleaner energy. Best time to use high-power appliances is during low carbon periods.</p>
      </div>
    </div>
  )
}
