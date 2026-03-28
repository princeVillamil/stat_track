import { useNavigate } from 'react-router-dom'

const REGIONS = [
  { id: 'NAmerica', label: 'NA'      },
  { id: 'Europe',   label: 'EU'      },
  { id: 'Asia',     label: 'Asia'    },
  { id: 'SAmerica', label: 'SA'      },
  { id: 'Oceania',  label: 'OCE'     },
]

interface Props {
  currentRegion: string
}

export default function RegionSelector({ currentRegion }: Props) {
  const navigate = useNavigate()

  return (
    <div className="flex gap-1 p-1 bg-slate-900 rounded-lg border border-slate-800">
      {REGIONS.map(region => (
        <button
          key={region.id}
          onClick={() => navigate(`/leaderboard/${region.id}`)}
          className={`
            px-4 py-1.5 rounded-md text-sm font-medium transition-all duration-150
            ${currentRegion === region.id
              ? 'bg-blue-600 text-white'
              : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800'
            }
          `}
        >
          {region.label}
        </button>
      ))}
    </div>
  )
}