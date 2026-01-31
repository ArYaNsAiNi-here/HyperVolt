'use client'

import { motion } from 'framer-motion'
import { TrendingDown, Leaf, IndianRupee, Zap } from 'lucide-react'
import { cn } from '@/lib/utils'

interface StatCardProps {
  title: string
  value: string | number
  unit: string
  change?: number
  icon: React.ReactNode
  color: 'green' | 'blue' | 'yellow' | 'purple'
  className?: string
}

export function StatCard({ title, value, unit, change, icon, color, className }: StatCardProps) {
  const colors = {
    green: {
      bg: 'bg-green-500/10',
      border: 'border-green-500/30',
      text: 'text-green-400',
      icon: 'text-green-500',
    },
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
    purple: {
      bg: 'bg-purple-500/10',
      border: 'border-purple-500/30',
      text: 'text-purple-400',
      icon: 'text-purple-500',
    },
  }

  const colorScheme = colors[color]

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className={cn(
        'relative p-6 rounded-lg border backdrop-blur-sm overflow-hidden',
        colorScheme.bg,
        colorScheme.border,
        className
      )}
    >
      {/* Background decoration */}
      <div className="absolute top-0 right-0 w-32 h-32 opacity-5">
        {icon}
      </div>

      <div className="relative">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-sm font-medium text-gray-400">{title}</h3>
          <div className={cn('p-2 rounded-lg', colorScheme.bg, colorScheme.icon)}>
            {icon}
          </div>
        </div>

        <div className="flex items-baseline gap-2 mb-2">
          <motion.span
            key={value}
            initial={{ scale: 1.2, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            className={cn('text-3xl font-bold', colorScheme.text)}
          >
            {value}
          </motion.span>
          <span className="text-sm text-gray-500">{unit}</span>
        </div>

        {change !== undefined && (
          <div className="flex items-center gap-1 text-xs">
            <TrendingDown className={cn('w-3 h-3', change < 0 ? 'text-green-400' : 'text-red-400')} />
            <span className={change < 0 ? 'text-green-400' : 'text-red-400'}>
              {Math.abs(change).toFixed(1)}% from baseline
            </span>
          </div>
        )}
      </div>
    </motion.div>
  )
}

interface StatsGridProps {
  carbonSavings: number
  costSavings: number
  powerConsumption: number
  efficiency: number
}

export default function StatsGrid({ carbonSavings, costSavings, powerConsumption, efficiency }: StatsGridProps) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      <StatCard
        title="Carbon Saved Today"
        value={carbonSavings.toFixed(1)}
        unit="kg CO₂"
        change={-12.5}
        icon={<Leaf className="w-6 h-6" />}
        color="green"
      />
      <StatCard
        title="Cost Savings"
        value={costSavings.toFixed(2)}
        unit="₹"
        change={-8.3}
        icon={<IndianRupee className="w-6 h-6" />}
        color="yellow"
      />
      <StatCard
        title="Power Consumption"
        value={powerConsumption.toFixed(2)}
        unit="W"
        icon={<Zap className="w-6 h-6" />}
        color="blue"
      />
      <StatCard
        title="System Efficiency"
        value={efficiency.toFixed(0)}
        unit="%"
        change={5.2}
        icon={<TrendingDown className="w-6 h-6" />}
        color="purple"
      />
    </div>
  )
}
