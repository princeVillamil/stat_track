import { useNavigate } from 'react-router-dom'
import type { LeaderboardEntry } from '../types/api'
import RankBadge from './RankBadge'
// import HeroIcons from './HeroIcons'
import SkeletonRow from './SkeletonRow'


interface Props {
  entries: LeaderboardEntry[]
  isLoading: boolean
  highlightedPlayer?: string   // account_name to highlight
}

const RANKS: Record<number, string> = {
  0: "Obscurus",
  1: "Initiate",
  2: "Seeker",
  3: "Alchemist",
  4: "Arcanist",
  5: "Ritualist",
  6: "Emissary",
  7: "Archon",
  8: "Oracle",
  9: "Phantom",
  10: "Ascendant",
  11: "Eternus",
}
function getRankName(tier: number): string {
  return RANKS[tier] ?? "Unknown"
}
function decodeBadgeLevel(badgeLevel: number) {
  return {
    tier: Math.floor(badgeLevel / 10),
    subrank: badgeLevel % 10,
  }
}


export default function LeaderboardTable({ entries, isLoading, highlightedPlayer }: Props) {
  const navigate = useNavigate()

  if (isLoading) {
    return (
      <div className="rounded-lg border border-slate-800 overflow-hidden">
        {Array.from({ length: 20 }).map((_, i) => (
          <SkeletonRow key={i} />
        ))}
      </div>
    )
  }

  if (entries.length === 0) {
    return (
      <div className="text-center py-16 text-slate-500">
        No leaderboard data yet. Check back in a few minutes.
      </div>
    )
  }

  return (
    <div className="rounded-lg border border-slate-800 overflow-hidden">
      {/* header */}
      <div className="grid grid-cols-[auto_1fr_auto_auto] gap-4 px-4 py-2 bg-slate-900/50 border-b border-slate-800">
        <span className="text-xs text-slate-500 uppercase tracking-wider w-12">Rank</span>
        <span className="text-xs text-slate-500 uppercase tracking-wider">Player</span>
        <span className="text-xs text-slate-500 uppercase tracking-wider">Tier</span>
        {/* <span className="text-xs text-slate-500 uppercase tracking-wider">Top Heroes</span> */}
      </div>

      {/* rows */}
      {entries.map(entry => (
        <div
          key={entry.account_name}
          onClick={() => navigate(`/player/${encodeURIComponent(entry.account_name)}`)}
          className={`
            grid grid-cols-[auto_1fr_auto_auto] gap-4 px-4 py-3
            border-b border-slate-800/50 cursor-pointer
            transition-colors duration-100
            hover:bg-slate-800/40
            ${highlightedPlayer === entry.account_name ? 'bg-blue-950/30' : ''}
            ${entry.rank <= 3 ? 'bg-yellow-950/10' : ''}
          `}
        >
          {/* rank */}
          <RankBadge rank={entry.rank} badgeLevel={entry.badge_level} />

          {/* player name */}
          <div className="flex items-center min-w-0">
            <span className="text-sm text-slate-200 truncate font-medium">
              {entry.account_name}
            </span>
            {/* ranked tier — shows as "XI-6" for ranked_rank=11, ranked_subrank=6 */}
            {/* {entry.ranked_rank && (
              <span className="ml-2 text-xs text-slate-500 flex-shrink-0">
                {toRoman(entry.ranked_rank)}-{entry.ranked_subrank}
              </span>
            )} */}
          </div>

          {/* badge level */}
          <span className="text-xs text-slate-400 font-mono self-center">
            {getRankName(decodeBadgeLevel(entry.badge_level).tier)}
            <span className="text-slate-600 ml-1">
              {decodeBadgeLevel(entry.badge_level).subrank > 0 ? `- ${toRoman(decodeBadgeLevel(entry.badge_level).subrank)}` : "Obscurus"}
            </span>
          </span>

          {/* hero icons */}
          {/* <div className="self-center">
            <HeroIcons heroIds={entry.top_hero_ids} max={3} />
          </div> */}
        </div>
      ))}
    </div>
  )
}

// convert ranked_rank number to roman numeral display
function toRoman(num: number): string {
  const map: [number, string][] = [
    [10, 'X'], [9, 'IX'], [5, 'V'], [4, 'IV'], [1, 'I']
  ]
  let result = ''
  for (const [value, numeral] of map) {
    while (num >= value) {
      result += numeral
      num -= value
    }
  }
  return result
}