'use client'

import { useState, useCallback } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { ChevronUp, ChevronDown, List, X, Terminal } from 'lucide-react'
import { StrategyLogEntry } from '@/lib/types'
import StrategyNarrator from './StrategyNarrator'

interface LogsViewerProps {
  logs: StrategyLogEntry[]
}

export default function LogsViewer({ logs }: LogsViewerProps) {
  const [isOpen, setIsOpen] = useState(false)
  const [isExpanded, setIsExpanded] = useState(false)
  const [actualLogCount, setActualLogCount] = useState(logs.length)

  const handleLogCountChange = useCallback((count: number) => {
    setActualLogCount(count)
  }, [])

  return (
    <>
      {/* Floating toggle button */}
      <motion.button
        initial={{ opacity: 0, scale: 0 }}
        animate={{ opacity: 1, scale: 1 }}
        whileHover={{ scale: 1.1 }}
        whileTap={{ scale: 0.95 }}
        onClick={() => setIsOpen(!isOpen)}
        className="fixed bottom-6 right-6 z-50 p-4 bg-gradient-to-br from-purple-600 to-blue-600 rounded-full shadow-2xl hover:shadow-purple-500/50 transition-all duration-300"
        aria-label="Toggle logs viewer"
      >
        <div className="relative">
          <Terminal className="w-6 h-6 text-white" />
          {actualLogCount > 0 && (
            <span className="absolute -top-3 -right-3 bg-red-500 text-white text-[10px] rounded-full w-5 h-5 flex items-center justify-center font-bold border-2 border-purple-600">
              {actualLogCount > 99 ? '99+' : actualLogCount}
            </span>
          )}
        </div>
      </motion.button>

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
                <Terminal className="w-5 h-5 text-purple-400" />
                <h3 className="text-lg font-semibold text-white">
                  System Logs
                </h3>
                <span className="text-xs text-gray-400 bg-gray-700 px-2 py-1 rounded">
                  {actualLogCount} events
                </span>
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

            {/* Logs content */}
            <div className={isExpanded ? 'h-[calc(100%-56px)]' : 'h-96'}>
              <StrategyNarrator
                initialLogs={logs}
                className="h-full"
                onLogCountChange={handleLogCountChange}
              />
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  )
}