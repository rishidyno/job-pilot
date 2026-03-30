/**
 * JOBPILOT — JobCard Component (redesigned)
 * Information-dense, scannable, with skill matching and freshness indicators.
 */

import { MapPin, ExternalLink, Star, Trash2, FileText, Eye, Bookmark, Wifi, Building2, ArrowRight, ChevronDown } from 'lucide-react'
import MatchScore from './MatchScore'
import PdfViewer from './PdfViewer'
import JobDetailModal from './JobDetailModal'
import ConfirmDialog from './ConfirmDialog'
import api from '../api/client'
import { portalLabel, portalColor, scoreLabel, scoreColor, freshness, truncate, statusColor, capitalize } from '../utils/helpers'
import { useState, useRef, useEffect } from 'react'

const APP_STATUSES = [
  { id: 'pending', label: 'Pending', icon: '⏳' },
  { id: 'submitted', label: 'Applied', icon: '📤' },
  { id: 'reviewing', label: 'Reviewing', icon: '👀' },
  { id: 'interview', label: 'Interview', icon: '🎤' },
  { id: 'offered', label: 'Offered', icon: '🎉' },
  { id: 'accepted', label: 'Accepted', icon: '✅' },
  { id: 'rejected', label: 'Rejected', icon: '❌' },
  { id: 'withdrawn', label: 'Withdrawn', icon: '↩️' },
]

function AppStatusSelector({ currentStatus, onChange }) {
  const [open, setOpen] = useState(false)
  const ref = useRef(null)

  useEffect(() => {
    if (!open) return
    const h = (e) => { if (ref.current && !ref.current.contains(e.target)) setOpen(false) }
    document.addEventListener('mousedown', h)
    return () => document.removeEventListener('mousedown', h)
  }, [open])

  const current = APP_STATUSES.find(s => s.id === currentStatus) || APP_STATUSES[0]

  return (
    <div className="relative" ref={ref}>
      <button onClick={() => setOpen(o => !o)}
        className={`flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg text-xs font-medium border transition-colors ${statusColor(currentStatus)}`}>
        <span>{current.icon}</span>
        <span>{current.label}</span>
        <ChevronDown className={`w-3 h-3 transition-transform ${open ? 'rotate-180' : ''}`} />
      </button>
      {open && (
        <div className="absolute right-0 top-full mt-1 w-44 bg-white dark:bg-surface-800 rounded-xl border border-gray-200 dark:border-surface-700 shadow-xl z-30 py-1 overflow-hidden">
          {APP_STATUSES.map(s => (
            <button key={s.id} onClick={() => { onChange(s.id); setOpen(false) }}
              className={`w-full flex items-center gap-2 px-3 py-2 text-xs text-left hover:bg-gray-50 dark:hover:bg-surface-700 transition-colors ${
                s.id === currentStatus ? 'bg-brand-50 dark:bg-brand-950/30 font-semibold' : ''
              }`}>
              <span>{s.icon}</span>
              <span className="text-gray-700 dark:text-surface-200">{s.label}</span>
              {s.id === currentStatus && <span className="ml-auto text-brand-600 dark:text-brand-400">✓</span>}
            </button>
          ))}
        </div>
      )}
    </div>
  )
}

function CompanyAvatar({ name }) {
  const colors = ['bg-brand-500', 'bg-emerald-500', 'bg-purple-500', 'bg-amber-500', 'bg-rose-500', 'bg-cyan-500', 'bg-indigo-500']
  const idx = (name || '').split('').reduce((a, c) => a + c.charCodeAt(0), 0) % colors.length
  return (
    <div className={`w-10 h-10 rounded-lg ${colors[idx]} flex items-center justify-center shrink-0`}>
      <span className="text-white text-sm font-bold">{(name || '?')[0].toUpperCase()}</span>
    </div>
  )
}

function SkillTag({ skill, matched }) {
  if (matched) return (
    <span className="px-1.5 py-0.5 bg-emerald-50 dark:bg-emerald-950/30 text-emerald-700 dark:text-emerald-300 text-xs rounded border border-emerald-200 dark:border-emerald-800">✓ {skill}</span>
  )
  return (
    <span className="px-1.5 py-0.5 bg-gray-50 dark:bg-surface-700 text-gray-500 dark:text-surface-400 text-xs rounded border border-gray-200 dark:border-surface-600">{skill}</span>
  )
}

