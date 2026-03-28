import {
  LineChart, Line, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer
} from 'recharts'
import type { RankHistoryPoint } from '../types/api'

interface Props {
  history: RankHistoryPoint[]
  playerName: string
}

// custom tooltip — shows rank and date on hover
function CustomTooltip({ active, payload, label }: any) {
  if (!active || !payload?.length) return null

  return (
    <div className="bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-sm">
      <p className="text-slate-400 text-xs mb-1">{label}</p>
      <p className="text-white font-mono font-bold">
        Rank #{payload[0].value}
      </p>
    </div>
  )
}

export default function RankHistoryChart({ history, playerName }: Props) {
  if (history.length < 2) {
    return (
      <div className="flex items-center justify-center h-32 text-slate-500 text-sm">
        Not enough data yet — check back after a few hours
      </div>
    )
  }

  // transform data for recharts
  // invert rank so rank 1 shows at the TOP of the chart (better UX)
  const maxRank = Math.max(...history.map(p => p.rank))

  const chartData = history.map(point => ({
    date: new Date(point.snapshot_at).toLocaleDateString('en-US', {
      month: 'short',
      day:   'numeric',
      hour:  'numeric',
    }),
    rank:         point.rank,
    invertedRank: maxRank - point.rank + 1,  // inverted for chart direction
  }))

  return (
    <ResponsiveContainer width="100%" height={200}>
      <LineChart data={chartData} margin={{ top: 5, right: 5, bottom: 5, left: 0 }}>
        <CartesianGrid
          strokeDasharray="3 3"
          stroke="#1e293b"
          vertical={false}
        />
        <XAxis
          dataKey="date"
          tick={{ fill: '#64748b', fontSize: 10 }}
          tickLine={false}
          axisLine={false}
          // show fewer ticks to avoid overcrowding
          interval={Math.floor(chartData.length / 5)}
        />
        <YAxis
          tick={{ fill: '#64748b', fontSize: 10 }}
          tickLine={false}
          axisLine={false}
          tickFormatter={(val) => `#${maxRank - val + 1}`}  // convert back to rank
          reversed={false}
          domain={['auto', 'auto']}
        />
        <Tooltip content={<CustomTooltip />} />
        <Line
          type="monotone"
          dataKey="invertedRank"
          stroke="#3b82f6"
          strokeWidth={2}
          dot={false}               // no dots on each data point — too cluttered
          activeDot={{ r: 4, fill: '#3b82f6', stroke: '#0a0a0f', strokeWidth: 2 }}
        />
      </LineChart>
    </ResponsiveContainer>
  )
}