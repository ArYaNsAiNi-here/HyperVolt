'use client'

import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts'
import { cn } from '@/lib/utils'
import { Sun, Battery, Zap } from 'lucide-react'

interface PowerDistributionProps {
  solarOutput: number
  batteryOutput: number
  gridOutput: number
  className?: string
}

export default function PowerDistribution({ solarOutput, batteryOutput, gridOutput, className }: PowerDistributionProps) {
  // Calculate total and percentages
  const total = solarOutput + batteryOutput + gridOutput
  
  const data = [
    { name: 'Solar', value: solarOutput, color: '#FDB022', icon: Sun },
    { name: 'Battery', value: batteryOutput, color: '#FF6B35', icon: Battery },
    { name: 'Grid', value: gridOutput, color: '#EF4444', icon: Zap },
  ].filter(item => item.value > 0)

  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const item = payload[0]
      const percentage = total > 0 ? ((item.value / total) * 100).toFixed(1) : 0
      return (
        <div className="bg-gray-800 border border-gray-700 rounded-lg p-3 shadow-lg">
          <p className="text-sm font-semibold" style={{ color: item.payload.color }}>
            {item.name}
          </p>
          <p className="text-sm text-gray-300">
            {item.value.toFixed(2)} kW ({percentage}%)
          </p>
        </div>
      )
    }
    return null
  }

  const CustomLabel = ({ cx, cy, midAngle, innerRadius, outerRadius, percent }: any) => {
    if (percent < 0.05) return null // Don't show label for very small slices
    
    const radius = innerRadius + (outerRadius - innerRadius) * 0.5
    const x = cx + radius * Math.cos(-midAngle * Math.PI / 180)
    const y = cy + radius * Math.sin(-midAngle * Math.PI / 180)

    return (
      <text 
        x={x} 
        y={y} 
        fill="white" 
        textAnchor={x > cx ? 'start' : 'end'} 
        dominantBaseline="central"
        className="text-xs font-semibold"
      >
        {`${(percent * 100).toFixed(0)}%`}
      </text>
    )
  }

  return (
    <div className={cn('bg-gray-900/50 rounded-lg p-6 border border-gray-700/50', className)}>
      <div className="mb-4">
        <h3 className="text-lg font-semibold text-white">Power Source Distribution</h3>
        <p className="text-xs text-gray-400 mt-1">
          Current energy contribution by source
        </p>
      </div>

      {total > 0 ? (
        <>
          <ResponsiveContainer width="100%" height={250}>
            <PieChart>
              <Pie
                data={data}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={CustomLabel}
                outerRadius={90}
                innerRadius={50}
                fill="#8884d8"
                dataKey="value"
                animationBegin={0}
                animationDuration={800}
              >
                {data.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip content={<CustomTooltip />} />
            </PieChart>
          </ResponsiveContainer>

          {/* Custom legend with icons */}
          <div className="mt-4 space-y-2">
            {data.map((item, idx) => {
              const Icon = item.icon
              const percentage = total > 0 ? ((item.value / total) * 100).toFixed(1) : 0
              return (
                <div key={idx} className="flex items-center justify-between text-sm">
                  <div className="flex items-center gap-2">
                    <div 
                      className="w-3 h-3 rounded-full" 
                      style={{ backgroundColor: item.color }}
                    />
                    <Icon className="w-4 h-4" style={{ color: item.color }} />
                    <span className="text-gray-300">{item.name}</span>
                  </div>
                  <div className="flex items-center gap-3">
                    <span className="text-gray-400">{item.value.toFixed(2)} kW</span>
                    <span className="text-gray-500 w-12 text-right">{percentage}%</span>
                  </div>
                </div>
              )
            })}
          </div>

          {/* Total output */}
          <div className="mt-4 pt-4 border-t border-gray-700/50">
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-400">Total Output</span>
              <span className="text-lg font-bold text-white">{total.toFixed(2)} kW</span>
            </div>
          </div>
        </>
      ) : (
        <div className="h-[250px] flex items-center justify-center text-gray-500">
          <p>No power sources active</p>
        </div>
      )}
    </div>
  )
}
