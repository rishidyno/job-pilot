/**
 * JOBPILOT — StatsCard Component
 */
import clsx from 'clsx'

export default function StatsCard({ label, value, icon: Icon, color = 'brand', subtext }) {
  const colorMap = {
    brand: 'bg-brand-50 text-brand-600 dark:bg-brand-950/40 dark:text-brand-400',
    green: 'bg-emerald-50 text-emerald-600 dark:bg-emerald-950/40 dark:text-emerald-400',
    amber: 'bg-amber-50 text-amber-600 dark:bg-amber-950/40 dark:text-amber-400',
    red: 'bg-red-50 text-red-600 dark:bg-red-950/40 dark:text-red-400',
    purple: 'bg-purple-50 text-purple-600 dark:bg-purple-950/40 dark:text-purple-400',
    blue: 'bg-blue-50 text-blue-600 dark:bg-blue-950/40 dark:text-blue-400',
  }

  return (
    <div className="bg-white dark:bg-surface-800 rounded-xl border border-gray-200 dark:border-surface-700 p-3 sm:p-5 hover:shadow-sm transition-shadow">
      <div className="flex items-center justify-between mb-2 sm:mb-3">
        <span className="text-xs sm:text-sm font-medium text-gray-500 dark:text-surface-400 truncate">{label}</span>
        {Icon && (
          <div className={clsx('p-1.5 sm:p-2 rounded-lg', colorMap[color])}>
            <Icon className="w-3.5 h-3.5 sm:w-4 sm:h-4" />
          </div>
        )}
      </div>
      <p className="text-xl sm:text-2xl font-bold text-gray-900 dark:text-white">{value ?? '—'}</p>
      {subtext && <p className="text-xs text-gray-400 dark:text-surface-500 mt-1 hidden sm:block">{subtext}</p>}
    </div>
  )
}
