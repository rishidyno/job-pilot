/**
 * JOBPILOT — Resume Manager Page (LaTeX-based)
 * Responsive with skeletons and toasts.
 */

import { useState } from 'react'
import { FileText, Sparkles, Eye, Save, Check } from 'lucide-react'
import EmptyState from '../components/EmptyState'
import PdfViewer from '../components/PdfViewer'
import Skeleton from '../components/Skeleton'
import api from '../api/client'
import { useApi, useApiMutation } from '../hooks/useApi'
import { useToast } from '../hooks/useToast'
import { timeAgo } from '../utils/helpers'

export default function ResumeManager() {
  const toast = useToast()
  const { data: latexData, loading: latexLoading, refetch: refetchLatex } = useApi(() => api.resumes.getLatex())
  const { data: listData, loading: listLoading, refetch: refetchList } = useApi(() => api.resumes.list())
  const { execute, loading: saving } = useApiMutation()
  const [latex, setLatex] = useState(null)
  const [saved, setSaved] = useState(false)
  const [pdfUrl, setPdfUrl] = useState(null)
  const [pdfTitle, setPdfTitle] = useState('')

  const editorContent = latex !== null ? latex : (latexData?.content || '')

  const handleSave = async () => {
    try {
      await execute(() => api.resumes.updateLatex(editorContent))
      setSaved(true)
      setTimeout(() => setSaved(false), 2000)
      refetchLatex()
      toast.success('Resume saved')
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Save failed')
    }
  }

  const handlePreviewBase = () => {
    const base = (listData?.resumes || []).find(r => r.is_base)
    if (base) {
      setPdfTitle('Base Resume')
      setPdfUrl(api.resumes.compileUrl(base._id))
    } else {
      toast.warning('Save your LaTeX first, then preview.')
    }
  }

  const tailoredResumes = (listData?.resumes || []).filter(r => !r.is_base)

  return (
    <div>
      <div className="mb-4 sm:mb-6">
        <h1 className="text-xl sm:text-2xl font-bold text-gray-900 dark:text-white">Resume Manager</h1>
        <p className="text-sm text-gray-500 dark:text-surface-400 mt-1">Edit your LaTeX resume and view tailored versions</p>
      </div>

      {/* LaTeX Editor */}
      <div className="bg-white dark:bg-surface-800 rounded-xl border border-gray-200 dark:border-surface-700 p-4 sm:p-6 mb-6 sm:mb-8">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-4">
          <div>
            <h2 className="text-base sm:text-lg font-semibold text-gray-900 dark:text-white">Base Resume (LaTeX)</h2>
            <p className="text-xs text-gray-500 dark:text-surface-400 mt-1">
              Source-of-truth resume. AI tailors copies for each job.
            </p>
          </div>
          <div className="flex items-center gap-2">
            <button onClick={handlePreviewBase}
              className="flex items-center gap-1.5 px-3 sm:px-4 py-2 text-sm border border-gray-200 dark:border-surface-700 rounded-lg hover:bg-gray-50 dark:hover:bg-surface-700"
              aria-label="Preview resume as PDF">
              <Eye className="w-4 h-4" /> <span className="hidden sm:inline">Preview</span> PDF
            </button>
            <button onClick={handleSave} disabled={saving}
              className="flex items-center gap-1.5 px-3 sm:px-4 py-2 bg-brand-600 text-white text-sm font-medium rounded-lg hover:bg-brand-700 disabled:opacity-50"
              aria-label="Save resume">
              {saved ? <Check className="w-4 h-4" /> : <Save className="w-4 h-4" />}
              {saved ? 'Saved!' : saving ? 'Saving...' : 'Save'}
            </button>
          </div>
        </div>

        {latexLoading ? (
          <Skeleton className="h-[400px] sm:h-[500px] w-full rounded-lg" />
        ) : (
          <textarea
            value={editorContent}
            onChange={(e) => setLatex(e.target.value)}
            className="w-full h-[400px] sm:h-[500px] font-mono text-xs bg-gray-900 dark:bg-surface-950 text-green-400 p-3 sm:p-4 rounded-lg border-0 focus:outline-none focus:ring-2 focus:ring-brand-500 resize-y"
            spellCheck={false}
            placeholder="Paste your LaTeX resume here..."
            aria-label="LaTeX resume editor"
          />
        )}
      </div>

      {/* Tailored Versions */}
      <div>
        <div className="flex items-center gap-2 mb-4">
          <Sparkles className="w-5 h-5 text-brand-500" />
          <h2 className="text-base sm:text-lg font-semibold text-gray-900 dark:text-white">Tailored Versions</h2>
          <span className="text-sm text-gray-400 dark:text-surface-500">({tailoredResumes.length})</span>
        </div>

        {listLoading ? (
          <div className="space-y-3">
            {Array.from({ length: 3 }).map((_, i) => (
              <div key={i} className="bg-white dark:bg-surface-800 rounded-xl border border-gray-200 dark:border-surface-700 p-4">
                <div className="flex items-center gap-3">
                  <Skeleton className="w-8 h-8 rounded" />
                  <div className="flex-1 space-y-1.5">
                    <Skeleton className="h-4 w-48" />
                    <Skeleton className="h-3 w-24" />
                  </div>
                  <Skeleton className="h-8 w-20 rounded-lg" />
                </div>
              </div>
            ))}
          </div>
        ) : tailoredResumes.length === 0 ? (
          <EmptyState
            title="No tailored resumes yet"
            message="Click 'Tailor Resume' on any job to generate a tailored version."
            preset="resumes"
          />
        ) : (
          <div className="space-y-3">
            {tailoredResumes.map(resume => (
              <div key={resume._id} className="bg-white dark:bg-surface-800 rounded-xl border border-gray-200 dark:border-surface-700 p-4">
                <div className="flex items-center justify-between gap-3">
                  <div className="flex items-center gap-3 min-w-0">
                    {/* Match score circle or fallback icon */}
                    {resume.job_match_score != null ? (
                      <div className="w-10 h-10 rounded-full bg-brand-50 dark:bg-brand-950/30 flex items-center justify-center shrink-0">
                        <span className="text-xs font-bold text-brand-600 dark:text-brand-400">{resume.job_match_score}</span>
                      </div>
                    ) : (
                      <FileText className="w-8 h-8 text-indigo-400 shrink-0" />
                    )}
                    <div className="min-w-0">
                      <p className="text-sm font-semibold text-gray-900 dark:text-white truncate">
                        {resume.job_title || `Job #${resume.job_id?.slice(-6)}`}
                      </p>
                      <div className="flex items-center gap-2 mt-0.5 flex-wrap">
                        <span className="text-xs text-gray-500 dark:text-surface-400">{resume.job_company || 'Unknown'}</span>
                        {resume.job_portal && (
                          <span className="text-xs text-gray-400 dark:text-surface-500">· {resume.job_portal}</span>
                        )}
                        <span className="text-xs text-gray-400 dark:text-surface-500">· {timeAgo(resume.created_at)}</span>
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center gap-1.5 shrink-0">
                    {resume.job_url && (
                      <a href={resume.job_url} target="_blank" rel="noopener noreferrer"
                        className="flex items-center gap-1 px-2.5 py-1.5 text-xs border border-gray-200 dark:border-surface-700 rounded-lg hover:bg-gray-50 dark:hover:bg-surface-700 text-gray-500 dark:text-surface-400"
                        aria-label="View original job posting">
                        Job ↗
                      </a>
                    )}
                    <button onClick={() => {
                      setPdfTitle(`${resume.job_title || 'Resume'} — ${resume.job_company || ''}`)
                      setPdfUrl(api.resumes.compileUrl(resume._id))
                    }}
                      className="flex items-center gap-1 px-3 py-1.5 text-xs bg-brand-50 dark:bg-brand-950/40 border border-brand-200 dark:border-brand-800 text-brand-700 dark:text-brand-300 rounded-lg hover:bg-brand-100 dark:hover:bg-brand-900/40"
                      aria-label="View tailored resume PDF">
                      <Eye className="w-3 h-3" /> View PDF
                    </button>
                  </div>
                </div>

                {resume.changes_made?.length > 0 && (
                  <div className="mt-3 pl-12">
                    <p className="text-xs text-gray-500 dark:text-surface-400 font-medium mb-1">Changes made:</p>
                    <ul className="space-y-0.5">
                      {resume.changes_made.map((change, i) => (
                        <li key={i} className="text-xs text-gray-400 dark:text-surface-500 flex items-start gap-1.5">
                          <span className="text-brand-400 mt-0.5">•</span> {change}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      {pdfUrl && (
        <PdfViewer url={pdfUrl} title={pdfTitle} onClose={() => setPdfUrl(null)} />
      )}
    </div>
  )
}
