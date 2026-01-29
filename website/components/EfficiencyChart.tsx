'use client'

import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'
import { cn } from '@/lib/utils'
import { TrendingUp } from 'lucide-react'

interface EfficiencyDataPoint {
  timestamp: string
  efficiency: number
}

interface EfficiencyChartProps {
  data: EfficiencyDataPoint[]
  className?: string
}

export default function EfficiencyChart({ data, className }: EfficiencyChartProps) {
  // Format data for chart
  const chartData = data.map(item => ({
    time: new Date(item.timestamp).toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' }),
    efficiency: item.efficiency,
  }))

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-gray-800 border border-gray-700 rounded-lg p-3 shadow-lg">
          <p className="text-gray-300 text-sm mb-2">{label}</p>
          <p className="text-sm text-purple-400">
            Efficiency: {payload[0].value?.toFixed(1)}%
          </p>
        </div>
      )
    }
    return null
  }

  // Calculate stats
  const avgEfficiency = chartData.length > 0
    ? chartData.reduce((sum, d) => sum + d.efficiency, 0) / chartData.length
    : 0
  const maxEfficiency = chartData.length > 0
    ? Math.max(...chartData.map(d => d.efficiency))
    : 0

  return (
    <div className={cn('bg-gray-900/50 rounded-lg p-6 border border-gray-700/50', className)}>
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-lg font-semibold text-white flex items-center gap-2">
            <TrendingUp className="w-5 h-5 text-purple-400" />
            System Efficiency
          </h3>
          <p className="text-xs text-gray-400 mt-1">
            Energy conversion efficiency over time
          </p>
        </div>
        <div className="flex gap-4">
          <div className="text-right">
            <div className="text-xs text-gray-400">Average</div>
            <div className="text-lg font-bold text-purple-400">{avgEfficiency.toFixed(1)}%</div>
          </div>
          <div className="text-right">
            <div className="text-xs text-gray-400">Peak</div>
            <div className="text-lg font-bold text-purple-400">{maxEfficiency.toFixed(1)}%</div>
          </div>
        </div>
      </div>

      {chartData.length > 0 ? (
        <ResponsiveContainer width="100%" height={250}>
          <AreaChart data={chartData}>
            <defs>
              <linearGradient id="colorEfficiency" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#A855F7" stopOpacity={0.4} />
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
              domain={[0, 100]}
              label={{ value: 'Efficiency %', angle: -90, position: 'insideLeft', style: { fill: '#9CA3AF' } }}
            />
            <Tooltip content={<CustomTooltip />} />
            <Area
              type="monotone"
              dataKey="efficiency"
              stroke="#A855F7"
              strokeWidth={2}
              fill="url(#colorEfficiency)"
            />
          </AreaChart>
        </ResponsiveContainer>
      ) : (
        <div className="h-[250px] flex items-center justify-center text-gray-500">
          <p>No efficiency data available</p>
        </div>
      )}

      {/* Performance indicator */}
      <div className="mt-4 pt-4 border-t border-gray-700/50">
        <div className="flex items-center justify-between text-xs">
          <span className="text-gray-400">Performance</span>
          <div className="flex items-center gap-2">
            <div className="flex gap-1">
              {[...Array(5)].map((_, i) => (
                <div 
                  key={i}
                  className={cn(
                    "w-2 h-4 rounded-sm",
                    i < Math.floor(avgEfficiency / 20) ? "bg-purple-500" : "bg-gray-700"
                  )}
                />
              ))}
            </div>
            <span className="text-purple-400 font-semibold">
              {avgEfficiency >= 90 ? 'Excellent' : avgEfficiency >= 75 ? 'Good' : avgEfficiency >= 60 ? 'Fair' : 'Poor'}
            </span>
          </div>
        </div>
      </div>
    </div>
  )
}
