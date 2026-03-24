/**
 * JOBPILOT — Layout Component
 * 
 * Main app shell: fixed sidebar on the left, scrollable content on the right.
 */

import Sidebar from './Sidebar'

export default function Layout({ children }) {
  return (
    <div className="flex h-screen overflow-hidden bg-gray-50">
      {/* Fixed sidebar */}
      <Sidebar />

      {/* Scrollable main content */}
      <main className="flex-1 overflow-y-auto">
        <div className="max-w-7xl mx-auto px-6 py-8">
          {children}
        </div>
      </main>
    </div>
  )
}
