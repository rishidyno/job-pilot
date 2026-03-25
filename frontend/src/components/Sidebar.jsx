/**
 * JOBPILOT — Sidebar Navigation
 * With dark mode toggle.
 */

import { NavLink } from 'react-router-dom'
import { LayoutDashboard, Briefcase, Send, FileText, Settings, Rocket, LogOut, X, Moon, Sun } from 'lucide-react'
import { useAuth } from '../hooks/useAuth'
import { useTheme } from '../hooks/useTheme'
import clsx from 'clsx'

const NAV_ITEMS = [
  { path: '/', label: 'Dashboard', icon: LayoutDashboard },
  { path: '/jobs', label: 'Jobs', icon: Briefcase },
  { path: '/applications', label: 'Applications', icon: Send },
  { path: '/resumes', label: 'Resumes', icon: FileText },
  { path: '/settings', label: 'Settings', icon: Settings },
]

export default function Sidebar({ onClose }) {
  const { user, logout } = useAuth()
  const { dark, toggle } = useTheme()

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
          <NavLink key={path} to={path} end={path === '/'} onClick={onClose}
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
        {/* Theme toggle */}
        <button onClick={toggle}
          className="flex items-center gap-3 w-full px-3 py-2 rounded-lg text-sm text-gray-600 dark:text-surface-400 hover:bg-gray-50 dark:hover:bg-surface-800"
          aria-label={dark ? 'Switch to light mode' : 'Switch to dark mode'}>
          {dark ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}
          {dark ? 'Light Mode' : 'Dark Mode'}
        </button>

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
