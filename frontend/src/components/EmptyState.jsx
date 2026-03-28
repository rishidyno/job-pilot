/**
 * JOBPILOT — EmptyState Component
 * Contextual illustrations and engaging CTAs.
 */
import { Inbox, Briefcase, FileText, Send, Search, Rocket } from 'lucide-react'

const PRESETS = {
  jobs: { icon: Briefcase, color: 'text-brand-500 dark:text-brand-400', bg: 'bg-brand-50 dark:bg-brand-950/30' },
  applications: { icon: Send, color: 'text-purple-500 dark:text-purple-400', bg: 'bg-purple-50 dark:bg-purple-950/30' },
  resumes: { icon: FileText, color: 'text-indigo-500 dark:text-indigo-400', bg: 'bg-indigo-50 dark:bg-indigo-950/30' },
  search: { icon: Search, color: 'text-amber-500 dark:text-amber-400', bg: 'bg-amber-50 dark:bg-amber-950/30' },
  welcome: { icon: Rocket, color: 'text-emerald-500 dark:text-emerald-400', bg: 'bg-emerald-50 dark:bg-emerald-950/30' },
  default: { icon: Inbox, color: 'text-gray-400 dark:text-surface-500', bg: 'bg-gray-100 dark:bg-surface-800' },
}

export default function EmptyState({ title = 'Nothing here yet', message, action, onAction, preset = 'default', secondaryAction, onSecondaryAction }) {
  const { icon: Icon, color, bg } = PRESETS[preset] || PRESETS.default

  return (
    <div className="flex flex-col items-center justify-center py-12 sm:py-16 px-4 text-center">
      <div className={`w-16 h-16 rounded-2xl ${bg} flex items-center justify-center mb-4`}>
        <Icon className={`w-7 h-7 ${color}`} />
      </div>
      <h3 className="text-base font-semibold text-gray-700 dark:text-surface-200 mb-1">{title}</h3>
      {message && <p className="text-sm text-gray-400 dark:text-surface-500 max-w-sm leading-relaxed">{message}</p>}
      {(action || secondaryAction) && (
        <div className="flex items-center gap-3 mt-5">
          {secondaryAction && onSecondaryAction && (
            <button onClick={onSecondaryAction}
              className="px-4 py-2 text-sm border border-gray-200 dark:border-surface-600 rounded-lg hover:bg-gray-50 dark:hover:bg-surface-700 text-gray-600 dark:text-surface-300">
              {secondaryAction}
            </button>
          )}
          {action && onAction && (
            <button onClick={onAction}
              className="px-5 py-2 bg-brand-600 text-white text-sm font-medium rounded-lg hover:bg-brand-700 active:scale-[0.98] transition-transform">
              {action}
            </button>
          )}
        </div>
      )}
    </div>
  )
}
