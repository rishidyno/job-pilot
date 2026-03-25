/**
 * Toast notification system — replaces all alert() calls.
 * Usage:
 *   import { useToast, ToastProvider } from './hooks/useToast'
 *   const toast = useToast()
 *   toast.success('Saved!')
 *   toast.error('Something went wrong')
 */
import { createContext, useContext, useState, useCallback, useRef } from 'react'
import { CheckCircle, XCircle, AlertTriangle, Info, X } from 'lucide-react'

const ToastContext = createContext(null)

const ICONS = {
  success: CheckCircle,
  error: XCircle,
  warning: AlertTriangle,
  info: Info,
}

const COLORS = {
  success: 'bg-emerald-50 border-emerald-200 text-emerald-800',
  error: 'bg-red-50 border-red-200 text-red-800',
  warning: 'bg-amber-50 border-amber-200 text-amber-800',
  info: 'bg-blue-50 border-blue-200 text-blue-800',
}

const ICON_COLORS = {
  success: 'text-emerald-500',
  error: 'text-red-500',
  warning: 'text-amber-500',
  info: 'text-blue-500',
}

let toastId = 0

export function ToastProvider({ children }) {
  const [toasts, setToasts] = useState([])
  const timers = useRef({})

  const remove = useCallback((id) => {
    clearTimeout(timers.current[id])
    delete timers.current[id]
    setToasts(prev => prev.map(t => t.id === id ? { ...t, exiting: true } : t))
    setTimeout(() => setToasts(prev => prev.filter(t => t.id !== id)), 300)
  }, [])

  const add = useCallback((type, message, duration = 4000) => {
    const id = ++toastId
    setToasts(prev => [...prev, { id, type, message, exiting: false }])
    timers.current[id] = setTimeout(() => remove(id), duration)
    return id
  }, [remove])

  const api = {
    success: (msg, dur) => add('success', msg, dur),
    error: (msg, dur) => add('error', msg, dur ?? 6000),
    warning: (msg, dur) => add('warning', msg, dur),
    info: (msg, dur) => add('info', msg, dur),
  }

  return (
    <ToastContext.Provider value={api}>
      {children}
      {/* Toast container — fixed top-right, stacks vertically */}
      <div className="fixed top-4 right-4 z-[100] flex flex-col gap-2 max-w-sm w-full pointer-events-none"
        aria-live="polite" aria-label="Notifications">
        {toasts.map(toast => {
          const Icon = ICONS[toast.type]
          return (
            <div key={toast.id}
              role="alert"
              className={`${toast.exiting ? 'toast-exit' : 'toast-enter'} pointer-events-auto flex items-start gap-3 px-4 py-3 rounded-xl border shadow-lg ${COLORS[toast.type]}`}>
              <Icon className={`w-5 h-5 shrink-0 mt-0.5 ${ICON_COLORS[toast.type]}`} />
              <p className="text-sm font-medium flex-1">{toast.message}</p>
              <button onClick={() => remove(toast.id)}
                className="shrink-0 p-0.5 rounded-md hover:bg-black/5"
                aria-label="Dismiss notification">
                <X className="w-4 h-4 opacity-50" />
              </button>
            </div>
          )
        })}
      </div>
    </ToastContext.Provider>
  )
}

export const useToast = () => useContext(ToastContext)
