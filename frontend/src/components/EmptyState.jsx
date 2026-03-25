/**
 * JOBPILOT — EmptyState Component
 */
import { Inbox } from 'lucide-react'

export default function EmptyState({ title = 'Nothing here yet', message, action, onAction }) {
  return (
    <div className="flex flex-col items-center justify-center py-16 px-4 text-center">
      <Inbox className="w-12 h-12 text-gray-300 dark:text-surface-600 mb-4" />
      <h3 className="text-sm font-semibold text-gray-600 dark:text-surface-300 mb-1">{title}</h3>
      {message && <p className="text-xs text-gray-400 dark:text-surface-500 max-w-xs">{message}</p>}
      {action && onAction && (
        <button onClick={onAction}
          className="mt-4 px-4 py-2 bg-brand-600 text-white text-sm rounded-lg hover:bg-brand-700">
          {action}
        </button>
      )}
    </div>
  )
}
