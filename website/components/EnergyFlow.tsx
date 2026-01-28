'use client'

import { motion } from 'framer-motion'
import { Sun, Battery, Zap, Home } from 'lucide-react'
import { cn } from '@/lib/utils'

interface EnergyFlowProps {
  activeSource: 'solar' | 'battery' | 'grid'
  solarOutput: number
  batteryOutput: number
  gridOutput: number
  homeConsumption: number
  className?: string
}

interface SourceNodeProps {
  type: 'solar' | 'battery' | 'grid'
  output: number
  isActive: boolean
  position: { x: number; y: number }
}

function SourceNode({ type, output, isActive, position }: SourceNodeProps) {
  const icons = {
    solar: <Sun className="w-8 h-8" />,
    battery: <Battery className="w-8 h-8" />,
    grid: <Zap className="w-8 h-8" />,
  }

  const colors = {
    solar: {
      bg: 'bg-yellow-500/20',
      border: 'border-yellow-500',
      text: 'text-yellow-500',
      glow: 'shadow-yellow-500/50',
    },
    battery: {
      bg: 'bg-orange-500/20',
      border: 'border-orange-500',
      text: 'text-orange-500',
      glow: 'shadow-orange-500/50',
    },
    grid: {
      bg: 'bg-red-500/20',
      border: 'border-red-500',
      text: 'text-red-500',
      glow: 'shadow-red-500/50',
    },
  }

  const color = colors[type]

  return (
    <motion.div
      className={cn(
        'absolute flex flex-col items-center gap-2',
      )}
      style={{
        left: `${position.x}%`,
        top: `${position.y}%`,
        transform: 'translate(-50%, -50%)',
      }}
      animate={{
        scale: isActive ? [1, 1.1, 1] : 1,
      }}
      transition={{
        duration: 2,
        repeat: isActive ? Infinity : 0,
        ease: 'easeInOut',
      }}
    >
      <div
        className={cn(
          'relative w-20 h-20 rounded-full flex items-center justify-center border-2',
          color.bg,
          color.border,
          color.text,
          isActive && `shadow-lg ${color.glow}`,
        )}
      >
        {icons[type]}
        {isActive && (
          <motion.div
            className={cn(
              'absolute inset-0 rounded-full border-2',
              color.border,
            )}
            initial={{ scale: 1, opacity: 1 }}
            animate={{ scale: 1.5, opacity: 0 }}
            transition={{
              duration: 1.5,
              repeat: Infinity,
              ease: 'easeOut',
            }}
          />
        )}
      </div>
      <div className="text-center">
        <div className={cn('text-sm font-semibold capitalize', color.text)}>
          {type}
        </div>
        <div className="text-xs text-gray-400">{output.toFixed(1)}kW</div>
      </div>
    </motion.div>
  )
}

function EnergyPath({ 
  from, 
  to, 
  isActive,
  color 
}: { 
  from: { x: number; y: number }
  to: { x: number; y: number }
  isActive: boolean
  color: string
}) {
  // Calculate path using percentages for responsive design
  const midX = (from.x + to.x) / 2
  const midY = (from.y + to.y) / 2 - 5 // Slight curve

  const pathD = `M ${from.x}% ${from.y}% Q ${midX}% ${midY}% ${to.x}% ${to.y}%`

  return (
    <>
      {/* Path line */}
      <motion.path
        d={pathD}
        fill="none"
        stroke={color}
        strokeWidth="3"
        strokeDasharray="8,4"
        initial={{ pathLength: 0, opacity: 0.3 }}
        animate={{ 
          pathLength: isActive ? 1 : 0,
          opacity: isActive ? 0.8 : 0.2,
        }}
        transition={{ duration: 0.5 }}
      />
      
      {/* Animated particles */}
      {isActive && (
        <>
          <motion.circle
            r="5"
            fill={color}
            initial={{ offsetDistance: '0%', opacity: 1 }}
            animate={{ offsetDistance: '100%', opacity: 0 }}
            transition={{
              duration: 2,
              repeat: Infinity,
              ease: 'linear',
              delay: 0,
            }}
            style={{
              offsetPath: `path("${pathD}")`,
            }}
          />
          <motion.circle
            r="5"
            fill={color}
            initial={{ offsetDistance: '0%', opacity: 1 }}
            animate={{ offsetDistance: '100%', opacity: 0 }}
            transition={{
              duration: 2,
              repeat: Infinity,
              ease: 'linear',
              delay: 0.7,
            }}
            style={{
              offsetPath: `path("${pathD}")`,
            }}
          />
          <motion.circle
            r="5"
            fill={color}
            initial={{ offsetDistance: '0%', opacity: 1 }}
            animate={{ offsetDistance: '100%', opacity: 0 }}
            transition={{
              duration: 2,
              repeat: Infinity,
              ease: 'linear',
              delay: 1.4,
            }}
            style={{
              offsetPath: `path("${pathD}")`,
            }}
          />
        </>
      )}
    </>
  )
}

