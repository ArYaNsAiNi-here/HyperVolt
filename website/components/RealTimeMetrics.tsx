'use client'

import { motion } from 'framer-motion'
import { Zap, TrendingDown, TrendingUp, Activity, IndianRupee, Leaf } from 'lucide-react'
import { cn } from '@/lib/utils'

interface LiveMetric {
  label: string
  value: string
  unit: string
  trend: 'up' | 'down' | 'neutral'
  trendValue?: string
  icon: React.ReactNode
  color: string
}

interface RealTimeMetricsProps {
  powerConsumption: number
  costRate: number
  carbonRate: number
  efficiency: number
  className?: string
}

export default function RealTimeMetrics({ 
  powerConsumption, 
  costRate, 
  carbonRate, 
  efficiency,
  className 
}: RealTimeMetricsProps) {
  const metrics: LiveMetric[] = [
    {
      label: 'Live Power',
      value: powerConsumption.toFixed(2),
      unit: 'W',
      trend: powerConsumption > 1.5 ? 'up' : 'down',
      icon: <Zap className="w-4 h-4" />,
      color: 'blue',
    },
    {
      label: 'Cost Rate',
      value: costRate.toFixed(2),
      unit: '₹/hr',
      trend: costRate < 5 ? 'down' : 'up',
      icon: <IndianRupee className="w-4 h-4" />,
      color: 'yellow',
    },
    {
      label: 'Carbon Rate',
      value: carbonRate.toFixed(1),
      unit: 'gCO₂/hr',
      trend: carbonRate < 200 ? 'down' : 'up',
      icon: <Leaf className="w-4 h-4" />,
      color: 'green',
    },
    {
      label: 'Efficiency',
      value: efficiency.toFixed(0),
      unit: '%',
      trend: efficiency > 80 ? 'up' : 'neutral',
      icon: <Activity className="w-4 h-4" />,
      color: 'purple',
    },
  ]

  const colorClasses = {
    blue: {
      bg: 'bg-blue-500/10',
      border: 'border-blue-500/30',
      text: 'text-blue-400',
      icon: 'text-blue-500',
    },
    yellow: {
      bg: 'bg-yellow-500/10',
      border: 'border-yellow-500/30',
      text: 'text-yellow-400',
      icon: 'text-yellow-500',
    },
    green: {
      bg: 'bg-green-500/10',
      border: 'border-green-500/30',
      text: 'text-green-400',
      icon: 'text-green-500',
    },
    purple: {
      bg: 'bg-purple-500/10',
      border: 'border-purple-500/30',
      text: 'text-purple-400',
      icon: 'text-purple-500',
    },
  }

  return (
    <div className={cn('bg-gray-900/50 rounded-lg p-6 border border-gray-700/50', className)}>
      <div className="mb-4">
        <h3 className="text-lg font-semibold text-white flex items-center gap-2">
          <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
          Real-Time Metrics
        </h3>
        <p className="text-xs text-gray-400 mt-1">
          Live system performance indicators
        </p>
      </div>

      <div className="grid grid-cols-2 gap-3">
        {metrics.map((metric, idx) => {
          const colors = colorClasses[metric.color as keyof typeof colorClasses]
          return (
            <motion.div
              key={idx}
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: idx * 0.1 }}
              className={cn(
                'p-4 rounded-lg border backdrop-blur-sm',
                colors.bg,
                colors.border
              )}
            >
              <div className="flex items-start justify-between mb-2">
                <span className="text-xs text-gray-400">{metric.label}</span>
                <div className={cn('p-1.5 rounded-lg', colors.bg, colors.icon)}>
                  {metric.icon}
                </div>
              </div>
              
              <div className="flex items-baseline gap-1 mb-1">
                <motion.span
                  key={metric.value}
                  initial={{ scale: 1.2, opacity: 0 }}
                  animate={{ scale: 1, opacity: 1 }}
                  className={cn('text-2xl font-bold', colors.text)}
                >
                  {metric.value}
                </motion.span>
                <span className="text-xs text-gray-500">{metric.unit}</span>
              </div>

              <div className="flex items-center gap-1">
                {metric.trend === 'up' ? (
                  <TrendingUp className="w-3 h-3 text-red-400" />
                ) : metric.trend === 'down' ? (
                  <TrendingDown className="w-3 h-3 text-green-400" />
                ) : (
                  <Activity className="w-3 h-3 text-gray-400" />
                )}
              </div>
            </motion.div>
          )
        })}
      </div>

      {/* Refresh indicator */}
      <div className="mt-4 pt-4 border-t border-gray-700/50 flex items-center justify-between text-xs text-gray-400">
        <span>Auto-refresh: 5s</span>
        <motion.div
          animate={{ rotate: 360 }}
          transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
          className="w-4 h-4"
        >
          <Activity className="w-4 h-4" />
        </motion.div>
      </div>
    </div>
  )
}
