/**
 * JOBPILOT — JobCard Component
 * Displays a job listing with title, company, score, status, and actions.
 */

import { MapPin, ExternalLink, Star, Clock, Trash2, FileText, Download, Eye } from 'lucide-react'
import StatusBadge from './StatusBadge'
import MatchScore from './MatchScore'
import { portalIcon, truncate, timeAgo } from '../utils/helpers'
import { useState } from 'react'

const API_BASE = import.meta.env.VITE_API_URL || ''

export default function JobCard({ job, onStatusChange, onApply, onScore, onDelete, onTailor }) {
  const [tailoring, setTailoring] = useState(false)
  const [scoring, setScoring] = useState(false)

  const handleTailor = async () => {
    setTailoring(true)
    try { await onTailor(job._id) } finally { setTailoring(false) }
  }
  const handleScore = async () => {
    setScoring(true)
    try { await onScore(job._id) } finally { setScoring(false) }
  }
  return (
    <div className="bg-white rounded-xl border border-gray-200 p-5 hover:shadow-md transition-shadow">
      {/* Header row: score + title + portal */}
      <div className="flex items-start gap-4">
        <MatchScore score={job.match_score} />
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <h3 className="text-sm font-semibold text-gray-900 truncate">{job.title}</h3>
            <span title={job.portal}>{portalIcon(job.portal)}</span>
          </div>
          <p className="text-sm text-gray-600 font-medium">{job.company}</p>
          <div className="flex items-center gap-3 mt-1.5 text-xs text-gray-400">
            {job.location && (
              <span className="flex items-center gap-1"><MapPin className="w-3 h-3" />{job.location}</span>
            )}
            {job.experience_required && (
              <span className="flex items-center gap-1"><Clock className="w-3 h-3" />{job.experience_required}</span>
            )}
          </div>
        </div>
        <StatusBadge status={job.status} />
      </div>

      {/* Skills */}
      {job.skills?.length > 0 && (
        <div className="flex flex-wrap gap-1.5 mt-3">
          {job.skills.slice(0, 6).map((skill, i) => (
            <span key={i} className="px-2 py-0.5 bg-gray-100 text-gray-600 text-xs rounded-md">{skill}</span>
          ))}
          {job.skills.length > 6 && (
            <span className="text-xs text-gray-400">+{job.skills.length - 6} more</span>
          )}
        </div>
      )}

      {/* Description preview */}
      {job.description && (
        <p className="text-xs text-gray-400 mt-2 line-clamp-2">{truncate(job.description, 200)}</p>
      )}

      {/* Tailored resume link */}
      {job.tailored_resume_id && (
        <div className="mt-3 flex items-center gap-2 px-3 py-2 bg-green-50 rounded-lg">
          <FileText className="w-3.5 h-3.5 text-green-600" />
          <span className="text-xs text-green-700 font-medium">Tailored resume ready</span>
          <button onClick={() => {
            const token = localStorage.getItem('token')
            window.open(`${API_BASE}/api/resumes/download/${job.tailored_resume_id}?style=original&preview=true&token=${token}`, '_blank')
          }} className="flex items-center gap-1 text-xs text-green-600 hover:underline ml-auto">
            <Eye className="w-3 h-3" /> Preview
          </button>
          <button onClick={() => {
            const token = localStorage.getItem('token')
            window.open(`${API_BASE}/api/resumes/download/${job.tailored_resume_id}?style=original&token=${token}`)
          }} className="flex items-center gap-1 text-xs text-green-600 hover:underline">
            <Download className="w-3 h-3" /> Download
          </button>
        </div>
      )}

      {/* Action row */}
      <div className="flex items-center justify-between mt-4 pt-3 border-t border-gray-100">
        <span className="text-xs text-gray-400">{timeAgo(job.created_at)}</span>
        <div className="flex items-center gap-2">
          {job.match_reasoning && (
            <span title={job.match_reasoning} className="text-xs text-brand-600 cursor-help">
              AI Insight ✨
            </span>
          )}
          {onScore && (
            <button onClick={handleScore} disabled={scoring}
              className="text-xs px-2.5 py-1 rounded-md bg-gray-50 text-gray-600 hover:bg-gray-100 disabled:opacity-50">
              <Star className="w-3 h-3 inline mr-1" />{scoring ? 'Scoring…' : 'Re-score'}
            </button>
          )}
          {onTailor && (
            <button onClick={handleTailor} disabled={tailoring}
              className="text-xs px-2.5 py-1 rounded-md bg-purple-50 text-purple-600 hover:bg-purple-100 disabled:opacity-50">
              <FileText className="w-3 h-3 inline mr-1" />{tailoring ? 'Tailoring…' : 'Tailor Resume'}
            </button>
          )}
          <a href={job.url} target="_blank" rel="noopener noreferrer"
            className="text-xs px-2.5 py-1 rounded-md bg-gray-50 text-gray-600 hover:bg-gray-100">
            <ExternalLink className="w-3 h-3 inline mr-1" />View
          </a>
          {['new', 'reviewed', 'shortlisted'].includes(job.status) && onApply && (
            <button onClick={() => onApply(job._id)}
              className="text-xs px-3 py-1 rounded-md bg-brand-600 text-white hover:bg-brand-700 font-medium">
              Apply
            </button>
          )}
          {onDelete && (
            <button onClick={() => { if (confirm('Delete this job?')) onDelete(job._id) }}
              className="text-xs px-2.5 py-1 rounded-md bg-red-50 text-red-600 hover:bg-red-100">
              <Trash2 className="w-3 h-3 inline mr-1" />Delete
            </button>
          )}
        </div>
      </div>
    </div>
  )
}
