/**
 * Login / Register — premium split-screen auth experience.
 */
import { useState, useEffect, useRef } from 'react'
import { useAuth } from '../hooks/useAuth'
import { useToast } from '../hooks/useToast'
import { Rocket, Eye, EyeOff, Check, X, ArrowRight, Briefcase, Sparkles, Shield, Zap } from 'lucide-react'

const FEATURES = [
  { icon: Briefcase, title: 'Multi-Portal Scraping', desc: 'LinkedIn, Naukri, Indeed & more — all in one place' },
  { icon: Sparkles, title: 'AI Resume Tailoring', desc: 'Resumes customized for every job description' },
  { icon: Zap, title: 'Smart Job Matching', desc: 'AI scores jobs against your profile automatically' },
  { icon: Shield, title: 'Application Tracking', desc: 'Track every application from apply to offer' },
]

function PasswordStrength({ password }) {
  const checks = [
    { label: '8+ characters', pass: password.length >= 8 },
    { label: 'Uppercase letter', pass: /[A-Z]/.test(password) },
    { label: 'Number', pass: /[0-9]/.test(password) },
  ]
  const score = checks.filter(c => c.pass).length
  const colors = ['bg-gray-200', 'bg-red-400', 'bg-amber-400', 'bg-emerald-400']
  if (!password) return null
  return (
    <div className="mt-2 space-y-2">
      <div className="flex gap-1">
        {[0, 1, 2].map(i => (
          <div key={i} className={`h-1 flex-1 rounded-full transition-colors duration-300 ${i < score ? colors[score] : 'bg-gray-200 dark:bg-surface-700'}`} />
        ))}
      </div>
      <div className="flex flex-wrap gap-x-3 gap-y-1">
        {checks.map(c => (
          <span key={c.label} className={`flex items-center gap-1 text-xs transition-colors ${c.pass ? 'text-emerald-600 dark:text-emerald-400' : 'text-gray-400 dark:text-surface-500'}`}>
            {c.pass ? <Check className="w-3 h-3" /> : <X className="w-3 h-3" />}{c.label}
          </span>
        ))}
      </div>
    </div>
  )
}

function InputField({ id, label, type = 'text', value, onChange, error, autoComplete, placeholder, children }) {
  return (
    <div>
      <label htmlFor={id} className="block text-sm font-medium text-gray-700 dark:text-surface-300 mb-1.5">{label}</label>
      <div className="relative">
        <input id={id} type={type} value={value} onChange={onChange} autoComplete={autoComplete} placeholder={placeholder}
          aria-invalid={!!error} aria-describedby={error ? `${id}-error` : undefined}
          className={`w-full px-3.5 py-2.5 rounded-lg text-sm border transition-colors
            ${error
              ? 'border-red-400 dark:border-red-500 focus:ring-red-500 bg-red-50/50 dark:bg-red-950/10'
              : 'border-gray-300 dark:border-surface-600 focus:ring-brand-500 bg-white dark:bg-surface-800'}
            focus:outline-none focus:ring-2 focus:border-transparent
            text-gray-900 dark:text-white placeholder:text-gray-400 dark:placeholder:text-surface-500`} />
        {children}
      </div>
      {error && <p id={`${id}-error`} className="mt-1 text-xs text-red-500 dark:text-red-400" role="alert">{error}</p>}
    </div>
  )
}

