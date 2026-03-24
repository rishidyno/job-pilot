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
  if (score >= 90) return 'text-emerald-600 bg-emerald-50'
  if (score >= 75) return 'text-blue-600 bg-blue-50'
  if (score >= 60) return 'text-amber-600 bg-amber-50'
  if (score >= 40) return 'text-orange-600 bg-orange-50'
  return 'text-red-600 bg-red-50'
}

/** Get color for application status badge */
export function statusColor(status) {
  const colors = {
    new: 'bg-slate-100 text-slate-700',
    reviewed: 'bg-blue-50 text-blue-700',
    shortlisted: 'bg-indigo-50 text-indigo-700',
    applied: 'bg-emerald-50 text-emerald-700',
    submitted: 'bg-emerald-50 text-emerald-700',
    pending: 'bg-amber-50 text-amber-700',
    interviewing: 'bg-purple-50 text-purple-700',
    interview: 'bg-purple-50 text-purple-700',
    offered: 'bg-green-50 text-green-700',
    accepted: 'bg-green-100 text-green-800',
    rejected: 'bg-red-50 text-red-700',
    failed: 'bg-red-50 text-red-700',
    skipped: 'bg-gray-100 text-gray-500',
    expired: 'bg-gray-100 text-gray-500',
    withdrawn: 'bg-gray-100 text-gray-500',
  }
  return colors[status] || 'bg-gray-100 text-gray-600'
}

/** Get portal icon/emoji */
export function portalIcon(portal) {
  const icons = {
    linkedin: '🔗', naukri: '🇮🇳', wellfound: '🚀',
    instahyre: '📩', indeed: '🔍', glassdoor: '🪟',
  }
  return icons[portal] || '🌐'
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
