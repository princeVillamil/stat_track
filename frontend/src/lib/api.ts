const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'

// generic fetch wrapper — handles errors consistently
async function apiFetch<T>(path: string, params?: Record<string, string | number>): Promise<T> {
  const url = new URL(`${API_BASE}${path}`)

  if (params) {
    Object.entries(params).forEach(([key, value]) => {
      url.searchParams.set(key, String(value))
    })
  }

  const response = await fetch(url.toString())

  if (!response.ok) {
    throw new Error(`API error: ${response.status} ${response.statusText}`)
  }

  return response.json()
}

// named API functions — components never call fetch() directly
export const api = {
  getLeaderboard: (region: string, limit = 50, offset = 0) =>
    apiFetch<import('../types/api').LeaderboardResponse>(
      `/api/v1/leaderboard/${region}`,
      { limit, offset }
    ),

  getPlayer: (accountName: string) =>
    apiFetch<import('../types/api').PlayerProfileResponse>(
      `/api/v1/players/${encodeURIComponent(accountName)}`
    ),

  getPlayerHistory: (accountName: string, region = 'NAmerica') =>
    apiFetch<import('../types/api').PlayerHistoryResponse>(
      `/api/v1/players/${encodeURIComponent(accountName)}/history`,
      { region }
    ),

  getHeroes: () =>
    apiFetch<import('../types/api').HeroResponse[]>('/api/v1/heroes/'),
}