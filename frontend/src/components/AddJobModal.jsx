/**
 * JOBPILOT — AddJobModal
 * Manually add a job by pasting a URL + basic info.
 */
import { useState, useEffect } from 'react'
import { X, Plus, Link } from 'lucide-react'

export default function AddJobModal({ onAdd, onClose }) {
  const [url, setUrl] = useState('')
  const [title, setTitle] = useState('')
  const [company, setCompany] = useState('')
  const [location, setLocation] = useState('')
  const [skills, setSkills] = useState('')
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    const h = (e) => { if (e.key === 'Escape') onClose() }
    document.addEventListener('keydown', h)
    return () => document.removeEventListener('keydown', h)
  }, [onClose])

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!url.trim() || !title.trim() || !company.trim()) return
    setLoading(true)
    try {
      await onAdd({
        url: url.trim(),
        title: title.trim(),
        company: company.trim(),
        location: location.trim() || null,
        skills: skills ? skills.split(',').map(s => s.trim()).filter(Boolean) : null,
      })
      onClose()
    } catch {
      setLoading(false)
    }
  }

  return (
    <div className="fixed inset-0 bg-black/40 z-50 flex items-end sm:items-center justify-center p-0 sm:p-4"
      onClick={onClose} role="dialog" aria-modal="true" aria-label="Add job manually">
      <div className="bg-white dark:bg-surface-800 rounded-t-2xl sm:rounded-xl w-full sm:max-w-md p-5 sm:p-6"
        onClick={e => e.stopPropagation()}>
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-brand-50 dark:bg-brand-950/30 flex items-center justify-center">
              <Link className="w-4 h-4 text-brand-600 dark:text-brand-400" />
            </div>
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Add Job Manually</h3>
          </div>
          <button onClick={onClose} className="p-1.5 rounded-lg hover:bg-gray-100 dark:hover:bg-surface-700">
            <X className="w-4 h-4 text-gray-400" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-3">
          <div>
            <label className="block text-xs font-medium text-gray-500 dark:text-surface-400 mb-1">Job URL *</label>
            <input type="url" value={url} onChange={e => setUrl(e.target.value)} required
              placeholder="https://careers.paypal.com/job/..."
              className="w-full px-3 py-2 bg-gray-50 dark:bg-surface-700 border border-gray-200 dark:border-surface-600 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-brand-500" />
          </div>
          <div>
            <label className="block text-xs font-medium text-gray-500 dark:text-surface-400 mb-1">Job Title *</label>
            <input type="text" value={title} onChange={e => setTitle(e.target.value)} required
              placeholder="Backend Engineer"
              className="w-full px-3 py-2 bg-gray-50 dark:bg-surface-700 border border-gray-200 dark:border-surface-600 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-brand-500" />
          </div>
          <div>
            <label className="block text-xs font-medium text-gray-500 dark:text-surface-400 mb-1">Company *</label>
            <input type="text" value={company} onChange={e => setCompany(e.target.value)} required
              placeholder="PayPal"
              className="w-full px-3 py-2 bg-gray-50 dark:bg-surface-700 border border-gray-200 dark:border-surface-600 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-brand-500" />
          </div>
          <div>
            <label className="block text-xs font-medium text-gray-500 dark:text-surface-400 mb-1">Location</label>
            <input type="text" value={location} onChange={e => setLocation(e.target.value)}
              placeholder="Bengaluru, Remote, etc."
              className="w-full px-3 py-2 bg-gray-50 dark:bg-surface-700 border border-gray-200 dark:border-surface-600 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-brand-500" />
          </div>
          <div>
            <label className="block text-xs font-medium text-gray-500 dark:text-surface-400 mb-1">Skills (comma-separated)</label>
            <input type="text" value={skills} onChange={e => setSkills(e.target.value)}
              placeholder="Java, Spring Boot, MongoDB"
              className="w-full px-3 py-2 bg-gray-50 dark:bg-surface-700 border border-gray-200 dark:border-surface-600 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-brand-500" />
          </div>

          <button type="submit" disabled={loading || !url || !title || !company}
            className="w-full flex items-center justify-center gap-2 py-2.5 bg-brand-600 text-white text-sm font-semibold rounded-lg hover:bg-brand-700 disabled:opacity-50 mt-4">
            {loading ? <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" /> : <Plus className="w-4 h-4" />}
            {loading ? 'Adding...' : 'Add Job'}
          </button>
        </form>
      </div>
    </div>
  )
}
