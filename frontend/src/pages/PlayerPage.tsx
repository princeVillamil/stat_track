import { useParams, useNavigate } from 'react-router-dom'
import { usePlayer, usePlayerHistory } from '../hooks/usePlayer'
import RankHistoryChart from '../components/RankHistoryChart'

const REGIONS = ['NAmerica', 'Europe', 'Asia', 'SAmerica', 'Oceania']

export default function PlayerPage() {
  const { accountName = '' } = useParams<{ accountName: string }>()
  const navigate = useNavigate()

  const decodedName = decodeURIComponent(accountName)
  const { data: player, isLoading, isError } = usePlayer(decodedName)
  const { data: history } = usePlayerHistory(decodedName)

  if (isLoading) {
    return (
      <div className="max-w-2xl mx-auto px-4 py-8">
        <div className="h-8 w-48 bg-slate-800 rounded animate-pulse mb-4" />
        <div className="h-4 w-32 bg-slate-800 rounded animate-pulse" />
      </div>
    )
  }

  if (isError || !player) {
    return (
      <div className="max-w-2xl mx-auto px-4 py-8">
        <button
          onClick={() => navigate(-1)}
          className="text-slate-400 hover:text-white text-sm mb-6 flex items-center gap-1"
        >
          ← Back
        </button>
        <div className="text-center py-16 text-slate-500">
          Player "{decodedName}" not found on any leaderboard.
        </div>
      </div>
    )
  }

  const rankedRegions = Object.entries(player.ranks)

  return (
    <div className="max-w-2xl mx-auto px-4 py-8">
      {/* back button */}
      <button
        onClick={() => navigate(-1)}
        className="text-slate-400 hover:text-white text-sm mb-6 flex items-center gap-1 transition-colors"
      >
        ← Back to leaderboard
      </button>

      {/* player header */}
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-white">{player.account_name}</h1>
        {player.first_seen && (
          <p className="text-slate-400 text-sm mt-1">
            First seen {new Date(player.first_seen).toLocaleDateString()}
          </p>
        )}
      </div>

      {/* region ranks grid */}
      <div className="mb-8">
        <h2 className="text-sm font-medium text-slate-400 uppercase tracking-wider mb-3">
          Rankings
        </h2>
        {rankedRegions.length === 0 ? (
          <p className="text-slate-500 text-sm">Not currently ranked in any region.</p>
        ) : (
          <div className="grid grid-cols-2 gap-3 sm:grid-cols-3">
            {rankedRegions.map(([region, data]) => (
              <div
                key={region}
                className="rounded-lg border border-slate-800 bg-slate-900/50 p-4"
              >
                <div className="text-xs text-slate-500 mb-1">{region}</div>
                <div className="text-xl font-bold text-white font-mono">
                  #{data.rank}
                </div>
                <div className="text-xs text-slate-400 mt-0.5">
                  Badge {data.badge_level}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* rank history — simple list for now, chart comes Day 11 */}
      {history && history.history.length > 0 && (
        <div>
          <h2 className="text-sm font-medium text-slate-400 uppercase tracking-wider mb-3">
            Rank history — NAmerica
          </h2>
          <div className="rounded-lg border border-slate-800 bg-slate-900/50 p-4">
            <RankHistoryChart
              history={history.history}
              playerName={player.account_name}
            />
          </div>
        </div>
      )}
    </div>
  )
}