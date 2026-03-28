import { useEffect, useRef, useState, useCallback } from 'react'
import { useQueryClient } from '@tanstack/react-query'
import type { WebSocketMessage } from '../types/api'

type Status = 'connecting' | 'connected' | 'disconnected' | 'error'

const WS_BASE = import.meta.env.VITE_WS_URL || 'ws://localhost:8000'

export function useLeaderboardSocket(region: string) {
  const queryClient = useQueryClient()
  const socketRef   = useRef<WebSocket | null>(null)
  // const retryRef    = useRef<ReturnType<typeof setTimeout>>() <-- expected 1 argument but none
  const retryRef = useRef<ReturnType<typeof setTimeout> | undefined>(undefined)
  const retryCount  = useRef(0)
  const maxRetries  = 5

  const [status, setStatus]       = useState<Status>('connecting')
  const [lastUpdate, setLastUpdate] = useState<Date | null>(null)

  const connect = useCallback(() => {
    // clean up existing connection before creating new one
    if (socketRef.current) {
      socketRef.current.close()
    }

    const url = `${WS_BASE}/ws/leaderboard/${region}`
    const ws  = new WebSocket(url)
    socketRef.current = ws

    ws.onopen = () => {
      setStatus('connected')
      retryCount.current = 0       // reset retry counter on successful connect
      console.log(`WebSocket connected: ${region}`)
    }

    ws.onmessage = (event) => {
      try {
        const message: WebSocketMessage = JSON.parse(event.data)

        if (message.event === 'ping') {
          // server keepalive — no action needed
          return
        }

        if (message.event === 'snapshot') {
          // initial data on connect — update React Query cache directly
          // this means the leaderboard shows instantly without an extra API call
          queryClient.setQueryData(
            ['leaderboard', region, 50, 0],
            {
              region:  message.region,
              total:   message.total,
              limit:   50,
              offset:  0,
              entries: message.entries,
            }
          )
          setLastUpdate(new Date())
        }

        if (message.event === 'leaderboard_updated') {
          // Celery just updated the data — invalidate cache so React Query
          // refetches fresh data in the background
          queryClient.invalidateQueries({
            queryKey: ['leaderboard', region]
          })
          setLastUpdate(new Date())
          console.log(`Leaderboard updated: ${message.updated} players`)
        }

      } catch (e) {
        console.error('Failed to parse WebSocket message:', e)
      }
    }

    ws.onclose = (event) => {
      setStatus('disconnected')

      // don't retry if closed intentionally (code 1000)
      if (event.code === 1000) return

      // exponential backoff: 1s, 2s, 4s, 8s, 16s
      if (retryCount.current < maxRetries) {
        const delay = Math.pow(2, retryCount.current) * 1000
        retryCount.current++

        console.log(`WebSocket closed. Retrying in ${delay}ms... (attempt ${retryCount.current})`)

        retryRef.current = setTimeout(() => {
          setStatus('connecting')
          connect()
        }, delay)
      } else {
        setStatus('error')
        console.error('WebSocket max retries reached')
      }
    }

    ws.onerror = () => {
      setStatus('error')
      // onclose fires after onerror — retry logic handled there
    }

  }, [region, queryClient])

  useEffect(() => {
    connect()

    // cleanup on unmount or region change
    return () => {
      clearTimeout(retryRef.current)
      socketRef.current?.close(1000, 'Component unmounted')
    }
  }, [connect])

  return { status, lastUpdate }
}