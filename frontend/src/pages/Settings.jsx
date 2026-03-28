/**
 * JOBPILOT — Settings Page
 * Responsive with skeletons and toasts.
 */

import { useState, useEffect } from 'react'
import { Save, CheckCircle, XCircle, Clock, Zap, FileText, User } from 'lucide-react'
import MarkdownEditor from '../components/MarkdownEditor'
import Skeleton from '../components/Skeleton'
import api from '../api/client'
import { useApi, useApiMutation } from '../hooks/useApi'
import { useToast } from '../hooks/useToast'
import { capitalize } from '../utils/helpers'

export default function Settings() {
  const toast = useToast()
  const { data: profile, loading: profileLoading } = useApi(() => api.settings.getProfile())
  const { data: scheduler } = useApi(() => api.settings.getScheduler())
  const { data: portals } = useApi(() => api.settings.getPortals())
  const { data: health } = useApi(() => api.settings.health())
  const { data: rulesData } = useApi(() => api.settings.getRules())
  const { data: profileMdData } = useApi(() => api.settings.getProfileMd())
  const { execute, loading: saving } = useApiMutation()
  const [saved, setSaved] = useState(false)

  const [formData, setFormData] = useState(null)
  const [rulesContent, setRulesContent] = useState('')
  const [profileMdContent, setProfileMdContent] = useState('')

  useEffect(() => {
    if (rulesData?.content != null) setRulesContent(rulesData.content)
  }, [rulesData])

  useEffect(() => {
    if (profileMdData?.content != null) setProfileMdContent(profileMdData.content)
  }, [profileMdData])

  if (profile && !formData) {
    setFormData({ ...profile })
  }

  const handleChange = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }))
  }

  const handleSave = async () => {
    try {
      await execute(() => api.settings.updateProfile(formData))
      setSaved(true)
      setTimeout(() => setSaved(false), 2000)
      toast.success('Profile saved')
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Save failed')
    }
  }

  const handleSaveRules = async () => {
    try {
      await api.settings.updateRules(rulesContent)
      toast.success('AI rules saved')
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Save failed')
    }
  }

  const handleSaveProfileMd = async () => {
    try {
      await api.settings.updateProfileMd(profileMdContent)
      toast.success('Candidate profile saved')
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Save failed')
    }
  }

  if (profileLoading) {
    return (
      <div>
        <div className="mb-6">
          <Skeleton className="h-7 w-32 mb-2" />
          <Skeleton className="h-4 w-64" />
        </div>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <Skeleton.Settings />
          <Skeleton.Settings />
        </div>
      </div>
    )
  }

  return (
    <div>
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-4 sm:mb-6">
        <div>
          <h1 className="text-xl sm:text-2xl font-bold text-gray-900 dark:text-white">Settings</h1>
          <p className="text-sm text-gray-500 dark:text-surface-400 mt-1">Profile, scheduler, and portal configuration</p>
        </div>
        <button onClick={handleSave} disabled={saving}
          className="flex items-center justify-center gap-2 px-4 py-2 bg-brand-600 text-white text-sm font-medium rounded-lg hover:bg-brand-700 disabled:opacity-50 w-full sm:w-auto"
          aria-label="Save profile changes">
          {saved ? <CheckCircle className="w-4 h-4" /> : <Save className="w-4 h-4" />}
          {saved ? 'Saved!' : saving ? 'Saving...' : 'Save Changes'}
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 sm:gap-6">
        {/* Profile Section */}
        <div className="bg-white dark:bg-surface-800 rounded-xl border border-gray-200 dark:border-surface-700 p-4 sm:p-6">
          <h2 className="text-base sm:text-lg font-semibold text-gray-900 dark:text-white mb-4">Profile</h2>
          <div className="space-y-3 sm:space-y-4">
            {[
              { label: 'Full Name', field: 'full_name' },
              { label: 'Email', field: 'email' },
              { label: 'Phone', field: 'phone' },
              { label: 'Current Role', field: 'current_role' },
              { label: 'Current Company', field: 'current_company' },
              { label: 'Experience (years)', field: 'total_experience_years', type: 'number' },
            ].map(({ label, field, type }) => (
              <div key={field}>
                <label htmlFor={`settings-${field}`} className="block text-xs font-medium text-gray-500 dark:text-surface-400 mb-1">{label}</label>
                <input id={`settings-${field}`} type={type || 'text'}
                  value={formData?.[field] ?? ''}
                  onChange={e => handleChange(field, type === 'number' ? parseFloat(e.target.value) : e.target.value)}
                  className="w-full px-3 py-2 bg-gray-50 dark:bg-surface-700 border border-gray-200 dark:border-surface-700 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-brand-500" />
              </div>
            ))}
          </div>
        </div>

        {/* Job Preferences */}
        <div className="bg-white dark:bg-surface-800 rounded-xl border border-gray-200 dark:border-surface-700 p-4 sm:p-6">
          <h2 className="text-base sm:text-lg font-semibold text-gray-900 dark:text-white mb-4">Job Preferences</h2>
          <div className="space-y-3 sm:space-y-4">
            <div>
              <label htmlFor="target-roles" className="block text-xs font-medium text-gray-500 dark:text-surface-400 mb-1">Target Roles (comma-separated)</label>
              <input id="target-roles" type="text" value={(formData?.target_roles || []).join(', ')}
                onChange={e => handleChange('target_roles', e.target.value.split(',').map(s => s.trim()))}
                className="w-full px-3 py-2 bg-gray-50 dark:bg-surface-700 border border-gray-200 dark:border-surface-700 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-brand-500" />
            </div>
            <div>
              <label htmlFor="target-locations" className="block text-xs font-medium text-gray-500 dark:text-surface-400 mb-1">Target Locations (comma-separated)</label>
              <input id="target-locations" type="text" value={(formData?.target_locations || []).join(', ')}
                onChange={e => handleChange('target_locations', e.target.value.split(',').map(s => s.trim()))}
                className="w-full px-3 py-2 bg-gray-50 dark:bg-surface-700 border border-gray-200 dark:border-surface-700 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-brand-500" />
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label htmlFor="exp-min" className="block text-xs font-medium text-gray-500 dark:text-surface-400 mb-1">Min Experience (years)</label>
                <input id="exp-min" type="number" step="0.5" min="0" value={formData?.target_experience_min ?? 0}
                  onChange={e => handleChange('target_experience_min', parseFloat(e.target.value))}
                  className="w-full px-3 py-2 bg-gray-50 dark:bg-surface-700 border border-gray-200 dark:border-surface-700 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-brand-500" />
              </div>
              <div>
                <label htmlFor="exp-max" className="block text-xs font-medium text-gray-500 dark:text-surface-400 mb-1">Max Experience (years)</label>
                <input id="exp-max" type="number" step="0.5" min="0" value={formData?.target_experience_max ?? 5}
                  onChange={e => handleChange('target_experience_max', parseFloat(e.target.value))}
                  className="w-full px-3 py-2 bg-gray-50 dark:bg-surface-700 border border-gray-200 dark:border-surface-700 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-brand-500" />
              </div>
            </div>
            <div>
              <label htmlFor="primary-skills" className="block text-xs font-medium text-gray-500 dark:text-surface-400 mb-1">Primary Skills (comma-separated)</label>
              <input id="primary-skills" type="text" value={(formData?.primary_skills || []).join(', ')}
                onChange={e => handleChange('primary_skills', e.target.value.split(',').map(s => s.trim()))}
                className="w-full px-3 py-2 bg-gray-50 dark:bg-surface-700 border border-gray-200 dark:border-surface-700 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-brand-500" />
            </div>
            <div>
              <label htmlFor="scrape-interval" className="block text-xs font-medium text-gray-500 dark:text-surface-400 mb-1">Scrape Interval (hours)</label>
              <input id="scrape-interval" type="number" min="1" max="48" value={formData?.scrape_interval_hours ?? 6}
                onChange={e => handleChange('scrape_interval_hours', parseInt(e.target.value))}
                className="w-full px-3 py-2 bg-gray-50 dark:bg-surface-700 border border-gray-200 dark:border-surface-700 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-brand-500" />
            </div>
            <div>
              <label htmlFor="min-score" className="block text-xs font-medium text-gray-500 dark:text-surface-400 mb-1">Min Match Score for Auto-Apply</label>
              <input id="min-score" type="number" min="0" max="100" value={formData?.min_match_score ?? 70}
                onChange={e => handleChange('min_match_score', parseInt(e.target.value))}
                className="w-full px-3 py-2 bg-gray-50 dark:bg-surface-700 border border-gray-200 dark:border-surface-700 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-brand-500" />
            </div>
            <div className="flex items-center justify-between p-3 bg-gray-50 dark:bg-surface-700 rounded-lg">
              <div>
                <p className="text-sm font-medium text-gray-700 dark:text-surface-200">Auto-Apply</p>
                <p className="text-xs text-gray-500 dark:text-surface-400">Automatically apply to high-match jobs</p>
              </div>
              <button onClick={() => handleChange('auto_apply_enabled', !formData?.auto_apply_enabled)}
                role="switch"
                aria-checked={!!formData?.auto_apply_enabled}
                aria-label="Toggle auto-apply"
                className={`w-12 h-6 rounded-full relative ${formData?.auto_apply_enabled ? 'bg-brand-600' : 'bg-gray-300 dark:bg-surface-600'}`}>
                <div className={`w-5 h-5 bg-white rounded-full shadow absolute top-0.5 ${formData?.auto_apply_enabled ? 'right-0.5' : 'left-0.5'}`} />
              </button>
            </div>
            <div>
              <label htmlFor="apply-mode" className="block text-xs font-medium text-gray-500 dark:text-surface-400 mb-1">Apply Mode</label>
              <select id="apply-mode" value={formData?.auto_apply_mode || 'semi'}
                onChange={e => handleChange('auto_apply_mode', e.target.value)}
                className="w-full px-3 py-2 bg-gray-50 dark:bg-surface-700 border border-gray-200 dark:border-surface-700 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-brand-500">
                <option value="semi">Semi-auto (review before applying)</option>
                <option value="auto">Full-auto (apply without review)</option>
              </select>
            </div>
          </div>
        </div>

        {/* Scheduler Status */}
        <div className="bg-white dark:bg-surface-800 rounded-xl border border-gray-200 dark:border-surface-700 p-4 sm:p-6">
          <h2 className="text-base sm:text-lg font-semibold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
            <Clock className="w-5 h-5 text-brand-500" /> Scheduler
          </h2>
          <div className="flex items-center gap-2 mb-4">
            <div className={`w-2.5 h-2.5 rounded-full ${scheduler?.running ? 'bg-emerald-500' : 'bg-red-500'}`}
              aria-hidden="true" />
            <span className="text-sm font-medium text-gray-700 dark:text-surface-200">
              {scheduler?.running ? 'Running' : 'Stopped'}
            </span>
          </div>
          {scheduler?.jobs?.length > 0 && (
            <div className="space-y-2">
              {scheduler.jobs.map(job => (
                <div key={job.id} className="flex items-center justify-between p-3 bg-gray-50 dark:bg-surface-700 rounded-lg">
                  <div className="min-w-0">
                    <p className="text-sm font-medium text-gray-700 dark:text-surface-200 truncate">{job.name}</p>
                    <p className="text-xs text-gray-500 dark:text-surface-400">Next: {job.next_run || 'N/A'}</p>
                  </div>
                  <Zap className="w-4 h-4 text-amber-500 shrink-0" />
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Portal Connections */}
        <div className="bg-white dark:bg-surface-800 rounded-xl border border-gray-200 dark:border-surface-700 p-4 sm:p-6">
          <h2 className="text-base sm:text-lg font-semibold text-gray-900 dark:text-white mb-4">Portal Connections</h2>
          <div className="space-y-2 sm:space-y-3">
            {portals && Object.entries(portals.portals || {}).map(([key, portal]) => (
              <div key={key} className="flex items-center justify-between p-3 bg-gray-50 dark:bg-surface-700 rounded-lg gap-3">
                <div className="flex items-center gap-3 min-w-0">
                  {portal.configured
                    ? <CheckCircle className="w-5 h-5 text-emerald-500 shrink-0" />
                    : <XCircle className="w-5 h-5 text-gray-300 shrink-0" />
                  }
                  <div className="min-w-0">
                    <p className="text-sm font-medium text-gray-700 dark:text-surface-200">{portal.name}</p>
                    <p className="text-xs text-gray-500 dark:text-surface-400 truncate">{portal.features?.join(', ')}</p>
                  </div>
                </div>
                <span className={`text-xs font-medium px-2 py-0.5 rounded-full whitespace-nowrap ${
                  portal.configured ? 'bg-emerald-50 dark:bg-emerald-950/30 text-emerald-700 dark:text-emerald-300' : 'bg-gray-100 dark:bg-surface-700 text-gray-500 dark:text-surface-400'
                }`}>
                  {portal.configured ? 'Connected' : 'Not set'}
                </span>
              </div>
            ))}
          </div>
          <p className="text-xs text-gray-400 dark:text-surface-500 mt-4">
            Configure portal credentials in your .env file.
          </p>
        </div>
      </div>

      {/* Rules & Profile Markdown Editors */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 sm:gap-6 mt-4 sm:mt-6">
        <MarkdownEditor
          value={rulesContent}
          onChange={setRulesContent}
          onSave={handleSaveRules}
          label="AI Rules"
          icon={FileText}
          description="Sent to AI when tailoring resumes and generating cover letters."
          placeholder="# Resume Rules&#10;- Must be 1 page&#10;- No fabricated skills&#10;..."
        />
        <MarkdownEditor
          value={profileMdContent}
          onChange={setProfileMdContent}
          onSave={handleSaveProfileMd}
          label="Candidate Profile"
          icon={User}
          description="AI uses this to keep resumes truthful and realistic."
          placeholder="# Personal Info&#10;- Name: ...&#10;- Skills: ...&#10;..."
        />
      </div>

      {/* Health info */}
      {health && (
        <div className="mt-4 sm:mt-6 p-3 sm:p-4 bg-gray-50 dark:bg-surface-700 rounded-xl border border-gray-200 dark:border-surface-700">
          <p className="text-xs text-gray-500 dark:text-surface-400">
            API: <span className="text-emerald-600 dark:text-emerald-400 font-medium">{health.status}</span> •
            AI Requests: {health.ai_tokens_used?.total_requests || 0} •
            Telegram: {health.telegram_configured ? '✅' : '❌'}
          </p>
        </div>
      )}
    </div>
  )
}
