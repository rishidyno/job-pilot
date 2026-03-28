/**
 * JOBPILOT — Job Comparison Modal
 * Side-by-side comparison of 2-3 jobs.
 */
import { useEffect } from 'react'
import { X } from 'lucide-react'
import MatchScore from './MatchScore'
import { capitalize } from '../utils/helpers'

const FIELDS = [
  { key: 'company', label: 'Company' },
  { key: 'location', label: 'Location' },
  { key: 'portal', label: 'Portal', format: capitalize },
  { key: 'match_score', label: 'Match Score', format: v => v != null ? `${v}/100` : '—' },
  { key: 'salary', label: 'Salary', format: v => v || '—' },
  { key: 'experience_required', label: 'Experience', format: v => v || '—' },
  { key: 'job_type', label: 'Type', format: v => v || '—' },
  { key: 'status', label: 'Status', format: capitalize },
  { key: 'skills', label: 'Skills', format: v => (v || []).join(', ') || '—' },
]

export default function JobComparison({ jobs, onClose }) {
  useEffect(() => {
    const h = (e) => { if (e.key === 'Escape') onClose() }
    document.addEventListener('keydown', h)
    return () => document.removeEventListener('keydown', h)
  }, [onClose])

  if (!jobs || jobs.length < 2) return null

  return (
    <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4" onClick={onClose}>
      <div className="bg-white dark:bg-surface-800 rounded-xl w-full max-w-4xl max-h-[85vh] flex flex-col shadow-2xl" onClick={e => e.stopPropagation()}>
        <div className="flex items-center justify-between px-5 py-4 border-b border-gray-200 dark:border-surface-700 shrink-0">
          <h2 className="text-lg font-bold text-gray-900 dark:text-white">Compare Jobs</h2>
          <button onClick={onClose} className="p-1.5 rounded-lg hover:bg-gray-100 dark:hover:bg-surface-700"><X className="w-5 h-5 text-gray-400" /></button>
        </div>

        <div className="flex-1 overflow-auto p-5">
          <table className="w-full text-sm">
            {/* Job titles header */}
            <thead>
              <tr>
                <th className="text-left text-xs text-gray-400 dark:text-surface-500 font-medium pb-3 w-28"></th>
                {jobs.map(j => (
                  <th key={j._id} className="text-left pb-3 px-2">
                    <div className="flex items-center gap-2">
                      <MatchScore score={j.match_score} size={36} />
                      <div className="min-w-0">
                        <p className="text-sm font-semibold text-gray-900 dark:text-white truncate">{j.title}</p>
                        <a href={j.url} target="_blank" rel="noopener noreferrer" className="text-xs text-brand-600 dark:text-brand-400 hover:underline">View posting →</a>
                      </div>
                    </div>
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {FIELDS.map(({ key, label, format }) => (
                <tr key={key} className="border-t border-gray-100 dark:border-surface-700">
                  <td className="py-2.5 text-xs font-medium text-gray-500 dark:text-surface-400 align-top">{label}</td>
                  {jobs.map(j => {
                    const val = format ? format(j[key]) : (j[key] || '—')
                    return (
                      <td key={j._id} className="py-2.5 px-2 text-xs text-gray-700 dark:text-surface-300 align-top">{val}</td>
                    )
                  })}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
