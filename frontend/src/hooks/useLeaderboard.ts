import { useQuery, useQueryClient } from '@tanstack/react-query'
import { api } from '../lib/api'
import type { LeaderboardResponse } from '../types/api'

export function useLeaderboard(region: string, limit = 50, offset = 0) {
  return useQuery({
    queryKey: ['leaderboard', region, limit, offset],
    queryFn: () => api.getLeaderboard(region, limit, offset),
    // background refetch every 30 seconds as a fallback
    // WebSocket updates will keep it fresh in real-time
    refetchInterval: 30_000,
  })
}

export function useHeroes() {
  return useQuery({
    queryKey: ['heroes'],
    queryFn: api.getHeroes,
    // heroes never change — cache for 1 hour matching backend
    staleTime: 3_600_000,
  })
}