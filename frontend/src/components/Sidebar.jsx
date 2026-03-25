/**
 * JOBPILOT — Sidebar Navigation
 * Responsive: full sidebar on desktop, closeable drawer on mobile.
 */

import { NavLink } from 'react-router-dom'
import { LayoutDashboard, Briefcase, Send, FileText, Settings, Rocket, LogOut, X } from 'lucide-react'
import { useAuth } from '../hooks/useAuth'
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

  return (
    <aside className="w-64 h-full bg-white border-r border-gray-200 flex flex-col shrink-0">
      {/* Logo + mobile close */}
      <div className="h-16 flex items-center justify-between px-6 border-b border-gray-100">
        <div className="flex items-center gap-2.5">
          <Rocket className="w-6 h-6 text-brand-600" />
          <span className="text-lg font-bold tracking-tight text-gray-900">
            Job<span className="text-brand-600">Pilot</span>
          </span>
        </div>
        {onClose && (
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg hover:bg-gray-100 lg:hidden"
            aria-label="Close navigation menu"
          >
            <X className="w-5 h-5 text-gray-500" />
          </button>
        )}
      </div>

      {/* Navigation links */}
      <nav className="flex-1 px-3 py-4 space-y-1">
        {NAV_ITEMS.map(({ path, label, icon: Icon }) => (
          <NavLink
            key={path}
            to={path}
            end={path === '/'}
            onClick={onClose}
            className={({ isActive }) =>
              clsx(
                'flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium',
                isActive
                  ? 'bg-brand-50 text-brand-700'
                  : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
              )
            }
          >
            <Icon className="w-5 h-5" />
            {label}
          </NavLink>
        ))}
      </nav>

      {/* Footer */}
      <div className="px-4 py-4 border-t border-gray-100">
        {user && (
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs text-gray-600 truncate max-w-[160px]">{user.full_name}</span>
            <button
              onClick={logout}
              className="p-1.5 rounded-md text-gray-400 hover:text-red-500 hover:bg-red-50"
              title="Logout"
              aria-label="Logout"
            >
              <LogOut className="w-4 h-4" />
            </button>
          </div>
        )}
        <p className="text-xs text-gray-400">JobPilot v1.0.0</p>
      </div>
    </aside>
  )
}
