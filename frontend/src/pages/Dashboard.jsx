/**
 * JOBPILOT — Dashboard Page — dark mode, improved charts.
 */

import { useState, useEffect, useRef } from 'react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar, Cell } from 'recharts'
import { Briefcase, Send, Target, TrendingUp, AlertCircle, Award, RefreshCw, Square, Loader2 } from 'lucide-react'
import StatsCard from '../components/StatsCard'
import StatusBadge from '../components/StatusBadge'
import ScrapeModal from '../components/ScrapeModal'
import OnboardingModal from '../components/OnboardingModal'
import Skeleton from '../components/Skeleton'
import api from '../api/client'
import { useApi } from '../hooks/useApi'
import { useToast } from '../hooks/useToast'
import { useTheme } from '../hooks/useTheme'
import { timeAgo, capitalize } from '../utils/helpers'

export default function Dashboard() {
  const toast = useToast()
  const { dark } = useTheme()
  const { data: stats, loading: statsLoading, refetch: refetchStats } = useApi(() => api.dashboard.getStats())
  const { data: timeline, loading: timelineLoading } = useApi(() => api.dashboard.getTimeline())
  const { data: portals, loading: portalsLoading } = useApi(() => api.dashboard.getPortals())
  const { data: pipeline } = useApi(() => api.dashboard.getPipeline())
  const { data: activity } = useApi(() => api.dashboard.getRecentActivity())
  const { data: salaryData } = useApi(() => api.dashboard.getSalaryInsights())
  const [scraping, setScraping] = useState(false)
  const [scrapeStatus, setScrapeStatus] = useState(null)
  const [showScrapeModal, setShowScrapeModal] = useState(false)
  const [showOnboarding, setShowOnboarding] = useState(() => !localStorage.getItem('onboarding_done'))
  const pollRef = useRef(null)

  // Chart colors based on theme
  const chartColor = dark ? '#60a5fa' : '#2563eb'
  const gridColor = dark ? '#334155' : '#f1f5f9'
  const tickColor = dark ? '#94a3b8' : '#64748b'

  // Distinct colors per portal — vibrant in light, softer in dark
  const portalColors = {
    linkedin: dark ? '#60a5fa' : '#0a66c2',
    naukri:   dark ? '#38bdf8' : '#0284c7',
    indeed:   dark ? '#a78bfa' : '#7c3aed',
    glassdoor: dark ? '#4ade80' : '#16a34a',
    google:   dark ? '#fb923c' : '#ea580c',
  }
  const getPortalColor = (portal) => portalColors[portal] || chartColor

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
            toast.success(`Scrape complete — ${data.new_jobs || 0} new jobs found`)
          }
        } catch {}
      }, 2000)
    }
    return () => clearInterval(pollRef.current)
  }, [scraping])

  useEffect(() => {
    api.jobs.scrapeStatus().then(({ data }) => {
      if (data.running) { setScraping(true); setScrapeStatus(data) }
    }).catch(() => {})
  }, [])

  const handleScrape = async (portals) => {
    setShowScrapeModal(false)
    try {
      await api.jobs.triggerScrape(portals)
      setScraping(true)
      toast.info('Scrape started...')
    } catch (e) {
      toast.error(e.response?.data?.detail || 'Failed to start scrape')
    }
  }

  const handleStop = async () => {
    try { await api.jobs.scrapeStop(); toast.warning('Scrape stopped') } catch {}
  }

  return (
    <div>
      {/* Header */}
      <div className="flex items-center justify-between mb-6 sm:mb-8">
        <div>
          <h1 className="text-xl sm:text-2xl font-bold text-gray-900 dark:text-white">Dashboard</h1>
          <p className="text-sm text-gray-500 dark:text-surface-400 mt-1 hidden sm:block">Your job search at a glance</p>
        </div>
        <div className="flex items-center gap-2">
          {scraping && (
            <button onClick={handleStop}
              className="flex items-center gap-1.5 px-3 sm:px-4 py-2 sm:py-2.5 bg-red-600 text-white text-sm font-medium rounded-lg hover:bg-red-700"
              aria-label="Stop scraping">
              <Square className="w-4 h-4" /> <span className="hidden sm:inline">Stop</span>
            </button>
          )}
          <button onClick={() => setShowScrapeModal(true)} disabled={scraping}
            className="flex items-center gap-1.5 px-3 sm:px-4 py-2 sm:py-2.5 bg-brand-600 text-white text-sm font-medium rounded-lg hover:bg-brand-700 disabled:opacity-50"
            aria-label="Start scraping jobs">
            <RefreshCw className={`w-4 h-4 ${scraping ? 'animate-spin' : ''}`} />
            <span className="hidden sm:inline">{scraping ? 'Scraping...' : 'Scrape Now'}</span>
          </button>
        </div>
      </div>

      {showScrapeModal && <ScrapeModal onScrape={handleScrape} onClose={() => setShowScrapeModal(false)} />}
      {showOnboarding && <OnboardingModal onClose={() => { setShowOnboarding(false); localStorage.setItem('onboarding_done', '1') }} />}

      {/* Live Scrape Monitor */}
      {scraping && scrapeStatus && (
        <div className="mb-6 bg-white dark:bg-surface-800 rounded-xl border border-brand-200 dark:border-brand-800 p-4 sm:p-5">
          <div className="flex items-center gap-2 mb-3">
            <Loader2 className="w-4 h-4 text-brand-600 dark:text-brand-400 animate-spin" />
            <h2 className="text-sm font-semibold text-gray-700 dark:text-surface-200">Live Scrape Monitor</h2>
            {scrapeStatus.stop_requested && (
              <span className="text-xs bg-red-100 dark:bg-red-950/30 text-red-700 dark:text-red-300 px-2 py-0.5 rounded-full">Stopping...</span>
            )}
          </div>

          {/* Stats counters */}
          <div className="grid grid-cols-3 sm:grid-cols-6 gap-2 sm:gap-3 mb-3">
            {[
              { label: 'Portal', value: capitalize(scrapeStatus.current_portal || '—'), color: 'text-brand-600 dark:text-brand-400' },
              { label: 'Found', value: scrapeStatus.jobs_found, color: 'text-gray-800 dark:text-white' },
              { label: 'New', value: scrapeStatus.new_jobs, color: 'text-emerald-600 dark:text-emerald-400' },
              { label: 'Duplicates', value: scrapeStatus.duplicates || 0, color: 'text-amber-600 dark:text-amber-400' },
              { label: 'Matches', value: scrapeStatus.high_matches || 0, color: 'text-purple-600 dark:text-purple-400' },
              { label: 'Errors', value: scrapeStatus.errors, color: 'text-red-600 dark:text-red-400' },
            ].map(({ label, value, color }) => (
              <div key={label} className="text-center p-2 bg-gray-50 dark:bg-surface-700 rounded-lg">
                <p className="text-xs text-gray-500 dark:text-surface-400">{label}</p>
                <p className={`text-sm font-semibold ${color}`}>{value}</p>
              </div>
            ))}
          </div>

          {/* Portal progress pills */}
          <div className="flex gap-1.5 flex-wrap mb-3">
            {(scrapeStatus.portals_done || []).map(p => (
              <span key={p} className="text-xs px-2 py-1 bg-emerald-50 dark:bg-emerald-950/30 text-emerald-700 dark:text-emerald-300 rounded-full">✓ {capitalize(p)}</span>
            ))}
            {scrapeStatus.current_portal && (
              <span className="text-xs px-2 py-1 bg-brand-50 dark:bg-brand-950/30 text-brand-700 dark:text-brand-300 rounded-full animate-pulse">⟳ {capitalize(scrapeStatus.current_portal)}</span>
            )}
            {(scrapeStatus.portals_remaining || []).map(p => (
              <span key={p} className="text-xs px-2 py-1 bg-gray-100 dark:bg-surface-700 text-gray-500 dark:text-surface-400 rounded-full">{capitalize(p)}</span>
            ))}
          </div>

          {/* Color-coded event log */}
          <div className="max-h-48 overflow-y-auto bg-gray-900 dark:bg-surface-950 rounded-lg p-3 space-y-0.5" ref={el => { if (el) el.scrollTop = el.scrollHeight }}>
            {(scrapeStatus.logs || []).slice(-30).map((log, i) => {
              const level = log.level || 'info'
              const colorMap = {
                new_job: 'text-emerald-400',
                match: 'text-purple-400 font-semibold',
                skip: 'text-amber-400/70',
                error: 'text-red-400',
                warn: 'text-amber-400',
                ok: 'text-emerald-300',
                step: 'text-blue-300',
                done: 'text-cyan-300 font-semibold',
                info: 'text-gray-300',
              }
              const levelBadge = {
                new_job: '✚', match: '★', skip: '↩', error: '✗',
                warn: '⚠', ok: '✓', step: '→', done: '■', info: '·',
              }
              return (
                <p key={i} className={`text-xs font-mono leading-relaxed ${colorMap[level] || 'text-gray-300'}`}>
                  <span className="text-gray-600 mr-1">{log.time?.slice(11, 19)}</span>
                  <span className="mr-1">{levelBadge[level] || '·'}</span>
                  {log.message}
                </p>
              )
            })}
            {(scrapeStatus.logs || []).length === 0 && (
              <p className="text-xs text-gray-500 font-mono">Waiting for events...</p>
            )}
          </div>
        </div>
      )}

      {/* Stats */}
      {statsLoading ? <Skeleton.StatsRow /> : (
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3 sm:gap-4 mb-6 sm:mb-8">
          <StatsCard label="Total Jobs" value={stats?.total_jobs} icon={Briefcase} color="brand" />
          <StatsCard label="New Today" value={stats?.new_today} icon={TrendingUp} color="blue" />
          <StatsCard label="High Matches" value={stats?.high_matches} icon={Target} color="green" />
          <StatsCard label="Applied" value={stats?.total_applied} icon={Send} color="purple" />
          <StatsCard label="Interviews" value={stats?.interviews} icon={Award} color="amber" />
          <StatsCard label="Avg Score" value={stats?.avg_match_score} icon={AlertCircle} color="brand" subtext="across all jobs" />
        </div>
      )}

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 sm:gap-6 mb-6 sm:mb-8">
        {timelineLoading ? <Skeleton.Chart /> : (
          <div className="bg-white dark:bg-surface-800 rounded-xl border border-gray-200 dark:border-surface-700 p-4 sm:p-5">
            <h2 className="text-sm font-semibold text-gray-700 dark:text-surface-200 mb-4">Jobs Found (Last 30 Days)</h2>
            {(timeline?.timeline || []).length === 0 ? (
              <div className="h-64 flex items-center justify-center text-sm text-gray-400 dark:text-surface-500">No data yet — run a scrape</div>
            ) : (
              <div className="h-52 sm:h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={timeline.timeline}>
                    <CartesianGrid strokeDasharray="3 3" stroke={gridColor} />
                    <XAxis dataKey="date" tick={{ fontSize: 10, fill: tickColor }} tickFormatter={d => d.slice(5)} />
                    <YAxis tick={{ fontSize: 10, fill: tickColor }} />
                    <Tooltip contentStyle={{ fontSize: 12, borderRadius: 8, background: dark ? '#1e293b' : '#fff', border: `1px solid ${dark ? '#334155' : '#e2e8f0'}`, color: dark ? '#e2e8f0' : '#1e293b' }} />
                    <Line type="monotone" dataKey="jobs" stroke={chartColor} strokeWidth={2} dot={false} />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            )}
          </div>
        )}

        {portalsLoading ? <Skeleton.Chart /> : (
          <div className="bg-white dark:bg-surface-800 rounded-xl border border-gray-200 dark:border-surface-700 p-4 sm:p-5">
            <h2 className="text-sm font-semibold text-gray-700 dark:text-surface-200 mb-4">Jobs by Portal</h2>
            {(portals?.portals || []).length === 0 ? (
              <div className="h-64 flex items-center justify-center text-sm text-gray-400 dark:text-surface-500">No portal data yet</div>
            ) : (
              <div className="h-52 sm:h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={portals.portals} layout="vertical">
                    <CartesianGrid strokeDasharray="3 3" stroke={gridColor} />
                    <XAxis type="number" tick={{ fontSize: 10, fill: tickColor }} />
                    <YAxis dataKey="portal" type="category" tick={{ fontSize: 10, fill: tickColor }} width={80} tickFormatter={capitalize} />
                    <Tooltip contentStyle={{ fontSize: 12, borderRadius: 8, background: dark ? '#1e293b' : '#fff', border: `1px solid ${dark ? '#334155' : '#e2e8f0'}`, color: dark ? '#e2e8f0' : '#1e293b' }} />
                    <Bar dataKey="total_jobs" radius={[0, 4, 4, 0]}>
                      {(portals.portals || []).map((entry, i) => (
                        <Cell key={i} fill={getPortalColor(entry.portal)} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Pipeline + Activity */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 sm:gap-6">
        <div className="bg-white dark:bg-surface-800 rounded-xl border border-gray-200 dark:border-surface-700 p-4 sm:p-5">
          <h2 className="text-sm font-semibold text-gray-700 dark:text-surface-200 mb-4">Application Pipeline</h2>
          <div className="space-y-3">
            {pipeline && Object.entries(pipeline.pipeline || {}).map(([status, count]) => (
              <div key={status} className="flex items-center justify-between">
                <StatusBadge status={status} />
                <div className="flex-1 mx-3">
                  <div className="h-2 bg-gray-100 dark:bg-surface-700 rounded-full overflow-hidden">
                    <div className="h-full bg-brand-500 rounded-full"
                      style={{ width: `${Math.min(100, (count / Math.max(1, stats?.total_applied || 1)) * 100)}%` }} />
                  </div>
                </div>
                <span className="text-sm font-semibold text-gray-700 dark:text-surface-200 w-8 text-right">{count}</span>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-white dark:bg-surface-800 rounded-xl border border-gray-200 dark:border-surface-700 p-4 sm:p-5">
          <h2 className="text-sm font-semibold text-gray-700 dark:text-surface-200 mb-4">Recent Activity</h2>
          <div className="space-y-3">
            {(activity?.activity || []).map((item, i) => (
              <div key={i} className="flex items-start gap-3 pb-3 border-b border-gray-50 dark:border-surface-700 last:border-0">
                <span className="text-lg" aria-hidden="true">{item.type === 'job_found' ? '🔍' : '📤'}</span>
                <div className="flex-1 min-w-0">
                  <p className="text-sm text-gray-800 dark:text-surface-200 font-medium truncate">{item.title} — {item.company}</p>
                  <p className="text-xs text-gray-400 dark:text-surface-500">
                    {item.type === 'job_found' ? `${capitalize(item.portal)} • Score: ${item.score ?? '?'}` : capitalize(item.status)}
                  </p>
                </div>
                <span className="text-xs text-gray-400 dark:text-surface-500 shrink-0">{timeAgo(item.timestamp)}</span>
              </div>
            ))}
            {(!activity?.activity || activity.activity.length === 0) && (
              <p className="text-sm text-gray-400 dark:text-surface-500 text-center py-4">No recent activity</p>
            )}
          </div>
        </div>
      </div>

      {/* Skill Demand + Salary Insights */}
      {salaryData && (salaryData.top_skills?.length > 0 || salaryData.salary_jobs?.length > 0) && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 sm:gap-6 mt-4 sm:mt-6">
          {/* Top Skills Demand */}
          {salaryData.top_skills?.length > 0 && (
            <div className="bg-white dark:bg-surface-800 rounded-xl border border-gray-200 dark:border-surface-700 p-4 sm:p-5">
              <h2 className="text-sm font-semibold text-gray-700 dark:text-surface-200 mb-4">Most Demanded Skills</h2>
              <div className="space-y-2">
                {salaryData.top_skills.map((s, i) => {
                  const max = salaryData.top_skills[0]?.count || 1
                  return (
                    <div key={s.skill} className="flex items-center gap-3">
                      <span className="text-xs text-gray-500 dark:text-surface-400 w-6 text-right">{i + 1}</span>
                      <div className="flex-1">
                        <div className="flex items-center justify-between mb-0.5">
                          <span className="text-xs font-medium text-gray-700 dark:text-surface-200">{s.skill}</span>
                          <span className="text-xs text-gray-400 dark:text-surface-500">{s.count} jobs</span>
                        </div>
                        <div className="h-1.5 bg-gray-100 dark:bg-surface-700 rounded-full overflow-hidden">
                          <div className="h-full bg-brand-500 rounded-full" style={{ width: `${(s.count / max) * 100}%` }} />
                        </div>
                      </div>
                    </div>
                  )
                })}
              </div>
            </div>
          )}

          {/* Salary Data */}
          {salaryData.salary_jobs?.length > 0 && (
            <div className="bg-white dark:bg-surface-800 rounded-xl border border-gray-200 dark:border-surface-700 p-4 sm:p-5">
              <h2 className="text-sm font-semibold text-gray-700 dark:text-surface-200 mb-4">
                Salary Data <span className="text-xs text-gray-400 dark:text-surface-500 font-normal">({salaryData.jobs_with_salary} jobs)</span>
              </h2>
              <div className="space-y-2 max-h-64 overflow-y-auto">
                {salaryData.salary_jobs.map((j, i) => (
                  <div key={i} className="flex items-center justify-between py-1.5 border-b border-gray-50 dark:border-surface-700 last:border-0">
                    <div className="min-w-0 flex-1">
                      <p className="text-xs font-medium text-gray-700 dark:text-surface-200 truncate">{j.title}</p>
                      <p className="text-xs text-gray-400 dark:text-surface-500">{j.company}</p>
                    </div>
                    <span className="text-xs font-semibold text-emerald-600 dark:text-emerald-400 shrink-0 ml-2">{j.salary}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
