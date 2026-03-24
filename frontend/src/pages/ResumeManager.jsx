/**
 * JOBPILOT — Resume Manager Page
 *
 * Manages your base resume and all AI-tailored versions.
 * Features: upload base resume, view tailored versions per job,
 * download PDFs, see what changes the AI made.
 */

import { useState, useRef } from 'react'
import { Upload, FileText, Download, Sparkles, Check, Eye, X } from 'lucide-react'
import EmptyState from '../components/EmptyState'
import api from '../api/client'
import { useApi, useApiMutation } from '../hooks/useApi'
import { timeAgo } from '../utils/helpers'

export default function ResumeManager() {
  const { data, loading, refetch } = useApi(() => api.resumes.list())
  const { execute, loading: mutating } = useApiMutation()
  const fileInputRef = useRef(null)
  const [uploadSuccess, setUploadSuccess] = useState(false)
  const [previewUrl, setPreviewUrl] = useState(null)

  const resumes = data?.resumes || []
  const baseResume = resumes.find(r => r.is_base)
  const tailoredResumes = resumes.filter(r => !r.is_base)

  const handleUpload = async (e) => {
    const file = e.target.files[0]
    if (!file) return
    try {
      await execute(() => api.resumes.uploadBase(file))
      setUploadSuccess(true)
      setTimeout(() => setUploadSuccess(false), 3000)
      refetch()
    } catch (err) {
      alert(`Upload failed: ${err.response?.data?.detail || err.message}`)
    }
  }

  return (
    <div>
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Resume Manager</h1>
        <p className="text-sm text-gray-500 mt-1">Your base resume and all AI-tailored versions</p>
      </div>

      {/* Base Resume Section */}
      <div className="bg-white rounded-xl border border-gray-200 p-6 mb-8">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="text-lg font-semibold text-gray-900">Base Resume</h2>
            <p className="text-xs text-gray-500 mt-1">
              This is your original resume — the source of truth. All tailored versions derive from this.
            </p>
          </div>
          <input type="file" accept=".pdf" ref={fileInputRef} onChange={handleUpload} className="hidden" />
          <button onClick={() => fileInputRef.current?.click()} disabled={mutating}
            className="flex items-center gap-2 px-4 py-2 bg-brand-600 text-white text-sm font-medium rounded-lg hover:bg-brand-700 disabled:opacity-50">
            {uploadSuccess ? <Check className="w-4 h-4" /> : <Upload className="w-4 h-4" />}
            {uploadSuccess ? 'Uploaded!' : mutating ? 'Uploading...' : baseResume ? 'Replace Resume' : 'Upload Resume'}
          </button>
        </div>

        {baseResume ? (
          <div className="flex items-center gap-4 p-4 bg-gray-50 rounded-lg">
            <FileText className="w-10 h-10 text-brand-500" />
            <div className="flex-1">
              <p className="text-sm font-medium text-gray-800">{baseResume.original_filename || 'base_resume.pdf'}</p>
              <p className="text-xs text-gray-500">
                Uploaded {timeAgo(baseResume.created_at)} •
                {baseResume.raw_text ? ` ${baseResume.raw_text.length.toLocaleString()} chars extracted` : ' text not extracted'}
              </p>
            </div>
            <a href={api.resumes.download(baseResume._id, 'original')} target="_blank"
              className="flex items-center gap-1 px-3 py-1.5 text-xs bg-white border border-gray-200 rounded-lg hover:bg-gray-100">
              <Download className="w-3 h-3" /> Download
            </a>
            <button onClick={() => setPreviewUrl(api.resumes.download(baseResume._id, 'original') + '&preview=true')}
              className="flex items-center gap-1 px-3 py-1.5 text-xs bg-brand-50 border border-brand-200 text-brand-700 rounded-lg hover:bg-brand-100">
              <Eye className="w-3 h-3" /> Preview
            </button>
          </div>
        ) : (
          <div className="p-8 border-2 border-dashed border-gray-200 rounded-lg text-center cursor-pointer hover:border-brand-300"
            onClick={() => fileInputRef.current?.click()}>
            <Upload className="w-8 h-8 text-gray-300 mx-auto mb-2" />
            <p className="text-sm text-gray-500">Click to upload your base resume (PDF)</p>
          </div>
        )}
      </div>

      {/* Tailored Resumes Section */}
      <div>
        <div className="flex items-center gap-2 mb-4">
          <Sparkles className="w-5 h-5 text-brand-500" />
          <h2 className="text-lg font-semibold text-gray-900">Tailored Versions</h2>
          <span className="text-sm text-gray-400">({tailoredResumes.length})</span>
        </div>

        {tailoredResumes.length === 0 ? (
          <EmptyState
            title="No tailored resumes yet"
            message="Tailored resumes are automatically generated when you apply to a job, or you can manually tailor from the Jobs page."
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
                      <p className="text-xs text-gray-500">
                        {resume.ai_model_used || 'Claude'} • {timeAgo(resume.created_at)}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    {resume.file_path_original_style && (
                      <a href={api.resumes.download(resume._id, 'original')}
                        className="flex items-center gap-1 px-3 py-1.5 text-xs bg-gray-50 border border-gray-200 rounded-lg hover:bg-gray-100">
                        <Download className="w-3 h-3" /> Original
                      </a>
                    )}
                    {resume.file_path_clean_style && (
                      <a href={api.resumes.download(resume._id, 'clean')}
                        className="flex items-center gap-1 px-3 py-1.5 text-xs bg-brand-50 border border-brand-200 text-brand-700 rounded-lg hover:bg-brand-100">
                        <Download className="w-3 h-3" /> Clean
                      </a>
                    )}
                  </div>
                </div>

                {/* Changes made */}
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

      {/* PDF Preview Modal */}
      {previewUrl && (
        <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4" onClick={() => setPreviewUrl(null)}>
          <div className="bg-white rounded-xl w-full max-w-4xl h-[85vh] flex flex-col" onClick={e => e.stopPropagation()}>
            <div className="flex items-center justify-between p-4 border-b">
              <h3 className="text-sm font-semibold text-gray-700">Resume Preview</h3>
              <button onClick={() => setPreviewUrl(null)} className="p-1 hover:bg-gray-100 rounded">
                <X className="w-4 h-4" />
              </button>
            </div>
            <iframe src={previewUrl} className="flex-1 w-full" title="Resume Preview" />
          </div>
        </div>
      )}
    </div>
  )
}
