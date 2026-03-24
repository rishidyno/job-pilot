/**
 * JOBPILOT — Sidebar Navigation
 */

import { NavLink } from 'react-router-dom'
import { LayoutDashboard, Briefcase, Send, FileText, Settings, Rocket } from 'lucide-react'
import clsx from 'clsx'

const NAV_ITEMS = [
  { path: '/', label: 'Dashboard', icon: LayoutDashboard },
  { path: '/jobs', label: 'Jobs', icon: Briefcase },
  { path: '/applications', label: 'Applications', icon: Send },
  { path: '/resumes', label: 'Resumes', icon: FileText },
  { path: '/settings', label: 'Settings', icon: Settings },
]

export default function Sidebar() {
  return (
    <aside className="w-64 bg-white border-r border-gray-200 flex flex-col shrink-0">
      {/* Logo */}
      <div className="h-16 flex items-center gap-2.5 px-6 border-b border-gray-100">
        <Rocket className="w-6 h-6 text-brand-600" />
        <span className="text-lg font-bold tracking-tight text-gray-900">
          Job<span className="text-brand-600">Pilot</span>
        </span>
      </div>

      {/* Navigation links */}
      <nav className="flex-1 px-3 py-4 space-y-1">
        {NAV_ITEMS.map(({ path, label, icon: Icon }) => (
          <NavLink
            key={path}
            to={path}
            end={path === '/'}
            className={({ isActive }) =>
              clsx(
                'flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors',
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
      <div className="px-6 py-4 border-t border-gray-100">
        <p className="text-xs text-gray-400">JobPilot v1.0.0</p>
        <p className="text-xs text-gray-400">Built by Rishi Raj</p>
      </div>
    </aside>
  )
}
