'use client'

import { useState } from 'react'
import { motion } from 'framer-motion'
import { Sun, Moon } from 'lucide-react'
import { cn } from '@/lib/utils'

interface BrightnessControlProps {
  value: number
  onChange: (value: number) => void
  className?: string
}

export default function BrightnessControl({ value, onChange, className }: BrightnessControlProps) {
  const [isDragging, setIsDragging] = useState(false)

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    onChange(Number(e.target.value))
  }

  return (
    <div className={cn('bg-gray-900/50 rounded-lg p-6', className)}>
      <div className="mb-4">
        <h3 className="text-lg font-semibold text-white flex items-center gap-2">
          <Sun className="w-5 h-5 text-yellow-400" />
          Brightness Threshold
        </h3>
        <p className="text-xs text-gray-400 mt-1">
          Set your preferred light intensity level
        </p>
      </div>

      <div className="space-y-6">
        {/* Slider */}
        <div className="relative">
          <div className="flex items-center gap-4">
            <Moon className="w-5 h-5 text-gray-500" />
            <div className="flex-1 relative">
              <input
                type="range"
                min="0"
                max="100"
                value={value}
                onChange={handleChange}
                onMouseDown={() => setIsDragging(true)}
                onMouseUp={() => setIsDragging(false)}
                onTouchStart={() => setIsDragging(true)}
                onTouchEnd={() => setIsDragging(false)}
                className="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer slider"
                style={{
                  background: `linear-gradient(to right, #FDB022 0%, #FDB022 ${value}%, #374151 ${value}%, #374151 100%)`,
                }}
              />
              
              {/* Value indicator */}
              <motion.div
                className="absolute top-0 transform -translate-y-10"
                style={{
                  left: `${value}%`,
                  x: '-50%',
                }}
                animate={{
                  scale: isDragging ? 1.2 : 1,
                }}
              >
                <div className="bg-yellow-500 text-gray-900 text-xs font-bold px-2 py-1 rounded">
                  {value}%
                </div>
              </motion.div>
            </div>
            <Sun className="w-5 h-5 text-yellow-400" />
          </div>
        </div>

        {/* Visual representation */}
        <div className="relative h-32 bg-gradient-to-t from-gray-800 to-gray-700 rounded-lg overflow-hidden">
          <motion.div
            className="absolute inset-0 bg-gradient-to-t from-yellow-500/50 to-yellow-300/30"
            animate={{
              opacity: value / 100,
            }}
            transition={{ duration: 0.3 }}
          />
          <div className="absolute inset-0 flex items-center justify-center">
            <motion.div
              animate={{
                scale: 0.5 + (value / 100) * 0.5,
                opacity: 0.5 + (value / 100) * 0.5,
              }}
              transition={{ duration: 0.3 }}
            >
              <Sun className="w-16 h-16 text-yellow-400" />
            </motion.div>
          </div>
        </div>

        {/* Description */}
        <div className="bg-gray-800/50 rounded-lg p-3 border border-gray-700/50">
          <p className="text-xs text-gray-400">
            {value < 30 && "Low brightness - Energy saving mode"}
            {value >= 30 && value < 70 && "Moderate brightness - Balanced comfort"}
            {value >= 70 && "High brightness - Maximum visibility"}
          </p>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-2 gap-4 text-center">
          <div className="bg-gray-800/50 rounded-lg p-3 border border-gray-700/50">
            <div className="text-xs text-gray-400 mb-1">Current LDR</div>
            <div className="text-lg font-bold text-yellow-400">{value}%</div>
          </div>
          <div className="bg-gray-800/50 rounded-lg p-3 border border-gray-700/50">
            <div className="text-xs text-gray-400 mb-1">Energy Saved</div>
            <div className="text-lg font-bold text-green-400">
              {((100 - value) * 0.01).toFixed(2)} kWh
            </div>
          </div>
        </div>
      </div>

      <style jsx>{`
        .slider::-webkit-slider-thumb {
          appearance: none;
          width: 20px;
          height: 20px;
          border-radius: 50%;
          background: #FDB022;
          cursor: pointer;
          box-shadow: 0 0 10px rgba(253, 176, 34, 0.5);
        }
        .slider::-moz-range-thumb {
          width: 20px;
          height: 20px;
          border-radius: 50%;
          background: #FDB022;
          cursor: pointer;
          border: none;
          box-shadow: 0 0 10px rgba(253, 176, 34, 0.5);
        }
      `}</style>
    </div>
  )
}
