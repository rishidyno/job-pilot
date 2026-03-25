/**
 * JOBPILOT — Applications Page
 * Responsive with skeletons and toasts.
 */

import { useState } from 'react'
import { ExternalLink, RotateCw, ChevronDown, ChevronUp } from 'lucide-react'
import StatusBadge from '../components/StatusBadge'
import EmptyState from '../components/EmptyState'
import Skeleton from '../components/Skeleton'
import api from '../api/client'
import { useApi, useApiMutation } from '../hooks/useApi'
import { useToast } from '../hooks/useToast'
import { timeAgo, capitalize } from '../utils/helpers'

const STATUS_TABS = ['all', 'pending', 'submitted', 'reviewing', 'interview', 'offered', 'rejected', 'failed']

export default function Applications() {
  const toast = useToast()
  const [activeTab, setActiveTab] = useState('all')
  const [expanded, setExpanded] = useState(null)

  const params = activeTab === 'all' ? {} : { status: activeTab }
  const { data, loading, refetch } = useApi(() => api.applications.list(params), [activeTab])
  const { execute } = useApiMutation()

  const handleStatusChange = async (appId, newStatus) => {
    try {
      await execute(() => api.applications.update(appId, { status: newStatus }))
      toast.success(`Status updated to ${newStatus}`)
      refetch()
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Update failed')
    }
  }

  const handleRetry = async (appId) => {
    try {
      await execute(() => api.applications.retry(appId))
      toast.info('Retrying application...')
      refetch()
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Retry failed')
    }
  }

  const apps = data?.applications || []

  return (
    <div>
      <div className="mb-4 sm:mb-6">
        <h1 className="text-xl sm:text-2xl font-bold text-gray-900">Applications</h1>
        <p className="text-sm text-gray-500 mt-1">{data?.total || 0} total applications</p>
      </div>

      {/* Status tabs — horizontally scrollable on mobile */}
      <div className="flex gap-2 mb-4 sm:mb-6 overflow-x-auto pb-2 -mx-4 px-4 sm:mx-0 sm:px-0 sm:flex-wrap scrollbar-none">
        {STATUS_TABS.map(tab => (
          <button key={tab} onClick={() => setActiveTab(tab)}
            className={`px-3 py-1.5 rounded-lg text-sm font-medium whitespace-nowrap shrink-0 ${
              activeTab === tab
                ? 'bg-brand-600 text-white'
                : 'bg-white border border-gray-200 text-gray-600 hover:bg-gray-50'
            }`}
            aria-label={`Filter by ${tab} status`}
            aria-pressed={activeTab === tab}>
            {capitalize(tab)}
          </button>
        ))}
      </div>

      {/* Applications list */}
      {loading ? (
        <Skeleton.AppList />
      ) : apps.length === 0 ? (
        <EmptyState title="No applications yet" message="Apply to jobs from the Jobs page to see them here." />
      ) : (
        <div className="space-y-3">
          {apps.map(app => (
            <div key={app._id} className="bg-white rounded-xl border border-gray-200 overflow-hidden">
              {/* Main row */}
              <div className="flex items-center gap-3 sm:gap-4 p-3 sm:p-4 cursor-pointer hover:bg-gray-50"
                onClick={() => setExpanded(expanded === app._id ? null : app._id)}
                role="button"
                aria-expanded={expanded === app._id}
                aria-label={`${app.job_title} at ${app.company}, status: ${app.status}`}>
                <StatusBadge status={app.status} />
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-semibold text-gray-900 truncate">{app.job_title || 'Unknown Job'}</p>
                  <p className="text-xs text-gray-500">{app.company || 'Unknown'} • {capitalize(app.portal || 'unknown')}</p>
                </div>
                <span className="text-xs text-gray-400 hidden sm:block">{timeAgo(app.applied_at)}</span>
                <div className="flex items-center gap-1.5 sm:gap-2">
                  {app.job_url && (
                    <a href={app.job_url} target="_blank" rel="noopener noreferrer"
                      onClick={e => e.stopPropagation()}
                      className="p-1.5 rounded-md hover:bg-gray-100"
                      aria-label="Open job posting">
                      <ExternalLink className="w-4 h-4 text-gray-400" />
                    </a>
                  )}
                  {app.status === 'failed' && (
                    <button onClick={(e) => { e.stopPropagation(); handleRetry(app._id) }}
                      className="flex items-center gap-1 px-2 py-1 text-xs bg-red-50 text-red-600 rounded-md hover:bg-red-100"
                      aria-label="Retry failed application">
                      <RotateCw className="w-3 h-3" /> Retry
                    </button>
                  )}
                  {expanded === app._id
                    ? <ChevronUp className="w-4 h-4 text-gray-400" />
                    : <ChevronDown className="w-4 h-4 text-gray-400" />
                  }
                </div>
              </div>

              {/* Expanded details */}
              {expanded === app._id && (
                <div className="px-3 sm:px-4 pb-3 sm:pb-4 border-t border-gray-100 bg-gray-50">
                  {/* Mobile timestamp */}
                  <p className="text-xs text-gray-400 mt-2 sm:hidden">{timeAgo(app.applied_at)}</p>

                  {/* Quick status actions — scrollable on mobile */}
                  <div className="flex items-center gap-2 mt-3 mb-4 overflow-x-auto pb-1 scrollbar-none">
                    <span className="text-xs text-gray-500 shrink-0 mr-1">Status:</span>
                    {['submitted', 'reviewing', 'interview', 'offered', 'accepted', 'rejected', 'withdrawn'].map(s => (
                      <button key={s} onClick={() => handleStatusChange(app._id, s)}
                        disabled={app.status === s}
                        className={`px-2 py-1 text-xs rounded-md border whitespace-nowrap shrink-0 ${
                          app.status === s ? 'border-brand-300 bg-brand-50 text-brand-700' : 'border-gray-200 bg-white text-gray-600 hover:bg-gray-100'
                        }`}
                        aria-label={`Change status to ${s}`}>
                        {capitalize(s)}
                      </button>
                    ))}
                  </div>

                  {app.error_message && (
                    <div className="p-3 bg-red-50 border border-red-100 rounded-lg mb-3" role="alert">
                      <p className="text-xs text-red-700 font-medium">Error: {app.error_message}</p>
                    </div>
                  )}

                  {app.events?.length > 0 && (
                    <div>
                      <h4 className="text-xs font-semibold text-gray-500 mb-2">Timeline</h4>
                      <div className="space-y-2">
                        {app.events.map((event, i) => (
                          <div key={i} className="flex items-start gap-2">
                            <div className="w-1.5 h-1.5 rounded-full bg-brand-400 mt-1.5 shrink-0" />
                            <div>
                              <p className="text-xs text-gray-700">{event.description}</p>
                              <p className="text-xs text-gray-400">{timeAgo(event.timestamp)}</p>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {app.notes && (
                    <div className="mt-3 p-3 bg-white border border-gray-200 rounded-lg">
                      <p className="text-xs text-gray-600">{app.notes}</p>
                    </div>
                  )}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