export default function Login() {
  const { login, register } = useAuth()
  const toast = useToast()
  const [mode, setMode] = useState('login') // 'login' | 'register'
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

  // Focus first field on mode switch
  useEffect(() => {
    setFieldErrors({})
    setGeneralError('')
    setTimeout(() => (isRegister ? nameRef : emailRef).current?.focus(), 100)
  }, [mode])

  // Client-side validation
  const validate = () => {
    const errs = {}
    if (isRegister && (!fullName.trim() || fullName.trim().length < 2)) errs.full_name = 'Name must be at least 2 characters'
    if (!email.trim() || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) errs.email = 'Enter a valid email address'
    if (!password) errs.password = 'Password is required'
    else if (isRegister) {
      if (password.length < 8) errs.password = 'Password must be at least 8 characters'
      else if (!/[A-Z]/.test(password)) errs.password = 'Needs at least one uppercase letter'
      else if (!/[0-9]/.test(password)) errs.password = 'Needs at least one number'
    }
    setFieldErrors(errs)
    return Object.keys(errs).length === 0
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setGeneralError('')
    if (!validate()) return

    setLoading(true)
    try {
      if (isRegister) {
        await register(email, password, fullName)
        setSuccess(true)
        toast.success('Welcome to JobPilot! 🚀')
      } else {
        await login(email, password)
        toast.success('Welcome back!')
      }
    } catch (err) {
      const detail = err.response?.data?.detail
      if (detail?.field_errors) {
        setFieldErrors(detail.field_errors)
      } else {
        setGeneralError(typeof detail === 'string' ? detail : 'Something went wrong. Please try again.')
      }
    } finally {
      setLoading(false)
    }
  }

  const switchMode = () => {
    setMode(m => m === 'login' ? 'register' : 'login')
    setPassword('')
    setSuccess(false)
  }

  return (
    <div className="min-h-screen flex bg-gray-50 dark:bg-surface-950">
      {/* Left panel — branding (hidden on mobile) */}
      <div className="hidden lg:flex lg:w-[45%] xl:w-[40%] bg-gradient-to-br from-brand-600 via-brand-700 to-brand-900 text-white p-12 flex-col justify-between relative overflow-hidden">
        {/* Decorative circles */}
        <div className="absolute -top-24 -right-24 w-96 h-96 bg-white/5 rounded-full" />
        <div className="absolute -bottom-32 -left-32 w-[500px] h-[500px] bg-white/5 rounded-full" />

        <div className="relative z-10">
          <div className="flex items-center gap-2.5 mb-2">
            <Rocket className="w-8 h-8" />
            <span className="text-2xl font-bold">JobPilot</span>
          </div>
          <p className="text-brand-200 text-sm">AI-powered job hunting, automated.</p>
        </div>

        <div className="relative z-10 space-y-6">
          {FEATURES.map(({ icon: Icon, title, desc }) => (
            <div key={title} className="flex items-start gap-3">
              <div className="w-9 h-9 rounded-lg bg-white/10 flex items-center justify-center shrink-0 mt-0.5">
                <Icon className="w-4.5 h-4.5" />
              </div>
              <div>
                <p className="text-sm font-semibold">{title}</p>
                <p className="text-xs text-brand-200 mt-0.5">{desc}</p>
              </div>
            </div>
          ))}
        </div>

        <p className="relative z-10 text-xs text-brand-300">Built by Rishi Raj — because job hunting should be automated.</p>
      </div>

      {/* Right panel — form */}
      <div className="flex-1 flex items-center justify-center px-6 py-12">
        <div className="w-full max-w-[400px]">
          {/* Mobile logo */}
          <div className="flex items-center justify-center gap-2 mb-8 lg:hidden">
            <Rocket className="w-7 h-7 text-brand-600 dark:text-brand-400" />
            <span className="text-xl font-bold text-gray-900 dark:text-white">
              Job<span className="text-brand-600 dark:text-brand-400">Pilot</span>
            </span>
          </div>

          <div className="mb-6">
            <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
              {isRegister ? 'Create your account' : 'Welcome back'}
            </h1>
            <p className="text-sm text-gray-500 dark:text-surface-400 mt-1">
              {isRegister ? 'Start automating your job search' : 'Sign in to your JobPilot dashboard'}
            </p>
          </div>

          {generalError && (
            <div className="mb-4 flex items-center gap-2 bg-red-50 dark:bg-red-950/30 border border-red-200 dark:border-red-800 text-red-700 dark:text-red-400 text-sm rounded-lg px-3.5 py-2.5" role="alert">
              <X className="w-4 h-4 shrink-0" />
              {generalError}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4" noValidate>
            {isRegister && (
              <InputField id="fullname" label="Full Name" value={fullName} placeholder="Rishi Raj"
                onChange={e => { setFullName(e.target.value); setFieldErrors(p => ({ ...p, full_name: undefined })) }}
                error={fieldErrors.full_name} autoComplete="name" ref={nameRef} />
            )}

            <InputField id="email" label="Email" type="email" value={email} placeholder="you@example.com"
              onChange={e => { setEmail(e.target.value); setFieldErrors(p => ({ ...p, email: undefined })) }}
              error={fieldErrors.email} autoComplete="email" ref={emailRef} />

            <div>
              <InputField id="password" label="Password" type={showPassword ? 'text' : 'password'}
                value={password} placeholder={isRegister ? 'Min 8 chars, 1 uppercase, 1 number' : '••••••••'}
                onChange={e => { setPassword(e.target.value); setFieldErrors(p => ({ ...p, password: undefined })) }}
                error={fieldErrors.password} autoComplete={isRegister ? 'new-password' : 'current-password'}>
                <button type="button" onClick={() => setShowPassword(s => !s)} tabIndex={-1}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 dark:hover:text-surface-300"
                  aria-label={showPassword ? 'Hide password' : 'Show password'}>
                  {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </InputField>
              {isRegister && <PasswordStrength password={password} />}
            </div>

            <button type="submit" disabled={loading || success}
              className="w-full flex items-center justify-center gap-2 py-2.5 bg-brand-600 text-white rounded-lg text-sm font-semibold
                hover:bg-brand-700 active:scale-[0.98] disabled:opacity-60 disabled:cursor-not-allowed
                focus:outline-none focus:ring-2 focus:ring-brand-500 focus:ring-offset-2 dark:focus:ring-offset-surface-950
                transition-all duration-150">
              {loading ? (
                <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
              ) : success ? (
                <><Check className="w-4 h-4" /> Done!</>
              ) : (
                <>{isRegister ? 'Create Account' : 'Sign In'} <ArrowRight className="w-4 h-4" /></>
              )}
            </button>
          </form>

          <div className="mt-6 text-center">
            <p className="text-sm text-gray-500 dark:text-surface-400">
              {isRegister ? 'Already have an account?' : "Don't have an account?"}{' '}
              <button type="button" onClick={switchMode}
                className="text-brand-600 dark:text-brand-400 font-semibold hover:underline underline-offset-2">
                {isRegister ? 'Sign in' : 'Create one'}
              </button>
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
