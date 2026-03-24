/**
 * JOBPILOT — StatsCard Component
 * Displays a single metric on the dashboard overview row.
 */

import clsx from 'clsx'

export default function StatsCard({ label, value, icon: Icon, color = 'brand', subtext }) {
  const colorMap = {
    brand: 'bg-brand-50 text-brand-600',
    green: 'bg-emerald-50 text-emerald-600',
    amber: 'bg-amber-50 text-amber-600',
    red: 'bg-red-50 text-red-600',
    purple: 'bg-purple-50 text-purple-600',
    blue: 'bg-blue-50 text-blue-600',
  }

  return (
    <div className="bg-white rounded-xl border border-gray-200 p-5 hover:shadow-sm transition-shadow">
      <div className="flex items-center justify-between mb-3">
        <span className="text-sm font-medium text-gray-500">{label}</span>
        {Icon && (
          <div className={clsx('p-2 rounded-lg', colorMap[color])}>
            <Icon className="w-4 h-4" />
          </div>
        )}
      </div>
      <p className="text-2xl font-bold text-gray-900">{value ?? '—'}</p>
      {subtext && <p className="text-xs text-gray-400 mt-1">{subtext}</p>}
    </div>
  )
}
