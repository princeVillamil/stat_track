import { Routes, Route, Navigate } from 'react-router-dom'
import LeaderboardPage from './pages/LeaderboardPage'
import PlayerPage from './pages/PlayerPage'

import NavBar from './components/NavBar'

export default function App() {
  return (
    <div className="min-h-screen bg-[#0a0a0f]">
      <NavBar />
      <Routes>
        <Route path="/" element={<Navigate to="/leaderboard/NAmerica" replace />} />
        <Route path="/leaderboard/:region" element={<LeaderboardPage />} />
        <Route path="/player/:accountName" element={<PlayerPage />} />
      </Routes>
    </div>
  )
}