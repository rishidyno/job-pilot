/**
 * Login / Register — matches homepage dark animated style.
 */
import { useState, useEffect, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'
import { useToast } from '../hooks/useToast'
import { Rocket, Eye, EyeOff, Check, X, ArrowRight, ArrowLeft } from 'lucide-react'

function PasswordStrength({ password }) {
  const checks = [
    { label: '8+ chars', pass: password.length >= 8 },
    { label: 'Uppercase', pass: /[A-Z]/.test(password) },
    { label: 'Number', pass: /[0-9]/.test(password) },
  ]
  const score = checks.filter(c => c.pass).length
  const colors = ['bg-gray-700', 'bg-red-400', 'bg-amber-400', 'bg-emerald-400']
  if (!password) return null
  return (
    <div className="mt-2 space-y-2">
      <div className="flex gap-1">
        {[0, 1, 2].map(i => (
          <div key={i} className={`h-1 flex-1 rounded-full transition-colors duration-300 ${i < score ? colors[score] : 'bg-gray-800'}`} />
        ))}
      </div>
      <div className="flex flex-wrap gap-x-3 gap-y-1">
        {checks.map(c => (
          <span key={c.label} className={`flex items-center gap-1 text-xs transition-colors ${c.pass ? 'text-emerald-400' : 'text-gray-600'}`}>
            {c.pass ? <Check className="w-3 h-3" /> : <X className="w-3 h-3" />}{c.label}
          </span>
        ))}
      </div>
    </div>
  )
}

export default function Login() {
  const { login, register } = useAuth()
  const toast = useToast()
  const navigate = useNavigate()
  const [mode, setMode] = useState('login')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [fullName, setFullName] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [fieldErrors, setFieldErrors] = useState({})
  const [generalError, setGeneralError] = useState('')
  const [loading, setLoading] = useState(false)
  const [success, setSuccess] = useState(false)
  const emailRef = useRef(null)
  const nameRef = useRef(null)
  const isRegister = mode === 'register'

  useEffect(() => {
    setFieldErrors({}); setGeneralError('')
    setTimeout(() => (isRegister ? nameRef : emailRef).current?.focus(), 100)
  }, [mode])

  const validate = () => {
    const errs = {}
    if (isRegister && (!fullName.trim() || fullName.trim().length < 2)) errs.full_name = 'Name must be at least 2 characters'
    if (!email.trim() || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) errs.email = 'Enter a valid email'
    if (!password) errs.password = 'Password is required'
    else if (isRegister) {
      if (password.length < 8) errs.password = 'Min 8 characters'
      else if (!/[A-Z]/.test(password)) errs.password = 'Needs an uppercase letter'
      else if (!/[0-9]/.test(password)) errs.password = 'Needs a number'
    }
    setFieldErrors(errs)
    return Object.keys(errs).length === 0
  }

  const handleSubmit = async (e) => {
    e.preventDefault(); setGeneralError('')
    if (!validate()) return
    setLoading(true)
    try {
      if (isRegister) { await register(email, password, fullName); setSuccess(true); toast.success('Welcome to JobPilot! 🚀') }
      else { await login(email, password); toast.success('Welcome back!') }
    } catch (err) {
      const detail = err.response?.data?.detail
      if (detail?.field_errors) setFieldErrors(detail.field_errors)
      else setGeneralError(typeof detail === 'string' ? detail : 'Something went wrong')
    } finally { setLoading(false) }
  }

  const switchMode = () => { setMode(m => m === 'login' ? 'register' : 'login'); setPassword(''); setSuccess(false) }

  const inputClass = (err) => `w-full px-4 py-3 bg-gray-900/50 border rounded-xl text-sm text-white placeholder:text-gray-600 focus:outline-none focus:ring-2 transition-colors ${
    err ? 'border-red-500/50 focus:ring-red-500/30' : 'border-gray-800 focus:ring-blue-500/30 focus:border-gray-700'
  }`

  return (
    <div className="min-h-screen bg-[#0a0a0f] flex items-center justify-center px-4 py-12 relative overflow-hidden">
      {/* Floating orbs — same as homepage */}
      <div className="absolute inset-0 pointer-events-none">
        <div className="absolute w-[500px] h-[500px] -top-40 -right-40 bg-blue-600/15 rounded-full blur-[120px] animate-float-slow" />
        <div className="absolute w-[400px] h-[400px] -bottom-20 -left-20 bg-purple-600/15 rounded-full blur-[100px] animate-float-medium" />
      </div>

      <div className="relative z-10 w-full max-w-[420px]">
        {/* Back to home */}
        <button onClick={() => navigate('/')}
          className="flex items-center gap-1.5 text-sm text-gray-500 hover:text-gray-300 mb-8 transition-colors">
          <ArrowLeft className="w-4 h-4" /> Back to home
        </button>

        {/* Logo */}
        <div className="flex items-center gap-2.5 mb-8 animate-fade-in">
          <Rocket className="w-8 h-8 text-blue-400" />
          <span className="text-2xl font-bold text-white">
            Job<span className="bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">Pilot</span>
          </span>
        </div>

        {/* Header */}
        <div className="mb-6 animate-fade-in-up">
          <h1 className="text-2xl font-bold text-white">{isRegister ? 'Create your account' : 'Welcome back'}</h1>
          <p className="text-sm text-gray-500 mt-1">{isRegister ? 'Start automating your job search' : 'Sign in to your dashboard'}</p>
        </div>

        {generalError && (
          <div className="mb-4 flex items-center gap-2 bg-red-500/10 border border-red-500/20 text-red-400 text-sm rounded-xl px-4 py-3 animate-fade-in" role="alert">
            <X className="w-4 h-4 shrink-0" />{generalError}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4 animate-fade-in-up-delay" noValidate>
          {isRegister && (
            <div>
              <label className="block text-sm font-medium text-gray-400 mb-1.5">Full Name</label>
              <input ref={nameRef} type="text" value={fullName} onChange={e => { setFullName(e.target.value); setFieldErrors(p => ({...p, full_name: undefined})) }}
                placeholder="Your full name" autoComplete="name" className={inputClass(fieldErrors.full_name)} />
              {fieldErrors.full_name && <p className="mt-1 text-xs text-red-400">{fieldErrors.full_name}</p>}
            </div>
          )}

          <div>
            <label className="block text-sm font-medium text-gray-400 mb-1.5">Email</label>
            <input ref={emailRef} type="email" value={email} onChange={e => { setEmail(e.target.value); setFieldErrors(p => ({...p, email: undefined})) }}
              placeholder="you@example.com" autoComplete="email" className={inputClass(fieldErrors.email)} />
            {fieldErrors.email && <p className="mt-1 text-xs text-red-400">{fieldErrors.email}</p>}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-400 mb-1.5">Password</label>
            <div className="relative">
              <input type={showPassword ? 'text' : 'password'} value={password}
                onChange={e => { setPassword(e.target.value); setFieldErrors(p => ({...p, password: undefined})) }}
                placeholder={isRegister ? 'Min 8 chars, 1 uppercase, 1 number' : '••••••••'}
                autoComplete={isRegister ? 'new-password' : 'current-password'}
                className={inputClass(fieldErrors.password)} />
              <button type="button" onClick={() => setShowPassword(s => !s)} tabIndex={-1}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-600 hover:text-gray-400 transition-colors">
                {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
              </button>
            </div>
            {fieldErrors.password && <p className="mt-1 text-xs text-red-400">{fieldErrors.password}</p>}
            {isRegister && <PasswordStrength password={password} />}
          </div>

          <button type="submit" disabled={loading || success}
            className="w-full flex items-center justify-center gap-2 py-3 bg-gradient-to-r from-blue-600 to-purple-600 text-white font-semibold rounded-xl
              hover:shadow-lg hover:shadow-blue-500/20 active:scale-[0.98] disabled:opacity-60
              focus:outline-none focus:ring-2 focus:ring-blue-500/30 transition-all duration-200">
            {loading ? <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
              : success ? <><Check className="w-4 h-4" /> Done!</>
              : <>{isRegister ? 'Create Account' : 'Sign In'} <ArrowRight className="w-4 h-4" /></>}
          </button>
        </form>

        <div className="mt-6 text-center animate-fade-in-up-delay-2">
          <p className="text-sm text-gray-500">
            {isRegister ? 'Already have an account?' : "Don't have an account?"}{' '}
            <button type="button" onClick={switchMode}
              className="text-blue-400 font-semibold hover:text-blue-300 transition-colors">
              {isRegister ? 'Sign in' : 'Create one'}
            </button>
          </p>
        </div>
      </div>
    </div>
  )
}
