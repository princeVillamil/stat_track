export interface LeaderboardEntry {
  rank: number
  account_name: string
  badge_level: number
  ranked_rank: number | null
  ranked_subrank: number | null
  top_hero_ids: number[]
}

export interface LeaderboardResponse {
  region: string
  total: number
  limit: number
  offset: number
  entries: LeaderboardEntry[]
}

export interface PlayerProfileResponse {
  account_name: string
  account_id: number | null
  ranks: Record<string, { rank: number; badge_level: number }>
  first_seen: string | null
}

export interface HeroResponse {
  id: number
  name: string
  class_name: string
  hero_type: string | null
  icon_url: string | null
}

export interface RankHistoryPoint {
  rank: number
  badge_level: number
  snapshot_at: string
}

export interface PlayerHistoryResponse {
  account_name: string
  region: string
  history: RankHistoryPoint[]
}

// WebSocket message types
export type WebSocketMessage =
  | { event: 'snapshot'; region: string; total: number; entries: LeaderboardEntry[] }
  | { event: 'leaderboard_updated'; region: string; updated: number }
  | { event: 'ping' }