'use client'

import { useEffect, useRef, useState, useCallback } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { AlertCircle, CheckCircle, Info, Zap } from 'lucide-react'
import { cn, formatTimestamp } from '@/lib/utils'
import { StrategyLogEntry } from '@/lib/types'

// NOTE: We removed the useWebSocket import since you are using REST API polling

interface StrategyNarratorProps {
  initialLogs?: StrategyLogEntry[]
  className?: string
  onLogCountChange?: (count: number) => void
  // 'logs' prop removed or made optional if you passed it from parent,
  // but we will manage state internally via polling.
}

function LogItem({ log }: { log: StrategyLogEntry }) {
  const icons = {
    info: <Info className="w-4 h-4" />,
    warning: <AlertCircle className="w-4 h-4" />,
    success: <CheckCircle className="w-4 h-4" />,
    decision: <Zap className="w-4 h-4" />,
    error: <AlertCircle className="w-4 h-4" />,
  }

  const colors = {
    info: 'text-blue-400 bg-blue-500/10 border-blue-500/30',
    warning: 'text-yellow-400 bg-yellow-500/10 border-yellow-500/30',
    success: 'text-green-400 bg-green-500/10 border-green-500/30',
    decision: 'text-purple-400 bg-purple-500/10 border-purple-500/30',
    error: 'text-red-400 bg-red-500/10 border-red-500/30',
  }

  const type = log.type || 'info'

  return (
    <motion.div
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: 20 }}
      transition={{ duration: 0.3 }}
      className={cn(
        'p-3 rounded-lg border mb-2 backdrop-blur-sm',
        colors[type] || colors.info
      )}
    >
      <div className="flex items-start gap-3">
        <div className="mt-0.5">{icons[type] || icons.info}</div>
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

export default function StrategyNarrator({ initialLogs = [], className, onLogCountChange }: StrategyNarratorProps) {
  const scrollRef = useRef<HTMLDivElement>(null)
  const [logs, setLogs] = useState<StrategyLogEntry[]>(initialLogs)

  // Track IDs we've already seen to prevent duplicates
  const processedIds = useRef<Set<string>>(new Set(initialLogs.map(l => l.id)))

  // Notify parent of log count changes
  useEffect(() => {
    onLogCountChange?.(logs.length)
  }, [logs.length, onLogCountChange])

  // --- POLLING LOGIC ---
  const fetchRecentDecisions = useCallback(async () => {
    try {
      // Poll the 'recent' endpoint from your AIDecisionViewSet
      // Adjust URL if your API base URL is different
      const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
      const res = await fetch(`${API_BASE}/api/ai-decisions/recent/?hours=1`)

      if (res.ok) {
        const decisions = await res.json()

        // Map Django AI decisions to StrategyLogEntry format
        const newLogs: StrategyLogEntry[] = []

        // Handle array response
        const decisionList = Array.isArray(decisions) ? decisions : (decisions.results || [])

        decisionList.forEach((decision: any) => {
          // Use DB ID or create a unique one
          const id = decision.id?.toString() || `decision-${decision.timestamp}`

          if (!processedIds.current.has(id)) {
            processedIds.current.add(id)

            // Extract meaningful info from the decision JSON
            const details = decision.decision?.recommendation || decision.reasoning || "AI Optimized Source"
            const source = decision.decision?.current_decision?.primary_source || "AUTO"

            newLogs.push({
              id,
              timestamp: decision.timestamp,
              type: 'decision', // Force type to 'decision' for the narrator
              message: `AI Decision: Switched to ${source.toUpperCase()}`,
              details: details
            })
          }
        })

        if (newLogs.length > 0) {
          // Add new logs to state, keeping the list size manageable (e.g., last 50)
          setLogs(prev => [...prev, ...newLogs].slice(-50))
        }
      }
    } catch (error) {
      console.warn("Failed to poll AI decisions", error)
    }
  }, [])

  // Poll every 5 seconds
  useEffect(() => {
    fetchRecentDecisions() // Initial fetch
    const interval = setInterval(fetchRecentDecisions, 5000)
    return () => clearInterval(interval)
  }, [fetchRecentDecisions])

  // Auto-scroll to bottom when logs change
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight
    }
  }, [logs])

  return (
    <div className={cn('flex flex-col h-full bg-gray-900/50 rounded-lg', className)}>
      <div className="px-4 py-3 border-b border-gray-700/50">
        <h3 className="text-lg font-semibold text-white flex items-center gap-2">
          <Zap className="w-5 h-5 text-purple-400" />
          AI Strategy Narrator
        </h3>
        <p className="text-xs text-gray-400 mt-1">
          Real-time decision explanations (Polling)
        </p>
      </div>

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