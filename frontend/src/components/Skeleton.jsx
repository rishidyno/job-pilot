/**
 * Skeleton loading placeholders.
 * Usage:
 *   <Skeleton className="h-4 w-32" />
 *   <Skeleton.Card />
 *   <Skeleton.StatsRow />
 *   <Skeleton.JobCard />
 */
import clsx from 'clsx'

export default function Skeleton({ className }) {
  return <div className={clsx('skeleton', className)} />
}

Skeleton.StatsRow = function StatsRow({ count = 6 }) {
  return (
    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
      {Array.from({ length: count }).map((_, i) => (
        <div key={i} className="bg-white rounded-xl border border-gray-200 p-5">
          <div className="flex items-center justify-between mb-3">
            <Skeleton className="h-4 w-20" />
            <Skeleton className="h-8 w-8 rounded-lg" />
          </div>
          <Skeleton className="h-8 w-16" />
        </div>
      ))}
    </div>
  )
}

Skeleton.Chart = function Chart() {
  return (
    <div className="bg-white rounded-xl border border-gray-200 p-5">
      <Skeleton className="h-4 w-40 mb-4" />
      <div className="h-64 flex items-end gap-2 px-4">
        {Array.from({ length: 12 }).map((_, i) => (
          <Skeleton key={i} className="flex-1 rounded-t-md" style={{ height: `${20 + Math.random() * 60}%` }} />
        ))}
      </div>
    </div>
  )
}

Skeleton.JobCard = function JobCard() {
  return (
    <div className="bg-white rounded-xl border border-gray-200 p-5">
      <div className="flex items-start gap-4">
        <Skeleton className="w-12 h-12 rounded-full shrink-0" />
        <div className="flex-1 space-y-2">
          <Skeleton className="h-4 w-48" />
          <Skeleton className="h-3 w-32" />
          <Skeleton className="h-3 w-24" />
        </div>
        <Skeleton className="h-6 w-20 rounded-full" />
      </div>
      <div className="flex gap-2 mt-3">
        <Skeleton className="h-5 w-16 rounded-md" />
        <Skeleton className="h-5 w-20 rounded-md" />
        <Skeleton className="h-5 w-14 rounded-md" />
      </div>
      <Skeleton className="h-3 w-full mt-3" />
      <Skeleton className="h-3 w-3/4 mt-1" />
    </div>
  )
}

Skeleton.JobList = function JobList({ count = 5 }) {
  return (
    <div className="space-y-4">
      {Array.from({ length: count }).map((_, i) => <Skeleton.JobCard key={i} />)}
    </div>
  )
}

Skeleton.AppCard = function AppCard() {
  return (
    <div className="bg-white rounded-xl border border-gray-200 p-4">
      <div className="flex items-center gap-4">
        <Skeleton className="h-6 w-20 rounded-full" />
        <div className="flex-1 space-y-1.5">
          <Skeleton className="h-4 w-44" />
          <Skeleton className="h-3 w-32" />
        </div>
        <Skeleton className="h-3 w-16" />
      </div>
    </div>
  )
}

Skeleton.AppList = function AppList({ count = 5 }) {
  return (
    <div className="space-y-3">
      {Array.from({ length: count }).map((_, i) => <Skeleton.AppCard key={i} />)}
    </div>
  )
}

Skeleton.Settings = function SettingsBlock() {
  return (
    <div className="bg-white rounded-xl border border-gray-200 p-6 space-y-4">
      <Skeleton className="h-5 w-24 mb-2" />
      {Array.from({ length: 5 }).map((_, i) => (
        <div key={i}>
          <Skeleton className="h-3 w-20 mb-1" />
          <Skeleton className="h-10 w-full rounded-lg" />
        </div>
      ))}
    </div>
  )
}