export default function JobCard({ job, onApply, onScore, onDelete, onTailor, onBookmark, onNote, onCompare, isComparing, userSkills = [], onAppStatusChange }) {
  const [tailoring, setTailoring] = useState(false)
  const [scoring, setScoring] = useState(false)
  const [pdfUrl, setPdfUrl] = useState(null)
  const [showDetail, setShowDetail] = useState(false)
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false)

  const handleTailor = async (e) => { e?.stopPropagation(); setTailoring(true); try { await onTailor(job._id) } finally { setTailoring(false) } }
  const handleScore = async (e) => { e?.stopPropagation(); setScoring(true); try { await onScore(job._id) } finally { setScoring(false) } }

  const fresh = freshness(job.date_posted || job.created_at)
  const userSkillsLower = new Set((userSkills || []).map(s => s.toLowerCase()))
  const label = scoreLabel(job.match_score)
  const isApplied = ['applied', 'interviewing', 'offered', 'accepted'].includes(job.status)

  return (
    <>
      <div className={`card-hover bg-white dark:bg-surface-800 rounded-xl border p-4 sm:p-5 cursor-pointer ${
          isComparing ? 'border-indigo-400 dark:border-indigo-500 ring-1 ring-indigo-200 dark:ring-indigo-800' : 'border-gray-200 dark:border-surface-700'
        }`}
        onClick={() => setShowDetail(true)} role="button" tabIndex={0}
        onKeyDown={(e) => { if (e.key === 'Enter') setShowDetail(true) }}
        aria-label={`${job.title} at ${job.company}`}>

        {/* Row 1: Avatar + Title + Meta + Bookmark */}
        <div className="flex items-start gap-3">
          <CompanyAvatar name={job.company} />
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 mb-0.5">
              <h3 className="text-sm font-semibold text-gray-900 dark:text-white truncate">{job.title}</h3>
            </div>
            <div className="flex items-center gap-2 text-xs text-gray-500 dark:text-surface-400 flex-wrap">
              <span className="font-medium text-gray-700 dark:text-surface-300">{job.company}</span>
              <span>·</span>
              <span className={portalColor(job.portal)}>{portalLabel(job.portal)}</span>
              {(job.is_manual || job.portal === 'manual') && <span className="text-xs font-medium text-amber-600 dark:text-amber-400 bg-amber-50 dark:bg-amber-950/30 px-1.5 py-0.5 rounded">📌 Manual</span>}
              {job.location && <><span>·</span><span className="flex items-center gap-0.5"><MapPin className="w-3 h-3" />{job.location}</span></>}
              {job.is_remote && <span className="flex items-center gap-0.5 text-emerald-600 dark:text-emerald-400"><Wifi className="w-3 h-3" />Remote</span>}
            </div>
          </div>
          <div className="flex items-center gap-1.5 shrink-0" onClick={e => e.stopPropagation()}>
            {fresh.label && <span className={`text-xs px-1.5 py-0.5 rounded-md font-medium ${fresh.color}`}>{fresh.label}</span>}
            {onBookmark && (
              <button onClick={() => onBookmark(job._id, !job.bookmarked)}
                className="p-1 rounded-md hover:bg-amber-50 dark:hover:bg-amber-950/30"
                aria-label={job.bookmarked ? 'Remove bookmark' : 'Bookmark'}>
                <Bookmark className={`w-4 h-4 ${job.bookmarked ? 'fill-amber-400 text-amber-400' : 'text-gray-300 dark:text-surface-600 hover:text-amber-300'}`} />
              </button>
            )}
          </div>
        </div>

        {/* Row 2: Salary + Score + Status badges */}
        <div className="flex items-center gap-2 mt-2.5 flex-wrap">
          {/* Score badge */}
          {job.match_score != null && (
            <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-semibold ${scoreColor(job.match_score)}`}>
              {job.match_score} · {label}
            </span>
          )}
          {/* Salary */}
          {job.salary && <span className="text-xs font-medium text-emerald-700 dark:text-emerald-400 bg-emerald-50 dark:bg-emerald-950/30 px-2 py-0.5 rounded-full">💰 {job.salary}</span>}
          {/* Experience */}
          {job.experience_required && <span className="text-xs text-gray-500 dark:text-surface-400 bg-gray-100 dark:bg-surface-700 px-2 py-0.5 rounded-full">{job.experience_required}</span>}
          {/* Applied indicator — only show if no status selector */}
          {isApplied && !job.application_id && <span className="text-xs font-medium text-brand-700 dark:text-brand-300 bg-brand-50 dark:bg-brand-950/30 px-2 py-0.5 rounded-full">✓ Applied</span>}
          {/* Tailored indicator */}
          {job.tailored_resume_id && !isApplied && <span className="text-xs font-medium text-purple-700 dark:text-purple-300 bg-purple-50 dark:bg-purple-950/30 px-2 py-0.5 rounded-full">📄 Tailored</span>}
        </div>

        {/* Row 3: Skills with match highlighting */}
        {job.skills?.length > 0 && (
          <div className="flex flex-wrap gap-1 mt-2.5">
            {job.skills.slice(0, 8).map((skill, i) => (
              <SkillTag key={i} skill={skill} matched={userSkillsLower.has(skill.toLowerCase())} />
            ))}
            {job.skills.length > 8 && <span className="text-xs text-gray-400 dark:text-surface-500 self-center">+{job.skills.length - 8}</span>}
          </div>
        )}

        {/* Row 4: Tailored resume banner */}
        {job.tailored_resume_id && (
          <div className="mt-2.5 flex items-center gap-2 px-3 py-2 bg-purple-50 dark:bg-purple-950/20 border border-purple-100 dark:border-purple-900 rounded-lg"
            onClick={e => e.stopPropagation()}>
            <FileText className="w-3.5 h-3.5 text-purple-600 dark:text-purple-400 shrink-0" />
            <span className="text-xs text-purple-700 dark:text-purple-300 font-medium flex-1">Tailored resume ready</span>
            <button onClick={() => setPdfUrl(api.resumes.compileUrl(job.tailored_resume_id))}
              className="flex items-center gap-1 text-xs font-medium text-purple-600 dark:text-purple-400 hover:text-purple-800 dark:hover:text-purple-200 bg-white dark:bg-surface-800 px-2 py-1 rounded-md border border-purple-200 dark:border-purple-800"
              aria-label="View tailored resume PDF">
              <Eye className="w-3 h-3" /> View PDF
            </button>
          </div>
        )}

        {/* Row 5: Notes */}
        {job.notes && (
          <div className="mt-2 px-2.5 py-1.5 bg-amber-50 dark:bg-amber-950/20 rounded-md" onClick={e => e.stopPropagation()}>
            <p className="text-xs text-amber-700 dark:text-amber-300 line-clamp-1">📝 {job.notes}</p>
          </div>
        )}

        {/* Row 6: Actions — clean, minimal */}
        <div className="flex items-center justify-between mt-3 pt-3 border-t border-gray-100 dark:border-surface-700"
          onClick={e => e.stopPropagation()}>
          {/* Left: secondary actions */}
          <div className="flex items-center gap-1">
            {onScore && (
              <button onClick={handleScore} disabled={scoring}
                className="text-xs px-2 py-1 rounded-md text-gray-500 dark:text-surface-400 hover:bg-gray-100 dark:hover:bg-surface-700 disabled:opacity-50">
                {scoring ? '...' : '⟳ Score'}
              </button>
            )}
            {onTailor && (
              <button onClick={handleTailor} disabled={tailoring}
                className="text-xs px-2 py-1 rounded-md text-purple-600 dark:text-purple-400 hover:bg-purple-50 dark:hover:bg-purple-950/30 disabled:opacity-50">
                {tailoring ? '...' : job.tailored_resume_id ? '✎ Re-tailor' : '✎ Tailor'}
              </button>
            )}
            {onCompare && (
              <button onClick={() => onCompare(job._id)}
                className={`text-xs px-2 py-1 rounded-md ${isComparing ? 'text-indigo-700 dark:text-indigo-300 bg-indigo-100 dark:bg-indigo-900/40' : 'text-gray-500 dark:text-surface-400 hover:bg-gray-100 dark:hover:bg-surface-700'}`}>
                {isComparing ? '✓ Comparing' : '⇔ Compare'}
              </button>
            )}
            {onDelete && (
              <button onClick={() => setShowDeleteConfirm(true)}
                className="text-xs p-1 rounded-md text-gray-400 dark:text-surface-500 hover:text-red-500 hover:bg-red-50 dark:hover:bg-red-950/30">
                <Trash2 className="w-3.5 h-3.5" />
              </button>
            )}
          </div>
          {/* Right: primary actions */}
          <div className="flex items-center gap-1.5">
            <a href={job.url} target="_blank" rel="noopener noreferrer"
              className="text-xs px-2.5 py-1.5 rounded-md border border-gray-200 dark:border-surface-600 text-gray-600 dark:text-surface-300 hover:bg-gray-50 dark:hover:bg-surface-700">
              View ↗
            </a>
            {/* Show status selector if application exists, Apply button if not */}
            {job.application_id && onAppStatusChange ? (
              <AppStatusSelector
                currentStatus={job.application_status || 'pending'}
                onChange={(newStatus) => onAppStatusChange(job.application_id, newStatus, job._id)}
              />
            ) : (
              !job.application_id && ['new', 'reviewed', 'shortlisted'].includes(job.status) && onApply && (
                <button onClick={() => onApply(job._id)}
                  className="text-xs px-3 py-1.5 rounded-md bg-brand-600 text-white hover:bg-brand-700 font-medium flex items-center gap-1">
                  Apply <ArrowRight className="w-3 h-3" />
                </button>
              )
            )}
          </div>
        </div>
      </div>

      {/* Modals */}
      {showDetail && <JobDetailModal job={job} onClose={() => setShowDetail(false)} onApply={onApply} onScore={onScore} onTailor={onTailor} />}
      {pdfUrl && <PdfViewer url={pdfUrl} title={`${job.title} — ${job.company}`} onClose={() => setPdfUrl(null)} />}
      {showDeleteConfirm && (
        <ConfirmDialog title="Delete Job" message={`Remove "${job.title}" at ${job.company}?`}
          confirmLabel="Delete" variant="danger"
          onConfirm={() => { setShowDeleteConfirm(false); onDelete(job._id) }}
          onCancel={() => setShowDeleteConfirm(false)} />
      )}
    </>
  )
}
