/**
 * JOBPILOT — Jobs Page
 * Responsive with skeletons, toasts, debounced search.
 */

import { useState, useCallback, useRef, useEffect } from 'react'
import { Search, Loader2 } from 'lucide-react'
import JobCard from '../components/JobCard'
import EmptyState from '../components/EmptyState'
import ScrapeModal from '../components/ScrapeModal'
import Skeleton from '../components/Skeleton'
import api from '../api/client'
import { useApi, useApiMutation } from '../hooks/useApi'
import { useToast } from '../hooks/useToast'

const STATUS_OPTIONS = ['all', 'new', 'reviewed', 'shortlisted', 'applied', 'interviewing', 'rejected', 'skipped']
const PORTAL_OPTIONS = ['all', 'linkedin', 'naukri', 'wellfound', 'instahyre', 'indeed', 'glassdoor']
const SORT_OPTIONS = [
  { value: 'match_score', label: 'Match Score' },
  { value: 'created_at', label: 'Date Found' },
  { value: 'title', label: 'Title' },
]

export default function Jobs() {
  const toast = useToast()
  const [statusFilter, setStatusFilter] = useState('all')
  const [portalFilter, setPortalFilter] = useState('all')
  const [minScore, setMinScore] = useState('')
  const [search, setSearch] = useState('')
  const [debouncedSearch, setDebouncedSearch] = useState('')
  const [sortBy, setSortBy] = useState('match_score')
  const [page, setPage] = useState(0)
  const [showScrapeModal, setShowScrapeModal] = useState(false)
  const [scraping, setScraping] = useState(false)
  const debounceRef = useRef(null)

  // Debounce search input — 400ms
  useEffect(() => {
    clearTimeout(debounceRef.current)
    debounceRef.current = setTimeout(() => {
      setDebouncedSearch(search)
      setPage(0)
    }, 400)
    return () => clearTimeout(debounceRef.current)
  }, [search])

  const handleScrape = async (portals) => {
    setScraping(true)
    setShowScrapeModal(false)
    try {
      await api.jobs.triggerScrape(portals)
      toast.info('Scrape started...')
    } catch (err) {
      toast.error(err.response?.data?.detail || err.message)
    } finally {
      setScraping(false)
      refetch()
    }
  }

  const buildParams = useCallback(() => ({
    ...(statusFilter !== 'all' && { status: statusFilter }),
    ...(portalFilter !== 'all' && { portal: portalFilter }),
    ...(minScore && { min_score: parseInt(minScore) }),
    ...(debouncedSearch && { search: debouncedSearch }),
    sort_by: sortBy,
    sort_order: 'desc',
    skip: page * 50,
    limit: 50,
  }), [statusFilter, portalFilter, minScore, debouncedSearch, sortBy, page])

  const { data, setData, loading, refetch } = useApi(
    () => api.jobs.list(buildParams()),
    [statusFilter, portalFilter, minScore, debouncedSearch, sortBy, page]
  )

  const { execute } = useApiMutation()

  const handleApply = async (jobId) => {
    try {
      await execute(() => api.applications.create(jobId, true))
      toast.success('Application created — job URL opened')
      refetch()
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Apply failed')
    }
  }

  const handleScore = async (jobId) => {
    try {
      const result = await execute(() => api.jobs.score(jobId))
      if (result?.score?.score !== undefined) {
        setData(prev => prev ? {
          ...prev,
          jobs: prev.jobs.map(j => j._id === jobId
            ? { ...j, match_score: result.score.score, match_reasoning: result.score.reasoning || '' }
            : j
          )
        } : prev)
        toast.success(`Scored: ${result.score.score}/100`)
      }
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Scoring failed')
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
        toast.success('Resume tailored successfully')
      }
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Tailoring failed')
    }
  }

  const handleDelete = async (jobId) => {
    try {
      await execute(() => api.jobs.delete(jobId))
      toast.success('Job deleted')
      refetch()
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Delete failed')
    }
  }

  const jobs = data?.jobs || []
  const total = data?.total || 0

  return (
    <div>
      {/* Page header */}
      <div className="flex items-center justify-between mb-4 sm:mb-6">
        <div>
          <h1 className="text-xl sm:text-2xl font-bold text-gray-900 dark:text-white">Jobs</h1>
          <p className="text-sm text-gray-500 dark:text-surface-400 mt-1">
            {total} job{total !== 1 ? 's' : ''} found
          </p>
        </div>
        <button onClick={() => setShowScrapeModal(true)} disabled={scraping}
          className="flex items-center gap-1.5 px-3 sm:px-4 py-2 bg-brand-600 text-white text-sm font-medium rounded-lg hover:bg-brand-700 disabled:opacity-50"
          aria-label="Start scraping jobs">
          {scraping ? <Loader2 className="w-4 h-4 animate-spin" /> : null}
          <span className="hidden sm:inline">{scraping ? 'Scraping...' : 'Scrape Now'}</span>
          <span className="sm:hidden">Scrape</span>
        </button>
      </div>

      {showScrapeModal && (
        <ScrapeModal onScrape={handleScrape} onClose={() => setShowScrapeModal(false)} />
      )}

      {/* Filters bar */}
      <div className="bg-white dark:bg-surface-800 rounded-xl border border-gray-200 dark:border-surface-700 p-3 sm:p-4 mb-4 sm:mb-6">
        <div className="flex flex-col sm:flex-row sm:flex-wrap items-stretch sm:items-center gap-2 sm:gap-3">
          {/* Search */}
          <div className="relative flex-1 min-w-0 sm:min-w-[200px]">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400 dark:text-surface-500" />
            <input type="text" placeholder="Search jobs..." value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full pl-9 pr-8 py-2 bg-gray-50 dark:bg-surface-700 border border-gray-200 dark:border-surface-700 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-transparent"
              aria-label="Search jobs"
            />
            {search && (
              <button onClick={() => setSearch('')}
                className="absolute right-2.5 top-1/2 -translate-y-1/2 text-gray-400 dark:text-surface-500 hover:text-gray-600 dark:hover:text-surface-300"
                aria-label="Clear search">
                ✕
              </button>
            )}
          </div>

          <div className="flex gap-2 flex-wrap">
            <select value={statusFilter} onChange={(e) => { setStatusFilter(e.target.value); setPage(0) }}
              className="px-3 py-2 bg-gray-50 dark:bg-surface-700 border border-gray-200 dark:border-surface-700 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-brand-500"
              aria-label="Filter by status">
              {STATUS_OPTIONS.map(s => <option key={s} value={s}>{s === 'all' ? 'All Status' : s.charAt(0).toUpperCase() + s.slice(1)}</option>)}
            </select>

            <select value={portalFilter} onChange={(e) => { setPortalFilter(e.target.value); setPage(0) }}
              className="px-3 py-2 bg-gray-50 dark:bg-surface-700 border border-gray-200 dark:border-surface-700 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-brand-500"
              aria-label="Filter by portal">
              {PORTAL_OPTIONS.map(p => <option key={p} value={p}>{p === 'all' ? 'All Portals' : p.charAt(0).toUpperCase() + p.slice(1)}</option>)}
            </select>

            <input type="number" placeholder="Min score" value={minScore}
              onChange={(e) => { setMinScore(e.target.value); setPage(0) }}
              className="w-24 px-3 py-2 bg-gray-50 dark:bg-surface-700 border border-gray-200 dark:border-surface-700 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-brand-500"
              min="0" max="100" aria-label="Minimum match score" />

            <select value={sortBy} onChange={(e) => setSortBy(e.target.value)}
              className="px-3 py-2 bg-gray-50 dark:bg-surface-700 border border-gray-200 dark:border-surface-700 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-brand-500"
              aria-label="Sort by">
              {SORT_OPTIONS.map(({ value, label }) => <option key={value} value={value}>{label}</option>)}
            </select>
          </div>
        </div>
      </div>

      {/* Job cards list */}
      {loading ? (
        <Skeleton.JobList />
      ) : jobs.length === 0 ? (
        <EmptyState
          title="No jobs found"
          message="Try adjusting your filters, or run a scrape to find new jobs."
          action="Scrape Now"
          onAction={() => setShowScrapeModal(true)}
          preset="jobs"
          secondaryAction="Clear Filters"
          onSecondaryAction={() => { setStatusFilter('all'); setPortalFilter('all'); setMinScore(''); setSearch('') }}
        />
      ) : (
        <div className="space-y-3 sm:space-y-4">
          {jobs.map(job => (
            <JobCard key={job._id} job={job} onApply={handleApply} onScore={handleScore} onTailor={handleTailor} onDelete={handleDelete} />
          ))}
        </div>
      )}

      {/* Pagination */}
      {total > 50 && (
        <div className="flex items-center justify-center gap-3 sm:gap-4 mt-6 sm:mt-8">
          <button onClick={() => setPage(p => Math.max(0, p - 1))} disabled={page === 0}
            className="px-3 sm:px-4 py-2 text-sm border border-gray-200 dark:border-surface-700 rounded-lg disabled:opacity-50 hover:bg-gray-50 dark:hover:bg-surface-700">
            Previous
          </button>
          <span className="text-sm text-gray-500 dark:text-surface-400">
            Page {page + 1} of {Math.ceil(total / 50)}
          </span>
          <button onClick={() => setPage(p => p + 1)} disabled={(page + 1) * 50 >= total}
            className="px-3 sm:px-4 py-2 text-sm border border-gray-200 dark:border-surface-700 rounded-lg disabled:opacity-50 hover:bg-gray-50 dark:hover:bg-surface-700">
            Next
          </button>
        </div>
      )}
    </div>
  )
}
