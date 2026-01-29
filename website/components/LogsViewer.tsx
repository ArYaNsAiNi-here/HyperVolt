'use client'

import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Terminal, X, ChevronDown, ChevronUp } from 'lucide-react'
import { StrategyLogEntry } from '@/lib/types'
import StrategyNarrator from './StrategyNarrator'

interface LogsViewerProps {
  logs: StrategyLogEntry[]
  className?: string
}

export default function LogsViewer({ logs, className }: LogsViewerProps) {
  const [isOpen, setIsOpen] = useState(false)
  const [isExpanded, setIsExpanded] = useState(false)

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
          {logs.length > 0 && (
            <span className="absolute -top-2 -right-2 bg-red-500 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center font-bold">
              {logs.length > 99 ? '99+' : logs.length}
            </span>
          )}
        </div>
      </motion.button>

      {/* Logs panel */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, y: 100 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 100 }}
            transition={{ type: 'spring', damping: 25, stiffness: 300 }}
            className={`fixed ${
              isExpanded ? 'inset-4' : 'bottom-4 right-4 w-full max-w-2xl'
            } z-40 bg-gray-900/95 backdrop-blur-lg border border-gray-700 rounded-lg shadow-2xl overflow-hidden ${className}`}
          >
            {/* Header */}
            <div className="flex items-center justify-between px-4 py-3 border-b border-gray-700 bg-gray-800/50">
              <div className="flex items-center gap-2">
                <Terminal className="w-5 h-5 text-purple-400" />
                <h3 className="text-lg font-semibold text-white">
                  System Logs
                </h3>
                <span className="text-xs text-gray-400 bg-gray-700 px-2 py-1 rounded">
                  {logs.length} events
                </span>
              </div>
              <div className="flex items-center gap-2">
                <button
                  onClick={() => setIsExpanded(!isExpanded)}
                  className="p-2 hover:bg-gray-700 rounded-lg transition-colors"
                  aria-label={isExpanded ? 'Minimize' : 'Maximize'}
                >
                  {isExpanded ? (
                    <ChevronDown className="w-5 h-5 text-gray-400" />
                  ) : (
                    <ChevronUp className="w-5 h-5 text-gray-400" />
                  )}
                </button>
                <button
                  onClick={() => setIsOpen(false)}
                  className="p-2 hover:bg-gray-700 rounded-lg transition-colors"
                  aria-label="Close logs"
                >
                  <X className="w-5 h-5 text-gray-400" />
                </button>
              </div>
            </div>

            {/* Logs content */}
            <div className={isExpanded ? 'h-[calc(100%-56px)]' : 'h-96'}>
              <StrategyNarrator logs={logs} className="h-full" />
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  )
}
