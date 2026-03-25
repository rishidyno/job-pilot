/**
 * Login / Register page — responsive, accessible.
 */
import { useState } from 'react'
import { useAuth } from '../hooks/useAuth'
import { useToast } from '../hooks/useToast'
import { Rocket } from 'lucide-react'

export default function Login() {
  const { login, register } = useAuth()
  const toast = useToast()
  const [isRegister, setIsRegister] = useState(false)
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [fullName, setFullName] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      if (isRegister) {
        await register(email, password, fullName)
        toast.success('Account created!')
      } else {
        await login(email, password)
      }
    } catch (err) {
      const msg = err.response?.data?.detail || 'Something went wrong'
      setError(msg)
      toast.error(msg)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-surface-950 px-4">
      <div className="w-full max-w-sm">
        <div className="flex items-center justify-center gap-2 mb-8">
          <Rocket className="w-8 h-8 text-brand-600 dark:text-brand-400" />
          <span className="text-2xl font-bold text-gray-900 dark:text-white">
            Job<span className="text-brand-600 dark:text-brand-400">Pilot</span>
          </span>
        </div>

        <form onSubmit={handleSubmit} className="bg-white dark:bg-surface-800 rounded-xl shadow-sm border border-gray-200 dark:border-surface-700 p-5 sm:p-6 space-y-4">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white text-center">
            {isRegister ? 'Create Account' : 'Sign In'}
          </h2>

          {error && (
            <div className="bg-red-50 dark:bg-red-950/30 text-red-600 dark:text-red-400 text-sm rounded-lg px-3 py-2" role="alert">{error}</div>
          )}

          {isRegister && (
            <div>
              <label htmlFor="fullname" className="sr-only">Full Name</label>
              <input id="fullname" type="text" placeholder="Full Name" value={fullName}
                onChange={(e) => setFullName(e.target.value)} required autoComplete="name"
                className="w-full px-3 py-2.5 border border-gray-300 dark:border-surface-600 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-brand-500" />
            </div>
          )}

          <div>
            <label htmlFor="email" className="sr-only">Email</label>
            <input id="email" type="email" placeholder="Email" value={email}
              onChange={(e) => setEmail(e.target.value)} required autoComplete="email"
              className="w-full px-3 py-2.5 border border-gray-300 dark:border-surface-600 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-brand-500" />
          </div>

          <div>
            <label htmlFor="password" className="sr-only">Password</label>
            <input id="password" type="password" placeholder="Password" value={password}
              onChange={(e) => setPassword(e.target.value)} required minLength={6} autoComplete={isRegister ? 'new-password' : 'current-password'}
              className="w-full px-3 py-2.5 border border-gray-300 dark:border-surface-600 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-brand-500" />
          </div>

          <button type="submit" disabled={loading}
            className="w-full py-2.5 bg-brand-600 text-white rounded-lg text-sm font-medium hover:bg-brand-700 disabled:opacity-50">
            {loading ? 'Please wait...' : isRegister ? 'Register' : 'Sign In'}
          </button>

          <p className="text-center text-sm text-gray-500 dark:text-surface-400">
            {isRegister ? 'Already have an account?' : "Don't have an account?"}{' '}
            <button type="button"
              onClick={() => { setIsRegister(!isRegister); setError('') }}
              className="text-brand-600 dark:text-brand-400 font-medium hover:underline">
              {isRegister ? 'Sign In' : 'Register'}
            </button>
          </p>
        </form>
      </div>
    </div>
  )
}
