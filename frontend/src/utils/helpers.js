/**
 * JOBPILOT — Frontend Utility Helpers
 */

import { formatDistanceToNow } from 'date-fns'

/** Format a date as relative time (e.g., "2 hours ago") */
export function timeAgo(date) {
  if (!date) return '—'
  return formatDistanceToNow(new Date(date), { addSuffix: true })
}

/** Get color class for a match score */
export function scoreColor(score) {
  if (score >= 90) return 'text-emerald-600 dark:text-emerald-400 bg-emerald-50 dark:bg-emerald-950/40'
  if (score >= 75) return 'text-brand-600 dark:text-brand-400 bg-brand-50 dark:bg-brand-950/40'
  if (score >= 60) return 'text-amber-600 dark:text-amber-400 bg-amber-50 dark:bg-amber-950/40'
  if (score >= 40) return 'text-orange-600 dark:text-orange-400 bg-orange-50 dark:bg-orange-950/40'
  return 'text-red-600 dark:text-red-400 bg-red-50 dark:bg-red-950/40'
}

/** Get color for application status badge */
export function statusColor(status) {
  const colors = {
    new: 'bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-300',
    reviewed: 'bg-blue-50 text-blue-700 dark:bg-blue-950/40 dark:text-blue-300',
    shortlisted: 'bg-indigo-50 text-indigo-700 dark:bg-indigo-950/40 dark:text-indigo-300',
    applied: 'bg-emerald-50 text-emerald-700 dark:bg-emerald-950/40 dark:text-emerald-300',
    submitted: 'bg-emerald-50 text-emerald-700 dark:bg-emerald-950/40 dark:text-emerald-300',
    pending: 'bg-amber-50 text-amber-700 dark:bg-amber-950/40 dark:text-amber-300',
    interviewing: 'bg-purple-50 text-purple-700 dark:bg-purple-950/40 dark:text-purple-300',
    interview: 'bg-purple-50 text-purple-700 dark:bg-purple-950/40 dark:text-purple-300',
    offered: 'bg-green-50 text-green-700 dark:bg-green-950/40 dark:text-green-300',
    accepted: 'bg-green-100 text-green-800 dark:bg-green-900/40 dark:text-green-300',
    rejected: 'bg-red-50 text-red-700 dark:bg-red-950/40 dark:text-red-300',
    failed: 'bg-red-50 text-red-700 dark:bg-red-950/40 dark:text-red-300',
    skipped: 'bg-gray-100 text-gray-500 dark:bg-surface-700 dark:text-surface-400',
    expired: 'bg-gray-100 text-gray-500 dark:bg-surface-700 dark:text-surface-400',
    withdrawn: 'bg-gray-100 text-gray-500 dark:bg-surface-700 dark:text-surface-400',
  }
  return colors[status] || 'bg-gray-100 text-gray-600 dark:bg-surface-700 dark:text-surface-400'
}

/** Portal display info */
const PORTALS = {
  linkedin: { label: 'LinkedIn', color: 'text-blue-600 dark:text-blue-400' },
  naukri: { label: 'Naukri', color: 'text-sky-500 dark:text-sky-400' },
  indeed: { label: 'Indeed', color: 'text-purple-600 dark:text-purple-400' },
  glassdoor: { label: 'Glassdoor', color: 'text-green-600 dark:text-green-400' },
  google: { label: 'Google', color: 'text-orange-500 dark:text-orange-400' },
}

/** Get portal display label */
export function portalLabel(portal) {
  return PORTALS[portal]?.label || capitalize(portal)
}

/** Get portal color class */
export function portalColor(portal) {
  return PORTALS[portal]?.color || 'text-gray-500 dark:text-surface-400'
}

/** Get portal icon — short text badge instead of emoji for cross-platform consistency */
export function portalIcon(portal) {
  return PORTALS[portal]?.label?.[0] || '?'
}

/** Capitalize first letter */
export function capitalize(str) {
  return str ? str.charAt(0).toUpperCase() + str.slice(1) : ''
}

/** Truncate text */
export function truncate(text, maxLen = 150) {
  if (!text || text.length <= maxLen) return text || ''
  return text.slice(0, maxLen) + '…'
}

/** Format number with K/M suffix */
export function formatCount(n) {
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`
  if (n >= 1_000) return `${(n / 1_000).toFixed(1)}K`
  return String(n ?? 0)
}
