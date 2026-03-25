/**
 * JOBPILOT — Resume Manager Page (LaTeX-based)
 *
 * Edit your base LaTeX resume, preview compiled PDF,
 * and view all tailored versions.
 */

import { useState, useRef } from 'react'
import { FileText, Sparkles, Eye, Save, Check } from 'lucide-react'
import EmptyState from '../components/EmptyState'
import api from '../api/client'
import { useApi, useApiMutation } from '../hooks/useApi'
import { timeAgo } from '../utils/helpers'

export default function ResumeManager() {
  const { data: latexData, loading: latexLoading, refetch: refetchLatex } = useApi(() => api.resumes.getLatex())
  const { data: listData, loading: listLoading, refetch: refetchList } = useApi(() => api.resumes.list())
  const { execute, loading: saving } = useApiMutation()
  const [latex, setLatex] = useState(null)
  const [saved, setSaved] = useState(false)

  // Initialize editor content from API
  const editorContent = latex !== null ? latex : (latexData?.content || '')

  const handleSave = async () => {
    try {
      await execute(() => api.resumes.updateLatex(editorContent))
      setSaved(true)
      setTimeout(() => setSaved(false), 2000)
      refetchLatex()
    } catch (err) {
      alert(`Save failed: ${err.response?.data?.detail || err.message}`)
    }
  }

  const handlePreviewBase = () => {
    // Find the base resume ID from the list
    const base = (listData?.resumes || []).find(r => r.is_base)
    if (base) {
      window.open(api.resumes.compileUrl(base._id), '_blank')
    } else {
      alert('Save your LaTeX first, then preview.')
    }
  }

  const tailoredResumes = (listData?.resumes || []).filter(r => !r.is_base)

  return (
    <div>
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Resume Manager</h1>
        <p className="text-sm text-gray-500 mt-1">Edit your LaTeX resume and view tailored versions</p>
      </div>

      {/* LaTeX Editor */}
      <div className="bg-white rounded-xl border border-gray-200 p-6 mb-8">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="text-lg font-semibold text-gray-900">Base Resume (LaTeX)</h2>
            <p className="text-xs text-gray-500 mt-1">
              This is your source-of-truth resume. AI tailors copies of this for each job.
            </p>
          </div>
          <div className="flex items-center gap-2">
            <button onClick={handlePreviewBase}
              className="flex items-center gap-2 px-4 py-2 text-sm border border-gray-200 rounded-lg hover:bg-gray-50">
              <Eye className="w-4 h-4" /> Preview PDF
            </button>
            <button onClick={handleSave} disabled={saving}
              className="flex items-center gap-2 px-4 py-2 bg-brand-600 text-white text-sm font-medium rounded-lg hover:bg-brand-700 disabled:opacity-50">
              {saved ? <Check className="w-4 h-4" /> : <Save className="w-4 h-4" />}
              {saved ? 'Saved!' : saving ? 'Saving...' : 'Save'}
            </button>
          </div>
        </div>

        {latexLoading ? (
          <div className="text-center py-12 text-gray-400">Loading...</div>
        ) : (
          <textarea
            value={editorContent}
            onChange={(e) => setLatex(e.target.value)}
            className="w-full h-[500px] font-mono text-xs bg-gray-900 text-green-400 p-4 rounded-lg border-0 focus:outline-none focus:ring-2 focus:ring-brand-500 resize-y"
            spellCheck={false}
            placeholder="Paste your LaTeX resume here..."
          />
        )}
      </div>

      {/* Tailored Versions */}
      <div>
        <div className="flex items-center gap-2 mb-4">
          <Sparkles className="w-5 h-5 text-brand-500" />
          <h2 className="text-lg font-semibold text-gray-900">Tailored Versions</h2>
          <span className="text-sm text-gray-400">({tailoredResumes.length})</span>
        </div>

        {tailoredResumes.length === 0 ? (
          <EmptyState
            title="No tailored resumes yet"
            message="Click 'Tailor Resume' on any job to generate a tailored version."
          />
        ) : (
          <div className="space-y-3">
            {tailoredResumes.map(resume => (
              <div key={resume._id} className="bg-white rounded-xl border border-gray-200 p-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <FileText className="w-8 h-8 text-indigo-400" />
                    <div>
                      <p className="text-sm font-medium text-gray-800">
                        Tailored for Job #{resume.job_id?.slice(-6)}
                      </p>
                      <p className="text-xs text-gray-500">{timeAgo(resume.created_at)}</p>
                    </div>
                  </div>
                  <button onClick={() => window.open(api.resumes.compileUrl(resume._id), '_blank')}
                    className="flex items-center gap-1 px-3 py-1.5 text-xs bg-brand-50 border border-brand-200 text-brand-700 rounded-lg hover:bg-brand-100">
                    <Eye className="w-3 h-3" /> View PDF
                  </button>
                </div>

                {resume.changes_made?.length > 0 && (
                  <div className="mt-3 pl-11">
                    <p className="text-xs text-gray-500 font-medium mb-1">Changes made:</p>
                    <ul className="space-y-0.5">
                      {resume.changes_made.map((change, i) => (
                        <li key={i} className="text-xs text-gray-400 flex items-start gap-1.5">
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
    </div>
  )
}