export default function EnergyFlow({
  activeSource,
  solarOutput,
  batteryOutput,
  gridOutput,
  homeConsumption,
  className,
}: EnergyFlowProps) {
  // Node positions (percentage) - adjusted to keep all nodes within bounds
  const positions = {
    solar: { x: 20, y: 25 },
    battery: { x: 20, y: 70 },
    grid: { x: 50, y: 50 },
    home: { x: 80, y: 50 },
  }

  const colors = {
    solar: '#FDB022',
    battery: '#FF6B35',
    grid: '#EF4444',
  }

  return (
    <div className={cn('relative w-full h-full bg-gray-900/50 rounded-lg p-8 overflow-hidden', className)}>
      {/* Energy paths - using percentage-based positioning */}
      <svg className="absolute inset-0 w-full h-full pointer-events-none" style={{ zIndex: 0 }}>
        <EnergyPath
          from={positions.solar}
          to={positions.home}
          isActive={activeSource === 'solar'}
          color={colors.solar}
        />
        <EnergyPath
          from={positions.battery}
          to={positions.home}
          isActive={activeSource === 'battery'}
          color={colors.battery}
        />
        <EnergyPath
          from={positions.grid}
          to={positions.home}
          isActive={activeSource === 'grid'}
          color={colors.grid}
        />
      </svg>

      {/* Source nodes */}
      <SourceNode
        type="solar"
        output={solarOutput}
        isActive={activeSource === 'solar'}
        position={positions.solar}
      />
      <SourceNode
        type="battery"
        output={batteryOutput}
        isActive={activeSource === 'battery'}
        position={positions.battery}
      />
      <SourceNode
        type="grid"
        output={gridOutput}
        isActive={activeSource === 'grid'}
        position={positions.grid}
      />

      {/* Home node */}
      <motion.div
        className="absolute flex flex-col items-center gap-2"
        style={{
          left: `${positions.home.x}%`,
          top: `${positions.home.y}%`,
          transform: 'translate(-50%, -50%)',
        }}
      >
        <div className="relative w-20 h-20 rounded-full flex items-center justify-center border-2 bg-blue-500/20 border-blue-500 text-blue-500">
          <Home className="w-8 h-8" />
        </div>
        <div className="text-center">
          <div className="text-sm font-semibold text-blue-500">Home</div>
          <div className="text-xs text-gray-400">{homeConsumption.toFixed(1)}kW</div>
        </div>
      </motion.div>

      {/* Legend */}
      <div className="absolute bottom-4 right-4 bg-gray-800/80 rounded-lg p-3 text-xs">
        <div className="text-gray-400 font-semibold mb-2">Active Source</div>
        <div className="flex items-center gap-2">
          <div className={cn(
            'w-3 h-3 rounded-full',
            activeSource === 'solar' && 'bg-yellow-500',
            activeSource === 'battery' && 'bg-orange-500',
            activeSource === 'grid' && 'bg-red-500',
          )} />
          <span className="text-gray-300 capitalize">{activeSource}</span>
        </div>
      </div>
    </div>
  )
}
