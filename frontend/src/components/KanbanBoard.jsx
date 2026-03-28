/**
 * JOBPILOT — Kanban Board for Applications
 * Drag-and-drop columns for application status pipeline.
 */
import { useState } from 'react'
import { ExternalLink, GripVertical, RotateCw } from 'lucide-react'
import { timeAgo, capitalize } from '../utils/helpers'

const COLUMNS = [
  { id: 'pending', label: 'Pending', color: 'border-amber-400', bg: 'bg-amber-50 dark:bg-amber-950/20' },
  { id: 'submitted', label: 'Applied', color: 'border-blue-400', bg: 'bg-blue-50 dark:bg-blue-950/20' },
  { id: 'reviewing', label: 'Reviewing', color: 'border-indigo-400', bg: 'bg-indigo-50 dark:bg-indigo-950/20' },
  { id: 'interview', label: 'Interview', color: 'border-purple-400', bg: 'bg-purple-50 dark:bg-purple-950/20' },
  { id: 'offered', label: 'Offered', color: 'border-emerald-400', bg: 'bg-emerald-50 dark:bg-emerald-950/20' },
  { id: 'rejected', label: 'Rejected', color: 'border-red-400', bg: 'bg-red-50 dark:bg-red-950/20' },
]

function KanbanCard({ app, onDragStart }) {
  return (
    <div draggable onDragStart={e => { e.dataTransfer.setData('appId', app._id); onDragStart?.(app._id) }}
      className="bg-white dark:bg-surface-800 rounded-lg border border-gray-200 dark:border-surface-700 p-3 cursor-grab active:cursor-grabbing hover:shadow-md transition-shadow group">
      <div className="flex items-start gap-2">
        <GripVertical className="w-3.5 h-3.5 text-gray-300 dark:text-surface-600 mt-0.5 shrink-0 opacity-0 group-hover:opacity-100 transition-opacity" />
        <div className="flex-1 min-w-0">
          <p className="text-sm font-medium text-gray-900 dark:text-white truncate">{app.job_title || 'Unknown'}</p>
          <p className="text-xs text-gray-500 dark:text-surface-400 truncate">{app.company} · {capitalize(app.portal || '')}</p>
          <p className="text-xs text-gray-400 dark:text-surface-500 mt-1">{timeAgo(app.applied_at)}</p>
        </div>
        {app.job_url && (
          <a href={app.job_url} target="_blank" rel="noopener noreferrer" onClick={e => e.stopPropagation()}
            className="p-1 rounded hover:bg-gray-100 dark:hover:bg-surface-700 shrink-0">
            <ExternalLink className="w-3.5 h-3.5 text-gray-400" />
          </a>
        )}
      </div>
    </div>
  )
}

export default function KanbanBoard({ applications, onStatusChange }) {
  const [dragOver, setDragOver] = useState(null)

  const handleDrop = (e, newStatus) => {
    e.preventDefault()
    setDragOver(null)
    const appId = e.dataTransfer.getData('appId')
    if (appId) onStatusChange?.(appId, newStatus)
  }

  return (
    <div className="flex gap-3 overflow-x-auto pb-4 -mx-4 px-4 sm:mx-0 sm:px-0 scrollbar-none">
      {COLUMNS.map(col => {
        const items = (applications || []).filter(a => a.status === col.id)
        const isOver = dragOver === col.id
        return (
          <div key={col.id}
            className={`flex-shrink-0 w-[260px] sm:w-[280px] flex flex-col rounded-xl border-t-2 ${col.color} ${col.bg} transition-colors ${isOver ? 'ring-2 ring-brand-400' : ''}`}
            onDragOver={e => { e.preventDefault(); setDragOver(col.id) }}
            onDragLeave={() => setDragOver(null)}
            onDrop={e => handleDrop(e, col.id)}>
            <div className="flex items-center justify-between px-3 py-2.5">
              <span className="text-xs font-semibold text-gray-700 dark:text-surface-200 uppercase tracking-wide">{col.label}</span>
              <span className="text-xs font-bold text-gray-400 dark:text-surface-500 bg-white dark:bg-surface-800 px-1.5 py-0.5 rounded-md">{items.length}</span>
            </div>
            <div className="flex-1 px-2 pb-2 space-y-2 min-h-[100px]">
              {items.map(app => <KanbanCard key={app._id} app={app} />)}
              {items.length === 0 && (
                <div className="flex items-center justify-center h-20 text-xs text-gray-400 dark:text-surface-500 border border-dashed border-gray-200 dark:border-surface-700 rounded-lg">
                  Drop here
                </div>
              )}
            </div>
          </div>
        )
      })}
    </div>
  )
}
