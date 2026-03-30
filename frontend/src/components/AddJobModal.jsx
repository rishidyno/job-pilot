/**
 * JOBPILOT — AddJobModal
 * Paste a URL → auto-fetch details → review → add.
 */
import { useState, useEffect } from 'react'
import { X, Link, Loader2, Check, AlertCircle } from 'lucide-react'
import api from '../api/client'

export default function AddJobModal({ onAdd, onClose }) {
  const [step, setStep] = useState('url') // 'url' | 'fetching' | 'review'
  const [url, setUrl] = useState('')
  const [title, setTitle] = useState('')
  const [company, setCompany] = useState('')
  const [location, setLocation] = useState('')
  const [description, setDescription] = useState('')
  const [skills, setSkills] = useState('')
  const [fetchSource, setFetchSource] = useState('')
  const [fetchError, setFetchError] = useState('')
  const [saving, setSaving] = useState(false)

  useEffect(() => {
    const h = (e) => { if (e.key === 'Escape') onClose() }
    document.addEventListener('keydown', h)
    return () => document.removeEventListener('keydown', h)
  }, [onClose])

  const handleFetch = async () => {
    if (!url.trim()) return
    setStep('fetching')
    setFetchError('')
    try {
      const { data } = await api.jobs.fetchDetails(url.trim())
      setTitle(data.title || '')
      setCompany(data.company || '')
      setLocation(data.location || '')
      setDescription(data.description || '')
      setSkills((data.skills || []).join(', '))
      setFetchSource(data.source || '')
      if (data.error) setFetchError(data.error)
      setStep('review')
    } catch (err) {
      setFetchError('Could not fetch URL. Fill in the details manually.')
      setStep('review')
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!url.trim() || !title.trim() || !company.trim()) return
    setSaving(true)
    try {
      await onAdd({
        url: url.trim(),
        title: title.trim(),
        company: company.trim(),
        location: location.trim() || null,
        description: description.trim() || null,
        skills: skills ? skills.split(',').map(s => s.trim()).filter(Boolean) : null,
      })
      onClose()
    } catch {
      setSaving(false)
    }
  }

  return (
    <div className="fixed inset-0 glass-overlay z-50 flex items-end sm:items-center justify-center p-0 sm:p-4"
      onClick={onClose} role="dialog" aria-modal="true" aria-label="Add job manually">
      <div className="bg-white dark:bg-surface-800 rounded-t-2xl sm:rounded-xl w-full sm:max-w-lg p-5 sm:p-6 max-h-[90vh] overflow-y-auto"
        onClick={e => e.stopPropagation()}>

        {/* Header */}
        <div className="flex items-center justify-between mb-5">
          <div className="flex items-center gap-2.5">
            <div className="w-9 h-9 rounded-lg bg-brand-50 dark:bg-brand-950/30 flex items-center justify-center">
              <Link className="w-4.5 h-4.5 text-brand-600 dark:text-brand-400" />
            </div>
            <div>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Add Job</h3>
              <p className="text-xs text-gray-400 dark:text-surface-500">Paste a link — we'll extract the details</p>
            </div>
          </div>
          <button onClick={onClose} className="p-1.5 rounded-lg hover:bg-gray-100 dark:hover:bg-surface-700">
            <X className="w-4 h-4 text-gray-400" />
          </button>
        </div>

        {/* Step 1: URL input */}
        <div className="mb-4">
          <label className="block text-xs font-medium text-gray-500 dark:text-surface-400 mb-1.5">Job URL</label>
          <div className="flex gap-2">
            <input type="url" value={url} onChange={e => { setUrl(e.target.value); if (step === 'review') setStep('url') }}
              placeholder="https://careers.company.com/job/..."
              className="flex-1 px-3 py-2.5 bg-gray-50 dark:bg-surface-700 border border-gray-200 dark:border-surface-600 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-brand-500"
              onKeyDown={e => { if (e.key === 'Enter' && step === 'url') { e.preventDefault(); handleFetch() } }}
              autoFocus />
            {step === 'url' && (
              <button onClick={handleFetch} disabled={!url.trim()}
                className="px-4 py-2.5 bg-brand-600 text-white text-sm font-medium rounded-lg hover:bg-brand-700 disabled:opacity-50 shrink-0">
                Fetch
              </button>
            )}
            {step === 'fetching' && (
              <div className="px-4 py-2.5 flex items-center gap-2 text-sm text-brand-600 dark:text-brand-400">
                <Loader2 className="w-4 h-4 animate-spin" /> Fetching...
              </div>
            )}
            {step === 'review' && !fetchError && (
              <div className="px-3 py-2.5 flex items-center gap-1.5 text-sm text-emerald-600 dark:text-emerald-400">
                <Check className="w-4 h-4" /> Done
              </div>
            )}
          </div>
        </div>

        {/* Fetch status */}
        {fetchError && (
          <div className="flex items-start gap-2 mb-4 px-3 py-2.5 bg-amber-50 dark:bg-amber-950/20 border border-amber-200 dark:border-amber-800 rounded-lg">
            <AlertCircle className="w-4 h-4 text-amber-500 mt-0.5 shrink-0" />
            <p className="text-xs text-amber-700 dark:text-amber-300">{fetchError}</p>
          </div>
        )}

        {fetchSource && !fetchError && (
          <p className="text-xs text-emerald-600 dark:text-emerald-400 mb-4">
            ✓ Extracted from {fetchSource === 'structured' ? 'structured data (high confidence)' : 'page metadata'} — review and edit if needed
          </p>
        )}

        {/* Step 2: Review form (shown after fetch or on error) */}
        {step === 'review' && (
          <form onSubmit={handleSubmit} className="space-y-3">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
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
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-500 dark:text-surface-400 mb-1">Location</label>
              <input type="text" value={location} onChange={e => setLocation(e.target.value)}
                placeholder="Bengaluru, Remote"
                className="w-full px-3 py-2 bg-gray-50 dark:bg-surface-700 border border-gray-200 dark:border-surface-600 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-brand-500" />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-500 dark:text-surface-400 mb-1">Skills (comma-separated)</label>
              <input type="text" value={skills} onChange={e => setSkills(e.target.value)}
                placeholder="Java, Spring Boot, MongoDB"
                className="w-full px-3 py-2 bg-gray-50 dark:bg-surface-700 border border-gray-200 dark:border-surface-600 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-brand-500" />
            </div>
            {description && (
              <div>
                <label className="block text-xs font-medium text-gray-500 dark:text-surface-400 mb-1">Description (auto-extracted)</label>
                <textarea value={description} onChange={e => setDescription(e.target.value)} rows={4}
                  className="w-full px-3 py-2 bg-gray-50 dark:bg-surface-700 border border-gray-200 dark:border-surface-600 rounded-lg text-xs focus:outline-none focus:ring-2 focus:ring-brand-500 resize-y" />
              </div>
            )}

            <button type="submit" disabled={saving || !title || !company}
              className="w-full flex items-center justify-center gap-2 py-2.5 bg-brand-600 text-white text-sm font-semibold rounded-lg hover:bg-brand-700 disabled:opacity-50 mt-2">
              {saving ? <Loader2 className="w-4 h-4 animate-spin" /> : null}
              {saving ? 'Adding...' : 'Add Job'}
            </button>
          </form>
        )}
      </div>
    </div>
  )
}
