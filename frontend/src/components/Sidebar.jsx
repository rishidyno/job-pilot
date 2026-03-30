/**
 * JOBPILOT — Sidebar Navigation
 * With dark mode toggle.
 */

import { NavLink } from 'react-router-dom'
import { LayoutDashboard, Briefcase, Send, FileText, Settings, Rocket, LogOut, X, Palette } from 'lucide-react'
import { useAuth } from '../hooks/useAuth'
import { useTheme } from '../hooks/useTheme'
import clsx from 'clsx'
import { useState } from 'react'

const NAV_ITEMS = [
  { path: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { path: '/jobs', label: 'Jobs', icon: Briefcase },
  { path: '/applications', label: 'Applications', icon: Send },
  { path: '/resumes', label: 'Resumes', icon: FileText },
  { path: '/settings', label: 'Settings', icon: Settings },
]

export default function Sidebar({ onClose }) {
  const { user, logout } = useAuth()
  const { theme, themeId, setTheme, themes } = useTheme()
  const [showThemes, setShowThemes] = useState(false)

  return (
    <aside className="w-64 h-full bg-white dark:bg-surface-900 border-r border-gray-200 dark:border-surface-700 flex flex-col shrink-0">
      {/* Logo */}
      <div className="h-16 flex items-center justify-between px-6 border-b border-gray-100 dark:border-surface-800">
        <div className="flex items-center gap-2.5">
          <Rocket className="w-6 h-6 text-brand-600 dark:text-brand-400" />
          <span className="text-lg font-bold tracking-tight text-gray-900 dark:text-white">
            Job<span className="text-brand-600 dark:text-brand-400">Pilot</span>
          </span>
        </div>
        {onClose && (
          <button onClick={onClose}
            className="p-1.5 rounded-lg hover:bg-gray-100 dark:hover:bg-surface-800 lg:hidden"
            aria-label="Close navigation menu">
            <X className="w-5 h-5 text-gray-500 dark:text-surface-400" />
          </button>
        )}
      </div>

      {/* Nav */}
      <nav className="flex-1 px-3 py-4 space-y-1">
        {NAV_ITEMS.map(({ path, label, icon: Icon }) => (
          <NavLink key={path} to={path} end={path === '/dashboard'} onClick={onClose}
            className={({ isActive }) =>
              clsx(
                'flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium',
                isActive
                  ? 'bg-brand-50 dark:bg-brand-950/40 text-brand-700 dark:text-brand-300'
                  : 'text-gray-600 dark:text-surface-400 hover:bg-gray-50 dark:hover:bg-surface-800 hover:text-gray-900 dark:hover:text-white'
              )
            }>
            <Icon className="w-5 h-5" />
            {label}
          </NavLink>
        ))}
      </nav>

      {/* Footer */}
      <div className="px-4 py-4 border-t border-gray-100 dark:border-surface-800 space-y-3">
        {/* Theme picker */}
        <div className="relative">
          <button onClick={() => setShowThemes(s => !s)}
            className="flex items-center gap-3 w-full px-3 py-2 rounded-lg text-sm text-gray-600 dark:text-surface-400 hover:bg-gray-50 dark:hover:bg-surface-800"
            aria-label="Change theme">
            <Palette className="w-4 h-4" />
            <span className="flex-1 text-left">{theme.icon} {theme.label}</span>
          </button>
          {showThemes && (
            <div className="absolute bottom-full left-0 right-0 mb-1 bg-white dark:bg-surface-800 border border-gray-200 dark:border-surface-700 rounded-xl shadow-xl overflow-hidden z-50">
              {themes.map(t => (
                <button key={t.id} onClick={() => { setTheme(t.id); setShowThemes(false) }}
                  className={`w-full flex items-center gap-3 px-3 py-2.5 text-left text-sm hover:bg-gray-50 dark:hover:bg-surface-700 ${
                    t.id === themeId ? 'bg-brand-50 dark:bg-brand-950/30' : ''
                  }`}>
                  <span className="text-base">{t.icon}</span>
                  <div className="flex-1 min-w-0">
                    <p className={`text-xs font-medium ${t.id === themeId ? 'text-brand-700 dark:text-brand-300' : 'text-gray-700 dark:text-surface-200'}`}>{t.label}</p>
                    <p className="text-xs text-gray-400 dark:text-surface-500">{t.description}</p>
                  </div>
                  {t.id === themeId && <span className="text-brand-600 dark:text-brand-400 text-xs">✓</span>}
                </button>
              ))}
            </div>
          )}
        </div>

        {user && (
          <div className="flex items-center justify-between">
            <span className="text-xs text-gray-600 dark:text-surface-400 truncate max-w-[160px]">{user.full_name}</span>
            <button onClick={logout}
              className="p-1.5 rounded-md text-gray-400 hover:text-red-500 hover:bg-red-50 dark:hover:bg-red-950/30"
              title="Logout" aria-label="Logout">
              <LogOut className="w-4 h-4" />
            </button>
          </div>
        )}
      </div>
    </aside>
  )
}
