/**
 * JOBPILOT — Job Detail Modal
 * Full job description view with all details, actions, and AI insights.
 */
import { useState, useEffect } from 'react'
import { X, MapPin, Clock, ExternalLink, Star, FileText, Send, Briefcase } from 'lucide-react'
import StatusBadge from './StatusBadge'
import MatchScore from './MatchScore'
import { capitalize, timeAgo } from '../utils/helpers'

export default function JobDetailModal({ job, onClose, onApply, onScore, onTailor }) {
  const [scoring, setScoring] = useState(false)
  const [tailoring, setTailoring] = useState(false)

  useEffect(() => {
    const h = (e) => { if (e.key === 'Escape') onClose() }
    document.addEventListener('keydown', h)
    return () => document.removeEventListener('keydown', h)
  }, [onClose])

  const handleScore = async () => {
    setScoring(true)
    try { await onScore?.(job._id) } finally { setScoring(false) }
  }
  const handleTailor = async () => {
    setTailoring(true)
    try { await onTailor?.(job._id) } finally { setTailoring(false) }
  }

  return (
    <div className="fixed inset-0 glass-overlay z-50 flex items-end sm:items-center justify-center p-0 sm:p-4"
      onClick={onClose} role="dialog" aria-modal="true" aria-label={`Job details: ${job.title}`}>
      <div className="bg-white dark:bg-surface-800 rounded-t-2xl sm:rounded-xl w-full sm:max-w-2xl max-h-[90vh] flex flex-col"
        onClick={e => e.stopPropagation()}>
        {/* Header */}
        <div className="flex items-start gap-4 p-5 border-b border-gray-200 dark:border-surface-700 shrink-0">
          <MatchScore score={job.match_score} size={56} />
          <div className="flex-1 min-w-0">
            <h2 className="text-lg font-bold text-gray-900 dark:text-white">{job.title}</h2>
            <p className="text-sm text-gray-600 dark:text-surface-300 font-medium">{job.company}</p>
            <div className="flex items-center gap-3 mt-1.5 text-xs text-gray-400 dark:text-surface-400 flex-wrap">
              {job.location && <span className="flex items-center gap-1"><MapPin className="w-3 h-3" />{job.location}</span>}
              {job.experience_required && <span className="flex items-center gap-1"><Clock className="w-3 h-3" />{job.experience_required}</span>}
              {job.portal && <span className="flex items-center gap-1"><Briefcase className="w-3 h-3" />{capitalize(job.portal)}</span>}
            </div>
          </div>
          <div className="flex items-center gap-2 shrink-0">
            <StatusBadge status={job.status} />
            <button onClick={onClose} className="p-1.5 rounded-lg hover:bg-gray-100 dark:hover:bg-surface-700" aria-label="Close">
              <X className="w-5 h-5 text-gray-400" />
            </button>
          </div>
        </div>

        {/* Body — scrollable */}
        <div className="flex-1 overflow-y-auto p-5 space-y-5">
          {/* AI Insight */}
          {job.match_reasoning && (
            <div className="p-3 bg-brand-50 dark:bg-brand-950/30 border border-brand-200 dark:border-brand-800 rounded-lg">
              <p className="text-xs font-semibold text-brand-700 dark:text-brand-300 mb-1">AI Match Insight</p>
              <p className="text-sm text-brand-600 dark:text-brand-400">{job.match_reasoning}</p>
            </div>
          )}

          {/* Skills */}
          {job.skills?.length > 0 && (
            <div>
              <h3 className="text-xs font-semibold text-gray-500 dark:text-surface-400 uppercase tracking-wide mb-2">Required Skills</h3>
              <div className="flex flex-wrap gap-1.5">
                {job.skills.map((skill, i) => (
                  <span key={i} className="px-2.5 py-1 bg-gray-100 dark:bg-surface-700 text-gray-700 dark:text-surface-300 text-xs rounded-lg font-medium">{skill}</span>
                ))}
              </div>
            </div>
          )}

          {/* Description */}
          {job.description && (
            <div>
              <h3 className="text-xs font-semibold text-gray-500 dark:text-surface-400 uppercase tracking-wide mb-2">Job Description</h3>
              <div className="text-sm text-gray-700 dark:text-surface-300 leading-relaxed whitespace-pre-wrap max-h-80 overflow-y-auto pr-2">
                {job.description}
              </div>
            </div>
          )}

          {/* Meta */}
          <div className="flex items-center gap-4 text-xs text-gray-400 dark:text-surface-500 pt-2 border-t border-gray-100 dark:border-surface-700">
            <span>Added {timeAgo(job.created_at)}</span>
            {job.posted_date && <span>Posted: {job.posted_date}</span>}
            {job.job_type && <span>{job.job_type}</span>}
          </div>
        </div>

        {/* Footer actions */}
        <div className="flex items-center justify-between gap-2 p-4 border-t border-gray-200 dark:border-surface-700 shrink-0">
          <a href={job.url} target="_blank" rel="noopener noreferrer"
            className="flex items-center gap-1.5 px-3 py-2 text-sm border border-gray-200 dark:border-surface-600 rounded-lg hover:bg-gray-50 dark:hover:bg-surface-700 text-gray-700 dark:text-surface-300"
            aria-label="View original job posting">
            <ExternalLink className="w-4 h-4" /> View Original
          </a>
          <div className="flex items-center gap-2">
            <button onClick={handleScore} disabled={scoring}
              className="flex items-center gap-1.5 px-3 py-2 text-sm bg-gray-100 dark:bg-surface-700 text-gray-700 dark:text-surface-300 rounded-lg hover:bg-gray-200 dark:hover:bg-surface-600 disabled:opacity-50"
              aria-label="Score this job with AI">
              <Star className="w-4 h-4" /> {scoring ? 'Scoring...' : 'AI Score'}
            </button>
            <button onClick={handleTailor} disabled={tailoring}
              className="flex items-center gap-1.5 px-3 py-2 text-sm bg-purple-100 dark:bg-purple-900/30 text-purple-700 dark:text-purple-300 rounded-lg hover:bg-purple-200 dark:hover:bg-purple-900/50 disabled:opacity-50"
              aria-label="Tailor resume for this job">
              <FileText className="w-4 h-4" /> {tailoring ? 'Tailoring...' : 'Tailor'}
            </button>
            {['new', 'reviewed', 'shortlisted'].includes(job.status) && onApply && (
              <button onClick={() => { onApply(job._id); onClose() }}
                className="flex items-center gap-1.5 px-4 py-2 text-sm bg-brand-600 text-white rounded-lg hover:bg-brand-700 font-medium"
                aria-label="Apply to this job">
                <Send className="w-4 h-4" /> Apply
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
