'use client'

import { motion } from 'framer-motion'
import { Sun, Battery, Plug, Home, Zap } from 'lucide-react'
import { cn } from '@/lib/utils'

interface EnergyFlowProps {
  activeSource: 'solar' | 'battery' | 'grid'
  solarOutput: number
  batteryOutput: number
  gridOutput: number
  homeConsumption: number
  className?: string
}

export default function EnergyFlow({
  activeSource,
  solarOutput,
  batteryOutput,
  gridOutput,
  homeConsumption,
}: EnergyFlowProps) {
  // CONFIG: 100x100 Coordinate System
  const positions = {
    solar:   { x: 20, y: 20 },
    grid:    { x: 80, y: 20 },
    battery: { x: 20, y: 80 },
    home:    { x: 50, y: 80 },
  }

  // Calculate paths that stop at the edge of the icons
  const getWirePath = (source: 'solar' | 'battery' | 'grid') => {
    const start = positions[source]
    const end = positions.home

    if (source === 'solar') {
      // Solar (Top-Left) to Home (Bottom-Center)
      // Enters from the top (y-10 is roughly 40px on typical screens)
      return `M ${start.x} ${start.y + 5} C ${start.x} ${start.y + 40}, ${end.x - 10} ${end.y - 40}, ${end.x} ${end.y - 10}`
    }
    if (source === 'grid') {
      // Grid (Top-Right) to Home (Bottom-Center)
      // Enters from the top
      return `M ${start.x} ${start.y + 5} C ${start.x} ${start.y + 40}, ${end.x + 10} ${end.y - 40}, ${end.x} ${end.y - 10}`
    }
    if (source === 'battery') {
      // Battery (Bottom-Left) to Home (Bottom-Center)
      // Enters from the LEFT.
      // FIXED: Reduced offset from 8 to 3.5 to account for wide aspect ratio.
      // This ensures the line reaches the circle boundary instead of stopping short.
      return `M ${start.x + 3.5} ${start.y} C ${start.x + 15} ${start.y}, ${end.x - 15} ${end.y}, ${end.x - 3.5} ${end.y}`
    }
    return ''
  }

  return (
    <div className="w-full h-full bg-gray-900/50 rounded-xl border border-gray-700/50 p-6 relative overflow-hidden flex flex-col min-h-[350px]">
      <h3 className="text-lg font-semibold text-gray-200 mb-4 flex items-center gap-2 relative z-10">
        <Zap className="w-5 h-5 text-yellow-400" />
        Real-time Power Flow
      </h3>

      <div className="flex-1 relative">
        {/* SVG Layer (Background Wires) */}
        <svg className="absolute inset-0 w-full h-full pointer-events-none z-0" viewBox="0 0 100 100" preserveAspectRatio="none">
          {/* Static Cables */}
          <path d={getWirePath('solar')} fill="none" stroke="#374151" strokeWidth="2" strokeLinecap="round" />
          <path d={getWirePath('grid')} fill="none" stroke="#374151" strokeWidth="2" strokeLinecap="round" />
          <path d={getWirePath('battery')} fill="none" stroke="#374151" strokeWidth="2" strokeLinecap="round" />

          {/* Animated Energy Flow */}
          <AnimatedWire
            path={getWirePath('solar')}
            color="#4ade80"
            isActive={activeSource === 'solar' || solarOutput > 0}
          />
          <AnimatedWire
            path={getWirePath('grid')}
            color="#f87171"
            isActive={activeSource === 'grid' || gridOutput > 0}
          />
          <AnimatedWire
            path={getWirePath('battery')}
            color="#facc15"
            isActive={activeSource === 'battery' || batteryOutput > 0}
          />
        </svg>

        {/* HTML Layer (Icons) */}
        <div className="relative w-full h-full z-10">
          <Node
            pos={positions.solar}
            icon={<Sun className="w-6 h-6" />}
            label="Solar"
            value={solarOutput}
            active={activeSource === 'solar'}
            color="text-green-400"
            bg="bg-green-500/10 border-green-500"
          />

          <Node
            pos={positions.grid}
            icon={<Plug className="w-6 h-6" />}
            label="Grid"
            value={gridOutput}
            active={activeSource === 'grid'}
            color="text-red-400"
            bg="bg-red-500/10 border-red-500"
          />

          <Node
            pos={positions.battery}
            icon={<Battery className="w-6 h-6" />}
            label="Battery"
            value={batteryOutput}
            active={activeSource === 'battery'}
            color="text-yellow-400"
            bg="bg-yellow-500/10 border-yellow-500"
          />

          {/* Home Node (Center Bottom) */}
          <div
            className="absolute transform -translate-x-1/2 -translate-y-1/2 flex flex-col items-center"
            style={{ left: `${positions.home.x}%`, top: `${positions.home.y}%` }}
          >
            <div className="relative">
              <div className="w-20 h-20 rounded-full bg-gray-900 border-4 border-blue-500 flex items-center justify-center shadow-[0_0_30px_rgba(59,130,246,0.4)] z-20">
                <Home className="w-9 h-9 text-blue-400" />
              </div>
              {/* Pulse Ring for Home */}
              <div className="absolute inset-0 rounded-full border border-blue-500/50 animate-[ping_3s_linear_infinite]" />
            </div>
            <div className="mt-2 text-center bg-gray-900/90 backdrop-blur px-3 py-1 rounded-lg border border-gray-700 shadow-xl">
              <p className="text-xs text-gray-400">Total Load</p>
              <p className="text-xl font-bold text-white">{homeConsumption.toFixed(2)} W</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

// --- Helper Components ---

function AnimatedWire({ path, color, isActive }: { path: string, color: string, isActive: boolean }) {
  if (!isActive) return null;

  return (
    <>
      {/* Glow path under the moving dash */}
      <motion.path
        d={path}
        fill="none"
        stroke={color}
        strokeWidth="3"
        strokeOpacity="0.4"
        strokeLinecap="round"
        initial={{ pathLength: 0 }}
        animate={{ pathLength: 1 }}
        transition={{ duration: 1 }}
      />

      {/* The Moving Dash (Energy Packet) */}
      <motion.path
        d={path}
        fill="none"
        stroke={color}
        strokeWidth="4"
        strokeDasharray="10 120" // Short dash (packet), long gap
        strokeLinecap="round"
        // Flow Animation: Moves from 0 to negative to simulate flow TOWARDS home
        animate={{ strokeDashoffset: [0, -130] }}
        transition={{
          duration: 1.5,
          repeat: Infinity,
          ease: "linear"
        }}
      />
    </>
  )
}

function Node({ pos, icon, label, value, active, color, bg }: any) {
  return (
    <motion.div
      className={cn(
        "absolute transform -translate-x-1/2 -translate-y-1/2 p-3 rounded-xl border backdrop-blur-sm transition-all duration-300",
        active
          ? `${bg} scale-110 shadow-[0_0_20px_rgba(0,0,0,0.5)] z-30 ring-2 ring-offset-2 ring-offset-gray-900 ring-opacity-60`
          : "bg-gray-800/50 border-gray-700 opacity-70 scale-95 grayscale"
      )}
      style={{
        left: `${pos.x}%`,
        top: `${pos.y}%`,
        // Dynamic coloring for the active ring based on the source color
        ['--tw-ring-color' as any]: active ? 'currentColor' : 'transparent'
      }}
    >
      <div className={`flex items-center gap-3 ${active ? color : 'text-gray-400'}`}>
        {icon}
        <div>
          <p className="text-xs font-medium uppercase tracking-wider">{label}</p>
          <p className="text-lg font-bold tabular-nums">{value.toFixed(2)} W</p>
        </div>
      </div>
    </motion.div>
  )
}