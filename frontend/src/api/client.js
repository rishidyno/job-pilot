/**
 * ╔═══════════════════════════════════════════════════════════════════╗
 * ║  JOBPILOT — API Client                                          ║
 * ║                                                                   ║
 * ║  Centralized Axios client for all backend API calls.             ║
 * ║  All API calls go through this module so we have:                ║
 * ║  - Single place for base URL configuration                      ║
 * ║  - Consistent error handling                                    ║
 * ║  - Request/response interceptors (logging, auth, etc.)          ║
 * ║                                                                   ║
 * ║  USAGE:                                                          ║
 * ║    import api from '../api/client'                               ║
 * ║    const { data } = await api.jobs.list({ status: 'new' })      ║
 * ╚═══════════════════════════════════════════════════════════════════╝
 */

import axios from 'axios'

// Base Axios instance — all requests go through this
const http = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '',
  timeout: 30000, // 30 second timeout
  headers: { 'Content-Type': 'application/json' },
})

// ── Request interceptor — attach JWT token ──
http.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

// ── Response interceptor for consistent error handling ──
http.interceptors.response.use(
  (response) => response,
  (error) => {
    const message = error.response?.data?.detail || error.message || 'Unknown error'
    console.error(`[API Error] ${error.config?.method?.toUpperCase()} ${error.config?.url}: ${message}`)
    // Redirect to login on 401/403
    if (error.response?.status === 401 || error.response?.status === 403) {
      localStorage.removeItem('token')
      if (window.location.pathname !== '/login') window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

/**
 * API methods grouped by resource.
 * Each method returns the Axios promise.
 */
const api = {
  // ── Auth ──
  auth: {
    login: (data) => http.post('/api/auth/login', data),
    register: (data) => http.post('/api/auth/register', data),
    me: () => http.get('/api/auth/me'),
  },

  // ── Dashboard ──
  dashboard: {
    getStats: () => http.get('/api/dashboard/stats'),
    getPipeline: () => http.get('/api/dashboard/pipeline'),
    getPortals: () => http.get('/api/dashboard/portals'),
    getTimeline: () => http.get('/api/dashboard/timeline'),
    getRecentActivity: () => http.get('/api/dashboard/recent-activity'),
  },

  // ── Jobs ──
  jobs: {
    list: (params = {}) => http.get('/api/jobs', { params }),
    get: (id) => http.get(`/api/jobs/${id}`),
    update: (id, data) => http.patch(`/api/jobs/${id}`, data),
    delete: (id) => http.delete(`/api/jobs/${id}`),
    triggerScrape: (portals = null) => http.post('/api/jobs/scrape', null, portals ? {
      params: { portals },
      paramsSerializer: { indexes: null },
    } : {}),
    scrapeStatus: () => http.get('/api/jobs/scrape/status'),
    scrapeStop: () => http.post('/api/jobs/scrape/stop'),
    score: (id) => http.post(`/api/jobs/${id}/score`, null, { timeout: 120000 }),
  },

  // ── Applications ──
  applications: {
    list: (params = {}) => http.get('/api/applications', { params }),
    get: (id) => http.get(`/api/applications/${id}`),
    create: (jobId, force = false) => http.post('/api/applications', null, { params: { job_id: jobId, force } }),
    update: (id, data) => http.patch(`/api/applications/${id}`, null, { params: data }),
    retry: (id) => http.post(`/api/applications/${id}/retry`),
  },

  // ── Resumes ──
  resumes: {
    list: (params = {}) => http.get('/api/resumes', { params }),
    get: (id) => http.get(`/api/resumes/${id}`),
    uploadBase: (file) => {
      const formData = new FormData()
      formData.append('file', file)
      return http.post('/api/resumes/upload-base', formData, { timeout: 120000 })
    },
    tailor: (jobId) => http.post('/api/resumes/tailor', null, { params: { job_id: jobId }, timeout: 120000 }),
    generateCoverLetter: (jobId, tone = 'professional') =>
      http.post('/api/resumes/cover-letter', null, { params: { job_id: jobId, tone } }),
    download: (id, style = 'original') => `/api/resumes/download/${id}?style=${style}`,
  },

  // ── Settings ──
  settings: {
    getProfile: () => http.get('/api/settings/profile'),
    updateProfile: (data) => http.put('/api/settings/profile', data),
    getScheduler: () => http.get('/api/settings/scheduler'),
    getPortals: () => http.get('/api/settings/portals'),
    health: () => http.get('/api/settings/health'),
    getRules: () => http.get('/api/settings/rules'),
    updateRules: (content) => http.put('/api/settings/rules', { content }),
    getProfileMd: () => http.get('/api/settings/profile-md'),
    updateProfileMd: (content) => http.put('/api/settings/profile-md', { content }),
  },
}

export default api
