import { Link } from 'react-router-dom'

export default function NavBar() {
  return (
    <nav className="border-b border-slate-800/50 bg-slate-950/50 backdrop-blur-sm sticky top-0 z-10">
      <div className="max-w-4xl mx-auto px-4 py-3 flex items-center justify-between">
        <Link
          to="/leaderboard/NAmerica"
          className="text-white font-bold tracking-tight hover:text-blue-400 transition-colors"
        >
          Deadlock<span className="text-blue-400">Stats</span>
        </Link>

        <div className="flex items-center gap-4 text-sm">
          <Link
            to="/leaderboard/NAmerica"
            className="text-slate-400 hover:text-white transition-colors"
          >
            Leaderboard
          </Link>
        </div>
      </div>
    </nav>
  )
}