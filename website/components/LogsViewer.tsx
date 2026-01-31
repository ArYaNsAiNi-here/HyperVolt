'use client'

import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { ChevronUp, ChevronDown, List, X } from 'lucide-react'
import { StrategyLogEntry } from '@/lib/types'
import StrategyNarrator from './StrategyNarrator'

interface LogsViewerProps {
  logs: StrategyLogEntry[]
}

export default function LogsViewer({ logs }: LogsViewerProps) {
  const [isOpen, setIsOpen] = useState(false)
  const [isExpanded, setIsExpanded] = useState(false)

  return (
    <>
      {/* Floating Toggle Button (Visible when closed) */}
      <AnimatePresence>
        {!isOpen && (
          <motion.button
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 20 }}
            onClick={() => setIsOpen(true)}
            className="fixed bottom-6 right-6 z-50 bg-purple-600 hover:bg-purple-500 text-white p-4 rounded-full shadow-lg border border-purple-400/30 backdrop-blur-sm transition-all hover:scale-105 group"
          >
            <List className="w-6 h-6" />
            <span className="absolute right-full mr-3 top-1/2 -translate-y-1/2 px-2 py-1 bg-gray-900 text-xs rounded opacity-0 group-hover:opacity-100 whitespace-nowrap transition-opacity pointer-events-none">
              View AI Logs
            </span>
          </motion.button>
        )}
      </AnimatePresence>

      {/* Main Logs Panel */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, y: 100, scale: 0.95 }}
            animate={{
              opacity: 1,
              y: 0,
              scale: 1,
              height: isExpanded ? '80vh' : 'auto',
              width: isExpanded ? '600px' : '400px'
            }}
            exit={{ opacity: 0, y: 100, scale: 0.95 }}
            transition={{ type: 'spring', damping: 25, stiffness: 200 }}
            className="fixed bottom-6 right-6 z-50 bg-gray-900/95 backdrop-blur-md border border-gray-700 rounded-xl shadow-2xl overflow-hidden flex flex-col"
          >
            {/* Header */}
            <div className="flex items-center justify-between px-4 py-3 bg-gray-800/50 border-b border-gray-700">
              <div className="flex items-center gap-2">
                <List className="w-4 h-4 text-purple-400" />
                <span className="font-semibold text-white">System Logs</span>
              </div>
              <div className="flex items-center gap-1">
                <button
                  onClick={() => setIsExpanded(!isExpanded)}
                  className="p-1.5 hover:bg-gray-700 rounded text-gray-400 hover:text-white transition-colors"
                  title={isExpanded ? "Collapse" : "Expand"}
                >
                  {isExpanded ? <ChevronDown className="w-4 h-4" /> : <ChevronUp className="w-4 h-4" />}
                </button>
                <button
                  onClick={() => setIsOpen(false)}
                  className="p-1.5 hover:bg-red-500/20 rounded text-gray-400 hover:text-red-400 transition-colors"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>
            </div>

            {/* Content Area */}
            <div className={isExpanded ? 'flex-1 min-h-0' : 'h-96'}>
              {/* FIX: Removed the 'logs' prop since StrategyNarrator now polls internally */}
              <StrategyNarrator
                className="h-full border-0 bg-transparent"
                initialLogs={logs} // Optional: Pass initial logs if you want to preload some
              />
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  )
}