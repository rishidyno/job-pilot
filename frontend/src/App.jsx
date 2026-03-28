/**
 * JOBPILOT — Root Application Component
 *
 * Sets up client-side routing between all pages.
 * Wraps everything in the Layout (sidebar + content area).
 * Protects all routes behind authentication.
 */

import { Routes, Route, Navigate } from 'react-router-dom'
import { useAuth } from './hooks/useAuth'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import Jobs from './pages/Jobs'
import Applications from './pages/Applications'
import ResumeManager from './pages/ResumeManager'
import Settings from './pages/Settings'
import Login from './pages/Login'

function ProtectedRoutes() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/jobs" element={<Jobs />} />
        <Route path="/applications" element={<Applications />} />
        <Route path="/resumes" element={<ResumeManager />} />
        <Route path="/settings" element={<Settings />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Layout>
  )
}

export default function App() {
  const { user, loading } = useAuth()

  if (loading) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center bg-gray-50 dark:bg-surface-950 gap-3">
        <div className="w-8 h-8 border-3 border-brand-200 dark:border-brand-800 border-t-brand-600 dark:border-t-brand-400 rounded-full animate-spin" />
        <span className="text-sm text-gray-400 dark:text-surface-500">Loading JobPilot...</span>
      </div>
    )
  }

  return (
    <Routes>
      <Route path="/login" element={user ? <Navigate to="/" replace /> : <Login />} />
      <Route path="/*" element={user ? <ProtectedRoutes /> : <Navigate to="/login" replace />} />
    </Routes>
  )
}
