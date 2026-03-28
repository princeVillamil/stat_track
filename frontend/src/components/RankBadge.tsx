interface Props {
  rank: number
  badgeLevel: number
}

// badge level maps to Deadlock's rank tiers
function getBadgeColor(badgeLevel: number): string {
  if (badgeLevel >= 110) return 'text-yellow-400 border-yellow-400'
  if (badgeLevel >= 100) return 'text-purple-400 border-purple-400'
  if (badgeLevel >= 90)  return 'text-blue-400 border-blue-400'
  return 'text-slate-400 border-slate-400'
}

export default function RankBadge({ rank, badgeLevel }: Props) {
  return (
    <div className="flex items-center gap-2">
      {/* rank number */}
      <span className={`
        text-sm font-mono font-bold w-8 text-center
        ${rank <= 3 ? 'text-yellow-400' : 'text-slate-400'}
      `}>
        #{rank}
      </span>

      {/* badge level pill */}
      <span className={`
        text-xs font-mono px-2 py-0.5 rounded-full border
        ${getBadgeColor(badgeLevel)}
        bg-transparent
      `}>
        {badgeLevel}
      </span>
    </div>
  )
}