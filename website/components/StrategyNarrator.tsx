'use client'

import { useEffect, useRef } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { AlertCircle, CheckCircle, Info, Zap } from 'lucide-react'
import { cn, formatTimestamp } from '@/lib/utils'
import { StrategyLogEntry } from '@/lib/types'

interface StrategyNarratorProps {
  logs: StrategyLogEntry[]
  className?: string
}

function LogItem({ log }: { log: StrategyLogEntry }) {
  const icons = {
    info: <Info className="w-4 h-4" />,
    warning: <AlertCircle className="w-4 h-4" />,
    success: <CheckCircle className="w-4 h-4" />,
    decision: <Zap className="w-4 h-4" />,
  }

  const colors = {
    info: 'text-blue-400 bg-blue-500/10 border-blue-500/30',
    warning: 'text-yellow-400 bg-yellow-500/10 border-yellow-500/30',
    success: 'text-green-400 bg-green-500/10 border-green-500/30',
    decision: 'text-purple-400 bg-purple-500/10 border-purple-500/30',
  }

  return (
    <motion.div
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: 20 }}
      transition={{ duration: 0.3 }}
      className={cn(
        'p-3 rounded-lg border mb-2 backdrop-blur-sm',
        colors[log.type]
      )}
    >
      <div className="flex items-start gap-3">
        <div className="mt-0.5">{icons[log.type]}</div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center justify-between gap-2 mb-1">
            <span className="text-xs text-gray-400 font-mono">
              {formatTimestamp(log.timestamp)}
            </span>
          </div>
          <p className="text-sm leading-relaxed">{log.message}</p>
          {log.details && (
            <p className="text-xs text-gray-500 mt-1">{log.details}</p>
          )}
        </div>
      </div>
    </motion.div>
  )
}

export default function StrategyNarrator({ logs, className }: StrategyNarratorProps) {
  const scrollRef = useRef<HTMLDivElement>(null)

  // Auto-scroll to bottom when new logs arrive
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight
    }
  }, [logs])

  return (
    <div className={cn('flex flex-col h-full bg-gray-900/50 rounded-lg', className)}>
      {/* Header */}
      <div className="px-4 py-3 border-b border-gray-700/50">
        <h3 className="text-lg font-semibold text-white flex items-center gap-2">
          <Zap className="w-5 h-5 text-purple-400" />
          AI Strategy Narrator
        </h3>
        <p className="text-xs text-gray-400 mt-1">
          Real-time decision explanations and system events
        </p>
      </div>

      {/* Log list */}
      <div
        ref={scrollRef}
        className="flex-1 overflow-y-auto p-4 space-y-2 scrollbar-thin scrollbar-thumb-gray-700 scrollbar-track-gray-800"
      >
        <AnimatePresence mode="popLayout">
          {logs.length === 0 ? (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="flex items-center justify-center h-full text-gray-500 text-sm"
            >
              <div className="text-center">
                <Info className="w-8 h-8 mx-auto mb-2 opacity-50" />
                <p>Waiting for system events...</p>
              </div>
            </motion.div>
          ) : (
            logs.map((log) => <LogItem key={log.id} log={log} />)
          )}
        </AnimatePresence>
      </div>

      {/* Footer stats */}
      <div className="px-4 py-2 border-t border-gray-700/50 bg-gray-800/50">
        <div className="flex items-center justify-between text-xs text-gray-400">
          <span>{logs.length} events logged</span>
          <span className="flex items-center gap-1">
            <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
            Live
          </span>
        </div>
      </div>
    </div>
  )
}
