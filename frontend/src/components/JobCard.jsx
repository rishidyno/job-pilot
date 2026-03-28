/**
 * JOBPILOT — JobCard Component
 * Dark mode, job detail modal on click, confirm dialog for delete.
 */

import { MapPin, ExternalLink, Star, Clock, Trash2, FileText, Eye, Bookmark } from 'lucide-react'
import StatusBadge from './StatusBadge'
import MatchScore from './MatchScore'
import PdfViewer from './PdfViewer'
import JobDetailModal from './JobDetailModal'
import ConfirmDialog from './ConfirmDialog'
import api from '../api/client'
import { portalLabel, portalColor, truncate, timeAgo } from '../utils/helpers'
import { useState } from 'react'

export default function JobCard({ job, onApply, onScore, onDelete, onTailor, onBookmark, onNote, onCompare, isComparing }) {
  const [tailoring, setTailoring] = useState(false)
  const [scoring, setScoring] = useState(false)
  const [pdfUrl, setPdfUrl] = useState(null)
  const [showDetail, setShowDetail] = useState(false)
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false)

  const handleTailor = async (e) => {
    e?.stopPropagation()
    setTailoring(true)
    try { await onTailor(job._id) } finally { setTailoring(false) }
  }
  const handleScore = async (e) => {
    e?.stopPropagation()
    setScoring(true)
    try { await onScore(job._id) } finally { setScoring(false) }
  }

  return (
    <>
      <div className={`bg-white dark:bg-surface-800 rounded-xl border p-4 sm:p-5 hover:shadow-md dark:hover:shadow-surface-900/50 transition-all cursor-pointer ${
          isComparing ? 'border-indigo-400 dark:border-indigo-500 ring-1 ring-indigo-200 dark:ring-indigo-800' : 'border-gray-200 dark:border-surface-700'
        }`}
        onClick={() => setShowDetail(true)} role="button" tabIndex={0}
        onKeyDown={(e) => { if (e.key === 'Enter') setShowDetail(true) }}
        aria-label={`${job.title} at ${job.company}, score ${job.match_score ?? 'unscored'}`}>
        {/* Header */}
        <div className="flex items-start gap-3 sm:gap-4">
          <div className="hidden sm:block"><MatchScore score={job.match_score} /></div>
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 mb-1">
              <span className="sm:hidden text-xs font-bold text-brand-600 dark:text-brand-400">{job.match_score ?? '?'}</span>
              <h3 className="text-sm font-semibold text-gray-900 dark:text-white truncate">{job.title}</h3>
              <span className={`text-xs font-semibold ${portalColor(job.portal)}`} title={portalLabel(job.portal)}>
                {portalLabel(job.portal)}
              </span>
            </div>
            <p className="text-sm text-gray-600 dark:text-surface-300 font-medium">{job.company}</p>
            <div className="flex items-center gap-3 mt-1.5 text-xs text-gray-400 dark:text-surface-500 flex-wrap">
              {job.location && <span className="flex items-center gap-1"><MapPin className="w-3 h-3" />{job.location}</span>}
              {job.experience_required && <span className="flex items-center gap-1"><Clock className="w-3 h-3" />{job.experience_required}</span>}
            </div>
          </div>
          <StatusBadge status={job.status} />
          {onBookmark && (
            <button onClick={e => { e.stopPropagation(); onBookmark(job._id, !job.bookmarked) }}
              className="p-1 rounded-md hover:bg-amber-50 dark:hover:bg-amber-950/30"
              aria-label={job.bookmarked ? 'Remove bookmark' : 'Bookmark this job'}>
              <Bookmark className={`w-4 h-4 ${job.bookmarked ? 'fill-amber-400 text-amber-400' : 'text-gray-300 dark:text-surface-600'}`} />
            </button>
          )}
        </div>

        {/* Skills */}
        {job.skills?.length > 0 && (
          <div className="flex flex-wrap gap-1.5 mt-3">
            {job.skills.slice(0, 6).map((skill, i) => (
              <span key={i} className="px-2 py-0.5 bg-gray-100 dark:bg-surface-700 text-gray-600 dark:text-surface-300 text-xs rounded-md">{skill}</span>
            ))}
            {job.skills.length > 6 && <span className="text-xs text-gray-400 dark:text-surface-500">+{job.skills.length - 6}</span>}
          </div>
        )}

        {job.description && (
          <p className="text-xs text-gray-400 dark:text-surface-500 mt-2 line-clamp-2">{truncate(job.description, 200)}</p>
        )}

        {job.tailored_resume_id && (
          <div className="mt-3 flex items-center gap-2 px-3 py-2 bg-green-50 dark:bg-green-950/30 rounded-lg"
            onClick={e => e.stopPropagation()}>
            <FileText className="w-3.5 h-3.5 text-green-600 dark:text-green-400" />
            <span className="text-xs text-green-700 dark:text-green-300 font-medium">Tailored resume ready</span>
            <button onClick={() => setPdfUrl(api.resumes.compileUrl(job.tailored_resume_id))}
              className="flex items-center gap-1 text-xs text-green-600 dark:text-green-400 hover:underline ml-auto"
              aria-label="View tailored resume PDF">
              <Eye className="w-3 h-3" /> View
            </button>
          </div>
        )}

        {/* Notes preview */}
        {job.notes && (
          <div className="mt-2 px-3 py-2 bg-amber-50 dark:bg-amber-950/20 rounded-lg" onClick={e => e.stopPropagation()}>
            <p className="text-xs text-amber-700 dark:text-amber-300 line-clamp-1">📝 {job.notes}</p>
          </div>
        )}

        {/* Actions */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between mt-4 pt-3 border-t border-gray-100 dark:border-surface-700 gap-2 sm:gap-0"
          onClick={e => e.stopPropagation()}>
          <span className="text-xs text-gray-400 dark:text-surface-500">{timeAgo(job.created_at)}</span>
          <div className="flex items-center gap-1.5 sm:gap-2 flex-wrap">
            {job.match_reasoning && (
              <span title={job.match_reasoning} className="text-xs text-brand-600 dark:text-brand-400 cursor-help">AI ✨</span>
            )}
            {onScore && (
              <button onClick={handleScore} disabled={scoring}
                className="text-xs px-2 sm:px-2.5 py-1 rounded-md bg-gray-50 dark:bg-surface-700 text-gray-600 dark:text-surface-300 hover:bg-gray-100 dark:hover:bg-surface-600 disabled:opacity-50"
                aria-label="Re-score this job with AI">
                <Star className="w-3 h-3 inline mr-0.5" />{scoring ? '...' : 'Score'}
              </button>
            )}
            {onTailor && (
              <button onClick={handleTailor} disabled={tailoring}
                className="text-xs px-2 sm:px-2.5 py-1 rounded-md bg-purple-50 dark:bg-purple-950/30 text-purple-600 dark:text-purple-300 hover:bg-purple-100 dark:hover:bg-purple-900/40 disabled:opacity-50"
                aria-label="Tailor resume for this job">
                <FileText className="w-3 h-3 inline mr-0.5" />{tailoring ? '...' : 'Tailor'}
              </button>
            )}
            <a href={job.url} target="_blank" rel="noopener noreferrer"
              className="text-xs px-2 sm:px-2.5 py-1 rounded-md bg-gray-50 dark:bg-surface-700 text-gray-600 dark:text-surface-300 hover:bg-gray-100 dark:hover:bg-surface-600"
              aria-label="View original posting">
              <ExternalLink className="w-3 h-3 inline mr-0.5" />View
            </a>
            {['new', 'reviewed', 'shortlisted'].includes(job.status) && onApply && (
              <button onClick={() => onApply(job._id)}
                className="text-xs px-2.5 sm:px-3 py-1 rounded-md bg-brand-600 text-white hover:bg-brand-700 font-medium"
                aria-label="Apply to this job">
                Apply
              </button>
            )}
            {onDelete && (
              <button onClick={() => setShowDeleteConfirm(true)}
                className="text-xs px-2 sm:px-2.5 py-1 rounded-md bg-red-50 dark:bg-red-950/30 text-red-600 dark:text-red-400 hover:bg-red-100 dark:hover:bg-red-900/40"
                aria-label="Delete this job">
                <Trash2 className="w-3 h-3" />
              </button>
            )}
            {onCompare && (
              <button onClick={() => onCompare(job._id)}
                className={`text-xs px-2 sm:px-2.5 py-1 rounded-md ${
                  isComparing
                    ? 'bg-indigo-600 text-white'
                    : 'bg-indigo-50 dark:bg-indigo-950/30 text-indigo-600 dark:text-indigo-400 hover:bg-indigo-100 dark:hover:bg-indigo-900/40'
                }`}
                aria-label={isComparing ? 'Remove from comparison' : 'Add to comparison'}
                aria-pressed={isComparing}>
                {isComparing ? '✓ Compare' : '⇔ Compare'}
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Modals */}
      {showDetail && (
        <JobDetailModal job={job} onClose={() => setShowDetail(false)}
          onApply={onApply} onScore={onScore} onTailor={onTailor} />
      )}
      {pdfUrl && (
        <PdfViewer url={pdfUrl} title={`${job.title} — ${job.company}`} onClose={() => setPdfUrl(null)} />
      )}
      {showDeleteConfirm && (
        <ConfirmDialog
          title="Delete Job"
          message={`Remove "${job.title}" at ${job.company} from your list? This can't be undone.`}
          confirmLabel="Delete"
          variant="danger"
          onConfirm={() => { setShowDeleteConfirm(false); onDelete(job._id) }}
          onCancel={() => setShowDeleteConfirm(false)}
        />
      )}
    </>
  )
}
