/**
 * JOBPILOT — Jobs Page
 *
 * Browse all scraped jobs with filtering, sorting, and actions.
 * Features: status filter, portal filter, score filter, search,
 * bulk actions, and per-job apply/score/status buttons.
 */

import { useState, useCallback } from 'react'
import { Search, Filter, SlidersHorizontal } from 'lucide-react'
import JobCard from '../components/JobCard'
import EmptyState from '../components/EmptyState'
import api from '../api/client'
import { useApi, useApiMutation } from '../hooks/useApi'

const STATUS_OPTIONS = ['all', 'new', 'reviewed', 'shortlisted', 'applied', 'interviewing', 'rejected', 'skipped']
const PORTAL_OPTIONS = ['all', 'linkedin', 'naukri', 'wellfound', 'instahyre', 'indeed', 'glassdoor']
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
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Jobs</h1>
        <p className="text-sm text-gray-500 mt-1">
          {total} job{total !== 1 ? 's' : ''} found
        </p>
      </div>

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
          onAction={() => api.jobs.triggerScrape()}
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
