import { useHeroes } from '../hooks/useLeaderboard'

interface Props {
  heroIds: number[]
  max?: number
}

export default function HeroIcons({ heroIds, max = 3 }: Props) {
  const { data: heroes } = useHeroes()

  if (!heroes || heroIds.length === 0) {
    return <span className="text-slate-600 text-xs">—</span>
  }

  const heroMap = new Map(heroes.map(h => [h.id, h]))
  const displayHeroes = heroIds.slice(0, max)

  return (
    <div className="flex items-center gap-1">
      {displayHeroes.map(id => {
        const hero = heroMap.get(id)
        if (!hero) return null

        return (
          <div
            key={id}
            className="w-7 h-7 rounded overflow-hidden bg-slate-800 border border-slate-700"
            title={hero.name}
          >
            {hero.icon_url ? (
              <img
                src={hero.icon_url}
                alt={hero.name}
                className="w-full h-full object-cover"
                loading="lazy"
              />
            ) : (
              // fallback — hero name initials
              <div className="w-full h-full flex items-center justify-center text-[9px] text-slate-400">
                {hero.name.slice(0, 2)}
              </div>
            )}
          </div>
        )
      })}
    </div>
  )
}