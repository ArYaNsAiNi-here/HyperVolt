'use client'

import { motion } from 'framer-motion'
import { Thermometer, Sun } from 'lucide-react'
import { cn } from '@/lib/utils'

interface SensorMetricsProps {
  temperature: number
  solarVoltage: number
  className?: string
}

export default function SensorMetrics({ 
  temperature, 
  solarVoltage,
  className 
}: SensorMetricsProps) {
  // Determine temperature status (optimal range 20-28°C)
  const tempStatus = temperature < 20 ? 'cold' : temperature > 28 ? 'hot' : 'optimal'
  const tempColor = tempStatus === 'cold' ? 'blue' : tempStatus === 'hot' ? 'red' : 'green'
  
  // Determine solar voltage status (good if above 12V for a typical solar panel)
  const solarStatus = solarVoltage < 5 ? 'low' : solarVoltage > 12 ? 'optimal' : 'moderate'
  const solarColor = solarStatus === 'low' ? 'gray' : solarStatus === 'optimal' ? 'yellow' : 'orange'

  const colorClasses = {
    blue: {
      bg: 'bg-blue-500/10',
      border: 'border-blue-500/30',
      text: 'text-blue-400',
      icon: 'text-blue-500',
    },
    red: {
      bg: 'bg-red-500/10',
      border: 'border-red-500/30',
      text: 'text-red-400',
      icon: 'text-red-500',
    },
    green: {
      bg: 'bg-green-500/10',
      border: 'border-green-500/30',
      text: 'text-green-400',
      icon: 'text-green-500',
    },
    yellow: {
      bg: 'bg-yellow-500/10',
      border: 'border-yellow-500/30',
      text: 'text-yellow-400',
      icon: 'text-yellow-500',
    },
    orange: {
      bg: 'bg-orange-500/10',
      border: 'border-orange-500/30',
      text: 'text-orange-400',
      icon: 'text-orange-500',
    },
    gray: {
      bg: 'bg-gray-500/10',
      border: 'border-gray-500/30',
      text: 'text-gray-400',
      icon: 'text-gray-500',
    },
  }

  const tempColors = colorClasses[tempColor]
  const solarColors = colorClasses[solarColor]

  return (
    <div className={cn('bg-gray-900/50 rounded-lg p-6 border border-gray-700/50', className)}>
      <div className="mb-4">
        <h3 className="text-lg font-semibold text-white flex items-center gap-2">
          <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
          Sensor Readings
        </h3>
        <p className="text-xs text-gray-400 mt-1">
          Temperature and solar voltage data
        </p>
      </div>

      <div className="grid grid-cols-2 gap-3">
        {/* Temperature Metric */}
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.1 }}
          className={cn(
            'p-4 rounded-lg border backdrop-blur-sm',
            tempColors.bg,
            tempColors.border
          )}
        >
          <div className="flex items-start justify-between mb-2">
            <span className="text-xs text-gray-400">Temperature</span>
            <div className={cn('p-1.5 rounded-lg', tempColors.bg, tempColors.icon)}>
              <Thermometer className="w-4 h-4" />
            </div>
          </div>
          
          <div className="flex items-baseline gap-1 mb-1">
            <motion.span
              key={temperature}
              initial={{ scale: 1.2, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              className={cn('text-2xl font-bold', tempColors.text)}
            >
              {temperature.toFixed(1)}
            </motion.span>
            <span className="text-xs text-gray-500">°C</span>
          </div>

          <div className="flex items-center gap-1">
            <span className={cn('text-xs capitalize', tempColors.text)}>
              {tempStatus}
            </span>
          </div>
        </motion.div>

        {/* Solar Voltage Metric */}
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.2 }}
          className={cn(
            'p-4 rounded-lg border backdrop-blur-sm',
            solarColors.bg,
            solarColors.border
          )}
        >
          <div className="flex items-start justify-between mb-2">
            <span className="text-xs text-gray-400">Solar Voltage</span>
            <div className={cn('p-1.5 rounded-lg', solarColors.bg, solarColors.icon)}>
              <Sun className="w-4 h-4" />
            </div>
          </div>
          
          <div className="flex items-baseline gap-1 mb-1">
            <motion.span
              key={solarVoltage}
              initial={{ scale: 1.2, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              className={cn('text-2xl font-bold', solarColors.text)}
            >
              {solarVoltage.toFixed(1)}
            </motion.span>
            <span className="text-xs text-gray-500">V</span>
          </div>

          <div className="flex items-center gap-1">
            <span className={cn('text-xs capitalize', solarColors.text)}>
              {solarStatus === 'low' ? 'Low' : solarStatus === 'optimal' ? 'Optimal' : 'Moderate'}
            </span>
          </div>
        </motion.div>
      </div>

      {/* Status indicator */}
      <div className="mt-4 pt-4 border-t border-gray-700/50 flex items-center justify-between text-xs text-gray-400">
        <span>Live sensor data</span>
        <div className="flex items-center gap-1">
          <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
          <span>Active</span>
        </div>
      </div>
    </div>
  )
}
