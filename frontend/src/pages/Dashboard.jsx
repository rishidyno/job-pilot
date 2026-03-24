/**
 * JOBPILOT — Dashboard Page
 *
 * Overview page with:
 * - Key metrics cards (total jobs, applied, interviews, etc.)
 * - Jobs-over-time line chart
 * - Portal breakdown
 * - Application pipeline
 * - Recent activity feed
 */

import { useState, useEffect, useRef } from 'react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar } from 'recharts'
import { Briefcase, Send, Target, TrendingUp, AlertCircle, Award, RefreshCw, Square, Loader2 } from 'lucide-react'
import StatsCard from '../components/StatsCard'
import StatusBadge from '../components/StatusBadge'
import api from '../api/client'
import { useApi } from '../hooks/useApi'
import { timeAgo, portalIcon, capitalize } from '../utils/helpers'

export default function Dashboard() {
  const { data: stats, loading: statsLoading, refetch: refetchStats } = useApi(() => api.dashboard.getStats())
  const { data: timeline } = useApi(() => api.dashboard.getTimeline())
  const { data: portals } = useApi(() => api.dashboard.getPortals())
  const { data: pipeline } = useApi(() => api.dashboard.getPipeline())
  const { data: activity } = useApi(() => api.dashboard.getRecentActivity())
  const [scraping, setScraping] = useState(false)
  const [scrapeStatus, setScrapeStatus] = useState(null)
  const pollRef = useRef(null)

  // Poll scrape status while running
  useEffect(() => {
    if (scraping) {
      pollRef.current = setInterval(async () => {
        try {
          const { data } = await api.jobs.scrapeStatus()
          setScrapeStatus(data)
          if (!data.running) {
            setScraping(false)
            clearInterval(pollRef.current)
            refetchStats()
          }
        } catch {}
      }, 2000)
    }
    return () => clearInterval(pollRef.current)
  }, [scraping])

  // Check if scrape is already running on mount
  useEffect(() => {
    api.jobs.scrapeStatus().then(({ data }) => {
      if (data.running) { setScraping(true); setScrapeStatus(data) }
    }).catch(() => {})
  }, [])

  const handleScrape = async () => {
    try {
      await api.jobs.triggerScrape()
      setScraping(true)
    } catch (e) {
      alert(e.response?.data?.detail || 'Failed to start scrape')
    }
  }

  const handleStop = async () => {
    try { await api.jobs.scrapeStop() } catch {}
  }

  return (
    <div>
      {/* Page header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
          <p className="text-sm text-gray-500 mt-1">Your job search at a glance</p>
        </div>
        <div className="flex items-center gap-2">
          {scraping && (
            <button onClick={handleStop}
              className="flex items-center gap-2 px-4 py-2.5 bg-red-600 text-white text-sm font-medium rounded-lg hover:bg-red-700">
              <Square className="w-4 h-4" /> Stop
            </button>
          )}
          <button onClick={handleScrape} disabled={scraping}
            className="flex items-center gap-2 px-4 py-2.5 bg-brand-600 text-white text-sm font-medium rounded-lg hover:bg-brand-700 disabled:opacity-50">
            <RefreshCw className={`w-4 h-4 ${scraping ? 'animate-spin' : ''}`} />
            {scraping ? 'Scraping...' : 'Scrape Now'}
          </button>
        </div>
      </div>

      {/* Live Scrape Monitor */}
      {scraping && scrapeStatus && (
        <div className="mb-6 bg-white rounded-xl border border-brand-200 p-5">
          <div className="flex items-center gap-2 mb-3">
            <Loader2 className="w-4 h-4 text-brand-600 animate-spin" />
            <h2 className="text-sm font-semibold text-gray-700">Live Scrape Monitor</h2>
            {scrapeStatus.stop_requested && (
              <span className="text-xs bg-red-100 text-red-700 px-2 py-0.5 rounded-full">Stopping...</span>
            )}
          </div>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-3">
            <div className="text-center p-2 bg-gray-50 rounded-lg">
              <p className="text-xs text-gray-500">Current Portal</p>
              <p className="text-sm font-semibold text-brand-600">{capitalize(scrapeStatus.current_portal || '—')}</p>
            </div>
            <div className="text-center p-2 bg-gray-50 rounded-lg">
              <p className="text-xs text-gray-500">Jobs Found</p>
              <p className="text-sm font-semibold text-gray-800">{scrapeStatus.jobs_found}</p>
            </div>
            <div className="text-center p-2 bg-gray-50 rounded-lg">
              <p className="text-xs text-gray-500">New Jobs</p>
              <p className="text-sm font-semibold text-emerald-600">{scrapeStatus.new_jobs}</p>
            </div>
            <div className="text-center p-2 bg-gray-50 rounded-lg">
              <p className="text-xs text-gray-500">Errors</p>
              <p className="text-sm font-semibold text-red-600">{scrapeStatus.errors}</p>
            </div>
          </div>
          {/* Portal progress */}
          <div className="flex gap-2 flex-wrap mb-3">
            {(scrapeStatus.portals_done || []).map(p => (
              <span key={p} className="text-xs px-2 py-1 bg-emerald-50 text-emerald-700 rounded-full">✓ {capitalize(p)}</span>
            ))}
            {scrapeStatus.current_portal && (
              <span className="text-xs px-2 py-1 bg-brand-50 text-brand-700 rounded-full animate-pulse">⟳ {capitalize(scrapeStatus.current_portal)}</span>
            )}
            {(scrapeStatus.portals_remaining || []).map(p => (
              <span key={p} className="text-xs px-2 py-1 bg-gray-100 text-gray-500 rounded-full">{capitalize(p)}</span>
            ))}
          </div>
          {/* Log feed */}
          <div className="max-h-32 overflow-y-auto bg-gray-900 rounded-lg p-3">
            {(scrapeStatus.logs || []).slice(-10).map((log, i) => (
              <p key={i} className="text-xs text-gray-300 font-mono">
                <span className="text-gray-500">{log.time?.slice(11, 19)}</span> {log.message}
              </p>
            ))}
          </div>
        </div>
      )}

      {/* Stats row */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4 mb-8">
        <StatsCard label="Total Jobs" value={stats?.total_jobs} icon={Briefcase} color="brand" />
        <StatsCard label="New Today" value={stats?.new_today} icon={TrendingUp} color="blue" />
        <StatsCard label="High Matches" value={stats?.high_matches} icon={Target} color="green" />
        <StatsCard label="Applied" value={stats?.total_applied} icon={Send} color="purple" />
        <StatsCard label="Interviews" value={stats?.interviews} icon={Award} color="amber" />
        <StatsCard label="Avg Score" value={stats?.avg_match_score} icon={AlertCircle} color="brand"
          subtext="across all jobs" />
      </div>

      {/* Charts row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        {/* Timeline chart */}
        <div className="bg-white rounded-xl border border-gray-200 p-5">
          <h2 className="text-sm font-semibold text-gray-700 mb-4">Jobs Found (Last 30 Days)</h2>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={timeline?.timeline || []}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                <XAxis dataKey="date" tick={{ fontSize: 10 }} tickFormatter={d => d.slice(5)} />
                <YAxis tick={{ fontSize: 10 }} />
                <Tooltip />
                <Line type="monotone" dataKey="jobs" stroke="#6366f1" strokeWidth={2} dot={false} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Portal breakdown */}
        <div className="bg-white rounded-xl border border-gray-200 p-5">
          <h2 className="text-sm font-semibold text-gray-700 mb-4">Jobs by Portal</h2>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={portals?.portals || []} layout="vertical">
                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                <XAxis type="number" tick={{ fontSize: 10 }} />
                <YAxis dataKey="portal" type="category" tick={{ fontSize: 10 }} width={80}
                  tickFormatter={capitalize} />
                <Tooltip />
                <Bar dataKey="total_jobs" fill="#6366f1" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Bottom row: Pipeline + Activity */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Application Pipeline */}
        <div className="bg-white rounded-xl border border-gray-200 p-5">
          <h2 className="text-sm font-semibold text-gray-700 mb-4">Application Pipeline</h2>
          <div className="space-y-3">
            {pipeline && Object.entries(pipeline.pipeline || {}).map(([status, count]) => (
              <div key={status} className="flex items-center justify-between">
                <StatusBadge status={status} />
                <div className="flex-1 mx-3">
                  <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
                    <div className="h-full bg-brand-500 rounded-full transition-all"
                      style={{ width: `${Math.min(100, (count / Math.max(1, stats?.total_applied || 1)) * 100)}%` }} />
                  </div>
                </div>
                <span className="text-sm font-semibold text-gray-700 w-8 text-right">{count}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Recent Activity */}
        <div className="bg-white rounded-xl border border-gray-200 p-5">
          <h2 className="text-sm font-semibold text-gray-700 mb-4">Recent Activity</h2>
          <div className="space-y-3">
            {(activity?.activity || []).map((item, i) => (
              <div key={i} className="flex items-start gap-3 pb-3 border-b border-gray-50 last:border-0">
                <span className="text-lg">{item.type === 'job_found' ? '🔍' : '📤'}</span>
                <div className="flex-1 min-w-0">
                  <p className="text-sm text-gray-800 font-medium truncate">
                    {item.title} — {item.company}
                  </p>
                  <p className="text-xs text-gray-400">
                    {item.type === 'job_found'
                      ? `Found on ${capitalize(item.portal)} • Score: ${item.score ?? '?'}`
                      : `${capitalize(item.status)}`
                    }
                  </p>
                </div>
                <span className="text-xs text-gray-400 shrink-0">{timeAgo(item.timestamp)}</span>
              </div>
            ))}
            {(!activity?.activity || activity.activity.length === 0) && (
              <p className="text-sm text-gray-400 text-center py-4">No recent activity</p>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
