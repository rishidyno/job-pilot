/**
 * JOBPILOT — Layout Component
 * Responsive with dark mode support.
 */

import { useState } from 'react'
import { Menu } from 'lucide-react'
import Sidebar from './Sidebar'

export default function Layout({ children }) {
  const [sidebarOpen, setSidebarOpen] = useState(false)

  return (
    <div className="flex h-screen overflow-hidden bg-gray-50 dark:bg-surface-950">
      {sidebarOpen && (
        <div className="fixed inset-0 bg-black/40 z-40 lg:hidden sidebar-overlay"
          onClick={() => setSidebarOpen(false)} aria-hidden="true" />
      )}

      <div className={`
        fixed inset-y-0 left-0 z-50 lg:static lg:z-auto
        ${sidebarOpen ? 'translate-x-0 sidebar-slide' : '-translate-x-full'}
        lg:translate-x-0
      `}>
        <Sidebar onClose={() => setSidebarOpen(false)} />
      </div>

      <main className="flex-1 overflow-y-auto min-w-0">
        <div className="sticky top-0 z-30 bg-white/80 dark:bg-surface-900/80 backdrop-blur-sm border-b border-gray-200 dark:border-surface-700 px-4 py-3 flex items-center gap-3 lg:hidden">
          <button onClick={() => setSidebarOpen(true)}
            className="p-2 -ml-2 rounded-lg hover:bg-gray-100 dark:hover:bg-surface-800"
            aria-label="Open navigation menu">
            <Menu className="w-5 h-5 text-gray-700 dark:text-surface-300" />
          </button>
          <span className="text-sm font-bold text-gray-900 dark:text-white">
            Job<span className="text-brand-600 dark:text-brand-400">Pilot</span>
          </span>
        </div>

        <div className="max-w-7xl mx-auto px-4 sm:px-6 py-6 sm:py-8">
          {children}
        </div>
      </main>
    </div>
  )
}
