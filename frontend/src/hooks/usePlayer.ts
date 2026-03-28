import { useQuery } from '@tanstack/react-query'
import { api } from '../lib/api'

export function usePlayer(accountName: string) {
  return useQuery({
    queryKey: ['player', accountName],
    queryFn: () => api.getPlayer(accountName),
    enabled: Boolean(accountName),   // don't fetch if name is empty
  })
}

export function usePlayerHistory(accountName: string, region = 'NAmerica') {
  return useQuery({
    queryKey: ['player-history', accountName, region],
    queryFn: () => api.getPlayerHistory(accountName, region),
    enabled: Boolean(accountName),
  })
}