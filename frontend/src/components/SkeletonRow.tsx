// skeleton rows show while data is loading
// better UX than a spinner — users see the layout before data arrives
export default function SkeletonRow() {
  return (
    <div className="flex items-center gap-4 px-4 py-3 border-b border-slate-800/50">
      <div className="w-12 h-4 bg-slate-800 rounded animate-pulse" />
      <div className="flex-1 h-4 bg-slate-800 rounded animate-pulse" />
      <div className="w-20 h-4 bg-slate-800 rounded animate-pulse" />
      <div className="flex gap-1">
        <div className="w-7 h-7 bg-slate-800 rounded animate-pulse" />
        <div className="w-7 h-7 bg-slate-800 rounded animate-pulse" />
        <div className="w-7 h-7 bg-slate-800 rounded animate-pulse" />
      </div>
    </div>
  )
}