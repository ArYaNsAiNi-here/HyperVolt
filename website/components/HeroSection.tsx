'use client'

import { motion } from 'framer-motion'
import { ChevronDown } from 'lucide-react'
import dynamic from 'next/dynamic'

const DigitalTwin = dynamic(() => import('@/components/DigitalTwin'), {
  ssr: false,
  loading: () => (
    <div className="w-full h-full flex items-center justify-center">
      <div className="flex flex-col items-center gap-3">
        <div className="w-12 h-12 border-4 border-blue-500 border-t-transparent rounded-full animate-spin" />
        <div className="text-white text-lg">Loading HyperVolt 3D Model...</div>
      </div>
    </div>
  ),
})

interface HeroSectionProps {
  lightIntensity: number
  activeSource: 'solar' | 'battery' | 'grid'
  brightnessThreshold: number
  weatherCondition: string
  onScrollClick: () => void
}

export default function HeroSection({
  lightIntensity,
  activeSource,
  brightnessThreshold,
  weatherCondition,
  onScrollClick,
}: HeroSectionProps) {
  return (
    // CHANGE 1: Use h-[100dvh] instead of h-screen to account for mobile browser bars
    <section className="relative w-full h-dvh">
      {/* Full viewport 3D model */}
      <div className="absolute inset-0 w-full h-full">
        <DigitalTwin
          lightIntensity={lightIntensity}
          activeSource={activeSource}
          brightnessThreshold={brightnessThreshold}
          weatherCondition={weatherCondition}
          className="w-full h-full"
        />
      </div>

      {/* Overlay with branding */}
      <div className="absolute inset-0 pointer-events-none">
        {/* CHANGE 2:
            - Reduced base padding to p-4 for smaller screens
            - Added pb-20 (padding-bottom) specifically to lift the bottom button up away from the address bar/home indicator
            - Kept md:p-8 for desktop layouts
        */}
        <div className="container mx-auto h-full flex flex-col justify-between p-4 pb-20 md:p-8">
          {/* Top branding */}
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5, duration: 0.8 }}
            className="text-center mt-8 md:mt-0" // Added margin-top for mobile safe area
          >
            <h1 className="text-5xl md:text-7xl font-bold text-white mb-4 drop-shadow-2xl">
              HyperVolt
            </h1>
            <p className="text-xl md:text-2xl text-gray-200 drop-shadow-lg">
              AI-Driven Energy Orchestrator
            </p>
          </motion.div>

          {/* Scroll indicator */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 1.5, duration: 0.8 }}
            className="flex flex-col items-center pointer-events-auto"
          >
            <button
              onClick={onScrollClick}
              className="flex flex-col items-center gap-2 group cursor-pointer hover:scale-110 transition-transform"
              aria-label="Scroll to dashboard"
            >
              <span className="text-white text-sm font-medium">
                Explore Dashboard
              </span>
              <motion.div
                animate={{ y: [0, 10, 0] }}
                transition={{
                  duration: 1.5,
                  repeat: Infinity,
                  ease: 'easeInOut',
                }}
                className="p-2 bg-white/10 backdrop-blur-sm rounded-full border border-white/20"
              >
                <ChevronDown className="w-6 h-6 text-white" />
              </motion.div>
            </button>
          </motion.div>
        </div>
      </div>

      {/* Gradient overlay for better text visibility */}
      <div className="absolute inset-0 bg-linear-to-b from-black/30 via-transparent to-black/30 pointer-events-none" />
    </section>
  )
}