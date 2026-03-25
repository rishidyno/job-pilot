/**
 * JOBPILOT — Jobs Page
 *
 * Browse all scraped jobs with filtering, sorting, and actions.
 * Features: status filter, portal filter, score filter, search,
 * bulk actions, and per-job apply/score/status buttons.
 */

import { useState, useCallback } from 'react'
import { Search, Filter, SlidersHorizontal, Loader2 } from 'lucide-react'
import JobCard from '../components/JobCard'
import EmptyState from '../components/EmptyState'
import api from '../api/client'
import { useApi, useApiMutation } from '../hooks/useApi'

const STATUS_OPTIONS = ['all', 'new', 'reviewed', 'shortlisted', 'applied', 'interviewing', 'rejected', 'skipped']
const PORTAL_OPTIONS = ['all', 'linkedin', 'naukri', 'wellfound', 'instahyre', 'indeed', 'glassdoor']
const ALL_PORTALS = ['linkedin', 'naukri', 'wellfound', 'instahyre', 'indeed', 'glassdoor']
const SORT_OPTIONS = [
  { value: 'match_score', label: 'Match Score' },
  { value: 'created_at', label: 'Date Found' },
  { value: 'title', label: 'Title' },
]

export default function Jobs() {
  // Filter state
  const [statusFilter, setStatusFilter] = useState('all')
  const [portalFilter, setPortalFilter] = useState('all')
  const [minScore, setMinScore] = useState('')
  const [search, setSearch] = useState('')
  const [sortBy, setSortBy] = useState('match_score')
  const [page, setPage] = useState(0)

  // Scrape modal state
  const [showScrapeModal, setShowScrapeModal] = useState(false)
  const [selectedPortals, setSelectedPortals] = useState(new Set(ALL_PORTALS))
  const [scraping, setScraping] = useState(false)

  const togglePortal = (p) => {
    setSelectedPortals(prev => {
      const next = new Set(prev)
      next.has(p) ? next.delete(p) : next.add(p)
      return next
    })
  }

  const handleScrape = async () => {
    if (selectedPortals.size === 0) return
    setScraping(true)
    setShowScrapeModal(false)
    try {
      await api.jobs.triggerScrape([...selectedPortals])
    } catch (err) {
      alert(`Scrape failed: ${err.response?.data?.detail || err.message}`)
    } finally {
      setScraping(false)
      refetch()
    }
  }

  // Build query params from filter state
  const buildParams = useCallback(() => ({
    ...(statusFilter !== 'all' && { status: statusFilter }),
    ...(portalFilter !== 'all' && { portal: portalFilter }),
    ...(minScore && { min_score: parseInt(minScore) }),
    ...(search && { search }),
    sort_by: sortBy,
    sort_order: 'desc',
    skip: page * 50,
    limit: 50,
  }), [statusFilter, portalFilter, minScore, search, sortBy, page])

  // Fetch jobs with current filters
  const { data, setData, loading, refetch } = useApi(
    () => api.jobs.list(buildParams()),
    [statusFilter, portalFilter, minScore, search, sortBy, page]
  )

  const { execute } = useApiMutation()

  const handleApply = async (jobId) => {
    try {
      await execute(() => api.applications.create(jobId, true))
      refetch()
    } catch (err) {
      alert(`Apply failed: ${err.response?.data?.detail || err.message}`)
    }
  }

  const handleScore = async (jobId) => {
    try {
      const result = await execute(() => api.jobs.score(jobId))
      // Update score in-place without refetching the whole list
      if (result?.score?.score !== undefined) {
        setData(prev => prev ? {
          ...prev,
          jobs: prev.jobs.map(j => j._id === jobId
            ? { ...j, match_score: result.score.score, match_reasoning: result.score.reasoning || '' }
            : j
          )
        } : prev)
      }
    } catch (err) {
      alert(`Scoring failed: ${err.response?.data?.detail || err.message}`)
    }
  }

  const handleTailor = async (jobId) => {
    try {
      const result = await execute(() => api.resumes.tailor(jobId))
      if (result?.resume_id) {
        setData(prev => prev ? {
          ...prev,
          jobs: prev.jobs.map(j => j._id === jobId
            ? { ...j, tailored_resume_id: result.resume_id }
            : j
          )
        } : prev)
      }
    } catch (err) {
      alert(`Tailoring failed: ${err.response?.data?.detail || err.message}`)
    }
  }

  const handleDelete = async (jobId) => {
    try {
      await execute(() => api.jobs.delete(jobId))
      refetch()
    } catch (err) {
      alert(`Delete failed: ${err.response?.data?.detail || err.message}`)
    }
  }

  const jobs = data?.jobs || []
  const total = data?.total || 0

  return (
    <div>
      {/* Page header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Jobs</h1>
          <p className="text-sm text-gray-500 mt-1">
            {total} job{total !== 1 ? 's' : ''} found
          </p>
        </div>
        <button onClick={() => setShowScrapeModal(true)} disabled={scraping}
          className="flex items-center gap-2 px-4 py-2 bg-brand-600 text-white text-sm font-medium rounded-lg hover:bg-brand-700 disabled:opacity-50">
          {scraping ? <Loader2 className="w-4 h-4 animate-spin" /> : null}
          {scraping ? 'Scraping...' : 'Scrape Now'}
        </button>
      </div>

      {/* Scrape Portal Selector Modal */}
      {showScrapeModal && (
        <div className="fixed inset-0 bg-black/40 z-50 flex items-center justify-center p-4" onClick={() => setShowScrapeModal(false)}>
          <div className="bg-white rounded-xl w-full max-w-sm p-6" onClick={e => e.stopPropagation()}>
            <h3 className="text-lg font-semibold text-gray-900 mb-1">Select Portals to Scrape</h3>
            <p className="text-xs text-gray-500 mb-4">Choose which job sites to scrape from</p>
            <div className="space-y-2 mb-5">
              {ALL_PORTALS.map(p => (
                <label key={p} className="flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-gray-50 cursor-pointer">
                  <input type="checkbox" checked={selectedPortals.has(p)} onChange={() => togglePortal(p)}
                    className="w-4 h-4 rounded border-gray-300 text-brand-600 focus:ring-brand-500" />
                  <span className="text-sm text-gray-700 capitalize">{p}</span>
                </label>
              ))}
            </div>
            <div className="flex items-center justify-between">
              <button onClick={() => {
                setSelectedPortals(prev => prev.size === ALL_PORTALS.length ? new Set() : new Set(ALL_PORTALS))
              }} className="text-xs text-brand-600 hover:underline">
                {selectedPortals.size === ALL_PORTALS.length ? 'Deselect All' : 'Select All'}
              </button>
              <div className="flex gap-2">
                <button onClick={() => setShowScrapeModal(false)}
                  className="px-4 py-2 text-sm border border-gray-200 rounded-lg hover:bg-gray-50">Cancel</button>
                <button onClick={handleScrape} disabled={selectedPortals.size === 0}
                  className="px-4 py-2 text-sm bg-brand-600 text-white rounded-lg hover:bg-brand-700 disabled:opacity-50">
                  Scrape {selectedPortals.size} Portal{selectedPortals.size !== 1 ? 's' : ''}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Filters bar */}
      <div className="bg-white rounded-xl border border-gray-200 p-4 mb-6">
        <div className="flex flex-wrap items-center gap-3">
          {/* Search */}
          <div className="relative flex-1 min-w-[200px]">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
            <input type="text" placeholder="Search jobs..." value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full pl-9 pr-3 py-2 bg-gray-50 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-transparent"
            />
          </div>

          {/* Status filter */}
          <select value={statusFilter} onChange={(e) => { setStatusFilter(e.target.value); setPage(0) }}
            className="px-3 py-2 bg-gray-50 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-brand-500">
            {STATUS_OPTIONS.map(s => <option key={s} value={s}>{s === 'all' ? 'All Status' : s.charAt(0).toUpperCase() + s.slice(1)}</option>)}
          </select>

          {/* Portal filter */}
          <select value={portalFilter} onChange={(e) => { setPortalFilter(e.target.value); setPage(0) }}
            className="px-3 py-2 bg-gray-50 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-brand-500">
            {PORTAL_OPTIONS.map(p => <option key={p} value={p}>{p === 'all' ? 'All Portals' : p.charAt(0).toUpperCase() + p.slice(1)}</option>)}
          </select>

          {/* Min score */}
          <input type="number" placeholder="Min score" value={minScore}
            onChange={(e) => { setMinScore(e.target.value); setPage(0) }}
            className="w-24 px-3 py-2 bg-gray-50 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-brand-500"
            min="0" max="100" />

          {/* Sort */}
          <select value={sortBy} onChange={(e) => setSortBy(e.target.value)}
            className="px-3 py-2 bg-gray-50 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-brand-500">
            {SORT_OPTIONS.map(({ value, label }) => <option key={value} value={value}>{label}</option>)}
          </select>
        </div>
      </div>

      {/* Job cards list */}
      {loading ? (
        <div className="text-center py-12 text-gray-400">Loading jobs...</div>
      ) : jobs.length === 0 ? (
        <EmptyState
          title="No jobs found"
          message="Try adjusting your filters, or run a scrape to find new jobs."
          action="Scrape Now"
          onAction={() => setShowScrapeModal(true)}
        />
      ) : (
        <div className="space-y-4">
          {jobs.map(job => (
            <JobCard key={job._id} job={job} onApply={handleApply} onScore={handleScore} onTailor={handleTailor} onDelete={handleDelete} />
          ))}
        </div>
      )}

      {/* Pagination */}
      {total > 50 && (
        <div className="flex items-center justify-center gap-4 mt-8">
          <button onClick={() => setPage(p => Math.max(0, p - 1))} disabled={page === 0}
            className="px-4 py-2 text-sm border border-gray-200 rounded-lg disabled:opacity-50 hover:bg-gray-50">
            Previous
          </button>
          <span className="text-sm text-gray-500">
            Page {page + 1} of {Math.ceil(total / 50)}
          </span>
          <button onClick={() => setPage(p => p + 1)} disabled={(page + 1) * 50 >= total}
            className="px-4 py-2 text-sm border border-gray-200 rounded-lg disabled:opacity-50 hover:bg-gray-50">
            Next
          </button>
        </div>
      )}
    </div>
  )
}
