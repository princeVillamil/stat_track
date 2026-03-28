import { useState } from 'react'
import { useParams } from 'react-router-dom'
import { useLeaderboard } from '../hooks/useLeaderboard'
import { useLeaderboardSocket } from '../hooks/useLeaderboardSocket'
import LeaderboardTable from '../components/LeaderboardTable'
import RegionSelector from '../components/RegionSelector'
import ConnectionStatus from '../components/ConnectionStatus'

const VALID_REGIONS = ['NAmerica', 'Europe', 'Asia', 'SAmerica', 'Oceania']
const PAGE_SIZE = 50

export default function LeaderboardPage() {
  const { region = 'NAmerica' } = useParams<{ region: string }>()
  const [offset, setOffset] = useState(0)

  const safeRegion = VALID_REGIONS.includes(region) ? region : 'NAmerica'

  const { data, isLoading, isError, dataUpdatedAt } = useLeaderboard(
    safeRegion, PAGE_SIZE, offset
  )

  // add this line — WebSocket for live updates
  const { status: wsStatus, lastUpdate } = useLeaderboardSocket(safeRegion)

  const totalPages  = data ? Math.ceil(data.total / PAGE_SIZE) : 0
  const currentPage = Math.floor(offset / PAGE_SIZE) + 1

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-white mb-1">Deadlock Leaderboard</h1>
        <p className="text-slate-400 text-sm">Top players updated every 5 minutes</p>
      </div>

      <div className="flex items-center justify-between mb-6 flex-wrap gap-4">
        <RegionSelector currentRegion={safeRegion} />

        <div className="flex items-center gap-4">
          {/* live connection indicator */}
          <ConnectionStatus status={wsStatus} />

          {data && (
            <span className="text-sm text-slate-400">
              {data.total.toLocaleString()} players
            </span>
          )}

          {/* show when WebSocket last got an update */}
          {lastUpdate && (
            <span className="text-xs text-slate-500">
              Live update {lastUpdate.toLocaleTimeString()}
            </span>
          )}
        </div>
      </div>

      {isError && (
        <div className="rounded-lg border border-red-900/50 bg-red-950/20 p-4 mb-6 text-red-400 text-sm">
          Failed to load leaderboard. Your backend may not be running.
        </div>
      )}

      <LeaderboardTable
        entries={data?.entries ?? []}
        isLoading={isLoading}
      />

      {totalPages > 1 && (
        <div className="flex items-center justify-between mt-6">
          <button
            onClick={() => setOffset(Math.max(0, offset - PAGE_SIZE))}
            disabled={offset === 0}
            className="px-4 py-2 text-sm rounded-lg border border-slate-700 text-slate-400 disabled:opacity-30 disabled:cursor-not-allowed hover:bg-slate-800 transition-colors"
          >
            ← Previous
          </button>
          <span className="text-sm text-slate-400">
            Page {currentPage} of {totalPages}
          </span>
          <button
            onClick={() => setOffset(offset + PAGE_SIZE)}
            disabled={currentPage >= totalPages}
            className="px-4 py-2 text-sm rounded-lg border border-slate-700 text-slate-400 disabled:opacity-30 disabled:cursor-not-allowed hover:bg-slate-800 transition-colors"
          >
            Next →
          </button>
        </div>
      )}
    </div>
  )
}